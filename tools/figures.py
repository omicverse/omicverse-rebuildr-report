#!/usr/bin/env python3
"""Export benchmark figures to the JPGs an article uses.

    python3 tools/figures.py W/port/report/figures/fig1.pdf W/org-home/articles/<slug>/figures/fig1.jpg
    python3 tools/figures.py W/port/report/figures/figS1_pvalue_scatter.pdf .../figures/figS1.jpg

PDF figures are rendered with pdftoppm (first page), PNG/JPG figures are resized with Pillow.
Output: RGB JPEG, 2400 px wide (or the source width if smaller), quality 88. The org-home build
makes the web copies and thumbnails from these files.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

WIDTH = 2400


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", type=Path)
    ap.add_argument("dest", type=Path)
    ap.add_argument("--width", type=int, default=WIDTH)
    a = ap.parse_args()
    a.dest.parent.mkdir(parents=True, exist_ok=True)
    if a.src.suffix.lower() == ".pdf":
        exe = shutil.which("pdftoppm")
        if not exe:
            sys.exit("pdftoppm not found (install poppler)")
        with tempfile.TemporaryDirectory() as td:
            stem = Path(td) / "page"
            subprocess.run([exe, "-png", "-singlefile", "-f", "1", "-l", "1", "-scale-to-x", str(a.width),
                            "-scale-to-y", "-1", str(a.src), str(stem)], check=True)
            im = Image.open(f"{stem}.png")
            im.load()
    else:
        im = Image.open(a.src)
    if im.mode in ("RGBA", "LA", "P"):
        bg = Image.new("RGB", im.size, "white")
        rgba = im.convert("RGBA")
        bg.paste(rgba, mask=rgba.split()[-1])
        im = bg
    im = im.convert("RGB")
    if im.width > a.width:
        im = im.resize((a.width, round(im.height * a.width / im.width)), Image.LANCZOS)
    im.save(a.dest, "JPEG", quality=88, optimize=True)
    print(f"[figures] {a.dest} {im.width}x{im.height}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
