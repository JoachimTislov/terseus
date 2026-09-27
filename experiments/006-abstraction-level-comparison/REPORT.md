# Structured abstraction-level report

## Decision

The most effective level is **not one global abstraction layer**:

- use **L0 concrete code** when the system is smaller than the declaration
  kernel and its behavior is operationally specific;
- use **L1 typed reusable components** at stable seams where multiple
  implementations or consumers must agree;
- use **bounded L2 declarations** only for naturally tabular, versioned,
  recursively composable workflows with deterministic expansion and existing
  test/mocking boundaries.

Applied to the pinned projects: `common-tools → L0`, `lite-jnc → L1`, and
`FoodSavr → L1 core with bounded L2 for third-party integration`.

## Evidence base

The agents inspected concrete paths including:

- common-tools: `ftp/ftp_client.py`, `ftp/test_ftp_client.py`, `ftp/doc.md`;
- lite-jnc: `parser/types.go`, `parser/parser.go`, `transpiler/transpiler.go`,
  `compiler/compiler.go`, `spec/spec.go`, `Status.md`;
- FoodSavr: `lib/interfaces/i_repository.dart`,
  `lib/repositories/product_repository.dart`,
  `lib/features/third_party_integration/services/import_service.dart`,
  `lib/features/third_party_integration/clients/base_client.dart`,
  `lib/injection.dart`, and related tests.

Observed facts, proposed designs, estimates, and assumptions were separated
in both outputs. Neither agent claimed to run project tests.

## Comparative scores

Dimension order: semantic fidelity, extensibility, change locality,
verification, reviewability, compression. Scores are 0–4 estimates.

| Project | L0 | L1 | L2 | Recommendation |
|---|---|---|---|---|
| common-tools | `[4,2,2,3,4,0]` | `[3,3,3,2,2,0]` | `[1,1,1,1,0,0]` | L0 |
| lite-jnc | `[4,3,2,1,3,0]` | `[3,4,3,3,3,1]` | `[2,2,2,2,1,1]` | L1 |
| FoodSavr | `[4,3,2,3,2,0]` | `[3,4,3,3,3,1]` | `[2,3,2,2,1,2]` | L1 + bounded L2 |

The second report used slightly different estimates, especially for L0
verification and compression, but reached the same ranking. That agreement
is directional evidence only; these are not independently calibrated scores.

## Extensibility stress tests

Each project was tested conceptually against:

1. adding a new capability;
2. replacing an implementation/provider;
3. changing a cross-cutting invariant or data shape;
4. nesting an existing capability in a composite workflow.

The most revealing tests were:

- **common-tools:** a second transport and remote-path invariant. L0 keeps
  FTP error behavior visible; a full L2 system would hide more than it
  compresses.
- **lite-jnc:** a standardized AST and a second backend. L1 localizes the
  unstable contract; L2 does not simplify lexer recovery or code generation.
- **FoodSavr:** a new grocery provider and a Product-shape migration. Existing
  interfaces/DI support L1; a provider-spec table may justify bounded L2, but
  migrations, widgets, localization, and Firebase behavior remain code.

## Reusable kernel

The convergent kernel is:

```text
Component {
  id, version,
  ports: typed inputs/outputs,
  contracts: pre/post predicates and compatibility,
  evidence: tests/checks/build artifacts tied to source/dependency digests,
  projection: implementation reference
}

Composition {
  ordered or branching component bindings,
  versioned references,
  bounded width/depth,
  deterministic expansion trace
}
```

Recursive expansion must consume a finite measure such as
`(remainingReferenceFuel, unexpandedNodeCount)` or a lexicographic
`(escalationDepthRemaining, attemptsRemaining)`. Cycles without a strict
decrease are rejected. Every projection records declaration hash, generator
version, component versions, dependency lock, and evidence IDs.

## Recommended implementation order

1. **FoodSavr bounded seam:** add `ProviderSpec`, provider registry, and
   golden-URI/coverage tests under
   `lib/features/third_party_integration/`. Require a third provider to avoid
   base-client edits.
2. **lite-jnc L1 seam:** define typed frontend/IR/backend interfaces,
   consolidate target selection, and add malformed-input, unsupported-target,
   and generated-output parseability tests.
3. **Only then evaluate L2:** implement a tiny offline declaration parser and
   expander for provider specs or compiler stage composition. Compare generated
   behavior against existing tests before expanding scope.

## Rejections and risks

L2 is explicitly rejected as the authoritative model for common-tools and
for lite-jnc lexer/parser/code-generation semantics. It is also rejected for
FoodSavr UI trees, migrations, authentication, and external-provider edge
cases. Risks include declaration/kernel overhead, two sources of truth,
generated behavior that is harder to debug, stale evidence, and false
confidence from hand-counted compression.

## Interpretation boundary

This experiment determines a defensible abstraction boundary from three real
repositories, not a universal language design. The result should be
validated by implementing the small FoodSavr ProviderSpec slice and the
lite-jnc backend seam, then measuring actual change locality, test failures,
review time, and generated-vs-handwritten semantic drift.
