#!/usr/bin/env python3
"""Unified scraper -> raw_data/<domain>/<slug>/ (original + jsonl + _SOURCE.json).

PDFs via PyMuPDF (one record per page); JSON feeds via httpx + orjson.
Shares common.py and records everything in the ingest log.

    py -3.13 scrape.py            # all PDFS + FEEDS from manifest
"""

import json
import os

import orjson
import pymupdf

from .common import (ONE_MB, RAW_DATA, IngestLog, category_of, http_get, logger,
                    sha256_file)
from .manifest import FEEDS, PDFS

BASE = RAW_DATA


def _source_file(folder, title, url, lic):
    json.dump({"source": title, "url": url, "license": lic},
              open(os.path.join(folder, "_SOURCE.json"), "w", encoding="utf-8"), indent=2)


def scrape_pdf(domain, slug, title, lic, url, log):
    folder = os.path.join(BASE, domain, slug); os.makedirs(folder, exist_ok=True)
    logger.info(f"=== PDF: {title} ===")
    r = http_get(url)
    if r.content[:4] != b"%PDF":
        logger.error(f"  not a PDF (HTTP {r.status_code})")
        log.record(kind="pdf", name=slug, category=category_of("pdf"), domain=domain,
                   description=title, source_url=url, origin_format="pdf",
                   license=lic, status="failed: not pdf")
        return
    open(os.path.join(folder, slug + ".pdf"), "wb").write(r.content)
    _source_file(folder, title, url, lic)
    out = os.path.join(folder, slug + ".jsonl")
    doc = pymupdf.open(stream=r.content, filetype="pdf"); n = 0
    with open(out, "w", encoding="utf-8") as f:
        for i, page in enumerate(doc, 1):
            txt = page.get_text().strip()
            if not txt:
                continue
            f.write(json.dumps({"source": title, "url": url, "license": lic,
                                "page": i, "text": txt}, ensure_ascii=False) + "\n")
            n += 1
    doc.close()
    size = os.path.getsize(out)
    logger.info(f"  {n} pages, {size/ONE_MB:.2f} MB")
    log.record(kind="pdf", name=slug, category=category_of("pdf"), domain=domain,
               description=title, source_url=url, origin_format="pdf",
               orig_mb=round(len(r.content) / ONE_MB, 1),
               jsonl_mb=round(size / ONE_MB, 1), rows=n, sha256=sha256_file(out),
               license=lic, status="ok")


def scrape_feed(domain, slug, title, lic, url, json_key, log):
    folder = os.path.join(BASE, domain, slug); os.makedirs(folder, exist_ok=True)
    logger.info(f"=== FEED: {title} ===")
    r = http_get(url, timeout=240)
    data = orjson.loads(r.content)
    open(os.path.join(folder, slug + ".json"), "wb").write(r.content)
    _source_file(folder, title, url, lic)
    records = data.get(json_key, [])
    if slug.startswith("mitre"):
        records = [o for o in records if o.get("type") == "attack-pattern"]
    out = os.path.join(folder, slug + ".jsonl")
    with open(out, "wb") as f:
        for rec in records:
            f.write(orjson.dumps(rec) + b"\n")
    size = os.path.getsize(out)
    logger.info(f"  {len(records):,} rows, {size/ONE_MB:.2f} MB")
    log.record(kind="feed", name=slug, category=category_of("feed"), domain=domain,
               description=title, source_url=url, origin_format="json",
               orig_mb=round(len(r.content) / ONE_MB, 1),
               jsonl_mb=round(size / ONE_MB, 1), rows=len(records),
               sha256=sha256_file(out), license=lic, status="ok")


def run(log=None):
    log = log or IngestLog()
    for e in PDFS:
        try:
            scrape_pdf(*e, log)
        except Exception as ex:
            logger.error(f"  FAILED {e[2]}: {type(ex).__name__}: {ex}")
    for e in FEEDS:
        try:
            scrape_feed(*e, log)
        except Exception as ex:
            logger.error(f"  FAILED {e[2]}: {type(ex).__name__}: {ex}")


if __name__ == "__main__":
    run()
    logger.info("=== SCRAPE DONE ===")
