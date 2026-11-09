# Role: setup

Prepare the work directory.

## Steps

1. `python3 R/tools/prepare.py <request.yaml> --workdir W` (add `--blind` if your prompt says
   BLIND). It clones the port repository and omicverse-org-home and writes `W/request.json` and
   `W/prepare.json`.
2. If `prepare.json` lists `numbers` (a numbers.tex or numbers.json under `W/port/report/figures/`):
   `python3 R/tools/numbers.py W/<that path> -o W/evidence/numbers.json`.
3. Check the tools in `prepare.json`: `latexmk`, `pdflatex`, `pdftoppm` and Python `PIL` are needed
   for the build. Missing tools are not fatal for the writing stages, but report them.
4. Do not read or summarise anything else; the Gather stage does that.

## Return

`ok` (true when the port has `report/` with a numbers file and figures), `missing` (list of missing
evidence or tools), `summary` (slug, package, upstream, current version from
`W/port/pyproject.toml`, number of numbers keys and how many are excluded).
