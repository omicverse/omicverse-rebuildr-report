# Validation: blind rebuild of the pyedger report

**Question.** Given only this repository, the port repository and `request.yaml`, can the pipeline
write a report as good as the one published at
[omicverse.org/articles/pyedger](https://omicverse.org/articles/pyedger)?

**Run.** `.claude/workflows/rebuildr-report.js` at commit `029c4ed`, with
`{"request": "examples/pyedger/request.yaml", "blind": true}` (the request then still listed the
original three authors). `--blind` deleted the published article from the work directory and the
org-home git history. 14 agents (setup, 3 gatherers, drafter, 2 review rounds of 3 reviewers + a
reviser each, final), 74 minutes, about 2.7 M subagent tokens, 619 tool calls.

**Blindness.** No agent that wrote or reviewed the text opened the published report, the live page
or the org-home history (checked over every tool call in the transcripts). The final stage, after
the text was finished, imported the preprint builder from a local omicverse-org-home checkout; the
roles now forbid reading any checkout other than `W/org-home` (COMMON rule 6).

Outputs are in [blind-run/](blind-run): `article.md`, `meta.yaml`, the PDF, a contact sheet of its
pages, the final stage's report and the comparison.

## Result

| | Blind rebuild | Published |
|---|---|---|
| Title | pyedger: a Python implementation of edgeR for differential expression analysis of count data | pyedger: a Python implementation of edgeR for differential expression analysis |
| lint | 0 errors, 0 warnings (with the budgets of the time) | 0 errors |
| References | 35 with DOI, all verified + rpy2 | 27 with DOI + 1 URL |
| Shared references | 23 | 23 |
| Abstract / main text | 208 / 1,932 words | 129 / 1,366 words |
| Supplementary methods | 925 words | 305 words |
| Fig. 1 legend | 257 words | 160 words |
| PDF | 7 pages; Fig. 1 alone on page 4 with a blank band | 5 pages |
| Banned phrases, earlier-release numbers | 0 | 0 |

Structure, tone and claims match the published report: the same four-paragraph introduction, the
statistical model, Table 1, the same comparison and the same headline results, with no defensive
writing, no post-mortem of 0.2.2 and no digs at other tools.

**Better than the published report.**

- Finer fact-checking: "42 tests, 28 of which compare pyedger with references from edgeR 4.10.5";
  every OmicVerse call path checked in the OmicVerse source (`pyDEG` QL and LRT, Milo `da_nhoods`,
  `ov.single.DCT`, spike-in ChIP); derived numbers shown with their formulas.
- A related port the published report missed (InMoose), cited neutrally.
- More references for the method components (Benjamini–Hochberg, weighted likelihood, robust
  dispersion, voom).

**Worse than the published report.** It says too much. It is 40% longer, and the supplement is three
times as long. The Fig. 1 legend is long enough that the figure takes a page of its own. The guides
then allowed up to 2,100 words, so nothing told the drafter to stop.

## Changes made after this run

- `guide/STRUCTURE.md`, `roles/drafter.md`: concision is a requirement. Main text 1,200–1,700 words,
  abstract 130–190, Supplementary methods under 700, legends under 180, five or six pages.
- `tools/lint.py`: warns on each of those budgets.
- AI declaration: the request's `ai_declaration` is used verbatim, defaulting to the authors' standard
  text (`tools/prepare.py`). The conflicts statement uses initials, and adds "the other authors…"
  only when there are other authors.
- `roles/implementation.md`: count all tests and the upstream-reference tests separately; check for
  PyPI name collisions and other ports. A single-session run on pylimma (omicverse-org-home PR #32)
  reported "9 tests" where 5 compare with limma, and called an independent limma port on PyPI
  "unrelated".
- `roles/COMMON.md`: scratch files in `W/tmp/`; build only in `W/org-home`; do not act on user
  messages relayed to an agent mid-run (one reached the final stage here and made it build a
  preprint).
- `tools/crossref.py check`: titles are compared without difflib's autojunk heuristic, which
  reported a false title mismatch for long reference lines.
- Request template: names written given name first with the surname last ("Xu Meng" for 孟旭).

## What the evidence stage found in py-edgeR

Not report content, but worth fixing in the port:

- 2 of 42 tests (`test_tmm_tied_log_ratios`, the TMMwsp tied pair) fail on macOS arm64 at about
  1e-3 relative; `make_reference.R` does not record the platform the references were made on.
- README and LICENSE say the LGPL-3.0-or-later licence "matches upstream", but edgeR is GPL (≥ 2).
- Docstrings still name edgeR 4.0.16 and limma 3.58.1.
- No R-parity tests for robust GLM dispersion, `glm_residuals`, classic `estimateTagwiseDisp`
  (moment-based), several trend methods, RLE/upper-quartile and `filterByExpr` with a design.
- OmicVerse pins `pyedger>=0.2.2`, not 0.2.3; a Milo comment says robust QL is missing, which is no
  longer true.
- `port.yaml` gives the exact-test maximum 5.1e-8 for "68 analyses"; over all 68 tasks it is 9.4e-8.
- README cites an ATAC (GSE274113) comparison that has no script or data in the repository.
- The benchmark's hardware, software patch levels and download date are not recorded in the repo.
