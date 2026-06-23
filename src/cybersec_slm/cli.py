#!/usr/bin/env python3
"""Unified command-line entry point for the pipeline.

Full pipeline (end-to-end):
    cybersec-slm all

Individual stages:
    cybersec-slm extract  [scrape|fetch|html|nvd|all|table] [--nvd-key KEY]
    cybersec-slm clean    [all|sanitize|dedup|pii|lang|report|balance] [--limit N] [--cap N]
    cybersec-slm chunk    [--chunk-size N] [--overlap N]
    cybersec-slm split    [--ratio 0.8 0.1 0.1] [--seed 42]
    cybersec-slm validate
"""

from __future__ import annotations

import argparse
import os


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cybersec-slm",
        description="Cybersecurity SLM data pipeline.",
    )
    sub = p.add_subparsers(dest="stage", required=True)

    # ── extract ──────────────────────────────────────────────────────────────
    e = sub.add_parser("extract", help="pull + normalise sources -> raw_data/")
    e.add_argument("action", nargs="?", default="all",
                   choices=["scrape", "fetch", "html", "nvd", "all", "table"])
    e.add_argument("--nvd-key", default=None,
                   help="NVD API key (env: NVD_API_KEY). Higher rate-limit.")

    # ── clean ─────────────────────────────────────────────────────────────────
    c = sub.add_parser("clean", help="clean raw_data/ -> cleaned/")
    c.add_argument("action", nargs="?", default="all",
                   choices=["all", "sanitize", "dedup", "pii", "lang",
                            "report", "balance"])
    c.add_argument("--limit", type=int, default=None,
                   help="cap records per file (smoke test)")
    c.add_argument("--cap", type=int, default=None,
                   help="max records per domain (balance action)")

    # ── chunk ─────────────────────────────────────────────────────────────────
    ch = sub.add_parser("chunk",
                        help="split cleaned records into training windows -> chunked/")
    ch.add_argument("--chunk-size", type=int, default=4000,
                    help="target chunk size in characters (default 4000 ≈ 1024 tokens)")
    ch.add_argument("--overlap", type=int, default=200,
                    help="overlap between consecutive chunks in characters (default 200)")

    # ── split ─────────────────────────────────────────────────────────────────
    sp = sub.add_parser("split",
                        help="stratified train/val/test split -> train/ val/ test/")
    sp.add_argument("--ratio", type=float, nargs=3, default=[0.8, 0.1, 0.1],
                    metavar=("TRAIN", "VAL", "TEST"),
                    help="split ratios, must sum to 1.0 (default: 0.8 0.1 0.1)")
    sp.add_argument("--seed", type=int, default=42)

    # ── validate ──────────────────────────────────────────────────────────────
    sub.add_parser("validate",
                   help="validate cleaned/ records against Pydantic schema")

    # ── all ───────────────────────────────────────────────────────────────────
    sub.add_parser("all", help="extract -> clean -> chunk -> split (full pipeline)")

    return p


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)

    if args.stage == "extract":
        from .extraction import run as extraction
        extraction.run(args.action,
                       nvd_key=args.nvd_key or os.environ.get("NVD_API_KEY"))

    elif args.stage == "clean":
        from .cleaning import run as cleaning
        if args.action == "balance":
            from .cleaning.balance import apply_cap, check_balance
            check_balance()
            if args.cap:
                apply_cap(args.cap)
        else:
            cleaning.run(args.action, limit=args.limit)

    elif args.stage == "chunk":
        from .chunking.chunker import run_chunking
        run_chunking(chunk_chars=args.chunk_size, overlap_chars=args.overlap)

    elif args.stage == "split":
        from .splitting.split import run_split
        run_split(ratio=tuple(args.ratio))  # type: ignore[arg-type]

    elif args.stage == "validate":
        from .cleaning.schema import validate_corpus
        validate_corpus()

    elif args.stage == "all":
        from .extraction import run as extraction
        from .cleaning import run as cleaning
        from .chunking.chunker import run_chunking
        from .splitting.split import run_split
        extraction.run("all")
        cleaning.run("all")
        run_chunking()
        run_split()


if __name__ == "__main__":
    main()
