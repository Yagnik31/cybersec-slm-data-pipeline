#!/usr/bin/env python3
"""Stratified train / val / test split.

Reads chunked/ (falls back to cleaned/ if chunked/ is empty) and writes:
    train/   val/   test/

Stratified by domain — each split gets a proportional slice of every domain
so no domain is missing from val or test. Records within each domain are
shuffled before splitting to avoid order bias from the crawl sequence.

Default ratio: 80 / 10 / 10. Configurable via ratio=(train, val, test).

    from cybersec_slm.splitting.split import run_split
    run_split()                               # 80/10/10 from chunked/
    run_split(ratio=(0.9, 0.05, 0.05))        # 90/5/5
"""

from __future__ import annotations

import csv
import os
import random

from ..core import CLEANED, JsonlWriter, iter_jsonl, logger

_CHUNKED = os.path.join(os.path.dirname(CLEANED), "chunked")
_TRAIN = os.path.join(os.path.dirname(CLEANED), "train")
_VAL = os.path.join(os.path.dirname(CLEANED), "val")
_TEST = os.path.join(os.path.dirname(CLEANED), "test")


def _collect_by_domain(input_dir: str) -> dict[str, list[dict]]:
    """Walk input_dir and group records by top-level domain folder."""
    by_domain: dict[str, list[dict]] = {}
    for entry in os.scandir(input_dir):
        if not entry.is_dir():
            continue
        domain = entry.name
        recs: list[dict] = []
        for root, _dirs, files in os.walk(entry.path):
            for fn in sorted(files):
                if not fn.endswith(".jsonl"):
                    continue
                recs.extend(iter_jsonl(os.path.join(root, fn)))
        if recs:
            by_domain[domain] = recs
    return by_domain


def _write_split(records: list[dict], domain: str, split_dir: str) -> int:
    path = os.path.join(split_dir, domain, f"{domain}.jsonl")
    w = JsonlWriter(path)
    for rec in records:
        w.write(rec)
    w.close()
    return len(records)


def run_split(
    input_dir: str | None = None,
    train_dir: str = _TRAIN,
    val_dir: str = _VAL,
    test_dir: str = _TEST,
    ratio: tuple[float, float, float] = (0.8, 0.1, 0.1),
    seed: int = 42,
) -> dict:
    """Stratified split across domains.

    Returns stats dict with per-split and per-domain counts.
    """
    r_train, r_val, r_test = ratio
    assert abs(r_train + r_val + r_test - 1.0) < 1e-6, "ratios must sum to 1.0"

    # Auto-select input: prefer chunked/ if it has content.
    if input_dir is None:
        if os.path.isdir(_CHUNKED) and any(
            f.endswith(".jsonl")
            for _, _, fs in os.walk(_CHUNKED)
            for f in fs
        ):
            input_dir = _CHUNKED
            logger.info("split: using chunked/ as input")
        else:
            input_dir = CLEANED
            logger.info("split: chunked/ empty, falling back to cleaned/")

    if not os.path.isdir(input_dir):
        logger.warning(f"split: {input_dir} not found — run cleaning/chunking first")
        return {}

    rng = random.Random(seed)
    by_domain = _collect_by_domain(input_dir)
    if not by_domain:
        logger.warning("split: no records found")
        return {}

    totals = {"train": 0, "val": 0, "test": 0}
    report_rows: list[dict] = []

    for domain, recs in sorted(by_domain.items()):
        rng.shuffle(recs)
        n = len(recs)
        n_val = max(1, round(n * r_val))
        n_test = max(1, round(n * r_test))
        n_train = n - n_val - n_test

        train_recs = recs[:n_train]
        val_recs = recs[n_train: n_train + n_val]
        test_recs = recs[n_train + n_val:]

        _write_split(train_recs, domain, train_dir)
        _write_split(val_recs, domain, val_dir)
        _write_split(test_recs, domain, test_dir)

        totals["train"] += len(train_recs)
        totals["val"] += len(val_recs)
        totals["test"] += len(test_recs)
        report_rows.append({
            "domain": domain, "total": n,
            "train": len(train_recs), "val": len(val_recs), "test": len(test_recs),
        })
        logger.info(f"  {domain}: {n:,} -> "
                    f"train={len(train_recs):,} val={len(val_recs):,} test={len(test_recs):,}")

    grand = totals["train"] + totals["val"] + totals["test"]
    logger.info(f"split total: {grand:,} records | "
                f"train={totals['train']:,} ({100*totals['train']/grand:.1f}%) | "
                f"val={totals['val']:,} ({100*totals['val']/grand:.1f}%) | "
                f"test={totals['test']:,} ({100*totals['test']/grand:.1f}%)")

    # Write report.
    logs_dir = os.path.join(os.path.dirname(CLEANED), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    report_path = os.path.join(logs_dir, "split_report.csv")
    with open(report_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["domain", "total", "train", "val", "test"])
        w.writeheader()
        w.writerows(report_rows)
        w.writerow({"domain": "TOTAL", **totals, "total": grand})
    logger.info(f"split report -> {report_path}")
    return {**totals, "domains": len(by_domain)}
