#!/usr/bin/env python3
"""Build the article in the work directory and check the result.

    python3 tools/build.py --workdir W

Runs omicverse-org-home's `scripts/build_articles.py --pdf --only <slug>` inside W/org-home,
then checks what a reader would see:

  * LaTeX errors, overfull lines wider than 2 pt, undefined references or citations
  * page count; every PDF page rendered to W/review/pages/p-N.png (90 dpi) and a contact
    sheet W/review/pages/overview.png, to be looked at (Read the PNGs)
  * the web page: number of references, figures and sections

Writes W/review/build.json and prints it. Exit status 1 if the build failed or LaTeX errors
were found.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

TEX_BIN = "/Library/TeX/texbin"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--workdir", type=Path, required=True)
    ap.add_argument("--no-pdf", action="store_true", help="web page only (reuses an existing PDF)")
    a = ap.parse_args()
    W = a.workdir.expanduser().resolve()
    req = json.loads((W / "request.json").read_text())
    slug = req["slug"]
    home = W / "org-home"
    env = dict(os.environ)
    if Path(TEX_BIN).exists():
        env["PATH"] = TEX_BIN + os.pathsep + env.get("PATH", "")

    cmd = [sys.executable, "scripts/build_articles.py", "--only", slug] + ([] if a.no_pdf else ["--pdf"])
    proc = subprocess.run(cmd, cwd=home, env=env, capture_output=True, text=True)
    out = {"command": " ".join(cmd), "returncode": proc.returncode,
           "stdout": proc.stdout[-3000:], "stderr": proc.stderr[-3000:]}

    log = home / "articles" / slug / "build" / f"{slug}.log"
    if log.exists():
        text = log.read_text(errors="replace")
        out["latex_errors"] = re.findall(r"^! .*$", text, re.M)[:20]
        overfull = []
        for m in re.finditer(r"Overfull \\hbox \(([\d.]+)pt too wide\)[^\n]*\n([^\n]*)", text):
            if float(m.group(1)) > 2.0:
                overfull.append(f"{m.group(1)}pt: {m.group(2).strip()[:120]}")
        out["overfull_hbox_over_2pt"] = overfull
        out["undefined"] = sorted(set(re.findall(r"(?:Citation|Reference) `([^']+)' .*undefined", text)))
    pdf = home / "src" / "assets" / "articles" / slug / f"{slug}.pdf"
    out["pdf"] = str(pdf) if pdf.exists() else None
    pages_dir = W / "review" / "pages"
    if pdf.exists() and shutil.which("pdftoppm"):
        shutil.rmtree(pages_dir, ignore_errors=True)
        pages_dir.mkdir(parents=True)
        subprocess.run(["pdftoppm", "-r", "90", "-png", str(pdf), str(pages_dir / "p")], check=True)
        pngs = sorted(pages_dir.glob("p-*.png"), key=lambda p: int(re.search(r"(\d+)", p.stem).group(1)))
        out["pages"] = len(pngs)
        out["page_images"] = [str(p) for p in pngs]
        try:
            from PIL import Image
            ims = [Image.open(p).convert("RGB") for p in pngs]
            w, h = ims[0].size
            cols = min(3, len(ims))
            rows = (len(ims) + cols - 1) // cols
            sheet = Image.new("RGB", (cols * w + (cols - 1) * 12, rows * h + (rows - 1) * 12), "#777")
            for i, im in enumerate(ims):
                sheet.paste(im, ((i % cols) * (w + 12), (i // cols) * (h + 12)))
            sheet.save(pages_dir / "overview.png")
            out["overview"] = str(pages_dir / "overview.png")
        except Exception as e:  # contact sheet is a convenience
            out["overview_error"] = str(e)
        if shutil.which("pdftotext"):
            txt = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True).stdout
            out["pdf_words"] = len(txt.split())

    page = home / "src" / "articles" / f"{slug}.html"
    if page.exists():
        h = page.read_text()
        out["web"] = {"page": str(page), "references": h.count('<li id="ref-'), "figures": h.count('class="paper-fig"'),
                      "tables": h.count('class="paper-table"'), "sections": len(re.findall(r'<section class="paper-section', h))}
    (W / "review").mkdir(exist_ok=True)
    (W / "review" / "build.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 1 if proc.returncode or out.get("latex_errors") else 0


if __name__ == "__main__":
    sys.exit(main())
