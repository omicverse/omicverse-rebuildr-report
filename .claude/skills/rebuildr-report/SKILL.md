---
name: rebuildr-report
description: Write the OmicVerse technical report (omicverse.org/articles page, two-column PDF, preprint copy) for an R package rebuilt in Python, from the port repository's report/ benchmark. Use when asked to write, draft or rebuild a technical report or article for a py-<pkg> port, or to run omicverse-rebuildr-report.
---

# rebuildr-report

Arguments: `<request.yaml> <workdir> [blind] [preprint]`. `R` below is this repository's root
(two levels above this file); use absolute paths everywhere.

If the Workflow tool is available, prefer it: run the named workflow `rebuildr-report` with
`{"repo": R, "request": <abs request>, "workdir": <abs workdir>, "blind": …, "preprint": …}` and
report its result. Otherwise run the same stages yourself, as below. Each stage's instructions are
in `R/roles/<role>.md`; every stage first reads `R/roles/COMMON.md`.

1. **Setup** — follow `roles/setup.md` yourself. Stop if it reports missing evidence; tell the user
   what the port's `report/` lacks (guide/EVIDENCE.md).
2. **Gather** — start three subagents in one message (Agent tool, general-purpose), one each for
   `roles/implementation.md`, `roles/benchmark.md`, `roles/literature.md`. Prompt each with: its role
   file path, `R`, `W`, and "BLIND" if requested. Wait for all three.
3. **Draft** — follow `roles/drafter.md` yourself (or one subagent). Lint must show 0 errors and the
   build must pass before review.
4. **Review** — three subagents in one message: `roles/review-tone.md`, `roles/review-facts.md`,
   `roles/review-layout.md`, each told to write `W/review/<role>-r1.json`.
5. **Revise** — follow `roles/reviser.md` with those files. If round 1 had blocking or major
   findings, run step 4 and 5 once more (round 2).
6. **Final** — follow `roles/final.md` (with the preprint copy if requested) and report to the user:
   where the article and PDFs are, `W/review/final.md`, and that the authors must confirm the
   "Use of AI tools" and "Conflicts of interest" statements before publication.

Do not commit, push or open pull requests unless the user asks.
