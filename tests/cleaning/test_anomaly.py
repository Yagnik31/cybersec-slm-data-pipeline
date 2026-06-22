from cybersec_slm.cleaning import anomaly
from cybersec_slm.cleaning.common import MAX_TEXT_CHARS


def test_empty_text_is_structural():
    bucket, _ = anomaly.classify({"text": ""})
    assert bucket == "structural"


def test_missing_text_is_structural():
    bucket, _ = anomaly.classify({"source": "x"})
    assert bucket == "structural"


def test_short_text_is_structural():
    bucket, _ = anomaly.classify({"text": "too short"})
    assert bucket == "structural"


def test_parse_error_is_structural():
    bucket, reason = anomaly.classify({"_parse_error": True})
    assert bucket == "structural" and "parse" in reason


def test_clean_paragraph():
    text = ("The quick brown fox jumps over the lazy dog and then runs back "
            "to the den for a long rest in the warm afternoon sun today.")
    bucket, _ = anomaly.classify({"text": text})
    assert bucket == "clean"


def test_repeated_lines_are_behavioral():
    text = "\n".join(["same boilerplate line here"] * 20)
    bucket, reason = anomaly.classify({"text": text})
    assert bucket == "behavioral"


def test_garbage_ratio_is_behavioral():
    text = "█" * 200
    bucket, reason = anomaly.classify({"text": text})
    assert bucket == "behavioral" and "garbage" in reason


def test_extreme_length_is_behavioral():
    text = "word " * (MAX_TEXT_CHARS // 2)        # well over the char cap
    bucket, reason = anomaly.classify({"text": text})
    assert bucket == "behavioral" and "length" in reason
