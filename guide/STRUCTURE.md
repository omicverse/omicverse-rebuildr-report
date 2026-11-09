# Structure of a technical report

A report on a rebuilt package is an **application note**: it says what the package is, how it is
built, and shows on real data that it gives the same results as the original. The model is a
*Bioinformatics* Applications Note: about
1,200–2,000 words of main text, one main figure, one table, a supplement, 20–35 references.

Write the report in British English (normalisation, tumour, modelling), as the published reports are.

## Title

`<package>: a Python implementation of <Upstream> for <task>`
or `<package>: a Python package for <task>`.

The title says what the package is. It makes no claim: no "faithful", "exact", "identical",
"reproduces", "to numerical precision", "fast", "drop-in", "validated". Claims belong in the
abstract and the results, where the evidence is.

## Abstract (`meta.yaml: abstract`), 150–220 words, one paragraph

1. What the package is and what it covers (one sentence, list the main methods).
2. How it is built (one sentence: ported from the upstream code paths, versioned against a release).
3. The headline results with 2–4 numbers: data size, identical calls, the largest difference, speed.
4. Integration and availability: OmicVerse, licence, repository URL, PyPI.

Plain text only (no Markdown, no `$…$`): the list page shows it as text. Unicode such as `×`,
`–`, `10⁻⁵` is fine.

## Main text

Sections are `#` headings, subsections `##`. Word budgets are targets, not limits.

### `# Introduction` (4 paragraphs, 250–450 words)

1. **The task and the upstream method.** What the analysis is for, why the upstream package is
   the standard (cite its papers), what its key ideas are (cite the method papers).
2. **The Python ecosystem and the gap.** Omics analysis in Python (scanpy/scverse, OmicVerse);
   the upstream package exists only in R.
3. **The current workaround and the target.** rpy2 and its costs (a second language runtime,
   data conversion, options behind a binding layer). Cite other native ports neutrally ("as pybar
   has shown for barR"); never quote their weaknesses. State the package's target positively
   ("an analysis in Python should return the same results as the same analysis in R").
4. **Here we present.** "Here we present <package>, … We describe its implementation and compare
   it with <Upstream> <version> on <data>."

### `# Implementation` (500–750 words)

- `## Statistical model` (or `## Method`): one paragraph on the model the upstream package fits,
  in plain terms, with citations for each component. No code names unless needed.
- `## Features and code structure`: what is implemented (release number), naming (Python and R
  names), data structures, dependencies (cite NumPy, SciPy, pandas, numba … at first mention),
  threading. Refer to **Table 1**: upstream function ↔ Python function ↔ largest difference on the
  benchmark data.
- `## Numerical parity with <Upstream>`: how agreement is achieved — which compiled code paths and
  dependency packages were ported, which R numerical routines were reproduced, one or two concrete
  details that matter on real data stated as features, and the test suite (number of tests,
  reference versions). Pinning: which package versions track which upstream release.
- `## Performance` (if the package is faster): where the time goes and what the implementation does
  about it. No numbers here; they are in the results.
- `## Use in OmicVerse` (if integrated): the exact API (function and arguments) and
  which OmicVerse features use the package. Check the OmicVerse source; do not guess.

### `# Comparison with <Upstream> on <data>` (400–650 words)

- `## Data and design`: cohorts, sample sizes, the comparison made, the small-sample regime,
  the exact pipeline both packages ran, thresholds, and the criteria compared (calls, downstream
  analysis, numerical agreement, run time). Refer details to Supplementary methods.
- `## <Results subsection 1>` named after what it shows (calls and downstream analysis): agreement
  of the calls (with totals), downstream agreement (with the scale of its own noise), Fig. 1a–b, Fig. S1.
- `## Numerical agreement and speed`: largest differences per quantity (refer to Table 1 and
  Fig. 1c rather than listing everything), the small-sample result (Fig. 1e), speed as "X to Y times
  faster" on one and N threads with one concrete example (Fig. 1d).

The main figure goes in this section as a `:::figure 1 fig1.jpg` block after the paragraph that
first cites it.

### `# Conclusion and future perspectives` (2 paragraphs, 150–300 words)

1. What the package gives users, restating the headline results positively, and what the
   integration makes possible.
2. **Future work**: what is not yet ported (from the README's scope or the upstream function list),
   phrased as plans ("Future work includes …"), and how releases will follow the upstream package.
   This is where shortcomings go.

## Back matter (`#*` sections, before `# References`)

- `#* Data and code availability`: licence, PyPI, repository, where the benchmark scripts are,
  data sources with URLs and access date, software versions (Python side and R side), hardware.
  Neutral; no remarks about the machine being shared or busy.
- `#* Use of AI tools`: required by preprint servers. State what AI tools were used for (code,
  benchmark scripts, drafting and editing) — check the port repository's commit trailers
  (`Co-Authored-By: Claude …`) — and that the authors take responsibility.
- `#* Conflicts of interest`: required by preprint servers. Draft from the affiliations (a company
  affiliation is disclosed) and mark it for the authors to confirm.

## `# References`

Numbered in order of first citation, one line each, ending with the DOI (guide/REFERENCES.md).

## `# Supplementary information`

- `## Supplementary methods`: paragraphs with bold lead-ins — data processing (how counts were
  obtained, what was removed and why), sampling of small-sample draws, downstream-analysis settings
  (ranking statistic, gene sets, size limits, thresholds, seeds), run-time set-up (stated neutrally:
  "one run per cohort and configuration, BLAS pinned to one thread"), implementation details that
  matter for bit-level agreement.
- `## Notes for users coming from R`: numbered list — versions and defaults, 0- vs 1-based
  indices, API differences.
- `:::figure S1 …` supplementary figures.

## Table 1

`:::table 1` — title line — pipe table with columns `<Upstream> | <package> | Largest difference
from <Upstream> <version> on <data>`; one row per user-facing function or function pair; the third
column names the quantity and its largest relative difference (`P-value $2 \times 10^{-6}$`,
`same cells kept`).

## Figure legends

Title line: what the figure compares ("pyfoo 1.4.0 versus fooR 2.1.3 on <data>."). Legend: one bold panel label per panel (`**(a)**`), each saying what is plotted,
axes, colours and thresholds. No interpretation, no caveats, no remarks about how it was run.
