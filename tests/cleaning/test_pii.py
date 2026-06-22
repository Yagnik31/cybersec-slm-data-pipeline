from cybersec_slm.cleaning.pii import Redactor


def test_regex_redacts_common_identifiers():
    r = Redactor(engine="regex")
    text = ("Email a@b.com IP 10.0.0.1 SSN 123-45-6789 "
            "card 4111 1111 1111 1111 please respond soon.")
    out, n = r.redact(text)
    assert "<EMAIL_ADDRESS>" in out
    assert "<IP_ADDRESS>" in out
    assert "<US_SSN>" in out
    assert "<CREDIT_CARD>" in out
    assert n >= 4
    assert "a@b.com" not in out


def test_invalid_credit_card_not_redacted():
    r = Redactor(engine="regex")
    # fails the Luhn check -> left as-is
    out, n = r.redact("number 1234 5678 9012 3457 here")
    assert "<CREDIT_CARD>" not in out


def test_no_pii_returns_zero():
    r = Redactor(engine="regex")
    out, n = r.redact("a perfectly ordinary sentence with no identifiers")
    assert n == 0
    assert out == "a perfectly ordinary sentence with no identifiers"
