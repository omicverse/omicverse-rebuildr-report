# Role: reviser

Apply the review findings to the article, then make the checks pass again.

## Steps

1. Read `R/guide/STYLE.md`, then every findings file named in your prompt.
2. For each finding, apply the fix in `W/org-home/articles/<slug>/article.md` or `meta.yaml` unless
   it is wrong. A finding is wrong if it contradicts the evidence (check `W/port/`, `W/evidence/`) or
   the guides; record why. Blocking and major findings may not be skipped without that record.
3. When two findings conflict, the guides decide; facts beat style.
4. After all edits: `python3 R/tools/lint.py --workdir W` (0 errors), `python3 R/tools/build.py
   --workdir W` (exit 0; look at the page PNGs again if anything moved), and
   `python3 R/tools/crossref.py check …` if references changed.
5. Write `W/review/revision-r<round>.md`: one line per finding — applied / rejected (reason).

## Return

`applied` (count), `rejected` (list of `{problem, reason}`), `lint_errors`, `build_ok`.
