# Experiment 007: 4GL-and-higher language comparison

## Question

Which 4GL-or-higher language families can express useful system boundaries
consistently while preserving extensibility, and is a hybrid custom Terseus
kernel justified?

The comparison covered SQL, GraphQL, OpenAPI, Protocol Buffers, Terraform/HCL
or Kubernetes-style resources, BPMN/DMN-style models, and a constrained
custom kernel. It used the three pinned public projects from Experiment 006:
common-tools, lite-jnc, and FoodSavr.

## Runs

Both agents received the same read-only prompt and were required to evaluate
stable boundaries, provider replacement, cross-cutting changes, workflow
composition, edge-case preservation, versioning, escape hatches, and
verification.

| Runner | Model | Wall time | Words | Input tokens | Output tokens |
|---|---|---:|---:|---:|---:|
| Codex | `gpt-5.6-sol` | 126.534 s | 2,384 | 159,237 | 6,294 |
| Vibe | `mistral-medium-3.5` | 68.999 s | 3,348 | unavailable | unavailable |
| Astra synthesis | `gpt-6-astra`, `xhigh` | 366.673 s | 2,392 | 1,061,503 | 10,613 |

All three reports exited successfully, stayed below their word limits, and
contained valid JSON appendices. Astra's synthesis was run after the two
independent language comparisons and read their artifacts as well as the
repository history.

## Decision

No single 4GL should express the whole system. The effective stack is:

| Responsibility | Best-fit family |
|---|---|
| relational data and invariants | SQL |
| public typed service contracts | OpenAPI and/or GraphQL |
| cross-language messages and generated bindings | Protocol Buffers |
| infrastructure desired state | Terraform/HCL or Kubernetes CRDs |
| explicit business decisions | DMN-style tables |
| bounded multi-step workflows | BPMN-style models or typed code |
| system-specific reusable seams | L1 typed components |
| experimental cross-cutting kernel | constrained custom Terseus model |

The custom kernel is justified only as a bounded hypothesis. It should
coordinate typed components, ports, contracts, evidence, versioned
composition, and finite recursion. It should not replace SQL semantics,
provider APIs, parser/AST semantics, UI behavior, migrations, or arbitrary
business logic.

## Cross-agent agreement

The Codex, Vibe, and Astra outputs converge on:

- responsibility-specific languages rather than a universal 4GL;
- Protocol Buffers for durable cross-language schema evolution;
- OpenAPI/GraphQL for API boundaries, not internal behavior;
- SQL for relational data truth;
- HCL/Kubernetes-style declarations for infrastructure reconciliation;
- typed components as the safest custom abstraction boundary;
- explicit handwritten escape hatches;
- versioned contracts, generated projections, stale-evidence detection, and
  independent verification;
- rejection of a general recursive DSL until a small implementation proves
  change locality and semantic fidelity.

## Falsifiers

The custom kernel should be rejected or narrowed if:

1. a ProviderSpec or typed-component slice requires more declaration,
   generator, and provenance code than the handwritten baseline;
2. adding a provider or invariant still requires edits to generated output or
   scattered orchestration rather than one bounded component;
3. generated projections diverge semantically from the handwritten baseline
   under golden, mutation, or migration tests;
4. reviewers cannot explain the expanded behavior faster than the direct code;
5. version/evidence invalidation cannot identify the affected projections
   without broad revalidation.

## Next experiment

Implement one small FoodSavr provider-boundary treatment against the pinned
snapshot: a typed `GroceryProvider` or `ProviderSpec` registry, replacing the
current provider switch/direct construction while preserving the existing
client behavior. Compare it with the L0 baseline using:

- changed files and lines;
- new-provider change locality;
- invariant and failure-isolation tests;
- golden request/output behavior;
- review time and unsupported assumptions;
- generated/declaration size versus handwritten size.

Do not introduce recursive composition in this first slice. It is a deliberate
test of whether L1 is sufficient before L2 is attempted.

## Limitations

No existing project tests or builds were run in this experiment. Scores and
language fit judgments are model analyses, not implementation measurements.
The public projects were pinned snapshots, and external provider/runtime
behavior was inferred from local source and tests. This experiment supports a
language-stack hypothesis, not proof that the proposed stack preserves
whole-system meaning.
