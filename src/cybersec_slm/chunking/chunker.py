#!/usr/bin/env python3
"""Text chunking — splits cleaned records into fixed-size training windows.

Reads cleaned/ JSONL, splits each `text` field into overlapping chunks, writes
to chunked/ (mirrors the same domain/source layout). Every chunk inherits all
provenance metadata from its parent record plus _chunk_index / _chunk_total.

Splitting strategy (in priority order):
  1. Paragraph boundaries (double newline)
  2. Sentence boundaries (. ! ? followed by whitespace)
  3. Hard character cut (last resort, avoids mid-word breaks)

Token counting:
  - tiktoken (cl100k_base) if installed — accurate, model-agnostic
  - Otherwise 1 token ≈ 4 characters

Defaults:  chunk_chars=4000 (~1024 tokens), overlap_chars=200 (~50 tokens)
"""

from __future__ import annotations

import os
import re

from ..core import CLEANED, JsonlWriter, iter_jsonl, logger, try_import

CHUNKED = os.path.join(os.path.dirname(CLEANED), "chunked")

_PARA_RE = re.compile(r"\n{2,}")
_SENT_RE = re.compile(r"(?<=[.!?])\s+")


def _make_token_counter():
    tiktoken = try_import("tiktoken")
    if tiktoken is not None:
        enc = tiktoken.get_encoding("cl100k_base")
        return lambda s: len(enc.encode(s))
    return lambda s: len(s) // 4


_count_tokens = _make_token_counter()


def split_text(text: str, chunk_chars: int = 4000,
               overlap_chars: int = 200) -> list[str]:
    """Split text into overlapping chunks at natural boundaries.

    Returns a list of strings. If text fits in one chunk, returns [text].
    Overlap is applied by prepending the tail of the previous chunk so the
    model sees context across chunk boundaries.
    """
    text = text.strip()
    if not text or len(text) <= chunk_chars:
        return [text] if text else []

    raw_chunks = _split_into_chunks(text, chunk_chars)

    if overlap_chars <= 0 or len(raw_chunks) <= 1:
        return raw_chunks

    overlapped = [raw_chunks[0]]
    for i in range(1, len(raw_chunks)):
        tail = raw_chunks[i - 1][-overlap_chars:].lstrip()
        overlapped.append(tail + "\n" + raw_chunks[i])
    return overlapped


def _split_into_chunks(text: str, chunk_chars: int) -> list[str]:
    """Split without overlap — handles paragraph, sentence, and hard cuts."""
    paragraphs = [p.strip() for p in _PARA_RE.split(text) if p.strip()]

    chunks: list[str] = []
    bucket: list[str] = []
    bucket_len = 0

    for para in paragraphs:
        if bucket_len + len(para) + 2 <= chunk_chars:
            bucket.append(para)
            bucket_len += len(para) + 2
        else:
            if bucket:
                chunks.append("\n\n".join(bucket))
                bucket, bucket_len = [], 0
            if len(para) <= chunk_chars:
                bucket.append(para)
                bucket_len = len(para)
            else:
                chunks.extend(_sentence_split(para, chunk_chars))

    if bucket:
        chunks.append("\n\n".join(bucket))
    return chunks or [text]


def _sentence_split(text: str, chunk_chars: int) -> list[str]:
    """Split a single long paragraph at sentence boundaries."""
    sentences = _SENT_RE.split(text)
    chunks: list[str] = []
    bucket: list[str] = []
    bucket_len = 0

    for sent in sentences:
        if bucket_len + len(sent) + 1 <= chunk_chars:
            bucket.append(sent)
            bucket_len += len(sent) + 1
        else:
            if bucket:
                chunks.append(" ".join(bucket))
                bucket, bucket_len = [], 0
            if len(sent) <= chunk_chars:
                bucket.append(sent)
                bucket_len = len(sent)
            else:
                # Hard cut as last resort — split at word boundaries.
                chunks.extend(_hard_cut(sent, chunk_chars))

    if bucket:
        chunks.append(" ".join(bucket))
    return chunks or [text]


def _hard_cut(text: str, chunk_chars: int) -> list[str]:
    """Hard-cut oversized text, preferring word boundaries."""
    parts = []
    while len(text) > chunk_chars:
        cut = chunk_chars
        space = text.rfind(" ", chunk_chars // 2, chunk_chars)
        if space != -1:
            cut = space
        parts.append(text[:cut].strip())
        text = text[cut:].strip()
    if text:
        parts.append(text)
    return parts


def chunk_record(rec: dict, chunk_chars: int = 4000,
                 overlap_chars: int = 200) -> list[dict]:
    """Expand one cleaned record into N chunk records.

    Single-chunk records are returned as-is (no _chunk_* metadata added)
    to avoid bloating records that are already short enough.
    """
    text = rec.get("text", "")
    if not isinstance(text, str) or not text.strip():
        return []
    parts = split_text(text, chunk_chars, overlap_chars)
    if not parts:
        return []
    if len(parts) == 1:
        return [rec]
    return [
        {**rec, "text": chunk, "_chunk_index": i, "_chunk_total": len(parts)}
        for i, chunk in enumerate(parts)
    ]


def run_chunking(input_dir: str = CLEANED, output_dir: str = CHUNKED,
                 chunk_chars: int = 4000, overlap_chars: int = 200) -> dict:
    """Chunk every record in input_dir and write to output_dir.

    Returns a stats dict: {files, in, out, skipped_empty, avg_chunks}.
    """
    stats: dict[str, int | float] = {
        "files": 0, "in": 0, "out": 0, "skipped_empty": 0,
    }
    if not os.path.isdir(input_dir):
        logger.warning(f"chunking: input dir not found: {input_dir} "
                       "(run the cleaning stage first)")
        return stats

    for root, _dirs, files in os.walk(input_dir):
        for fn in files:
            if not fn.endswith(".jsonl"):
                continue
            src = os.path.join(root, fn)
            rel = os.path.relpath(src, input_dir).replace("\\", "/")
            dst = os.path.join(output_dir, rel)
            w = JsonlWriter(dst)
            try:
                for rec in iter_jsonl(src):
                    stats["in"] += 1
                    chunks = chunk_record(rec, chunk_chars, overlap_chars)
                    if not chunks:
                        stats["skipped_empty"] += 1
                        continue
                    for chunk in chunks:
                        w.write(chunk)
                        stats["out"] += 1
            finally:
                w.close()
            stats["files"] += 1

    avg = stats["out"] / stats["in"] if stats["in"] else 0.0
    logger.info(
        f"chunking: {stats['files']} files | "
        f"in={stats['in']:,} records | out={stats['out']:,} chunks "
        f"(avg {avg:.1f}x) | output -> {output_dir}"
    )
    return stats
