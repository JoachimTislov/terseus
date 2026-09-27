# 4GL-and-higher language comparison

Work read-only. Use the pinned projects under `experiments/006-*` as the
concrete systems under test. Do not use network access, modify files, or
claim that a language has been validated by running code unless you actually
run an existing read-only check.

Determine which 4GL-or-higher language family can express useful parts of
these systems consistently while preserving extensibility:

- SQL / relational schema and queries;
- GraphQL / typed API schema and queries;
- OpenAPI / REST contract description;
- Protocol Buffers / IDL and generated bindings;
- Terraform/HCL or Kubernetes-style declarative resources;
- BPMN/DMN-style workflow and decision models;
- a constrained custom Terseus kernel combining typed components, contracts,
  provenance, and bounded composition.

Treat these as complementary languages, not interchangeable replacements.
For each language, state its semantic center, generated/projection boundary,
extension mechanism, versioning model, verification strength, and likely
escape hatch.

Evaluate each language against each pinned project using these tasks:

1. express one stable core boundary;
2. add a new provider or implementation;
3. change a cross-cutting invariant or data shape;
4. compose a multi-step workflow;
5. preserve a project-specific edge case without hiding it.

Return exactly these sections:

1. `Observed system boundaries`
2. `Language families and semantic centers`
3. `Capability matrix`
4. `Extensibility and versioning stress`
5. `Best-fit language stack per project`
6. `Hybrid custom kernel design`
7. `What not to unify`
8. `Verification and provenance`
9. `Buildable language experiment`
10. `Decision and falsifiers`

Required substance:

- 0–4 scores for semantic fidelity, extensibility, change-locality,
  verification, reviewability, compression, and escape-hatch quality;
- identify the best-fit language or stack for each project and why;
- distinguish schema/IDL, query, workflow, infrastructure, and implementation
  semantics;
- include a hybrid kernel with typed component, port, contract, evidence,
  composition, version, and finite recursion measure;
- define at least three falsifiers that would reject the custom kernel;
- propose a buildable experiment using one real project and concrete files,
  tests, baseline, treatment, and acceptance criteria;
- include a final fenced JSON object with keys `languages`, `projects`,
  `scores`, `hybrid_kernel`, `falsifiers`, `next_experiment`, and
  `unsupported_claims`.

Keep the report under 4,000 words. Mark all estimates and unverified claims.
