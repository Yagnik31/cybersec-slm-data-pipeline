#!/usr/bin/env python3
"""Chunking orchestrator."""

from __future__ import annotations

import sys

from ..core import logger
from .chunker import CHUNKED, run_chunking


def run(chunk_chars: int = 4000, overlap_chars: int = 200) -> None:
    run_chunking(chunk_chars=chunk_chars, overlap_chars=overlap_chars)
    logger.info("=== CHUNKING DONE ===")


def main() -> None:
    chunk_chars = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
    overlap_chars = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    run(chunk_chars, overlap_chars)


if __name__ == "__main__":
    main()
