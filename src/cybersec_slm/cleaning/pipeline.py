#!/usr/bin/env python3
"""Pipeline — runs the cleaning stages in flowchart order over raw_data.

    Sanitize -> Anomaly Check -> Dedup -> PII Removal -> Language filter -> cleaned/

Reads the extraction output under raw_data/ and mirrors its layout into
cleaned/ (passed), flagged/ (behavioral anomalies for annotation) and dropped/
(structural + dedup + language drops, each annotated with a reason). A per-file
report is written to logs/clean_report.csv.
"""

from __future__ import annotations

import csv
import os

from . import anomaly
from . import sanitize
from .common import (OUT_CLEANED, OUT_DROPPED, OUT_FLAGGED, OUT_STAGES,
                    PARSE_ERROR, RAW_DATA, REPORTS, JsonlWriter,
                    find_input_files, iter_jsonl, logger, text_of)
from .dedup import Deduper
from .langfilter import LangFilter
from .pii import Redactor

REPORT_COLS = ["sub_domain", "source", "file", "in", "sanitized", "struct_fixed",
               "struct_dropped", "behavioral_flagged", "exact_dups", "near_dups",
               "pii_redacted", "non_en_dropped", "out"]


def _annotate(rec, sub, source, relfile, stage, reason):
    out = dict(rec)
    out["_sub_domain"] = sub
    out["_source"] = source
    out["_file"] = relfile
    out["_stage"] = stage
    out["_reason"] = reason
    return out


def _new_counts():
    return {k: 0 for k in REPORT_COLS[3:]}


def run_all(input_dir: str = RAW_DATA, limit: int | None = None) -> list[dict]:
    """Full pipeline. `limit` optionally caps records per file (for smoke runs)."""
    deduper = Deduper()
    redactor = Redactor()
    langf = LangFilter()
    logger.info(f"cleaning input: {input_dir}")
    logger.info(f"backends -> dedup:{deduper.backend} pii:{redactor.engine} "
                f"lang:{langf.backend}")

    rows: list[dict] = []
    files = list(find_input_files(input_dir))
    if not files:
        logger.warning(f"no .jsonl files under {input_dir} "
                       "(run the extraction stage first)")
        return rows

    for ap, sub, source, rel in files:
        c = _new_counts()
        cw = JsonlWriter(os.path.join(OUT_CLEANED, rel))
        fw = JsonlWriter(os.path.join(OUT_FLAGGED, rel))
        dw = JsonlWriter(os.path.join(OUT_DROPPED, rel))
        try:
            for i, rec in enumerate(iter_jsonl(ap)):
                if limit is not None and i >= limit:
                    break
                c["in"] += 1

                if rec.get(PARSE_ERROR):
                    c["struct_dropped"] += 1
                    dw.write(_annotate(rec, sub, source, rel, "anomaly", "json parse error"))
                    continue

                pre_bucket, _ = anomaly.classify(rec)
                rec2, changed = sanitize.sanitize_record(rec)
                if changed:
                    c["sanitized"] += 1

                bucket, reason = anomaly.classify(rec2)
                if bucket == "structural":
                    c["struct_dropped"] += 1
                    dw.write(_annotate(rec2, sub, source, rel, "anomaly", reason))
                    continue
                if pre_bucket == "structural":      # sanitize rescued it
                    c["struct_fixed"] += 1
                if bucket == "behavioral":
                    c["behavioral_flagged"] += 1
                    fw.write(_annotate(rec2, sub, source, rel, "anomaly", reason))
                    continue

                is_dup, dreason = deduper.add(text_of(rec2))
                if is_dup:
                    if "exact" in dreason:
                        c["exact_dups"] += 1
                    else:
                        c["near_dups"] += 1
                    dw.write(_annotate(rec2, sub, source, rel, "dedup", dreason))
                    continue

                new_text, npii = redactor.redact(text_of(rec2))
                if npii:
                    c["pii_redacted"] += 1
                    rec2["text"] = new_text

                if not langf.is_allowed(text_of(rec2)):
                    c["non_en_dropped"] += 1
                    lang = langf.detect(text_of(rec2))
                    dw.write(_annotate(rec2, sub, source, rel, "langfilter",
                                       f"non-allowed language: {lang}"))
                    continue

                cw.write(rec2)
                c["out"] += 1
        finally:
            cw.close(); fw.close(); dw.close()

        logger.info(f"  {rel}: in={c['in']} out={c['out']} "
                    f"flagged={c['behavioral_flagged']} "
                    f"dropped={c['struct_dropped']+c['exact_dups']+c['near_dups']+c['non_en_dropped']}")
        rows.append({"sub_domain": sub, "source": source, "file": rel, **c})

    _write_report(rows)
    return rows


def _write_report(rows: list[dict]) -> str:
    os.makedirs(REPORTS, exist_ok=True)
    path = os.path.join(REPORTS, "clean_report.csv")
    totals = _new_counts()
    for r in rows:
        for k in totals:
            totals[k] += r.get(k, 0)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=REPORT_COLS)
        w.writeheader()
        for r in rows:
            w.writerow(r)
        w.writerow({"sub_domain": "TOTAL", "source": "", "file": f"{len(rows)} files",
                    **totals})
    logger.info(f"report -> {path}")
    logger.info("TOTAL " + " ".join(f"{k}={totals[k]}" for k in
                ("in", "out", "struct_dropped", "behavioral_flagged",
                 "exact_dups", "near_dups", "pii_redacted", "non_en_dropped")))
    return path


# ---------------------------------------------------- single-stage diagnostics
def run_single_stage(stage: str, input_dir: str = RAW_DATA,
                     limit: int | None = None) -> dict:
    """Apply one stage across the input into _stages/<stage>/ for inspection.

    Not the production path (use run_all); a debugging aid for one transform.
    """
    if stage not in ("sanitize", "dedup", "pii", "lang"):
        raise ValueError(f"unknown stage: {stage}")
    deduper = Deduper() if stage == "dedup" else None
    redactor = Redactor() if stage == "pii" else None
    langf = LangFilter() if stage == "lang" else None
    stats = {"in": 0, "out": 0, "affected": 0}

    for ap, _sub, _source, rel in find_input_files(input_dir):
        w = JsonlWriter(os.path.join(OUT_STAGES, stage, rel))
        try:
            for i, rec in enumerate(iter_jsonl(ap)):
                if limit is not None and i >= limit:
                    break
                if rec.get(PARSE_ERROR):
                    continue
                stats["in"] += 1
                if stage == "sanitize":
                    rec2, changed = sanitize.sanitize_record(rec)
                    stats["affected"] += int(changed)
                    w.write(rec2); stats["out"] += 1
                elif stage == "dedup":
                    is_dup, _ = deduper.add(text_of(rec))
                    if is_dup:
                        stats["affected"] += 1
                        continue
                    w.write(rec); stats["out"] += 1
                elif stage == "pii":
                    nt, n = redactor.redact(text_of(rec))
                    if n:
                        stats["affected"] += 1
                        rec = {**rec, "text": nt}
                    w.write(rec); stats["out"] += 1
                elif stage == "lang":
                    if langf.is_allowed(text_of(rec)):
                        w.write(rec); stats["out"] += 1
                    else:
                        stats["affected"] += 1
        finally:
            w.close()
    logger.info(f"stage '{stage}': in={stats['in']} out={stats['out']} "
                f"affected={stats['affected']} -> {os.path.join(OUT_STAGES, stage)}")
    return stats


def build_report_from_outputs() -> str:
    """Recount existing cleaned/flagged/dropped trees into a summary line."""
    def count_tree(root):
        n = 0
        for r, _d, fs in os.walk(root):
            for fn in fs:
                if fn.endswith(".jsonl"):
                    with open(os.path.join(r, fn), encoding="utf-8", errors="replace") as f:
                        n += sum(1 for ln in f if ln.strip())
        return n
    cleaned = count_tree(OUT_CLEANED)
    flagged = count_tree(OUT_FLAGGED)
    dropped = count_tree(OUT_DROPPED)
    logger.info(f"outputs -> cleaned={cleaned} flagged={flagged} dropped={dropped}")
    return f"cleaned={cleaned} flagged={flagged} dropped={dropped}"
