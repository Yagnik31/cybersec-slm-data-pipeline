#!/usr/bin/env python3
"""PII Removal — redact personally identifying information.

Uses Microsoft Presidio (analyze + anonymize) when installed; otherwise a
regex fallback for the most common identifiers. Redactions replace the span
with a typed placeholder, e.g. <EMAIL_ADDRESS>.

Public API:
    r = Redactor()                  # engine auto-selected
    new_text, n = r.redact(text)    # n = number of spans redacted
"""

from __future__ import annotations

import re

from .common import logger, try_import

# --- regex fallback patterns (order matters: specific -> generic) ---
_EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
_SSN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
_IPV4 = re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")
_CC = re.compile(r"\b(?:\d[ -]?){13,19}\b")
_PHONE = re.compile(r"(?<!\w)(?:\+?\d{1,3}[ .-]?)?(?:\(?\d{2,4}\)?[ .-]?){2,4}\d{2,4}(?!\w)")


def _luhn_ok(digits: str) -> bool:
    ds = [int(c) for c in digits if c.isdigit()]
    if not 13 <= len(ds) <= 19:
        return False
    total, alt = 0, False
    for d in reversed(ds):
        if alt:
            d *= 2
            if d > 9:
                d -= 9
        total += d
        alt = not alt
    return total % 10 == 0


def _regex_redact(text: str) -> tuple[str, int]:
    count = 0

    def sub(pattern, label, s, validator=None):
        nonlocal count

        def repl(m):
            nonlocal count
            if validator and not validator(m.group(0)):
                return m.group(0)
            count += 1
            return f"<{label}>"

        return pattern.sub(repl, s)

    text = sub(_EMAIL, "EMAIL_ADDRESS", text)
    text = sub(_SSN, "US_SSN", text)
    text = sub(_CC, "CREDIT_CARD", text, validator=_luhn_ok)
    text = sub(_IPV4, "IP_ADDRESS", text)
    # phone last: require >=7 digits to avoid eating plain numbers/years
    text = sub(_PHONE, "PHONE_NUMBER", text,
               validator=lambda s: sum(c.isdigit() for c in s) >= 7)
    return text, count


class Redactor:
    def __init__(self, engine="auto"):
        self.engine = "regex"
        self._analyzer = None
        self._anonymizer = None
        if engine in ("auto", "presidio"):
            pa = try_import("presidio_analyzer")
            pan = try_import("presidio_anonymizer")
            if pa is not None and pan is not None:
                try:
                    self._analyzer = pa.AnalyzerEngine()
                    self._anonymizer = pan.AnonymizerEngine()
                    self.engine = "presidio"
                except Exception as ex:           # model not downloaded, etc.
                    logger.warning(f"pii: presidio init failed ({type(ex).__name__}); "
                                   "using regex fallback")
        if engine == "presidio" and self.engine != "presidio":
            logger.warning("pii: presidio requested but unavailable; using regex")
        logger.debug(f"pii: engine = {self.engine}")

    def redact(self, text: str) -> tuple[str, int]:
        if not text:
            return text, 0
        if self.engine == "presidio":
            results = self._analyzer.analyze(text=text, language="en")
            if not results:
                return text, 0
            out = self._anonymizer.anonymize(text=text, analyzer_results=results)
            return out.text, len(results)
        return _regex_redact(text)
