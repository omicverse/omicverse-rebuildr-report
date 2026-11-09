# Role: literature

Write `W/evidence/references.md`: 22–35 verified references, each with the place in the report
where it will be cited.

## Read

`R/guide/REFERENCES.md` (what to cite where, line format), `R/guide/STRUCTURE.md` (sections),
`W/port/README.md` and `W/port/port.yaml` (upstream package, its citation, ported dependencies),
the upstream package's own citation (Bioconductor/CRAN page or `inst/CITATION`), and the benchmark
scripts in `W/port/report/scripts/` (data sources and downstream tools to cite).

## Steps

1. Make a list of claims that need a citation, by section (guide/REFERENCES.md table): the task
   review, upstream package papers (original + latest major version), the method paper for each
   model component and test the package implements, Python ecosystem (scanpy, scverse, OmicVerse),
   rpy2, other native ports and their upstream, core dependencies (NumPy, SciPy, pandas, numba …),
   ported dependency packages, OmicVerse methods that call the package, data sources, downstream
   tools and resources.
2. For each: `python3 R/tools/crossref.py search "<authors title year>"`, pick the right work, then
   `python3 R/tools/crossref.py doi <doi>` to get the formatted `line`. Check title, first author,
   year and journal against what you expected. Use the print year.
3. Software without a paper (rpy2): `Surname I. Title. URL` as in guide/REFERENCES.md.

## Write `W/evidence/references.md`

A table: `id | cite where (section, claim) | formatted line (from crossref.py) | doi`. Use short ids
(`edger2010`, `tmm`), not numbers — the drafter numbers them by first appearance.

## Return

`file`, `summary` (count, and any claim you could not find a reference for), `gaps`.
