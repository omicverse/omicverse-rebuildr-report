# Role: benchmark analyst

Write `W/evidence/benchmark.md`: the design, every result number and a panel-by-panel description of
each figure, so that the drafter never has to open the benchmark itself.

## Read

`R/guide/EVIDENCE.md`, then `W/port/report/README.md`, every script in `W/port/report/scripts/`
(data preparation, upstream run, Python run, downstream analysis, figures, the driver), the TSVs in
`W/port/report/figures/`, and `W/evidence/numbers.json` (made by the setup stage; keys marked
`"excluded": true` describe an earlier release — list them under "Do not use" and never quote them).
Look at every figure (Read the PNG, or render the PDF with
`python3 R/tools/figures.py <pdf> W/review/_look_<name>.jpg` and Read that).

## Write `W/evidence/benchmark.md`

1. **Data**: sources (portal, URLs, file names), cohorts/data sets and sizes, inclusion/exclusion
   steps (from the preparation script), the small-sample draws (sizes, number of draws, seed,
   sampling without/with replacement).
2. **Pipeline**: exactly what both packages ran (functions, design, defaults), thresholds used for
   calls, number of features retained.
3. **Downstream analysis**: tool, gene sets / resource and version, ranking statistic, size limits,
   seeds, significance threshold.
4. **Run-time set-up**: what was timed, repetitions, threads, BLAS pinning, how runs were scheduled
   (from the driver script), hardware if stated.
5. **Software versions** on both sides.
6. **Results**: a table `key | value | meaning` for every non-excluded key in numbers.json, then any
   number that is only in a TSV or a figure label (with the file it came from).
7. **Derived numbers**: anything the report will need that must be computed (speed-ups as the
   inverse of time ratios, ranges, totals). Show the formula and inputs, e.g.
   `speed-up on 1 thread = 1/rtMax … 1/rtMin = 1/0.83 … 1/0.67 = 1.20 … 1.49 → "1.2 to 1.5 times"`.
8. **Figures**: for each figure file, what each panel shows — axes, colours, thresholds, annotations,
   any logos or labels in the image — and the suggested legend facts.
9. **Do not use**: excluded keys and any table describing an earlier release (e.g. `*_v<old>.tsv`).
10. **Gaps**.

## Return

`file`, `summary` (5 lines: data size, headline agreement numbers, speed), `gaps`.
