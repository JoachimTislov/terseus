# Abstraction-level comparison benchmark

Work read-only. Do not modify files, use network access, or claim that an
experiment was implemented. You may inspect these pinned local projects:

- `experiments/006-common-tools` — a small reusable utility repository;
- `experiments/006-lite-jnc` — a Go compiler/parser/transpiler;
- `experiments/006-foodsavr` — a Flutter application with inventory and meal
  planning.

Determine which abstraction level is most effective for expressing each
system while preserving extensibility. Compare exactly these levels:

**L0 — concrete implementation:** existing language modules, functions,
classes, tests, and configuration are the authoritative expression.

**L1 — typed reusable components:** explicit components with typed ports,
contracts, evidence, and versioned composition; generated code remains the
execution projection.

**L2 — recursive declarative system:** nested components/workflows are
declared in a compact representation; expansion, constraints, provenance,
and recursive termination produce implementation projections.

Do not assume L2 wins. Select the best level per system and explain when a
lower level is safer or more effective.

For each repository, inspect enough source, tests, and documentation to cite
specific paths and symbols. Then perform the following thought experiment on
the same baseline:

1. Add one new capability that should fit the existing architecture.
2. Replace one implementation detail with a second provider/strategy.
3. Change one cross-cutting invariant or data shape.
4. Nest one existing capability inside a composite workflow.

Return exactly these sections:

1. `Scope and evidence`
2. `Abstraction-level definitions`
3. `Per-project comparison`
4. `Extensibility stress tests`
5. `Compression versus semantic distance`
6. `Recommended level and hybrid boundary`
7. `Reusable declaration kernel`
8. `Verification and provenance requirements`
9. `Buildable follow-up`
10. `Decision table`

Required substance:

- a 0–4 score for each level on semantic fidelity, extensibility,
  change-locality, verification, reviewability, and compression for each
  project;
- explicit scoring criteria and unsupported-claim counts;
- concrete affected files/modules for every stress test;
- at least two cases where L2 is rejected as over-abstraction;
- a reusable declaration kernel with typed `Component`, `Port`, `Contract`,
  `Evidence`, `Composition`, and a finite recursion measure;
- a worked example from one of the real projects;
- a proposed next implementation slice with tests and acceptance criteria;
- a final fenced JSON object with keys `projects`, `scores`, `stress_tests`,
  `recommendation`, `kernel`, `risks`, and `next_slice`.

Keep the answer under 3,500 words. Clearly distinguish observed repository
facts, model proposals, hand-counted estimates, and unverified assumptions.
