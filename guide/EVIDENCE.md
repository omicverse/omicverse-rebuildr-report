# Evidence

A report is written from evidence, never from memory. This page says what the port repository must
provide, how to design the benchmark if it is missing, and where each part of the report comes from.

## What the port repository provides

```
<port repo>/
  README.md, port.yaml          scope, API, upstream package and version, parity table
  pyproject.toml                current version (the version the report describes)
  CHANGELOG.md                  feature list of the current release only (never bug narratives)
  <package>/                    source: the implementation details in "Numerical parity" come from here
  tests/                        number of parity tests, reference versions, how references are generated
  report/
    README.md                   how to reproduce: data download, environments, commands
    scripts/01_… 05_…           data preparation, upstream run, Python run, downstream analysis, figures
    scripts/run_all.sh          the benchmark driver (threads, BLAS pinning, repetitions)
    figures/fig1.pdf|png        the main figure (panels a–e)
    figures/figS*.pdf|png       supplementary figures
    figures/numbers.tex|json    every number quoted in the report, one key per number
    figures/*.tsv               per-task tables behind the figures
```

`tools/prepare.py` reports what is missing. Without `report/` there is nothing to write about:
stop and design the benchmark first.

## Benchmark design (for a port that has none yet)

The benchmark answers one question: does a user get the same results in Python as in R?

1. **Real data at several scales.** Five to ten public data sets that differ in size, plus a
   **small-sample regime** drawn from one of them (many random draws at a few small sizes, fixed
   seed).
2. **The upstream defaults.** Both packages run the same default pipeline, end to end, with the
   upstream release pinned (Bioconductor via bioconda) and the Python release pinned.
3. **Four criteria.**
   - *Calls*: the discrete result users act on (significant features at the usual thresholds;
     clusters; labels) — agreements and disagreements per data set.
   - *Downstream*: one standard analysis on top of the result, run on both outputs with the same
     seed, plus once more with a second seed to show its own noise.
   - *Numerical agreement*: per-feature relative differences for every intermediate quantity as
     CDFs; the maxima go in numbers.tex and Table 1.
   - *Speed*: wall time of the full pipeline, upstream vs Python on one thread and on N threads,
     under the same load, BLAS pinned to one thread.
4. **numbers.tex.** `05_figures.py` writes every quoted number as `\newcommand{\key}{value}`.
   Numbers that describe an earlier release must use an `old`/`prev` prefix (they are then excluded
   from the report) — better, keep them out of the report directory altogether.
5. **One main figure** with panels for calls agreement, downstream agreement against its own seed
   noise, CDFs of relative differences, run times and the small-sample maxima. Supplementary
   figures: per-data-set scatter plots of the main statistic.

## Where each part of the report comes from

| Report part | Evidence |
|---|---|
| Features, API, naming, dependencies | README.md, port.yaml, pyproject.toml, `<package>/__init__.py` |
| Statistical model | upstream documentation and method papers (cite them) |
| Numerical parity details | source code, tests/, `tests/data/make_reference.R`, README parity table |
| Performance mechanisms | source code (kernels, caching, threading), CHANGELOG of the current release |
| Use in OmicVerse | the OmicVerse source (`gh search code "<package>" --repo omicverse/omicverse`, then read the calling code) |
| Data and design | report/README.md, report/scripts/01–04, run_all.sh |
| All results numbers | report/figures/numbers.tex (via `evidence/numbers.json`) and the TSVs |
| Table 1 third column | numbers.json maxima, the Fig. 1c legend, the TSVs |
| Figure legends | the figure itself (look at it) and 05_figures.py (what is plotted, thresholds) |
| Data availability, versions, hardware | report/README.md, scripts, run logs, numbers |
| Use of AI tools | commit trailers in the port repository (`git log --format=%B | grep -i co-authored`) |
| Authors, affiliations, dates, DOI | the request (request.yaml) only |
