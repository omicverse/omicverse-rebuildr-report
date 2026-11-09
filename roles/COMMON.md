# Common rules for every stage

You are one stage of the omicverse-rebuildr-report pipeline, which writes an OmicVerse technical
report (omicverse.org/articles/<slug>, a web page plus a two-column PDF) about a Python port of an
R package. Every stage starts from files, not from conversation: read what your role file lists.

## Paths

`R` is the pipeline repository, `W` the work directory (both given in your prompt).

| Path | What |
|---|---|
| `W/request.json` | the request: package, upstream, slug, authors, affiliations, dates, links |
| `W/prepare.json` | what `tools/prepare.py` found and which tools exist |
| `W/port/` | the port repository (source, tests, README, `report/` benchmark) |
| `W/org-home/` | omicverse-org-home; the article lives in `W/org-home/articles/<slug>/` |
| `W/org-home/docs/ARTICLES.md` | the article dialect (`article.md` syntax) and `meta.yaml` fields |
| `W/evidence/` | Gather notes: `implementation.md`, `benchmark.md`, `references.md`, `numbers.json` |
| `W/review/` | lint, build and review outputs |
| `R/guide/` | STRUCTURE.md, STYLE.md, EVIDENCE.md, REFERENCES.md, CHECKLIST.md |
| `R/tools/` | prepare.py, numbers.py, crossref.py, figures.py, lint.py, build.py |

Run tools from `R` with absolute paths, e.g. `python3 R/tools/lint.py --workdir W`.

## Rules

1. **Evidence only.** Every statement about the package or the benchmark must come from `W/port/`,
   `W/evidence/`, the OmicVerse source on GitHub, or a cited paper. Do not write from memory; if
   something cannot be found, say so in your output instead of guessing.
2. **Current release only.** The report describes the version in `W/port/pyproject.toml`. Nothing
   about earlier releases, their bugs or their numbers (guide/STYLE.md §2).
3. **Stay in your lane.** Write only the files your role names. Do not commit, push, open pull
   requests or post anything anywhere.
4. **Network.** Allowed: GitHub through `gh` (read-only), the Crossref API through
   `tools/crossref.py`, the upstream package's documentation pages. Nothing else.
5. **Blind runs.** If your prompt says BLIND, the report must be written from evidence alone: do not
   open omicverse.org/articles/<slug>, any earlier PDF or HTML of this report, or the history and
   pull requests of omicverse-org-home, and do not follow links to the published report that appear
   in the port repository.
6. **Return value.** Your final message is data for the orchestrator, not prose for a person:
   return exactly what your role's "Return" section asks for.
