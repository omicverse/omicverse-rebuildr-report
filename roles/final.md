# Role: final check

Decide whether the report is ready for the authors.

## Steps

1. Go through `R/guide/CHECKLIST.md` item by item, running the tools it names and reading the page
   PNGs. Fix small things yourself (a word, a rounding, a stray space) and rebuild; anything larger
   goes to `open_items`.
2. Read the article once from title to supplement as a reader new to the package: is it clear what
   the package is, how it was tested and what the result is? Note any paragraph that does not earn
   its place.
3. If your prompt asks for a preprint copy: `cd W/org-home && PATH=/Library/TeX/texbin:$PATH python3
   scripts/build_articles.py --pdf --only <slug> --preprint`, then check
   `articles/<slug>/preprint/<slug>-preprint.pdf` (single column, line numbers, no OmicVerse logo,
   CC BY line) and that `<slug>-preprint-latex.zip` exists.
4. Write `W/review/final.md`: the checklist with ticks, warnings you accepted and why, open items,
   and the list of files the authors must review before publication (the AI-use and conflicts
   statements always).

## Return

`pass` (true only if lint has 0 errors, every reference is ok and the build is clean), `lint_errors`,
`lint_warnings`, `references_ok`, `build_ok`, `pages`, `open_items` (list), `preprint_pdf` (path or
empty).
