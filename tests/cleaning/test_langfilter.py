from cybersec_slm.cleaning.langfilter import LangFilter


def test_english_is_allowed():
    lf = LangFilter(backend="heuristic")
    text = ("The system processes the data and stores it in the database "
            "for analysis and reporting to the team every day.")
    assert lf.detect(text) == "en"
    assert lf.is_allowed(text)


def test_non_latin_is_dropped():
    lf = LangFilter(backend="heuristic")
    ru = ("Это пример текста на русском языке для проверки определения "
          "языка системой очистки данных и фильтрации.")
    assert not lf.is_allowed(ru)


def test_uncertain_is_kept():
    lf = LangFilter(backend="heuristic")
    # too little signal to decide -> conservative keep
    assert lf.is_allowed("OK")
