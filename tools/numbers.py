#!/usr/bin/env python3
"""Turn a benchmark's numbers file into evidence/numbers.json.

    python3 tools/numbers.py W/port/report/figures/numbers.tex -o W/evidence/numbers.json

Reads `\\newcommand{\\key}{value}` lines (numbers.tex) or a flat JSON object (numbers.json)
and writes {key: {"raw": ..., "text": ..., "value": float|null, "excluded": bool}}.

Keys that describe an earlier release of the package (prefixes old/prev/previous/legacy/v0...)
are marked "excluded": a report describes the current release only, so those numbers must not
appear in it (tools/lint.py checks this).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

EXCLUDE = re.compile(r"^(old|prev|previous|legacy|before|baseline_old|v\d)", re.I)
NEWCMD = re.compile(r"\\newcommand\{\\([A-Za-z]+)\}\{(.*)\}\s*$")


def plain(raw: str) -> str:
    s = raw.strip().strip("$")
    s = re.sub(r"\\times\s*10\^\{?(-?\d+)\}?", r" × 10^\1", s)
    s = s.replace("\\,", "").replace("{,}", ",").replace("\\%", "%").replace("~", " ")
    return re.sub(r"\s+", " ", s).strip()


def value(text: str) -> float | None:
    t = text.replace(",", "").replace("%", "").strip()
    m = re.fullmatch(r"(-?\d+(?:\.\d+)?)\s*× 10\^(-?\d+)", t)
    if m:
        return float(m.group(1)) * 10 ** int(m.group(2))
    try:
        return float(t)
    except ValueError:
        return None


def load(path: Path) -> dict:
    out = {}
    if path.suffix == ".json":
        for k, v in json.loads(path.read_text()).items():
            raw = str(v)
            out[k] = {"raw": raw, "text": plain(raw), "value": value(plain(raw)), "excluded": bool(EXCLUDE.match(k))}
        return out
    for line in path.read_text().splitlines():
        m = NEWCMD.match(line.strip())
        if m:
            k, raw = m.groups()
            out[k] = {"raw": raw, "text": plain(raw), "value": value(plain(raw)), "excluded": bool(EXCLUDE.match(k))}
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("numbers", type=Path)
    ap.add_argument("-o", "--out", type=Path)
    a = ap.parse_args()
    data = load(a.numbers)
    txt = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(txt)
    excluded = [k for k, v in data.items() if v["excluded"]]
    print(f"[numbers] {len(data)} keys, {len(excluded)} excluded (earlier release): {', '.join(excluded) or '-'}", file=sys.stderr)
    if not a.out:
        print(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
