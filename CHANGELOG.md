# Changelog

All notable changes to this scaffold are tracked here, grouped by release.
Format follows [Keep a Changelog](https://keepachangelog.com/), with a
versioning scheme adapted for a reference/theory repo rather than a
software package -- see `CONTRIBUTING.md` for what bumps each number.

## [Unreleased]

Future experiments and their evidence.

## [0.1.2] - 2026-09-15

### Added
- `experiments/002-aivcs-bootstrap` as a pinned submodule of the selected
  `ai-native-vcs` project.
- `experiments/002-aivcs-bootstrap-study/` with isolated Path A, B, and C
  protocols, evidence boundaries, and external references.

## [0.1.3] - 2026-09-15

### Added
- `experiments/003-refviz-bootstrap` as a pinned submodule of the selected
  RefViz project.
- `experiments/003-refviz-bootstrap-study/` with isolated paths and a common
  0–4 benchmark for semantic fidelity, flexibility, change resilience,
  correctness, maintainability, traceability, reviewability, and
  reproducibility.

## [0.1.1] - 2026-09-15

### Added
- `FOUNDATION.md` -- open representation position and experiment contract.
- `PATHS.md` -- three isolated initial research paths with explicit
  non-goals and external references.
- README positioning for domain knowledge distributed across large systems.

## [0.1.0] - 2026-09-15

### Added
- `THEORY.md` -- core proposition, the two design axes (where the model
  operates; what triggers a new abstraction), the historical tension
  with controlled-natural-language precedent, the empirical
  cross-target-verification finding, and the open measurement question.
- `OPEN_QUESTIONS.md` -- eight unresolved design questions.
- `PRIOR_ART.md` -- ten-category survey: keyword-driven binding,
  schema-first codegen, declarative infra with pluggable providers,
  cross-language/cross-platform compilation, language workbenches,
  controlled natural language, LLM-embedded language execution,
  program synthesis with typed holes, spec-verified LLM synthesis
  research, and low-code platforms with code escape hatches.
- `experiments/001-domainkit/` -- an earlier, narrower prototype folded
  in as a labeled data point (schema -> contract-verified synthesis ->
  multi-target wiring, with bindings as an optional override), with its
  own `EXPERIMENT_NOTES.md` stating what it did and did not test.
- `LICENSE` (MIT), `.gitignore`.
