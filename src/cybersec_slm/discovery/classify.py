#!/usr/bin/env python3
"""Infer sheet fields that are knowable from a search result alone.

Two jobs, both pure functions:

* :func:`infer_category_and_format` — map a URL/host to the sheet's ``Category``
  ("Dataset", "Repository", "Document", "Website") and a best-guess
  ``Original Format`` ("" when it can't be known without fetching the page).
* :func:`refine_domain` — the snippet fallback: given the keyword's default
  Sub-Domain and the result's text, reassign only if another domain's
  vocabulary scores strictly higher.
"""

from __future__ import annotations

from urllib.parse import urlparse

from .keywords import DOMAIN_VOCAB


def infer_category_and_format(url: str) -> tuple[str, str]:
    """Return ``(category, original_format)`` from the URL/host shape.

    Format is left "" whenever it cannot be told from the URL — those rows get
    their real format filled in by the extraction stage, not guessed here.
    """
    low = (url or "").lower()
    host = urlparse(low).netloc

    if low.endswith(".pdf"):
        return "Document", "PDF"
    if low.endswith((".csv", ".json", ".jsonl", ".parquet", ".xlsx", ".txt")):
        fmt = low.rsplit(".", 1)[-1].upper()
        fmt = {"JSONL": "JSONL", "XLSX": "XLSX"}.get(fmt, fmt)
        return "Dataset", fmt

    if "huggingface.co" in host and "/datasets/" in low:
        return "Dataset", ""
    if "kaggle.com" in host and "/datasets/" in low:
        return "Dataset", ""
    if "github.com" in host or "gitlab.com" in host or "raw.githubusercontent" in host:
        return "Repository", ""
    if "arxiv.org" in host:
        return "Document", "PDF"
    if "zenodo.org" in host or "figshare.com" in host or "data.gov" in host:
        return "Dataset", ""
    return "Website", "HTML"


def _score(text: str, vocab: set[str]) -> int:
    return sum(1 for term in vocab if term in text)


def refine_domain(default_domain: str, title: str, snippet: str) -> str:
    """Reassign Sub-Domain only when the snippet clearly points elsewhere.

    Scores the combined text against each domain's vocabulary. The default wins
    ties (it is the keyword that actually surfaced the result); another domain
    must score *strictly higher* to take over.
    """
    text = f"{title} {snippet}".lower()
    base = _score(text, DOMAIN_VOCAB.get(default_domain, set()))
    best_domain, best_score = default_domain, base
    for domain, vocab in DOMAIN_VOCAB.items():
        if domain == default_domain:
            continue
        s = _score(text, vocab)
        if s > best_score:
            best_domain, best_score = domain, s
    return best_domain
