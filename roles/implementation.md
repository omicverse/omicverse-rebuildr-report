# Role: implementation analyst

Write `W/evidence/implementation.md`: everything the Introduction and Implementation sections need
about the package, with the file each fact came from.

## Read

`R/guide/EVIDENCE.md` (the table at the end says where each part comes from), then in `W/port/`:
README.md, port.yaml, pyproject.toml, CHANGELOG.md (current release entry only — features, not
bug stories), the package source (`__init__.py` for the public API, the kernels, threading),
`tests/` (count the parity tests; how references are generated, e.g. `tests/data/make_reference.R`;
which upstream and dependency versions they pin).

Then the OmicVerse integration: `gh search code "<package>" --repo omicverse/omicverse` and read the
calling code (`gh api repos/omicverse/omicverse/contents/<path> --jq .content | base64 -d`) to get
the exact public API and the methods that call the package. Do not infer an API from its name.

Finally the AI-assistance record (the clone is shallow, so use the API):
`gh api 'repos/<owner>/<repo>/commits?per_page=100' --jq '.[].commit.message'` and count commits
with a `Co-Authored-By: Claude` (or other AI) trailer.

## Write `W/evidence/implementation.md`

Sections, each fact followed by its source in brackets (`[README.md]`, `[<package>/_core.py]`):

1. **Identity**: package, PyPI name, current version, licence, repository, upstream package and the
   exact upstream version it tracks, upstream's own dependencies that were ported.
2. **Scope**: implemented functions/workflows (upstream name ↔ Python name), naming conventions,
   data structures, return types; what is explicitly out of scope (for future work).
3. **The statistical model / method** in plain words, with the upstream papers it relies on (names
   and years only; the literature stage finds DOIs).
4. **How parity is achieved**: which compiled code paths and R routines are ported, concrete
   numerical details that matter on real data (stated as features of the current release), the
   test suite (count, reference versions, how references are regenerated).
5. **Performance mechanisms**: what is cached, vectorised, compiled or parallelised, and whether
   results depend on thread count.
6. **Dependencies**: core Python dependencies with versions if pinned.
7. **Use in OmicVerse**: exact functions and arguments, which OmicVerse methods call the package
   (with file paths in the OmicVerse repository).
8. **Notes for R users**: indexing, defaults, version caveats, API differences (from README).
9. **AI assistance**: n of N commits with an AI co-author trailer; what they covered (code, tests,
   benchmark, docs).
10. **Gaps**: anything a report would need that you could not find.

## Return

`file` (path written), `summary` (5 lines), `gaps` (list).
