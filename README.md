# omicverse-rebuildr-report

Writes the technical report for an R package rebuilt in Python, from the port's benchmark, as an
article on [omicverse.org/articles](https://omicverse.org/articles): a journal-style web page and a
two-column PDF, plus a single-column copy for preprint servers.

It is the last step after [omicverse-rebuildr](https://github.com/omicverse/omicverse-rebuildr):
rebuildr ports the package and proves parity; rebuildr-report turns that evidence into a paper.

```
request.yaml ─▶ Prepare ─▶ Gather ──────────────▶ Draft ─▶ Review ──────────────▶ Revise ─▶ Final
                clone       implementation          meta.yaml   tone & structure       apply      checklist
                port +      benchmark & numbers     article.md  facts & numbers        findings,  lint, refs,
                org-home    literature (Crossref)   figures     references & layout    rebuild    build, preprint
```

## What you provide

1. **The port repository** with a benchmark under `report/` (scripts, figures, `numbers.tex`).
   [guide/EVIDENCE.md](guide/EVIDENCE.md) says what it must contain and how to design it.
2. **A request** — only what the evidence cannot tell: authors, affiliations, dates, links.
   Copy [templates/request.template.yaml](templates/request.template.yaml);
   [examples/pyedger/request.yaml](examples/pyedger/request.yaml) is a complete one.

Everything else — features, model, parity details, every number, figure legends, 20–35 verified
references — is gathered from the port, the OmicVerse source and Crossref.

## Run it

Requirements: Python 3.9+ with `pyyaml` and `pillow` (`pip install -r requirements.txt`), git, the
GitHub CLI `gh`, TeX Live or MacTeX (`latexmk`, `pdflatex`) and poppler (`pdftoppm`, `pdftotext`).

**Multi-agent workflow (Claude Code).** Open Claude Code in this repository and say:

```text
Run the rebuildr-report workflow with args
{"repo": "<abs path to this repo>", "request": "<abs path>/request.yaml",
 "workdir": "<abs path to an empty work dir>", "preprint": true}
```

The workflow ([.claude/workflows/rebuildr-report.js](.claude/workflows/rebuildr-report.js)) runs
about ten agents: one setup, three evidence gatherers in parallel, a drafter, three reviewers in
parallel (tone and structure; facts and numbers; references and layout), a reviser (a second
review round only if the first found blocking or major problems) and a final check.

**Single session.** Without the workflow tool, run `/rebuildr-report <request.yaml> <workdir>`
([.claude/skills/rebuildr-report/SKILL.md](.claude/skills/rebuildr-report/SKILL.md)); it walks the
same stages with subagents.

**By hand.** Each stage is a role file in [roles/](roles/); any agent or person can follow them in
order: setup → implementation, benchmark, literature → drafter → review-tone, review-facts,
review-layout → reviser → final.

## Output

In the work directory:

| Path | What |
|---|---|
| `org-home/articles/<slug>/` | `meta.yaml`, `article.md`, `figures/`, `pdf.json` — the report source |
| `org-home/src/articles/<slug>.html`, `org-home/src/assets/articles/<slug>/` | the web page and the two-column PDF |
| `org-home/articles/<slug>/preprint/` | single-column, line-numbered, unbranded PDF and LaTeX zip (with `preprint: true`) |
| `evidence/` | the gathered notes and `numbers.json` |
| `review/` | lint, build, review findings, revisions, `final.md` with what the authors must confirm |

To publish, copy `articles/<slug>/` into an omicverse-org-home branch, run
`python3 scripts/build_articles.py --pdf --only <slug>` there and open a pull request. The authors
must confirm the "Use of AI tools" and "Conflicts of interest" statements first.

## The rules the report follows

- [guide/STRUCTURE.md](guide/STRUCTURE.md) — an application note: title, abstract, four-paragraph
  introduction, implementation, comparison on real data, conclusion and future perspectives,
  back matter, supplement; word budgets.
- [guide/STYLE.md](guide/STYLE.md) — no defensive writing, no negative results or post-mortems
  about earlier releases, no digs at other tools, results not process, one form per number.
- [guide/REFERENCES.md](guide/REFERENCES.md) — what to cite where; every DOI through Crossref.
- [guide/CHECKLIST.md](guide/CHECKLIST.md) — what "done" means.

`tools/lint.py` enforces the mechanical parts: claims in the title, banned defensive and
post-mortem wording, earlier-release versions and numbers, citation order, figure and table
references, numbers that cannot be traced to the evidence, leftover placeholders, length budgets.

## Tools

| Tool | Does |
|---|---|
| `tools/prepare.py` | clones the port and omicverse-org-home into the work directory, checks evidence and tools; `--blind` removes any published version |
| `tools/numbers.py` | `numbers.tex`/`numbers.json` → `evidence/numbers.json`, marking earlier-release keys as excluded |
| `tools/crossref.py` | `search`, `doi` (formatted reference line) and `check` (verify every reference in an article) |
| `tools/figures.py` | figure PDF/PNG → 2400 px JPG for the article |
| `tools/lint.py` | the static checks above → `review/lint.json` |
| `tools/build.py` | builds the page and PDF with omicverse-org-home, checks the LaTeX log, renders every page to PNG |

## Validation

[examples/pyedger](examples/pyedger) is the request for the pyedger report
([omicverse.org/articles/pyedger](https://omicverse.org/articles/pyedger)). Running the workflow on
it with `"blind": true` deletes the published report from the work directory and rebuilds it from
the evidence alone; [examples/pyedger/VALIDATION.md](examples/pyedger/VALIDATION.md) compares the
result with the published version.
