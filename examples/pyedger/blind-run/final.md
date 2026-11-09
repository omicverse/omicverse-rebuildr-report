# Final check: pyedger (blind rebuild)

Locations are given twice: `article.md L<n>` / `meta.yaml L<n>` are lines of the source files in
`W/org-home/articles/pyedger/`; `pp. <n>` are the printed line numbers of the line-numbered preprint
copy `W/org-home/articles/pyedger/preprint/pyedger-preprint.pdf` (floats and captions carry no
line numbers).

## Result

- lint: 0 errors, 0 warnings (main text 1,958 words, 36 references).
- crossref: 35 references `ok`, reference 13 (rpy2) `no-doi` with URL, as guide/REFERENCES.md prescribes.
- build: exit 0, no LaTeX errors, no overfull box > 2 pt, no undefined citations; 7 pages; web page
  lists 36 references, 2 figures, 1 table, 12 sections.
- preprint (single column, line numbers): 8 pages, 296 numbered lines, 0 overfull boxes, no undefined
  references; `pyedger-preprint-latex.zip` present (tex, cls, bst, pdf, fig1.jpg, figS1.jpg).

## Preprint copy (line numbers)

The run prompt said to skip the preprint, but the user's request asked for the line numbers, which
only the preprint copy carries (the site PDF is the two-column OmicVerse layout without `lineno`).
The preprint was therefore built. The `W/org-home` snapshot of `scripts/build_articles.py` predates
the `--preprint` option, so `build_preprint()` and the `variant="preprint"` header of the current
omicverse-org-home checkout were run against `W/org-home/articles/pyedger` through
`<scratch>/rr-final-tools/build_preprint_w.py`
(`render_blocks_tex` and `pdarticle.cls` are identical in both copies). Checked on the page PNGs
(`W/review/preprint-pages/`): single column; line numbers 1-296 in the right margin on every page;
no OmicVerse logo or corner graphic; rail reads "Preprint, November 2026 · Technical Report";
footer carries the CC BY 4.0 licence line.

## Changes made in this stage

The first preprint build had text running over the line numbers. Both fixes are rewordings with
no change of content; the site PDF was rebuilt after them and is still clean.

1. article.md L51 (pp. 92-98), Use in OmicVerse: overfull by 62.5 pt and 19.8 pt in the preprint.
   "`method="edgepy"` runs … and `method="limma"` takes" -> "With `method="edgepy"` it runs … and
   with `method="limma"` it takes"; "`ov.bulk.spikein_chip_analysis` compares paired spike-in
   ChIP-seq samples" -> "The spike-in ChIP-seq function `ov.bulk.spikein_chip_analysis` compares
   paired samples" (`spikein_chip_analysis` is a function: OV `omicverse/bulk/_spikein_chip.py:679`).
2. article.md L160 (pp. 288-289), Notes item 4: overfull by 2.4 pt in the preprint.
   "`exactTest(dispersion=...)` accepts a numeric vector." -> "The `dispersion` argument of
   `exactTest` accepts a numeric vector."

## Checklist

### Mechanical (tools)

- [x] `tools/lint.py` — 0 errors, 0 warnings.
- [x] `tools/crossref.py check` — every reference ok (rpy2 has no DOI by design).
- [x] `tools/build.py` — exit 0, no LaTeX errors, no overfull > 2 pt, no undefined citations; web
      page lists every reference (36) and figure (2) and the table.

### Read the PDF (W/review/pages/p-1 … p-7)

- [x] p.1: title, authors with affiliation and correspondence marks, five affiliations,
      correspondence e-mails, summary, keywords.
- [x] No table alone on a page; no heading at the bottom of a page. Fig. 1 has p.4 to itself with
      about a fifth of the page blank below the legend — accepted (see warnings).
- [x] Table 1 (cited p.1, article.md L9) at the top of p.2; Fig. 1 (first cited p.3, L63) on p.4.
- [x] Supplement starts on a new page (p.6) after the references (p.5).
- [x] No text in the margin; no inline code overflowing a column (site PDF and preprint).

### Content

- [x] Title (meta.yaml L5) descriptive, no claim.
- [x] Abstract (meta.yaml L19-34; pp. 12-25): scope, how built, headline numbers (identical calls,
      same significant pathways, P-values within 1.2 × 10⁻⁵, 3.4-3.5× faster on eight threads),
      OmicVerse integration, licence and availability.
- [x] Introduction has four paragraphs (article.md L3, L5, L7, L9; pp. 28-47); rpy2, PyDESeq2 and
      InMoose cited neutrally.
- [x] Statistical model (L31) cites the method papers ([@3-8], [@17-22]).
- [x] Numbers traced: re-derived from `port/report/figures/comparison_per_task.tsv`,
      `timing_full.tsv`, `timing_stages_BRCA.tsv` and `evidence/numbers.json` — 4,972 samples,
      421-1,208, 206,021 genes, 22,730-27,801 and 18,455-21,161 genes kept, 61,578 QL calls,
      0 discordant calls/FDR flips, Table 1 maxima (4.9e-15, 1.1e-12, 5.6e-10, 8.6e-10, 1.2e-5,
      3.3e-8, 3.8e-7, 9.7e-13, 5.1e-8), 1.3e-6 in the draws, 257/400 pathways, 8 seed flips,
      2.5e-8 and 0.081 NES, 351/277/102 s, 1.1-1.3× and 3.4-3.5× (per-cohort ratios 1.12-1.31 and
      3.40-3.52), all 15 stage timings in L147, 42 tests / 28 parity cases, 10 of 16 commits.
      AveLogCPM 5 × 10⁻¹² (Table 1, L17) comes from the Fig. 1c legend (05_figures.py), not a TSV.
- [x] Nothing about earlier releases; no `old*` number used (6, 24, 1.16-1.26, 0.79, 443 absent).
- [x] No defensive asides; set-up details are in Supplementary methods (L139-149).
- [x] Future work (L82; pp. 136-142) lists what is not ported, as plans.
- [x] Figure legends (L65-68, L165-168) describe each panel and match the figures (colours, axes,
      thresholds); the in-figure label mismatches are listed under open items.
- [x] Use of AI tools (L88-90; pp. 152-156) and Conflicts of interest (L92-94; pp. 157-158)
      present — authors must confirm both.
- [x] OmicVerse API names checked against omicverse/omicverse master through `gh api`:
      `omicverse.external.pyedger` (alias, `sys.modules[__name__] = pyedger`), `ov.bulk.pyDEG`
      (`deg_analysis`, methods `edger`/`edgepy`/`limma` at `_Deseq2.py:799/845/889`),
      `ov.single.Milo.da_nhoods(..., solver="edger")` (`_milo_dev.py:414-423`),
      `ov.single.DCT` `method == 'milopy'` with `solver="edger"` (`_deg_ct.py:180-186`),
      `ov.bulk.spikein_chip_analysis` (`_spikein_chip.py:679`, exported in `bulk/__init__.py:50`).

## Warnings accepted, and why

- Reference 13 (rpy2), `no-doi`: the software has no paper; REFERENCES.md gives this exact line.
- 36 references, one above the 20-35 range of guide/REFERENCES.md; lint does not flag it and each
  reference is cited for a distinct statement.
- Fig. 1 alone on p.4 of the site PDF with about 20% blank below the legend: it is a full-width
  float in the two-column template, which places such floats only at the top of a page or on a
  float page, so body text cannot fill the space below it.
- Site PDF: two underfull lines (badness 1082 and 1052) in the code-dense paragraph article.md
  L51; spacing is slightly loose, nothing overflows.
- Preprint p.6: the references end about two thirds down the page because the supplement must
  start on a new page.
- Reference 13 URL breaks across lines ("rpy2.githu / b.io") through `xurl` in the template
  (pdarticle.cls); the reference text itself follows REFERENCES.md.

## Reader pass (new to the package)

What the package is (abstract; L3-9), how it was tested (L57-59, Supplementary methods) and the
result (L63-76, Table 1, Fig. 1) are clear on a first read. Paragraphs that do not fully earn their
place in the main text:

- article.md L41 (pp. 76-78), "One detail matters on large cohorts" (`q2qnbinom` on the log
  scale): a single implementation detail between the parity overview and the test suite; the same
  mechanism is already in Supplementary methods L149. Candidate to fold into L149 or into the
  parity paragraph L39.
- article.md L43 (pp. 81-82), last sentence ("pyedger 0.2.x tracks edgeR 4.10.5 (Bioconductor 3.23) and uses
  the defaults of edgeR 4.10"): repeats Notes item 1 (L153) and L35/L9.

Neither was changed here (content decisions for the authors).

## Open items

1. Fig. 1 artwork (`port/report/scripts/05_figures.py`, then re-export `figures/fig1.jpg`; legend
   at article.md L67): panel c in-figure label "unit-test tolerance" (05_figures.py:204) vs legend
   "default tolerance of the R-parity tests"; panel e x-axis "TCGA-LUAD, normal vs tumour (20 draws
   each)" vs legend "tumours versus as many normals" (05_figures.py:237); panel b legend sits on the
   data; panel c legend needs an opaque frame; fonts below 5.5 pt at 05_figures.py:154/192/209/256.
   Carried over from layout-r2 finding 5 and tone-r2 finding 11; outside article.md/meta.yaml.
2. Data and code availability, article.md L86 (pp. 143-151): data download date, R patch level of
   the benchmark run (text says R 4.5; parity references say R 4.5.3, L43), fgsea version, Python
   and package versions of the run, and CPU/cores/memory are not recorded in W/port or W/evidence;
   the authors must supply them (evidence/benchmark.md:177-179, :467-468).
3. PyPI: "installed from PyPI" (article.md L86, p. 144; meta.yaml L33) could not be verified
   for 0.2.3 (PyPI outside the allowed network; the publish workflow is manual). Confirm 0.2.3 is
   on PyPI before publication.
4. OmicVerse pins `pyedger>=0.2.2` (OV pyproject.toml:86), not 0.2.3, while article.md L51
   (pp. 92-98) describes OmicVerse using the 0.2.3 code. Raise the pin or accept.
5. Port test suite: 2 of the 42 cases fail on macOS arm64 (`test_tmm_tied_log_ratios`, relative
   difference 9.8e-4; `test_tmmwsp` tied pair, 8.5e-4; evidence/implementation.md:430-436). The
   report (article.md L43, pp. 79-82) states only the counts, not that all pass; the tied-ratio
   references should be regenerated or the platform recorded in `tests/data/make_reference.R`.
6. Preprint build path: the `W/org-home` snapshot has no `--preprint`; if the article is copied
   into omicverse-org-home, rebuild the preprint there with
   `scripts/build_articles.py --pdf --only pyedger --preprint`.

## Files the authors must review before publication

- `articles/pyedger/article.md` L88-90 — Use of AI tools (pp. 152-156): confirm the description of
  Claude's role and the 10-of-16 commit count.
- `articles/pyedger/article.md` L92-94 — Conflicts of interest (pp. 157-158): confirm for all three
  authors.
- `articles/pyedger/meta.yaml` L9-18 — author names, affiliation marks, affiliations,
  corresponding e-mails; L19-34 abstract.
- `articles/pyedger/article.md` L84-86 — Data and code availability (open items 2-3).
- `articles/pyedger/figures/fig1.jpg`, `figS1.jpg` — open item 1.
- `articles/pyedger/preprint/pyedger-preprint.pdf` and `pyedger-preprint-latex.zip` — the
  line-numbered single-column copy (CC BY 4.0).
- `src/assets/articles/pyedger/pyedger.pdf` and `src/articles/pyedger.html` — the site PDF and page.
