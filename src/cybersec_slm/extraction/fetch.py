#!/usr/bin/env python3
"""Unified dataset fetcher -> raw_data/<domain>/<owner>/ (original + jsonl).

One handler per source kind (hf, kaggle, github, url), all sharing common.py.
Files over the 5 GB cap are skipped but still recorded in the ingest log so they
appear in the final table.

    py -3.13 fetch.py            # fetch everything in manifest.DATASETS
    py -3.13 fetch.py hf ai4privacy/pii-masking-200k "Data Security and Privacy" topic
"""

import os
import shutil
import sys
from urllib.parse import urlparse

from .common import (CAP_BYTES, EXT_PRIORITY, ONE_MB, RAW_DATA, SKIP_SUBSTRINGS,
                    IngestLog, OversizeError, category_of, count_lines, download,
                    group_key, logger, remote_size, sha256_file, to_jsonl)

BASE = RAW_DATA


def _github_target(url: str) -> tuple[str, str] | None:
    """Resolve a github.com URL to something downloadable + a filename.

    Repo root / tree URLs point at a *page*, not a file, so rewrite them to the
    branch archive zip (processed by the zip path below). ``/blob/`` URLs become
    their raw-file equivalent. Direct ``raw.githubusercontent.com`` links and
    file URLs return None (handled as-is). Returns ``(download_url, name)``.
    """
    p = urlparse(url)
    if p.netloc not in ("github.com", "www.github.com"):
        return None
    parts = [x for x in p.path.split("/") if x]
    if len(parts) < 2:
        return None
    owner, repo = parts[0], parts[1][:-4] if parts[1].endswith(".git") else parts[1]
    if len(parts) == 2:                       # owner/repo  -> default branch zip
        return f"https://github.com/{owner}/{repo}/archive/HEAD.zip", f"{repo}.zip"
    if parts[2] == "tree" and len(parts) >= 4:   # .../tree/<branch>[/subdir]
        return (f"https://github.com/{owner}/{repo}/archive/refs/heads/{parts[3]}.zip",
                f"{repo}.zip")
    if parts[2] == "blob" and len(parts) >= 5:   # .../blob/<branch>/<path> -> raw
        branch, rest = parts[3], "/".join(parts[4:])
        return (f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{rest}",
                os.path.basename(rest))
    return None


def _folder(domain, owner, name, counts):
    base = owner if counts.get(owner, 0) <= 1 else f"{owner}-{name}"
    d = os.path.join(BASE, domain, base)
    os.makedirs(d, exist_ok=True)
    return d


def _convert_and_log(original, jsonl, log, *, kind, name, domain, desc, url, lic):
    """Convert one original file -> jsonl, enforce cap, record provenance."""
    fmt = os.path.splitext(original)[1].lstrip(".")
    orig_mb = os.path.getsize(original) / ONE_MB
    meta = dict(kind=kind, name=name, category=category_of(kind), domain=domain,
                description=desc, source_url=url, origin_format=fmt, license=lic)
    if os.path.getsize(original) > CAP_BYTES:
        logger.warning(f"SKIP >5GB original: {os.path.basename(original)}")
        os.remove(original)
        log.record(**meta, orig_mb=round(orig_mb, 1), status="skipped (>5GB)")
        return
    record_meta = {"source": desc, "url": url, "license": lic}
    size = to_jsonl(original, jsonl, meta=record_meta)
    if size > CAP_BYTES:
        logger.warning(f"SKIP >5GB jsonl: {os.path.basename(jsonl)}")
        if os.path.exists(jsonl):
            os.remove(jsonl)
        os.remove(original)
        log.record(**meta, orig_mb=round(orig_mb, 1), status="skipped (jsonl >5GB)")
        return
    rows = count_lines(jsonl)
    logger.info(f"  {os.path.basename(jsonl)}: {rows:,} rows, {size/ONE_MB:.1f} MB")
    log.record(**meta, orig_mb=round(orig_mb, 1), jsonl_mb=round(size / ONE_MB, 1),
               rows=rows, sha256=sha256_file(jsonl), status="ok")


# ------------------------------------------------------------ handlers -------
def fetch_hf(ref, domain, desc, lic, folder, log):
    from huggingface_hub import HfApi
    info = HfApi().dataset_info(ref, files_metadata=True)
    sib = {s.rfilename: (s.size or 0) for s in info.siblings}
    cand = [f for f in sib if f.lower().endswith(EXT_PRIORITY)
            and not any(s in f.lower() for s in SKIP_SUBSTRINGS)]
    for ext in EXT_PRIORITY:
        chosen = [f for f in cand if f.lower().endswith(ext)]
        if chosen:
            break
    # Group sharded files (train-00000-of-N...) so they accumulate into one jsonl
    # instead of overwriting each other.
    groups = {}
    for rel in chosen:
        groups.setdefault(group_key(rel), []).append(rel)

    for key, members in groups.items():
        name = f"{ref.split('/')[-1]}/{key}"
        url0 = f"https://huggingface.co/datasets/{ref}/resolve/main/{members[0]}"
        fext = os.path.splitext(members[0])[1]
        meta = dict(kind="hf", name=name, category=category_of("hf"), domain=domain,
                    description=desc, source_url=url0, origin_format=fext.lstrip("."),
                    license=lic)
        jsonl = os.path.join(folder, key + ".jsonl")
        open(jsonl, "wb").close()
        total = rows = orig_total = 0
        skipped = False
        shard_meta = {"source": desc, "url": url0, "license": lic}
        for i, rel in enumerate(sorted(members)):
            if sib.get(rel, 0) > CAP_BYTES:
                skipped = True
                break
            url = f"https://huggingface.co/datasets/{ref}/resolve/main/{rel}"
            orig = os.path.join(folder, (key if len(members) == 1 else f"{key}.part{i}")
                                + (".original.jsonl" if fext == ".jsonl" else fext))
            download(url, orig)
            orig_total += os.path.getsize(orig)
            tmp = jsonl + ".part"
            to_jsonl(orig, tmp, meta=shard_meta)
            with open(tmp, "rb") as src, open(jsonl, "ab") as dst:
                shutil.copyfileobj(src, dst)
            os.remove(tmp)
            total = os.path.getsize(jsonl)
            if total > CAP_BYTES:
                skipped = True
                break
        if skipped:
            logger.warning(f"SKIP >5GB (cumulative): {name}")
            if os.path.exists(jsonl):
                os.remove(jsonl)
            log.record(**meta, orig_mb=round(orig_total / ONE_MB, 1) or None,
                       status="skipped (>5GB)")
            continue
        rows = count_lines(jsonl)
        logger.info(f"  {key}.jsonl: {rows:,} rows, {total/ONE_MB:.1f} MB"
                    + (f" ({len(members)} shards)" if len(members) > 1 else ""))
        log.record(**meta, orig_mb=round(orig_total / ONE_MB, 1),
                   jsonl_mb=round(total / ONE_MB, 1), rows=rows,
                   sha256=sha256_file(jsonl), status="ok")


def fetch_kaggle(ref, domain, desc, lic, folder, log):
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi(); api.authenticate()
    files = api.dataset_list_files(ref).files
    sizes = {f.name: (getattr(f, "totalBytes", None) or getattr(f, "total_bytes", 0) or 0)
             for f in files}
    cand = [n for n in sizes if n.lower().endswith(EXT_PRIORITY)
            and not any(s in n.lower() for s in SKIP_SUBSTRINGS)]
    for ext in EXT_PRIORITY:
        chosen = [f for f in cand if f.lower().endswith(ext)]
        if chosen:
            break
    url = f"https://www.kaggle.com/datasets/{ref}"
    tmp = os.path.join(folder, "_dl"); os.makedirs(tmp, exist_ok=True)
    for rel in sorted(chosen):
        stem, fext = os.path.splitext(os.path.basename(rel))[0], os.path.splitext(rel)[1]
        name = f"{ref.split('/')[-1]}/{stem}"
        if sizes.get(rel, 0) > CAP_BYTES:
            logger.warning(f"SKIP >5GB (pre-check): {rel} ({sizes[rel]/1024**3:.1f} GB)")
            log.record(kind="kaggle", name=name, category=category_of("kaggle"), domain=domain,
                       description=desc, source_url=url, origin_format=fext.lstrip("."),
                       orig_mb=round(sizes[rel] / ONE_MB, 1), license=lic,
                       status="skipped (>5GB)")
            continue
        api.dataset_download_file(ref, rel, path=tmp, quiet=True)
        got = os.path.join(tmp, os.path.basename(rel))
        if not os.path.exists(got) and os.path.exists(got + ".zip"):
            import zipfile
            with zipfile.ZipFile(got + ".zip") as z:
                z.extractall(tmp)
        if not os.path.exists(got):
            logger.error(f"  download missing: {rel}"); continue
        orig = os.path.join(folder, os.path.basename(rel))
        shutil.move(got, orig)
        _convert_and_log(orig, os.path.join(folder, stem + ".jsonl"), log,
                         kind="kaggle", name=name, domain=domain, desc=desc, url=url, lic=lic)
    shutil.rmtree(tmp, ignore_errors=True)


def fetch_url(url, domain, desc, lic, folder, log, kind="url"):
    gh = _github_target(url)
    if gh:
        url, name = gh           # repo page -> archive zip / raw file
    else:
        name = os.path.basename(url.split("?")[0])
    sz = remote_size(url)
    stem, fext = os.path.splitext(name)
    if sz and sz > CAP_BYTES:
        logger.warning(f"SKIP >5GB (pre-check): {name}")
        log.record(kind=kind, name=stem, category=category_of(kind), domain=domain,
                   description=desc, source_url=url, origin_format=fext.lstrip("."),
                   orig_mb=round(sz / ONE_MB, 1), license=lic, status="skipped (>5GB)")
        return
    orig = os.path.join(folder, name)
    download(url, orig)
    if orig.lower().endswith(".zip"):
        import zipfile
        zdir = os.path.join(folder, "_z"); os.makedirs(zdir, exist_ok=True)
        with zipfile.ZipFile(orig) as z:
            z.extractall(zdir)
        os.remove(orig)
        data = [os.path.join(r, f) for r, _d, fs in os.walk(zdir) for f in fs
                if f.lower().endswith(EXT_PRIORITY)
                and not any(s in f.lower() for s in SKIP_SUBSTRINGS)]
        for ext in EXT_PRIORITY:
            data = [f for f in data if f.lower().endswith(ext)] or data
            if any(f.lower().endswith(ext) for f in data):
                break
        for path in sorted(data):
            inner = os.path.splitext(os.path.basename(path))[0]
            tgt = os.path.join(folder, os.path.basename(path))
            shutil.move(path, tgt)
            _convert_and_log(tgt, os.path.join(folder, inner + ".jsonl"), log,
                             kind=kind, name=f"{stem}/{inner}", domain=domain,
                             desc=desc, url=url, lic=lic)
        shutil.rmtree(zdir, ignore_errors=True)
        return
    _convert_and_log(orig, os.path.join(folder, stem + ".jsonl"), log,
                     kind=kind, name=stem, domain=domain, desc=desc, url=url, lic=lic)


# --------------------------------------------------------------- driver ------
def run(datasets, log=None):
    log = log or IngestLog()
    counts = {}
    for entry in datasets:
        kind, ref = entry[0], entry[1]
        owner = ref.split("/")[0] if "/" in ref and kind in ("hf", "kaggle") else kind
        counts[owner] = counts.get(owner, 0) + 1
    for entry in datasets:
        kind, ref, domain, desc, lic = entry[:5]
        name = ref.split("/")[-1]
        owner = ref.split("/")[0] if "/" in ref and kind in ("hf", "kaggle") else name
        folder = _folder(domain, owner, name, counts)
        logger.info(f"=== {kind}: {ref}  [{domain} / {desc}] ===")
        try:
            if kind == "hf":
                fetch_hf(ref, domain, desc, lic, folder, log)
            elif kind == "kaggle":
                fetch_kaggle(ref, domain, desc, lic, folder, log)
            elif kind in ("github", "url"):
                fetch_url(entry[5], domain, desc, lic, folder, log, kind=kind)
        except OversizeError as ex:
            logger.warning(f"  oversize: {ex}")
        except Exception as ex:
            logger.error(f"  FAILED {ref}: {type(ex).__name__}: {ex}")
            log.record(kind=kind, name=name, category=category_of(kind), domain=domain,
                       description=desc, license=lic, status=f"failed: {type(ex).__name__}")


if __name__ == "__main__":
    if len(sys.argv) >= 5:
        run([tuple(sys.argv[1:6])])
    else:
        from .manifest import DATASETS
        run(DATASETS)
    logger.info("=== FETCH DONE ===")
