export const meta = {
  name: 'rebuildr-report',
  description: 'Write an OmicVerse technical report for a rebuilt R package from its benchmark evidence',
  whenToUse: 'A py-<pkg> port has a report/ benchmark and needs its technical report on omicverse.org/articles',
  phases: [
    { title: 'Prepare', detail: 'clone the port and omicverse-org-home, extract the numbers' },
    { title: 'Gather', detail: 'implementation, benchmark and literature evidence in parallel' },
    { title: 'Draft', detail: 'meta.yaml, article.md and figures; lint and build until clean' },
    { title: 'Review', detail: 'tone/structure, facts/numbers and references/layout reviewers in parallel' },
    { title: 'Revise', detail: 'apply the findings, rebuild' },
    { title: 'Final', detail: 'checklist, optional preprint copy' },
  ],
}

// args: { repo, request, workdir, blind?, preprint?, rounds? }  (absolute paths)
//   repo      checkout of omicverse-rebuildr-report
//   request   request.yaml (see templates/request.template.yaml)
//   workdir   empty or reusable work directory
//   blind     true to rebuild a report without access to any published version (validation)
//   preprint  true to also build the single-column preprint copy
//   rounds    review/revise rounds (default 2; round 2 runs only if round 1 had blocking/major findings)
const A = args || {}
if (!A.repo || !A.request || !A.workdir) {
  throw new Error('args must give repo, request and workdir as absolute paths')
}
const R = A.repo
const W = A.workdir
const ROUNDS = A.rounds || 2

const blind = A.blind
  ? '\nBLIND: this is a blind rebuild. Follow rule 5 in roles/COMMON.md strictly.'
  : ''
const stage = (role, extra = '') =>
  `You are the "${role}" stage of the omicverse-rebuildr-report pipeline.
Pipeline repository R = ${R}
Work directory W = ${W}
Read ${R}/roles/COMMON.md, then ${R}/roles/${role}.md, and do exactly what the role file says.${blind}${extra ? '\n' + extra : ''}`

const PREP = {
  type: 'object',
  properties: {
    ok: { type: 'boolean' },
    missing: { type: 'array', items: { type: 'string' } },
    summary: { type: 'string' },
  },
  required: ['ok', 'missing', 'summary'],
}
const NOTE = {
  type: 'object',
  properties: {
    file: { type: 'string' },
    summary: { type: 'string' },
    gaps: { type: 'array', items: { type: 'string' } },
  },
  required: ['file', 'summary', 'gaps'],
}
const DRAFT = {
  type: 'object',
  properties: {
    title: { type: 'string' },
    main_words: { type: 'number' },
    references: { type: 'number' },
    lint_errors: { type: 'number' },
    build_ok: { type: 'boolean' },
    notes: { type: 'string' },
  },
  required: ['title', 'main_words', 'references', 'lint_errors', 'build_ok', 'notes'],
}
const FINDINGS = {
  type: 'object',
  properties: {
    reviewer: { type: 'string' },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          severity: { type: 'string', enum: ['blocking', 'major', 'minor'] },
          location: { type: 'string' },
          problem: { type: 'string' },
          fix: { type: 'string' },
        },
        required: ['severity', 'location', 'problem', 'fix'],
      },
    },
  },
  required: ['reviewer', 'findings'],
}
const REVISION = {
  type: 'object',
  properties: {
    applied: { type: 'number' },
    rejected: {
      type: 'array',
      items: {
        type: 'object',
        properties: { problem: { type: 'string' }, reason: { type: 'string' } },
        required: ['problem', 'reason'],
      },
    },
    lint_errors: { type: 'number' },
    build_ok: { type: 'boolean' },
  },
  required: ['applied', 'rejected', 'lint_errors', 'build_ok'],
}
const FINAL = {
  type: 'object',
  properties: {
    pass: { type: 'boolean' },
    lint_errors: { type: 'number' },
    lint_warnings: { type: 'number' },
    references_ok: { type: 'boolean' },
    build_ok: { type: 'boolean' },
    pages: { type: 'number' },
    open_items: { type: 'array', items: { type: 'string' } },
    preprint_pdf: { type: 'string' },
  },
  required: ['pass', 'lint_errors', 'lint_warnings', 'references_ok', 'build_ok', 'pages', 'open_items', 'preprint_pdf'],
}

// ── Prepare ──────────────────────────────────────────────────────────────────
phase('Prepare')
const prep = await agent(
  stage('setup', `Request file: ${A.request}${A.blind ? '\nRun prepare.py with --blind.' : ''}`),
  { label: 'setup', phase: 'Prepare', schema: PREP, effort: 'low' },
)
if (!prep || !prep.ok) {
  log(`Stopped: evidence or tools missing: ${prep ? prep.missing.join(', ') : 'setup failed'}`)
  return { stage: 'prepare', prep }
}
log(prep.summary)

// ── Gather (barrier: the drafter needs all three notes) ─────────────────────
phase('Gather')
const notes = await parallel(
  ['implementation', 'benchmark', 'literature'].map((role) => () =>
    agent(stage(role), { label: role, phase: 'Gather', schema: NOTE }),
  ),
)
const gaps = notes.filter(Boolean).flatMap((n) => n.gaps)
if (notes.some((n) => !n)) log('A Gather stage failed; the drafter will work from the notes that exist.')
if (gaps.length) log(`Evidence gaps: ${gaps.join(' | ')}`)

// ── Draft ────────────────────────────────────────────────────────────────────
phase('Draft')
const draft = await agent(stage('drafter'), { label: 'drafter', phase: 'Draft', schema: DRAFT })
if (!draft) return { stage: 'draft', prep, notes }
log(`Draft: "${draft.title}", ${draft.main_words} words, ${draft.references} references, lint errors ${draft.lint_errors}`)

// ── Review ⇄ Revise ──────────────────────────────────────────────────────────
const REVIEWERS = ['review-tone', 'review-facts', 'review-layout']
const history = []
for (let round = 1; round <= ROUNDS; round++) {
  // barrier: the reviser needs every reviewer's findings together
  const reviews = (
    await parallel(
      REVIEWERS.map((r) => () =>
        agent(stage(r, `Review round ${round}. Also write your findings JSON to ${W}/review/${r}-r${round}.json`), {
          label: `${r} r${round}`,
          phase: 'Review',
          schema: FINDINGS,
        }),
      ),
    )
  ).filter(Boolean)
  const findings = reviews.flatMap((r) => r.findings.map((f) => ({ ...f, reviewer: r.reviewer })))
  const serious = findings.filter((f) => f.severity !== 'minor')
  log(`Round ${round}: ${findings.length} findings, ${serious.length} blocking or major`)
  history.push({ round, findings: findings.length, serious: serious.length })
  if (!findings.length) break
  const revision = await agent(
    stage('reviser', `Round ${round}. Findings files: ${REVIEWERS.map((r) => `${W}/review/${r}-r${round}.json`).join(', ')}`),
    { label: `reviser r${round}`, phase: 'Revise', schema: REVISION },
  )
  history[history.length - 1].revision = revision
  if (!serious.length) break // only minor findings: no need for another review round
}

// ── Final ────────────────────────────────────────────────────────────────────
phase('Final')
const final = await agent(
  stage('final', A.preprint ? 'Build the preprint copy (step 3).' : 'No preprint copy this time; skip step 3.'),
  { label: 'final', phase: 'Final', schema: FINAL },
)
return {
  article: `${W}/org-home/articles/`,
  pdf: `${W}/org-home/src/assets/articles/`,
  prep: prep.summary,
  gaps,
  draft,
  rounds: history,
  final,
}
