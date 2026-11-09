# Final checklist

Run before declaring a report done. Every box must be ticked or the reason written in
`W/review/final.md`.

## Mechanical (tools)

- [ ] `python3 tools/lint.py --workdir W` — 0 errors; every warning looked at and either fixed or
      justified in final.md
- [ ] `python3 tools/crossref.py check W/org-home/articles/<slug>/article.md` — every reference `ok`
- [ ] `python3 tools/build.py --workdir W` — exit 0, no LaTeX errors, no overfull lines > 2 pt,
      no undefined citations, web page lists every reference and figure

## Read the PDF (open every PNG in W/review/pages/)

- [ ] page 1: title, authors with marks, affiliations, correspondence, summary, keywords
- [ ] no figure or table alone on a page with a large empty area, no heading at the bottom of a page
- [ ] Table 1 and Fig. 1 appear near where they are first cited
- [ ] the supplement starts on a new page after the references
- [ ] no text runs into the margin; inline code does not overflow a column

## Content

- [ ] title is descriptive and makes no claim (guide/STRUCTURE.md)
- [ ] abstract: scope, how built, 2–4 headline numbers, integration and availability
- [ ] introduction has the four paragraphs; related tools cited neutrally
- [ ] statistical model paragraph cites the method papers
- [ ] every number traces to `evidence/numbers.json`, a TSV or the port repository
- [ ] nothing about earlier releases; no `old*`/`prev*` numbers
- [ ] no defensive asides; set-up details neutral and in Supplementary methods
- [ ] future work lists what is not ported, as plans
- [ ] figure legends describe each panel and match what the figure shows
- [ ] Use of AI tools and Conflicts of interest present (marked for author confirmation)
- [ ] OmicVerse API names checked against the OmicVerse source
