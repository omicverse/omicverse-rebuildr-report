# Style

A report is a paper about the current release of a package. It states what the package is and
what the evidence shows, plainly and with confidence. A paper may have shortcomings; it does not
argue with an imagined reviewer. `tools/lint.py` enforces the mechanical parts of these rules.

In the examples, `pyfoo` is a Python port of the R package `fooR`.

## 1. No defensive writing

Do not pre-empt criticism, apologise for the evidence or explain differences away. State each fact
once, with its tolerance if it has one, and move on.

| Defensive | Written as a paper |
|---|---|
| Timings are single runs on a node shared with other jobs, so differences of 10–20% should not be over-interpreted. | *(nothing in the results; in Supplementary methods:)* Run times are wall-clock times of the full pipeline, with one run per data set and configuration. |
| Coefficients differ by at most 2 × 10⁻⁹ (relative differences look larger only for coefficients close to zero). | Coefficients differ by at most 2 × 10⁻⁹. |
| The larger differences come from the variance estimate, which fooR computes with `optimize(tol=1e-5)`, so it is only defined to about four digits in R itself. | Test statistics agree within 3 × 10⁻⁵, the tolerance of the optimiser fooR uses for the variance. |
| Results agree to the optimiser, not to the last bit. | *(say it once, in the results; do not repeat it as a caveat)* |
| pyfoo is used by OmicVerse, so OmicVerse users run the package validated here. | pyfoo is the fooR backend of OmicVerse: `ov.single.foo` calls it with … |

Banned: "should not be over-interpreted", "with caution", "note that", "it should be noted",
"admittedly", "to be fair", remarks about shared or busy machines.

## 2. No negative results, no post-mortems

The report describes the current release. It does not describe bugs in earlier releases, tests
that used to fail, what "the benchmark found", or how a problem "went unnoticed". A fix becomes a
feature of the current release:

| Post-mortem | Feature |
|---|---|
| In pyfoo 1.3, twelve cells were assigned to the wrong cluster because ties in the distance matrix were broken differently from R; pyfoo 1.4 fixes this. | Ties in the distance matrix are broken in R's order, which keeps cluster labels identical to fooR's when distances are tied. |
| The benchmark exposed an overflow in the likelihood for very large counts, which the unit tests had missed. | The likelihood is evaluated on the log scale, which keeps it finite for very large counts; on 1,000 extreme inputs pyfoo matches fooR to 10⁻¹⁰. |
| Validating on real data, rather than on the small simulations of the unit tests, was what found the remaining defects. | *(remove)* |

Never use numbers of an earlier release. `tools/numbers.py` marks them (`old*`, `prev*` keys) and
`tools/lint.py` fails if one appears. Do not read the CHANGELOG for anything but the feature list
of the current release. Release notes belong on GitHub, not in the report.

## 3. No digs at other tools

Cite related work for what it achieved. Do not quote another tool's limitation as a foil, and avoid
"not X but Y" contrasts that imply one.

| Comparative | Neutral |
|---|---|
| pybar showed that a port is useful, but also that it gives "similar, but not identical" results. The bar should be higher. | A native implementation removes these costs, as pybar has shown for barR. We set a specific target for pyfoo: an analysis in Python should return the same clusters and the same statistics as in R. |
| pyfoo gives users fooR's results, not an approximation of them. | pyfoo brings fooR's workflow to Python with results that match fooR to numerical precision. |

## 4. Results, not process

Write what is true of the software and the data, not how the authors got there: no "we found by
comparing against R", "regenerating the references reproduced every file byte for byte", "it turned
out". Methods describe the procedure in the past tense; the software is described in the present
tense.

## 5. Numbers

- Every number comes from the benchmark's numbers file, its tables, the port repository or a
  citation. If a number is derived (a speed-up from a time ratio), derive it from those and keep the
  same rounding throughout.
- One metric, one form: speed as "1.2 to 1.5 times faster", never "0.67 to 0.83 of the time" in
  one place and "faster" in another.
- At most four or five numbers in a paragraph. The rest go to Table 1, the figure or the supplement.
- Scientific notation as `$1.2 \times 10^{-5}$` in the body, `1.2 × 10⁻⁵` in the abstract.
- Thousands separators: `4,972`, `61,578`.

## 6. What goes in the supplement

Implementation trivia that only matters for bit-level agreement (a floating-point ulp, an R
indexing quirk), data-processing steps, run-time set-up, downstream-analysis settings, and notes for
users switching from R. The main text keeps one or two concrete details, stated as features.

## 7. Sentences

- Most sentences under 35 words; split anything over 45 (lint warns).
- Lists of more than five items: a table, or one semicolon-separated list introduced by a colon.
- Hedges ("may", "might", "could", "appears to") only where the evidence is genuinely uncertain.
- Package names keep their own case (pyfoo, fooR) even at the start of a sentence.
- No marketing words: "powerful", "seamless", "cutting-edge", "robust" (except as a statistical term).

## 8. Shortcomings

Shortcomings are allowed and stated once, plainly: in the future-work paragraph as plans ("Future
work includes the trajectory functions (`fooTraj`) …"), or in the Supplementary methods as a neutral
description of the set-up. Not as apologies in the results.
