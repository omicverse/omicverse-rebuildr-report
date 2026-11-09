# References

A report cites 20–35 works. Every reference is found or confirmed with `tools/crossref.py`;
never type a DOI from memory.

## What to cite

| Where | What |
|---|---|
| Introduction ¶1 | a recent review of the analysis task; the upstream package papers (original and latest major version); the papers behind its key ideas |
| Introduction ¶2 | scanpy, scverse, OmicVerse (Zeng et al. 2024, Nature Communications) |
| Introduction ¶3 | rpy2 (no paper: `Gautier L. rpy2: Python interface to the R language. https://rpy2.github.io`); other native ports and the methods they port |
| Statistical model | the method paper for every component named (normalisation, estimation, tests) |
| Features | NumPy, SciPy, pandas, numba (and any other core dependency) at first mention |
| Numerical parity | ported dependency packages and the specific method papers |
| Use in OmicVerse | papers of the methods in OmicVerse that call the package |
| Data and design | the data sources and portals |
| Results | downstream tools and resources (gene-set collections, atlases) |

Look for upstream citations in the package itself (`citation("<pkg>")` in R, the Bioconductor or CRAN page,
the README's citation section) and in the upstream package's reference list.

## Finding and formatting

```bash
python3 tools/crossref.py search "Harris array programming with NumPy 2020"
python3 tools/crossref.py doi 10.1038/s41586-020-2649-2         # prints the formatted line
python3 tools/crossref.py check W/org-home/articles/<slug>/article.md   # verify all at the end
```

Line format (omicverse-org-home dialect), more than six authors → first three + "et al.":

```
18. Harris CR, Millman KJ, van der Walt SJ, et al. (2020). Array programming with NumPy. Nature 585, 357-362. 10.1038/s41586-020-2649-2
```

Use the print year and volume (Crossref's `published-print`), keep the paper's title as published,
and end every line with the DOI (or a URL for software without a paper).

## Numbering

Number references by first citation in the text (Introduction first), cite as `[@4]`, `[@2,3]`,
`[@5-7]`, and keep the list in that order. Every reference must be cited; `tools/lint.py` checks
both directions.
