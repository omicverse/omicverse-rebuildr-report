#!/usr/bin/env python3
"""Set up the work directory for one technical report.

    python3 tools/prepare.py examples/pyedger/request.yaml --workdir ~/reports/pyedger
    python3 tools/prepare.py request.yaml --workdir W --blind      # validation run

Creates
    W/request.json   the request, normalised (every later stage reads this, not the YAML)
    W/port/          shallow clone of the port repository, including its report/ benchmark
    W/org-home/      shallow clone of omicverse-org-home, where the article is written and built
    W/evidence/      filled by the Gather stage
    W/review/        filled by the Review and Build stages
    W/prepare.json   what was found, what is missing, and which tools are available

--blind deletes any existing article for the slug from W/org-home and removes the org-home git
history, so that no earlier version of the report is reachable from the work directory.
Use it to check that the pipeline can write a report from evidence alone.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

ORG_HOME = "https://github.com/omicverse/omicverse-org-home.git"
# The authors' standard declaration; a request can override it with `ai_declaration`.
AI_DECLARATION = ("The authors used Claude Opus 5.5, GPT-6 Astra, and OmicOS to proofread grammar and syntax, "
                  "improve readability. Any AI-assisted edits were reviewed by the authors, who take full "
                  "responsibility for the content of this publication.")
TEX_BIN = Path("/Library/TeX/texbin")          # MacTeX; on Linux TeX Live is usually on PATH already


def repo_url(spec: str) -> str:
    if spec.startswith(("http://", "https://", "git@")) or Path(spec).expanduser().exists():
        return str(Path(spec).expanduser()) if Path(spec).expanduser().exists() else spec
    return f"https://github.com/{spec}.git"           # owner/name


def clone(src: str, dest: Path, ref: str | None = None) -> None:
    if dest.exists():
        shutil.rmtree(dest)
    cmd = ["git", "clone", "--quiet", "--depth", "1"]
    if ref:
        cmd += ["--branch", ref]
    src_path = Path(src)
    if src_path.exists():                              # local checkout: clone it so the original stays untouched
        cmd += [f"file://{src_path.resolve()}", str(dest)]
    else:
        cmd += [src, str(dest)]
    subprocess.run(cmd, check=True)


def which(name: str) -> str | None:
    found = shutil.which(name)
    if not found and (TEX_BIN / name).exists():
        found = str(TEX_BIN / name)
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("request", type=Path)
    ap.add_argument("--workdir", type=Path, required=True)
    ap.add_argument("--blind", action="store_true", help="remove any existing version of the report")
    ap.add_argument("--keep", action="store_true", help="reuse existing clones in the work directory")
    args = ap.parse_args()

    req = yaml.safe_load(args.request.read_text())
    for key in ("port_repo", "package", "upstream", "slug", "authors", "affiliations"):
        if key not in req:
            sys.exit(f"request is missing '{key}' (see templates/request.template.yaml)")
    for k in ("published",):
        if isinstance(req.get(k), (dt.date, dt.datetime)):
            req[k] = req[k].isoformat()
    req.setdefault("type", "Technical Report")
    req.setdefault("version", 1)
    req.setdefault("org_home", ORG_HOME)
    req.setdefault("ai_declaration", AI_DECLARATION)
    req["blind"] = bool(args.blind or req.get("blind"))

    W = args.workdir.expanduser().resolve()
    W.mkdir(parents=True, exist_ok=True)
    for sub in ("evidence", "review"):
        (W / sub).mkdir(exist_ok=True)

    port, home = W / "port", W / "org-home"
    if not (args.keep and port.exists()):
        clone(repo_url(req["port_repo"]), port, req.get("port_ref"))
    if not (args.keep and home.exists()):
        clone(repo_url(req["org_home"]), home)

    slug = req["slug"]
    removed = []
    if req["blind"]:
        for rel in (f"articles/{slug}", f"src/articles/{slug}.html", f"src/assets/articles/{slug}"):
            p = home / rel
            if p.exists():
                shutil.rmtree(p) if p.is_dir() else p.unlink()
                removed.append(rel)
        shutil.rmtree(home / ".git", ignore_errors=True)        # no earlier version reachable
    (home / "articles" / slug / "figures").mkdir(parents=True, exist_ok=True)

    rep = port / "report"
    figs = rep / "figures"
    evidence = {
        "port_readme": (port / "README.md").exists(),
        "port_yaml": (port / "port.yaml").exists(),
        "changelog": (port / "CHANGELOG.md").exists(),
        "tests": (port / "tests").is_dir(),
        "report_readme": (rep / "README.md").exists(),
        "report_scripts": sorted(p.name for p in (rep / "scripts").glob("*")) if (rep / "scripts").is_dir() else [],
        "numbers": next((str(p.relative_to(W)) for p in (figs / "numbers.json", figs / "numbers.tex") if p.exists()), None),
        "figures": sorted(p.name for p in figs.glob("*") if p.suffix.lower() in (".pdf", ".png", ".jpg", ".jpeg")) if figs.is_dir() else [],
        "tables": sorted(p.name for p in figs.glob("*.tsv")) if figs.is_dir() else [],
    }
    missing = [k for k in ("report_readme", "numbers") if not evidence[k]]
    if not evidence["figures"]:
        missing.append("figures")
    tools = {name: which(name) for name in ("git", "latexmk", "pdflatex", "pdftoppm", "pdftotext", "gh")}
    try:
        import PIL  # noqa: F401
        tools["python:PIL"] = "ok"
    except ImportError:
        tools["python:PIL"] = None

    summary = {
        "workdir": str(W), "slug": slug, "package": req["package"], "upstream": req["upstream"],
        "blind": req["blind"], "removed_existing": removed,
        "paths": {"port": str(port), "org_home": str(home), "article": str(home / "articles" / slug),
                  "evidence": str(W / "evidence"), "review": str(W / "review")},
        "evidence": evidence, "missing_evidence": missing, "tools": tools,
    }
    (W / "request.json").write_text(json.dumps(req, indent=2, ensure_ascii=False) + "\n")
    (W / "prepare.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
