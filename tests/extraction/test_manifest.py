from cybersec_slm.extraction import manifest


def test_catalog_non_empty():
    assert len(manifest.DATASETS) > 0
    assert len(manifest.PDFS) > 0
    assert len(manifest.SITES) > 0
    assert len(manifest.FEEDS) > 0


def test_dataset_shapes():
    valid_kinds = {"hf", "kaggle", "github", "url"}
    for entry in manifest.DATASETS:
        assert len(entry) >= 5, entry
        kind = entry[0]
        assert kind in valid_kinds, kind
        if kind in ("github", "url"):     # need an explicit URL in slot 6
            assert len(entry) == 6 and entry[5].startswith("http"), entry


def test_pdf_and_feed_shapes():
    for e in manifest.PDFS:               # (domain, slug, title, license, url)
        assert len(e) == 5
        assert e[4].startswith("http")
    for e in manifest.FEEDS:              # (domain, slug, title, license, url, json_key)
        assert len(e) == 6
        assert e[4].startswith("http")
    for e in manifest.SITES:              # (domain, slug, url, lic, js, max, prefix, desc)
        assert len(e) == 8
