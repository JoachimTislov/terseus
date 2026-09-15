# Experiment 002: bootstrapping AI VCS

## Selected system

This study uses [`ai-native-vcs`](https://github.com/JoachimTislov/ai-native-vcs)
as a submodule at `../002-aivcs-bootstrap`. It was selected because its
existing concepts—specifications, sessions, contracts, review, bisection, and
drift—already expose the boundary between domain intent and implementation in
a large-system workflow.

The submodule is pinned independently. This study does not edit or vendor its
source; changes to that project must happen in its own repository.

## Bootstrap objective

Use the same narrow AI-VCS slice to compare three isolated approaches:

- **Path A:** represent a change domain as an open record of concepts,
  constraints, examples, decisions, and unresolved alternatives.
- **Path B:** trace two projections of that record (a specification and a
  review/test artifact) and measure impact after one domain change.
- **Path C:** ask AI to propose a structured change with affected claims,
  projections, uncertainty, and evidence, then require a human decision.

The paths are sequentially comparable but not merged. A result in one path
does not validate the assumptions of another.

## Proposed system slice

The slice is the existing `spec -> session -> review -> test oracle` flow.
The initial domain question is:

> How should a session record and expose the intent, scope, evidence, and
> unresolved ambiguity of a change without making the provider or generated
> code the source of truth?

## Evidence to collect

For each path, preserve inputs, artifacts, links, decisions, and a short
evaluation:

- reconstruction accuracy and disagreement visibility;
- claim-to-artifact coverage and stale-link detection;
- proposal usefulness, unsupported claims, review time, and rejected-change
  clarity;
- effort and impact after one meaningful requirement change.

The study does not claim that AI-VCS is correct, that one representation is
universal, or that generated code is safe without independent tests.

## External references

- [W3C PROV overview](https://www.w3.org/TR/prov-overview/) — provenance
  concepts for entities, activities, and agents.
- [OMG DMN](https://www.omg.org/spec/DMN/) — portable decision models with
  notation and executable expressions.
- [Language Workbench](https://martinfowler.com/articles/languageWorkbench.html)
  — domain-specific language and projection practice.
- [Protocol Buffers](https://protobuf.dev/overview/) — schema evolution and
  multi-language projections.
- [DSPy](https://arxiv.org/abs/2310.03714) — declarative LM modules and
  pipelines.
- [Sketch](https://people.csail.mit.edu/asolar/SynthesisCourse/Sketch.pdf)
  and [Rosette](https://plt.cs.northwestern.edu/pkg-build/doc/rosette-guide/)
  — bounded synthesis and verification precedents.

These references influence the questions and evidence vocabulary only. They
do not turn any one path into the architecture under test.

## Baseline status

The pinned submodule was fetched successfully. Its test command currently
requires the package to be installed (`ModuleNotFoundError: aivcs` when
running `pytest -q` directly from the checkout); this is recorded as a
baseline environment issue, not changed in the submodule.
