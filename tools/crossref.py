#!/usr/bin/env python3
"""Find, format and verify references with the Crossref API.

    python3 tools/crossref.py search "edgeR v4 powerful differential analysis" [--rows 5]
    python3 tools/crossref.py doi 10.1093/nar/gkaf018 10.1186/gb-2010-11-3-r25
    python3 tools/crossref.py check path/to/article.md

`doi` prints each work as JSON together with `line`, the reference formatted for the
omicverse-org-home article dialect:

    Surname AB, Surname CD, Surname EF (Year). Title. Journal Volume, pages. DOI

(more than six authors: the first three, then "et al."). `check` reads the References section
of an article.md, fetches every DOI and reports references whose DOI does not resolve or whose
title, first author or year disagree with Crossref. Exit status 1 if any reference fails.

Never invent a DOI: every reference in a report must come out of `search` or `doi`.
"""

from __future__ import annotations

import argparse
import difflib
import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request

API = "https://api.crossref.org/works"
UA = "omicverse-rebuildr-report (https://github.com/omicverse/omicverse-rebuildr-report)"


def _get(url: str) -> dict:
    last = None
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:  # network hiccups and 429s
            last = e
            time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"{url}: {last}")


def clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text or "")
    text = re.sub(r"\s+", " ", html.unescape(text)).strip()
    return re.sub(r"\s+([:;,.?])", r"\1", text)


def year_of(m: dict) -> int | None:
    for key in ("published-print", "journal-issue", "published-online", "issued", "posted", "created"):
        node = m.get(key)
        if key == "journal-issue":
            node = (node or {}).get("published-print")
        parts = (node or {}).get("date-parts") or [[None]]
        if parts and parts[0] and parts[0][0]:
            return int(parts[0][0])
    return None


def initials(given: str) -> str:
    return "".join(p[0] for p in re.split(r"[\s\-.]+", given or "") if p)


def authors_of(m: dict) -> list[str]:
    out = []
    for a in m.get("author", []):
        if a.get("family"):
            out.append(f"{a['family']} {initials(a.get('given', ''))}".strip())
        elif a.get("name"):
            out.append(a["name"])
    return out


def summarise(m: dict) -> dict:
    authors = authors_of(m)
    names = ", ".join(authors[:3]) + ", et al." if len(authors) > 6 else ", ".join(authors)
    title = clean((m.get("title") or [""])[0])
    journal = clean((m.get("container-title") or [""])[0]) or ("bioRxiv" if "10.1101/" in m.get("DOI", "") else "")
    if not journal and m.get("type") == "posted-content":
        journal = clean(m.get("institution", [{}])[0].get("name", "")) if m.get("institution") else "Preprint"
    vol = m.get("volume", "")
    pages = (m.get("page") or m.get("article-number") or "").replace("--", "-")
    loc = " ".join(x for x in (journal, vol) if x)
    if pages:
        loc += f", {pages}" if loc else pages
    if m.get("type") in ("book", "monograph") and m.get("publisher"):
        loc = clean(m["publisher"])
    year = year_of(m)
    line = f"{names} ({year}). {title}. {loc}. {m.get('DOI', '')}".replace(" .", ".").replace("..", ".")
    return {"doi": m.get("DOI"), "type": m.get("type"), "year": year, "authors": authors, "title": title,
            "journal": journal, "volume": vol, "pages": pages, "line": line}


def cmd_doi(dois: list[str]) -> int:
    bad = 0
    out = []
    for d in dois:
        d = re.sub(r"^https?://(dx\.)?doi\.org/", "", d.strip())
        try:
            out.append(summarise(_get(f"{API}/{urllib.parse.quote(d)}")["message"]))
        except Exception as e:
            out.append({"doi": d, "error": str(e)})
            bad += 1
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 1 if bad else 0


def cmd_search(query: str, rows: int) -> int:
    q = urllib.parse.urlencode({"query.bibliographic": query, "rows": rows})
    items = _get(f"{API}?{q}")["message"]["items"]
    print(json.dumps([summarise(m) for m in items], indent=2, ensure_ascii=False))
    return 0


REF_LINE = re.compile(r"^(\d+)\.\s+(.*)$")
DOI_RE = re.compile(r"(10\.\d{4,9}/\S+?)\.?$")


def cmd_check(path: str) -> int:
    text = open(path, encoding="utf-8").read()
    m = re.search(r"^# References\s*\n(.*?)(?=^# |\Z)", text, re.S | re.M)
    if not m:
        print("no '# References' section"); return 1
    failures = 0
    for line in m.group(1).splitlines():
        r = REF_LINE.match(line.strip())
        if not r:
            continue
        n, body = r.groups()
        dm = DOI_RE.search(body)
        if not dm:
            status = "no-doi" if "http" in body else "MISSING-DOI"
            if status == "MISSING-DOI":
                failures += 1
            print(f"[{n}] {status}: {body[:90]}")
            continue
        doi = dm.group(1)
        try:
            meta = summarise(_get(f"{API}/{urllib.parse.quote(doi)}")["message"])
        except Exception as e:
            failures += 1
            print(f"[{n}] DOI-NOT-FOUND {doi}: {e}")
            continue
        norm = lambda x: re.sub(r"[^a-z0-9]+", " ", x.lower()).strip()      # noqa: E731
        t, b = norm(meta["title"]), norm(body)
        title_ok = t in b or difflib.SequenceMatcher(None, t, b, autojunk=False).find_longest_match(
            0, len(t), 0, len(b)).size >= min(40, int(0.6 * len(t)))
        first = (meta["authors"][0].split()[0] if meta["authors"] else "").lower()
        author_ok = (not first) or first in body.lower()
        ym = re.search(r"\((\d{4})\)", body)
        year_ok = (not ym or meta["year"] is None or abs(int(ym.group(1)) - meta["year"]) <= 1
                   or meta["type"] == "posted-content")      # preprints: cited version may be newer than v1
        ok = title_ok and author_ok and year_ok
        failures += 0 if ok else 1
        flags = [k for k, v in (("title", title_ok), ("first-author", author_ok), ("year", year_ok)) if not v]
        print(f"[{n}] {'ok' if ok else 'MISMATCH ' + ','.join(flags)}  {doi}  | {meta['line'][:110]}")
        time.sleep(0.2)
    return 1 if failures else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search"); s.add_argument("query"); s.add_argument("--rows", type=int, default=5)
    d = sub.add_parser("doi"); d.add_argument("dois", nargs="+")
    c = sub.add_parser("check"); c.add_argument("article")
    a = ap.parse_args()
    if a.cmd == "search":
        return cmd_search(a.query, a.rows)
    if a.cmd == "doi":
        return cmd_doi(a.dois)
    return cmd_check(a.article)


if __name__ == "__main__":
    sys.exit(main())
