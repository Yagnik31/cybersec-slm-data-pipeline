#!/usr/bin/env python3
"""Content hashing, near-duplicate detection, and failure tracking.

Covers three flowchart bands:
  * Content Hash Generation — ``hashlib.sha256`` over content-only fields, so the
    fingerprint is time-independent (timestamps/ids excluded).
  * Near Duplicate Check    — ``datasketch`` MinHash + MinHashLSH at Jaccard 0.65,
    with state rebuildable from an existing ``dataset.jsonl`` (``pathlib``).
  * FailureTracker          — per-source reject counts; a source that crosses the
    hard-pause threshold (20) is flagged for a trip back to cleaning.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from datasketch import MinHash, MinHashLSH

from ..core import logger

# near-dup tuning (mirrors the diagram: threshold 0.65)
LSH_THRESHOLD = 0.65
MINHASH_PERM = 128
SHINGLE_SIZE = 5               # word-shingle length
HARD_PAUSE_FAILURES = 20      # per-source rejects before a hard pause

_WORD = re.compile(r"\w+")


def _norm_for_hash(text: str) -> str:
    """Lowercase + collapse whitespace: a content-only, time-independent view."""
    return " ".join(_WORD.findall(text.lower()))


def content_hash(text: str) -> str:
    """sha256 fingerprint of the normalized content (excludes ids/timestamps)."""
    return hashlib.sha256(_norm_for_hash(text).encode("utf-8")).hexdigest()


def _minhash(text: str) -> MinHash:
    m = MinHash(num_perm=MINHASH_PERM)
    tokens = _WORD.findall(text.lower())
    if len(tokens) < SHINGLE_SIZE:
        shingles = {" ".join(tokens)} if tokens else set()
    else:
        shingles = {" ".join(tokens[i:i + SHINGLE_SIZE])
                    for i in range(len(tokens) - SHINGLE_SIZE + 1)}
    for sh in shingles:
        m.update(sh.encode("utf-8"))
    return m


class NearDuplicateIndex:
    """Exact (sha256) + near-dup (MinHash/LSH) membership with resumable state.

    ``seen`` holds exact content hashes for O(1) exact-dup rejection; the LSH
    index catches near-duplicates above the Jaccard threshold. ``add`` commits a
    record to both (the flowchart's "Update Hash List").
    """

    def __init__(self, threshold: float = LSH_THRESHOLD):
        self.lsh = MinHashLSH(threshold=threshold, num_perm=MINHASH_PERM)
        self.seen: set[str] = set()
        self._n = 0

    def is_duplicate(self, text: str, chash: str) -> tuple[bool, str]:
        """Return (is_dup, reason) without mutating state."""
        if chash in self.seen:
            return True, "exact"
        m = _minhash(text)
        if self.lsh.query(m):
            return True, "near"
        return False, ""

    def add(self, text: str, chash: str, key: str) -> None:
        """Commit a kept record: register its exact hash and LSH signature."""
        self.seen.add(chash)
        try:
            self.lsh.insert(key, _minhash(text))
        except ValueError:
            pass                # duplicate LSH key (already inserted) — ignore
        self._n += 1

    def rebuild_from_jsonl(self, path: str | Path) -> int:
        """Repopulate state from an existing dataset.jsonl so runs are resumable.

        Reads each prior record's stored ``content_hash``/``text`` back into the
        exact set and LSH index. Returns the number of records reloaded.
        """
        p = Path(path)
        if not p.exists():
            return 0
        n = 0
        with p.open(encoding="utf-8", errors="replace") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                text = rec.get("text") or ""
                chash = rec.get("content_hash") or content_hash(text)
                key = rec.get("id") or chash
                if chash in self.seen:
                    continue
                self.add(text, chash, key)
                n += 1
        logger.info(f"normalize: rebuilt dedup state from {p.name} ({n} records)")
        return n

    def __len__(self) -> int:
        return self._n


class FailureTracker:
    """Per-source reject accounting (flowchart: FailureTracker.classify_failure).

    Each rejected record is recorded against its source. When a single source
    crosses :data:`HARD_PAUSE_FAILURES`, :meth:`should_pause` flips True once so
    the caller can stop that source and send it back to the cleaning stage.
    """

    def __init__(self, threshold: int = HARD_PAUSE_FAILURES):
        self.threshold = threshold
        self.failures: Counter[str] = Counter()
        self.reasons: Counter[str] = Counter()
        self._paused: set[str] = set()

    def classify_failure(self, source: str, reason: str) -> None:
        self.failures[source] += 1
        self.reasons[reason] += 1

    def should_pause(self, source: str) -> bool:
        """True exactly once, when ``source`` first crosses the threshold."""
        if self.failures[source] >= self.threshold and source not in self._paused:
            self._paused.add(source)
            logger.error(f"normalize: HARD PAUSE — source '{source}' hit "
                         f"{self.failures[source]} rejects (>= {self.threshold}); "
                         f"send back to cleaning")
            return True
        return False

    def paused_sources(self) -> set[str]:
        return set(self._paused)
