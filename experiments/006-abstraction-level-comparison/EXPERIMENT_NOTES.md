# Experiment 006: abstraction levels across three real projects

## Question

What abstraction level most effectively expresses a system while preserving
extensibility: concrete implementation (L0), typed reusable components (L1),
or a recursively expanded declarative system (L2)?

The study deliberately allows different answers for different systems. It
tests whether abstraction should follow recurring structure and stable
contracts rather than be imposed uniformly.

## Pinned inputs

| Project | Role | Pinned revision |
|---|---|---|
| `006-common-tools` | small FTP utility/library | `58246521116c7a2a0fd6213613f0e91d4ed43e5f` |
| `006-lite-jnc` | Go Java parser/transpiler/compiler | `e6066394f27fa5bbc53988445997af34e8744345` |
| `006-foodsavr` | Flutter food inventory application | `3e3fd20df20560e17844272bf3bd8c63d77f671d` |

`PROMPT.md` was identical for Codex and Vibe. It required evidence from
source/tests/docs, four extensibility stress tests per project, 0–4 scores
for six dimensions, a reusable declaration kernel, rejected L2 cases, and a
buildable follow-up.

## Runners

| Runner | Version | Model | Wall time | Final words |
|---|---|---|---:|---:|
| Codex | `codex-cli 0.156.1` | `gpt-5.6-sol` | 117.216 s | 2,026 |
| Vibe | `vibe 2.25.4` | `mistral-medium-3.5` | 272.593 s | 2,601 |

Both exited successfully, stayed below the 3,500-word limit, included all
ten required sections, and produced valid final JSON appendices. Codex
reported 125,816 input tokens, 100,224 cached input tokens, 5,800 output
tokens, and 470 reasoning tokens. Vibe's exported JSON did not expose token
or cost counters.

## Result

The independent recommendations agree:

| Project | Effective level | Boundary |
|---|---|---|
| common-tools | **L0** | Add a narrow L1 transport seam only after a second provider exists |
| lite-jnc | **L1** | Typed AST/frontend/backend contracts; optional shallow pipeline composition |
| FoodSavr | **L1 core + bounded L2 seam** | Use declaration tables for third-party integration; retain Dart for UI, migrations, and provider edge cases |

The most effective general rule is therefore **typed components at stable
change boundaries, with declarative recursion only where the subsystem is
small, tabular, versionable, and mechanically expandable**. L2 is not the
default authoritative representation.

Both reports reject L2 for common-tools because the meta-model would exceed
the utility's semantic size, and for lite-jnc's lexer/parser/code-generation
semantics because the behavior is algorithmic and difficult to review after
expansion. They identify FoodSavr's provider/integration family as the only
credible bounded L2 candidate because it already has registry-shaped data,
interfaces, dependency injection, and mockable client seams.

## Score interpretation

Scores are reasoned estimates, not measured outcomes:

1. semantic fidelity;
2. extensibility;
3. change locality;
4. verification;
5. reviewability;
6. compression.

`0` means unusable at that level; `4` means native, localized, and
mechanically checkable. Compression is not allowed to dominate: semantic
distance and verification remain separate dimensions.

The agents disagree slightly on absolute values but agree on the ranking.
Codex scores L1 highest for lite-jnc and FoodSavr and L0 highest for
common-tools. Vibe reaches the same recommendation and adds a stricter
hybrid-boundary rule: use L2 only for naturally tabular data, a small number
of declaration kinds, and projections covered by existing mock seams.

## Buildable follow-up

The cheapest falsifiable next slice is FoodSavr's
`features/third_party_integration`: introduce a typed `ProviderSpec` and
registry for endpoint/environment metadata, preserve `Client.fetch`, and add
enum-coverage, environment-key, and golden-URI tests. Acceptance requires
adding a third provider without editing the base client and preserving HTTP
behavior. If the registry is heavier than the two existing providers justify,
that is evidence against the bounded L2 seam.

The higher-value structural slice for lite-jnc is a typed backend boundary:
export an IR/frontend result, register targets through one validated backend
registry, and test unsupported targets, malformed input, and generated-output
parseability. No recursive DSL should be introduced until this L1 seam is
working.

## Limitations

No project tests or builds were run in this round. Stress-test file counts,
scores, and compression estimates are model-produced estimates. The
comparison does not measure developer time, semantic equivalence, or actual
change success. Submodule snapshots are reproducible, but external provider
behavior and current CI health are outside this study.
