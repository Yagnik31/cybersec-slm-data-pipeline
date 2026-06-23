#!/usr/bin/env python3
"""Cleaning orchestrator (thin CLI wrapper around the pipeline)."""

from __future__ import annotations

import sys

from . import pipeline
from .common import logger

STAGES = {"sanitize", "dedup", "pii", "lang"}


def run(cmd: str = "all", limit: int | None = None) -> None:
    """Run a cleaning command: all | sanitize | dedup | pii | lang | report | balance."""
    if cmd == "all":
        pipeline.run_all(limit=limit)
    elif cmd in STAGES:
        pipeline.run_single_stage(cmd, limit=limit)
    elif cmd == "report":
        pipeline.build_report_from_outputs()
    elif cmd == "balance":
        from .balance import check_balance
        check_balance()
    else:
        raise ValueError(f"unknown cleaning command: {cmd}")
    logger.info("=== CLEANING DONE ===")


def main() -> None:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else None
    run(cmd, limit)


if __name__ == "__main__":
    main()
