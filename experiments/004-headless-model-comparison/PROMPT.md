# Headless model comparison prompt

Read this repository without modifying any files. Treat the task as a
Path C experiment: AI output is a proposal, not proof, and human acceptance
is mandatory.

Analyze the repository's current research position and propose one narrowly
scoped next experiment that tests an unresolved question. Return a structured
report with exactly these headings:

1. `Executive summary`
2. `Evidence reviewed` — cite repository paths and quote no more than short
   phrases
3. `Proposed benchmark` — hypothesis, independent/dependent variables,
   controls, procedure, and stopping rule
4. `Measurement plan` — define observable metrics and scoring
5. `Risks and unsupported claims`
6. `Reproducibility checklist`
7. `Machine-readable appendix` — a fenced JSON object with keys
   `hypothesis`, `open_questions`, `inputs`, `controls`, `metrics`,
   `risks`, and `confidence`

Stay within 1,500 words. Do not suggest changing source files, do not use
network access, and do not claim that an experiment was run. Prefer a design
that can be repeated without an API key.
