from cybersec_slm.cleaning import sanitize


def test_fills_missing_required_fields():
    rec, changed = sanitize.sanitize_record({"text": "hello world"})
    assert changed
    for k in ("source", "url", "license", "text"):
        assert k in rec


def test_strips_control_chars_and_collapses_whitespace():
    rec, _ = sanitize.sanitize_record({"text": "a\x00b\x07c    d\t\te"})
    assert rec["text"] == "abc d e"


def test_normalizes_crlf_and_blank_lines():
    rec, _ = sanitize.sanitize_record({"text": "line1\r\n\r\n\r\n\r\nline2"})
    assert rec["text"] == "line1\n\nline2"


def test_unicode_nfc():
    # 'e' + combining acute accent -> single NFC codepoint 'é'
    rec, _ = sanitize.sanitize_record({"text": "café " + "x" * 10})
    assert "é" in rec["text"]          # é
    assert "́" not in rec["text"]      # combining mark gone


def test_unambiguous_date_to_iso():
    rec, changed = sanitize.sanitize_record(
        {"text": "x" * 60, "date": "January 5, 2021"})
    assert rec["date"] == "2021-01-05"
    assert changed


def test_iso_date_passthrough():
    rec, _ = sanitize.sanitize_record({"text": "x" * 60, "date": "2021-01-05"})
    assert rec["date"] == "2021-01-05"
