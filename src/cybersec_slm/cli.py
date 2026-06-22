#!/usr/bin/env python3
"""Unified command-line entry point for the pipeline.

    cybersec-slm extract [scrape|fetch|html|all|table]
    cybersec-slm clean   [all|sanitize|dedup|pii|lang|report] [--limit N]
    cybersec-slm all                       # extract all, then clean all

Equivalent to ``python -m cybersec_slm ...``.
"""

from __future__ import annotations

import argparse

from .cleaning import run as cleaning
from .extraction import run as extraction


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="cybersec-slm",
                                description="Cybersecurity SLM data pipeline.")
    sub = p.add_subparsers(dest="stage", required=True)

    e = sub.add_parser("extract", help="pull + normalize sources -> raw_data/")
    e.add_argument("action", nargs="?", default="all",
                   choices=["scrape", "fetch", "html", "all", "table"])

    c = sub.add_parser("clean", help="clean raw_data/ -> cleaned/")
    c.add_argument("action", nargs="?", default="all",
                   choices=["all", "sanitize", "dedup", "pii", "lang", "report"])
    c.add_argument("--limit", type=int, default=None,
                   help="cap records per file (smoke test)")

    sub.add_parser("all", help="extract all, then clean all")
    return p


def main(argv: list[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    if args.stage == "extract":
        extraction.run(args.action)
    elif args.stage == "clean":
        cleaning.run(args.action, limit=args.limit)
    elif args.stage == "all":
        extraction.run("all")
        cleaning.run("all")


if __name__ == "__main__":
    main()
