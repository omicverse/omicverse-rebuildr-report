#!/usr/bin/env python3
"""Compare two versions of a report (e.g. a blind rebuild against the published one).

    python3 tools/compare.py --a W/org-home/articles/pyedger --b /path/to/published/articles/pyedger \
        [--numbers W/evidence/numbers.json] [--out W/review/compare.md]

Reports, side by side: title, abstract length, sections and subsections with word counts, main-text
words, figures and tables, references (count, DOIs shared / only in one), which numbers.json values
each version quotes, and the wording checks of tools/lint.py (banned phrases) on each.
Use it to validate the pipeline after changing a guide or a role.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lint  # noqa: E402


def load(d: Path) -> dict:
    meta = yaml.safe_load((d / "meta.yaml").read_text())
    md = (d / "article.md").read_text()
    secs, cur = [], None
    for line in md.splitlines():
        m = re.match(r"^(#\*?|##)\s+(.*)$", line.strip())
        if m:
            cur = {"level": m.group(1), "name": m.group(2), "lines": []}
            secs.append(cur)
        elif cur is not None:
            cur["lines"].append(line)
    def words(lines):
        t = re.sub(r"^:::(figure|table).*?^:::\s*$", " ", "\n".join(lines), flags=re.S | re.M)
        return len(re.sub(r"[$`*#\[\]@]", " ", t).split())
    refs = re.search(r"^# References\s*\n(.*?)(?=^# |\Z)", md, re.S | re.M)
    dois = set(re.findall(r"(10\.\d{4,9}/\S+?)\.?\s*$", refs.group(1), re.M)) if refs else set()
    body = md.split("\n# References")[0]
    main = 0
    in_main = True
    for s in secs:
        if s["level"] == "#*" or s["name"] in ("References",) or s["name"].startswith("Supplementary"):
            in_main = s["level"] == "##" and in_main
        if s["level"] == "#" and not s["name"].startswith("Supplementary") and s["name"] != "References":
            in_main = True
        if in_main and s["level"] != "#*":
            main += words(s["lines"])
    phrases = []
    for pat, why in lint.PHRASE_ERRORS:
        phrases += [f"{why}: {m.group(0)}" for m in re.finditer(pat, body + meta.get("abstract", ""), re.I)]
    return {"meta": meta, "md": md, "sections": secs, "dois": dois, "main_words": main,
            "figures": re.findall(r"^:::figure\s+(\S+)", md, re.M), "tables": re.findall(r"^:::table\s+(\S+)", md, re.M),
            "abstract_words": len(str(meta.get("abstract", "")).split()), "phrases": phrases,
            "numbers": [v for _, v, _ in lint.numbers_in(body + " " + str(meta.get("abstract", "")))],
            "words": words}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--a", type=Path, required=True, help="first version (e.g. the rebuild)")
    ap.add_argument("--b", type=Path, required=True, help="second version (e.g. the published report)")
    ap.add_argument("--numbers", type=Path)
    ap.add_argument("--out", type=Path)
    x = ap.parse_args()
    A, B = load(x.a), load(x.b)
    out = [f"# Comparison: A = `{x.a}`, B = `{x.b}`", ""]
    out += ["| | A | B |", "|---|---|---|",
            f"| title | {A['meta'].get('title')} | {B['meta'].get('title')} |",
            f"| abstract words | {A['abstract_words']} | {B['abstract_words']} |",
            f"| main-text words | {A['main_words']} | {B['main_words']} |",
            f"| figures | {', '.join(A['figures'])} | {', '.join(B['figures'])} |",
            f"| tables | {', '.join(A['tables'])} | {', '.join(B['tables'])} |",
            f"| references | {len(A['dois'])} DOIs | {len(B['dois'])} DOIs |",
            f"| banned phrases | {len(A['phrases'])} | {len(B['phrases'])} |", ""]
    shared = A["dois"] & B["dois"]
    out += [f"References: {len(shared)} shared; only in A: {len(A['dois'] - B['dois'])}; only in B: {len(B['dois'] - A['dois'])}.", ""]
    if A["dois"] - B["dois"]:
        out += ["Only in A: " + ", ".join(sorted(A["dois"] - B["dois"])), ""]
    if B["dois"] - A["dois"]:
        out += ["Only in B: " + ", ".join(sorted(B["dois"] - A["dois"])), ""]
    for tag, V in (("A", A), ("B", B)):
        out += [f"## Sections in {tag}", ""]
        out += [f"- {'  ' if s['level'] == '##' else ''}{s['level']} {s['name']} ({V['words'](s['lines'])} words)" for s in V["sections"]]
        out += [""]
        if V["phrases"]:
            out += [f"Banned phrases in {tag}: " + "; ".join(V["phrases"]), ""]
    if x.numbers and x.numbers.exists():
        nums = json.loads(x.numbers.read_text())
        rows = ["| key | value | A | B |", "|---|---|---|---|"]
        for k, v in nums.items():
            if v.get("value") is None:
                continue
            ina = any(lint._match(v["value"], n, 2) for n in A["numbers"])
            inb = any(lint._match(v["value"], n, 2) for n in B["numbers"])
            if ina or inb:
                rows.append(f"| {k}{' (excluded)' if v.get('excluded') else ''} | {v['text']} | {'✓' if ina else ''} | {'✓' if inb else ''} |")
        out += ["## numbers.json values quoted", ""] + rows + [""]
    text = "\n".join(out) + "\n"
    if x.out:
        x.out.write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
