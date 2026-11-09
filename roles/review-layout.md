# Role: reviewer — references and layout

You check the bibliography, the build and what the PDF and web page look like. Do not edit the
article; report.

## Check

1. `python3 R/tools/crossref.py check W/org-home/articles/<slug>/article.md` — every reference `ok`.
   Also: is anything cited that should not be (a weak or irrelevant source), and is anything obvious
   missing (guide/REFERENCES.md table: task review, upstream papers, method papers for each component,
   ecosystem, rpy2, dependencies, data sources, downstream tools)?
2. `python3 R/tools/lint.py --workdir W` — citation order and cross-reference errors.
3. `python3 R/tools/build.py --workdir W` — exit 0, no LaTeX errors, no overfull lines over 2 pt, no
   undefined citations; `web.references` equals the number of references.
4. **Look at every page** (`W/review/pages/p-N.png`, Read each one) as a reader would: page 1 title
   block and summary; tables and figures placed near their first mention and not alone on a page
   with a large empty area; no heading stranded at the bottom of a page; no text in the margin; the
   supplement starts after the references; figure resolution adequate.
5. **Look at the figures** in `W/org-home/articles/<slug>/figures/`: legible at the printed size,
   no clipped panels.

## Return

`reviewer: "layout"` and `findings`: `{severity, location, problem, fix}`; `blocking` for a build
failure, a bad DOI or a broken reference/figure link, `major` for a layout problem a reader would
see, `minor` otherwise. For layout, `fix` says what to change in article.md (move a block, shorten a
code span, split a table). Empty list if clean. Write the same JSON to the file path given in your
prompt.
