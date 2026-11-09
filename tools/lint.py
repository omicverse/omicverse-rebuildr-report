#!/usr/bin/env python3
"""Static checks on a drafted report.

    python3 tools/lint.py --workdir W          # writes W/review/lint.json, exit 1 on errors

Reads W/request.json, W/org-home/articles/<slug>/{meta.yaml,article.md}, W/evidence/numbers.json
and the evidence notes. Errors must be fixed; warnings must each be looked at.

errors
  title        claims in the title (accuracy, speed, "faithful", "reproduces" ...)
  phrase       defensive or negative wording from guide/STYLE.md's banned list
  version      the package named with a version other than the current release
  excluded     a number that only exists for an earlier release (numbers.json "excluded")
  citation     citations not numbered by first appearance, uncited or missing references
  xref         Fig./Table mentioned but not defined, or defined but never mentioned
  structure    a required section is missing
  placeholder  TODO/TBD, <Placeholder> or an HTML comment left in the text
warnings
  number       a number that cannot be traced to numbers.json or the evidence notes
  style        hedges, process narration, comparative framing, long sentences
  length       section word budgets from guide/STRUCTURE.md
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path

import yaml

# ── wording ────────────────────────────────────────────────────────────────────────────────
TITLE_BANNED = r"\b(faithful\w*|exact(ly)?|identical|precis\w+|reproduc\w+|validated|accurate\w*|bit-identical|parity|fast\w*|speed\w*|drop-in)\b"
PHRASE_ERRORS = [
    (r"over-?interpret", "apology for the evidence"),
    (r"should be (interpreted|read) with caution|with caution", "apology for the evidence"),
    (r"\bto be fair\b|\badmittedly\b|\bit should be noted\b|\bnote that\b", "defensive aside"),
    (r"shared with other jobs|on a (busy|shared|loaded) (node|machine)", "apology for the benchmark set-up"),
    (r"\bnot an approximation\b|\brather than aiming\b|similar, but not identical|the bar should be", "comparative dig at other tools"),
    (r"\b(previous|earlier|prior|last|old|older) (release|version)s?\b(?! of (edgeR|R|Bioconductor))", "earlier release of the package"),
    (r"\bbugs?\b|\bdefects?\b|\bregressions?\b|\bwent unnoticed\b|\bfixed in\b|\bwere fixed\b|\bsilenced\b", "negative result / post-mortem"),
    (r"\bwhat the benchmark found\b|\bthe benchmark (found|exposed|revealed|uncovered)\b", "post-mortem framing"),
    (r"\bREADME example failed\b|\btests? (failed|fail)\b", "negative result / post-mortem"),
]
PHRASE_WARNINGS = [
    (r"\b(may|might|could|possibly|potentially|appears? to|seems? to|presumably)\b", "hedge"),
    (r"\bwe (found|noticed|discovered|realised|realized)\b|\bwas what found\b|\bit turned out\b", "process narration"),
    (r"\bbyte for byte\b|\bregenerating the references\b|\bnot only on simulations\b", "process narration"),
    (r"\brather than\b|\bnot (just|only|merely)\b|\binstead of being\b", "comparative framing; check it is not a dig"),
    (r"\b(only|merely|just) (\d|a few|one)\b", "minimising"),
    (r"\blimitations?\b|\bshortcomings?\b|\bdrawbacks?\b", "limitations belong in future work, phrased as plans"),
    (r"\b(single|one) run\b", "set-up detail; keep it neutral and in Supplementary methods"),
]
REQUIRED = [("Introduction", r"^Introduction$"), ("Implementation", r"^Implementation$"),
            ("Comparison", r"^Comparison with "), ("Conclusion and future perspectives", r"^Conclusion and future perspectives$")]
BACK_REQUIRED = [("Data and code availability", r"^Data and code availability$")]
BUDGET = {"__main__": (1200, 2100), "Introduction": (230, 460), "Conclusion and future perspectives": (120, 320)}
ABSTRACT_WORDS = (120, 230)
LONG_SENTENCE = 45

SUP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-")


# ── numbers ────────────────────────────────────────────────────────────────────────────────
def numbers_in(text: str) -> list[tuple[str, float, int]]:
    """(token, value, significant digits) for every number worth tracing."""
    found = []
    t = text
    for m in re.finditer(r"(\d+(?:\.\d+)?)\s*(?:\\times|×)\s*10\s*(?:\^\{?\s*(-?\d+)\s*\}?|([⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+))", t):
        exp = int(m.group(2) if m.group(2) is not None else m.group(3).translate(SUP))
        mant = m.group(1)
        found.append((m.group(0), float(mant) * 10 ** exp, len(mant.replace(".", "").lstrip("0"))))
    t = re.sub(r"(\d+(?:\.\d+)?)\s*(?:\\times|×)\s*10\s*(?:\^\{?\s*-?\d+\s*\}?|[⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+)", " ", t)
    for m in re.finditer(r"(?<![\w.])10\^\{\s*(-?\d+)\s*\}", t):
        found.append((m.group(0), 10.0 ** int(m.group(1)), 1))
    t = re.sub(r"10\^\{\s*-?\d+\s*\}", " ", t)
    t = re.sub(r"\b\d+\.\d+\.\d+(?:[-.]\d+)*\b", " ", t)          # versions such as 4.10.5 or 1.5-9.12
    t = re.sub(r"\b(?:fig|table|figure)\.?\s*S?\d+[a-z]?", " ", t, flags=re.I)
    t = re.sub(r"\[@[\d,\-]+\]", " ", t)
    for m in re.finditer(r"(?<![\w.^{\-])(\d{1,3}(?:,\d{3})+|\d+\.\d+|\d+)(?![\w])", t):
        tok = m.group(1)
        val = float(tok.replace(",", ""))
        if "." not in tok and "," not in tok and (val < 100 or 1900 <= val <= 2100):
            continue                                              # small counts and years
        sig = len(tok.replace(",", "").replace(".", "").lstrip("0").rstrip("0" if "." not in tok else "")) or 1
        found.append((tok, val, sig))
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--workdir", type=Path, required=True)
    a = ap.parse_args()
    W = a.workdir.expanduser().resolve()
    req = json.loads((W / "request.json").read_text())
    slug, pkg = req["slug"], req["package"]
    art = W / "org-home" / "articles" / slug
    meta = yaml.safe_load((art / "meta.yaml").read_text())
    md = (art / "article.md").read_text()

    errors, warnings = [], []

    def err(kind, msg, where=""):
        errors.append({"kind": kind, "msg": msg, "where": where})

    def warn(kind, msg, where=""):
        warnings.append({"kind": kind, "msg": msg, "where": where})

    # ── split into sections ──
    sections, cur, kind = [], None, "body"
    for line in md.splitlines():
        m = re.match(r"^(#\*?|##)\s+(.*)$", line.strip())
        if m and m.group(1) != "##":
            name = m.group(2).strip()
            kind = "back" if m.group(1) == "#*" else "refs" if name == "References" else "supp" if name.startswith("Supplementary") else "body"
            cur = {"name": name, "kind": kind, "lines": []}
            sections.append(cur)
            continue
        if cur is not None:
            cur["lines"].append(line)
    body_secs = [s for s in sections if s["kind"] == "body"]
    names = [s["name"] for s in sections]

    for label, pat in REQUIRED:
        if not any(re.match(pat, s["name"]) for s in body_secs):
            err("structure", f"missing section '{label}'")
    for label, pat in BACK_REQUIRED:
        if not any(re.match(pat, s["name"]) for s in sections if s["kind"] == "back"):
            err("structure", f"missing back-matter section '#* {label}'")
    for label in ("Use of AI tools", "Conflicts of interest"):
        if not any(s["name"].lower() == label.lower() for s in sections if s["kind"] == "back"):
            warn("structure", f"no '#* {label}' section (preprint servers require it; draft it for the authors to confirm)")
    if "References" not in names:
        err("structure", "missing '# References'")
    if not any(s["kind"] == "supp" for s in sections):
        warn("structure", "no '# Supplementary information' (methods details, notes for R users, Fig. S*)")

    # ── title / abstract ──
    title = meta.get("title", "")
    if re.search(TITLE_BANNED, title, re.I):
        err("title", f"title makes a claim ('{re.search(TITLE_BANNED, title, re.I).group(0)}'); describe what the package is", title)
    if not title.lower().startswith(pkg.lower() + ":"):
        warn("style", f"title should start with '{pkg}: '", title)
    abstract = re.sub(r"\s+", " ", meta.get("abstract", "")).strip()
    nw = len(abstract.split())
    if not ABSTRACT_WORDS[0] <= nw <= ABSTRACT_WORDS[1]:
        warn("length", f"abstract has {nw} words (aim for {ABSTRACT_WORDS[0]}-{ABSTRACT_WORDS[1]})")

    # ── wording ──
    scan = [("abstract", abstract), ("title", title)]
    for s in sections:
        if s["kind"] in ("refs",):
            continue
        for i, line in enumerate(s["lines"]):
            if line.strip():
                scan.append((s["name"], line))
    for where, text in scan:
        for pat, why in PHRASE_ERRORS:
            for m in re.finditer(pat, text, re.I):
                err("phrase", f"{why}: '{m.group(0)}'", f"{where}: …{text[max(0, m.start() - 60):m.end() + 60]}…")
        for pat, why in PHRASE_WARNINGS:
            if where.startswith("Supplementary") and "set-up" in why:
                continue
            for m in re.finditer(pat, text, re.I):
                warn("style", f"{why}: '{m.group(0)}'", f"{where}: …{text[max(0, m.start() - 60):m.end() + 60]}…")

    # ── leftovers ──
    for where, text in scan:
        bare = re.sub(r"`[^`]*`|\$[^$]*\$", " ", text)
        for m in re.finditer(r"\b(TODO|TBD|FIXME|XXX)\b|<[A-Za-z][A-Za-z _/-]{1,30}>|<!--", bare):
            err("placeholder", f"leftover placeholder '{m.group(0)}'", f"{where}: …{bare[max(0, m.start() - 50):m.end() + 50]}…")

    # ── package version ──
    current = str(req.get("package_version") or "")
    if not current:
        pp = W / "port" / "pyproject.toml"
        if pp.exists():
            m = re.search(r'^version\s*=\s*"([^"]+)"', pp.read_text(), re.M)
            current = m.group(1) if m else ""
    if current:
        for where, text in scan:
            for m in re.finditer(rf"\b{re.escape(pkg)}\s+v?(\d+\.\d+(?:\.\d+)?)\b", text, re.I):
                v = m.group(1)
                if not (v == current or current.startswith(v + ".")):
                    err("version", f"'{m.group(0)}' is not the current release {current}", where)

    # ── citations ──
    refs_sec = next((s for s in sections if s["kind"] == "refs"), None)
    ref_nums = [int(m.group(1)) for line in (refs_sec["lines"] if refs_sec else []) for m in [re.match(r"^\s*(\d+)\.\s+", line)] if m]
    n_refs = len(ref_nums)
    if ref_nums != list(range(1, n_refs + 1)):
        err("citation", f"reference list is not numbered 1..{n_refs}")
    order = []
    cite_text = "\n".join(l for s in sections if s["kind"] != "refs" for l in s["lines"])
    for m in re.finditer(r"\[@([\d,\-\s]+)\]", cite_text):
        for part in m.group(1).replace(" ", "").split(","):
            if "-" in part:
                x, y = part.split("-")
                order += list(range(int(x), int(y) + 1))
            elif part:
                order.append(int(part))
    first = []
    for n in order:
        if n not in first:
            first.append(n)
    if first != list(range(1, len(first) + 1)):
        bad = next(i for i, n in enumerate(first) if n != i + 1)
        err("citation", f"citations are not numbered by first appearance (the {bad + 1}th new citation is [{first[bad]}])")
    missing = sorted(set(order) - set(ref_nums))
    uncited = sorted(set(ref_nums) - set(order))
    if missing:
        err("citation", f"cited but not in the reference list: {missing}")
    if uncited:
        err("citation", f"in the reference list but never cited: {uncited}")
    if n_refs < 15:
        warn("citation", f"only {n_refs} references; a report usually needs 20-35 (guide/REFERENCES.md)")
    for line in (refs_sec["lines"] if refs_sec else []):
        m = re.match(r"^\s*(\d+)\.\s+(.*)$", line)
        if m and not re.search(r"10\.\d{4,9}/\S+\s*$|https?://\S+\s*$", m.group(2)):
            err("citation", f"reference {m.group(1)} has no DOI or URL at the end", m.group(2)[:100])

    # ── figure / table cross references ──
    figs = set(re.findall(r"^:::figure\s+(S?\d+)\s", md, re.M))
    tabs = set(re.findall(r"^:::table\s+(S?\d+)", md, re.M))
    prose = re.sub(r"^:::(figure|table).*?^:::\s*$", " ", md, flags=re.S | re.M)
    fig_mentions = set(re.findall(r"\bFigs?\.\s*(S?\d+)", prose))
    tab_mentions = set(re.findall(r"\bTables?\s+(S?\d+)", prose))
    for f in sorted(fig_mentions - figs):
        err("xref", f"Fig. {f} is mentioned but not defined")
    for f in sorted(figs - fig_mentions):
        err("xref", f"Fig. {f} is defined but never mentioned in the text")
    for t in sorted(tab_mentions - tabs):
        err("xref", f"Table {t} is mentioned but not defined")
    for t in sorted(tabs - tab_mentions):
        err("xref", f"Table {t} is defined but never mentioned in the text")
    for f in re.findall(r"^:::figure\s+S?\d+\s+(\S+)", md, re.M):
        if not (art / "figures" / f).exists():
            err("xref", f"figure file figures/{f} does not exist")

    # ── numbers ──
    nums_path = W / "evidence" / "numbers.json"
    nums = json.loads(nums_path.read_text()) if nums_path.exists() else {}
    allowed = [v["value"] for v in nums.values() if not v.get("excluded") and v.get("value") is not None]
    excluded = [(k, v["value"]) for k, v in nums.items() if v.get("excluded") and v.get("value") is not None]
    evidence_text = ""
    for p in list((W / "evidence").glob("*.md")) + [W / "port" / "README.md", W / "port" / "report" / "README.md"]:
        if p.exists():
            evidence_text += "\n" + p.read_text(errors="replace")
    for p in (W / "port" / "report" / "figures").glob("*.tsv") if (W / "port" / "report" / "figures").exists() else []:
        if re.search(r"(^|_)(old|prev|previous|legacy|v\d{2,})(_|\.|$)", p.stem, re.I):
            continue                                              # tables of an earlier release are not evidence
        evidence_text += "\n" + p.read_text(errors="replace")[:200000]
    evidence_vals = [v for _, v, _ in numbers_in(evidence_text)]
    evidence_vals += [float(x) for x in re.findall(r"(?<![\w.])\d+(?:\.\d+)?(?:e-?\d+)?(?![\w.])", evidence_text)[:200000] if _isfloat(x)]
    pool = allowed + evidence_vals

    def traced(val, sig):
        return any(_match(src, val, sig) for src in pool)

    for where, text in scan + [("meta", json.dumps(meta.get("links", {})))]:
        if where in ("Data and code availability",):
            continue
        for tok, val, sig in numbers_in(text):
            if traced(val, sig):
                continue
            hit = [k for k, ev in excluded if _match(ev, val, sig) and (sig >= 2 or val >= 10)]
            if hit:
                err("excluded", f"{tok} matches {', '.join(hit)} (earlier release), not the current one", f"{where}")
            else:
                warn("number", f"{tok} not found in numbers.json or the evidence notes (derived? then say from what)", f"{where}: …{_ctx(text, tok)}…")

    # ── lengths and sentences ──
    def words(lines):
        txt = "\n".join(lines)
        txt = re.sub(r"^:::(figure|table).*?^:::\s*$", " ", txt, flags=re.S | re.M)
        return len(re.sub(r"[$`*#\[\]@]", " ", txt).split())
    main_words = sum(words(s["lines"]) for s in body_secs)
    lo, hi = BUDGET["__main__"]
    if not lo <= main_words <= hi:
        warn("length", f"main text has {main_words} words (aim for {lo}-{hi})")
    for s in body_secs:
        if s["name"] in BUDGET:
            lo, hi = BUDGET[s["name"]]
            n = words(s["lines"])
            if not lo <= n <= hi:
                warn("length", f"'{s['name']}' has {n} words (aim for {lo}-{hi})")
    for s in body_secs:
        for sent in sentences("\n".join(s["lines"])):
            n = len(sent.split())
            if n > LONG_SENTENCE:
                warn("style", f"{n}-word sentence; split it", f"{s['name']}: {sent[:140]}…")

    seen, uniq = set(), []
    for w in warnings:
        key = (w["kind"], w["msg"], w["where"][:80])
        if key not in seen:
            seen.add(key)
            uniq.append(w)
    warnings = uniq
    report = {"slug": slug, "main_words": main_words, "references": n_refs, "errors": errors, "warnings": warnings}
    (W / "review").mkdir(exist_ok=True)
    (W / "review" / "lint.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(f"[lint] {slug}: {len(errors)} errors, {len(warnings)} warnings, main text {main_words} words, {n_refs} references")
    for e in errors:
        print(f"  ERROR {e['kind']}: {e['msg']}" + (f"\n        {e['where'][:200]}" if e["where"] else ""))
    for w in warnings:
        print(f"  warn  {w['kind']}: {w['msg']}" + (f"\n        {w['where'][:200]}" if w["where"] else ""))
    return 1 if errors else 0


ABBREV = re.compile(r"\b(Figs?|Eqs?|e\.g|i\.e|et al|vs|approx|cf|No)\.", re.I)


def sentences(text: str) -> list[str]:
    """Sentences of the prose, one paragraph at a time (figure/table blocks and headings dropped)."""
    text = re.sub(r"^:::(figure|table).*?^:::\s*$", "\n\n", text, flags=re.S | re.M)
    out = []
    for para in re.split(r"\n\s*\n|^#+ .*$", text, flags=re.M):
        para = re.sub(r"\s+", " ", para or "").strip()
        if not para or para.startswith(("1. ", "|")):
            continue
        para = ABBREV.sub(lambda m: m.group(0).replace(".", "\u2024"), para)
        out += [x.replace("\u2024", ".") for x in re.split(r"(?<=[.!?])\s+(?=[A-Za-z(`$\[])", para)]
    return out


def _isfloat(x: str) -> bool:
    try:
        float(x)
        return True
    except ValueError:
        return False


def _match(src: float, val: float, sig: int) -> bool:
    """val (as written, `sig` significant digits) equals src, src rounded, or 1/src rounded (speed-ups from time ratios)."""
    for s in (src, 1 / src if src else None):
        if s is None or s == 0 or val == 0:
            continue
        if math.isclose(s, val, rel_tol=1e-9):
            return True
        e = -int(math.floor(math.log10(abs(s)))) + (max(sig, 1) - 1)
        if math.isclose(round(s, e), val, rel_tol=1e-9):
            return True
    return False


def _ctx(text: str, tok: str) -> str:
    i = text.find(tok)
    return text[max(0, i - 50): i + len(tok) + 50] if i >= 0 else text[:100]


if __name__ == "__main__":
    sys.exit(main())
