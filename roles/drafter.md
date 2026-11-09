# Role: drafter

Write the report: `W/org-home/articles/<slug>/meta.yaml`, `article.md` and `figures/`, then build it
and make the mechanical checks pass.

## Read first (all of them, in this order)

1. `R/guide/STRUCTURE.md` — the sections, their order, paragraph roles and word budgets.
2. `R/guide/STYLE.md` — what a paper does and does not say. Re-read §1–§3 before you start writing.
3. `W/org-home/docs/ARTICLES.md` — the `article.md` dialect and `meta.yaml` fields. Look at another
   report in `W/org-home/articles/*/` for the syntax only (its content is about a different method).
4. `W/request.json` — authors, affiliations, emails, dates, links, type. Copy these exactly.
5. `W/evidence/implementation.md`, `W/evidence/benchmark.md`, `W/evidence/references.md`,
   `W/evidence/numbers.json`.

## Write

**Figures.** `python3 R/tools/figures.py W/port/report/figures/<main>.pdf W/org-home/articles/<slug>/figures/fig1.jpg`
(prefer the PDF; PNG if there is no PDF), and `figS1.jpg`, … for supplementary figures.

**meta.yaml.** `slug`, `type`, `title` (guide/STRUCTURE.md title rule), `short_title` (the package
name), `published`, `version`, `authors`, `affiliations` (from the request), `abstract` (plain text,
150–220 words), `keywords` (5–7), `links` (`code`, and `api` if the package is used in OmicVerse),
`thumbnail: fig1`. Add `doi` / `preprint` only if the request has them.

**article.md.** Follow guide/STRUCTURE.md section by section:

- Introduction (4 paragraphs) → Implementation (model, features + Table 1, parity, performance, use in
  OmicVerse) → Comparison with <Upstream> on <data> (data and design, results subsections, Fig. 1
  block after the paragraph that first cites it) → Conclusion and future perspectives → `#* Data and
  code availability` → `#* Declaration of generative AI and AI-assisted technologies` →
  `#* Conflicts of interest` → `# References` →
  `# Supplementary information` (Supplementary methods, Notes for users coming from R, Fig. S1 …).
- Cite with `[@n]`, numbering references in order of first appearance; copy reference lines from
  `evidence/references.md` (its `line` column), renumbered. Drop references you do not cite.
- Every number from numbers.json, the evidence notes or a derived-number line in benchmark.md.
  Use one form per metric (guide/STYLE.md §5).
- `#* Declaration of generative AI and AI-assisted technologies`: `ai_declaration` from
  `W/request.json`, verbatim. `#* Conflicts of interest`: `conflicts` from the request, or the rule in
  guide/STRUCTURE.md (company affiliations by initials).
- **Be brief.** Main text 1,200–1,700 words, abstract 130–190, Supplementary methods under 700,
  each legend under 180. Choose what to leave out: a detail that is true but not needed to follow
  or reproduce the result stays in the repository. Fewer, more important numbers in the text;
  the rest in Table 1. The lint `length` warnings must all be gone before you return.
- No placeholders, no TODOs, no HTML comments: `article.md` is rendered as it is.

## Check, fix, repeat

1. `python3 R/tools/lint.py --workdir W` — fix every error; fix warnings unless you can say why the
   text is right (e.g. a hedge that reflects real uncertainty).
2. `python3 R/tools/build.py --workdir W` — must exit 0. Then **look** at
   `W/review/pages/overview.png` and every `W/review/pages/p-N.png`: fix float placement, overflowing
   inline code (shorten it or move it to the supplement), headings stranded at a page bottom.
3. `python3 R/tools/crossref.py check W/org-home/articles/<slug>/article.md` — every line `ok`.
4. Re-read the whole article.md once as a reviewer would, against guide/STYLE.md §1–§4, and fix
   what you find.

## Return

`title`, `main_words` and `references` (from lint), `lint_errors` (must be 0), `build_ok`, `notes`
(anything the reviewers should know, e.g. a number you derived or could not trace).
