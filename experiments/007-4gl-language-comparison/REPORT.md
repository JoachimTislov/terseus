# Structured 4GL progress report

## Conclusion

The experiments do not support a universal 4GL or general-purpose custom
domain language for expressing an entire system. They support a **hybrid
language stack** in which each language owns the semantics it already
handles well, while a small typed-component kernel coordinates stable
cross-language boundaries.

The proposed custom kernel is not an answer yet. It is a falsifiable
implementation hypothesis.

## Recommended stack

| System concern | Recommended expression | Boundary |
|---|---|---|
| relational data, constraints, queries | SQL | database truth and migrations |
| public API shape | OpenAPI and/or GraphQL | request/response contract |
| cross-language messages | Protocol Buffers | versioned IDL and generated bindings |
| infrastructure state | Terraform/HCL or Kubernetes CRDs | provider/controller reconciliation |
| business decisions | DMN-style tables | explicit decision logic |
| workflows | BPMN-style model or typed code | bounded orchestration only |
| project-specific reusable parts | L1 typed components | contracts, ports, evidence |
| experimental system kernel | constrained Terseus declaration | composition and provenance only |

This is a division of semantic responsibility, not a claim that all projects
need every language.

## Project fit

- **common-tools:** retain concrete Python. A custom declaration would exceed
  the utility's semantic size and obscure FTP error/path behavior. At most add
  a narrow typed transport port if a second backend is real.
- **lite-jnc:** use typed L1 boundaries for lexer/parser/IR/backend contracts.
  Keep parser recovery, AST semantics, and code generation in Go. A shallow
  stage pipeline may be declared later, after a working IR and backend.
- **FoodSavr:** use existing Dart interfaces and DI, SQL or Protocol Buffers
  where the backend/message boundary needs them, and optionally a small
  provider-spec table. Keep UI, migrations, authentication, and external
  provider edge cases in Dart.

## Custom kernel boundary

The minimum useful kernel contains:

```text
Component(id, version, ports, contract, evidence, projection)
Port(name, direction, type, cardinality)
Contract(preconditions, postconditions, compatibility)
Evidence(kind, artifact_digest, source_revision, covers)
Composition(versioned_bindings, explicit ordering, budget)
```

Recursive composition must consume a finite measure such as remaining
reference fuel, depth, or node budget. Cycles without a strict decrease are
rejected. Expansion must be deterministic and emit a trace linking each
generated projection to declaration, component, generator, and dependency
digests.

The kernel must expose escape hatches to handwritten code. It must not encode
SQL query semantics, GraphQL resolver behavior, OpenAPI transport policy,
protobuf wire evolution, infrastructure provider behavior, or a project's
domain-specific algorithms.

## Versioning and verification

Required safeguards are additive evolution rules, immutable component
references, explicit major/minor compatibility, schema/projection golden
tests, stale evidence invalidation, deterministic expansion, and independent
checks for types, termination, tenant/isolation constraints, migration
compatibility, and generated-output behavior.

Protocol Buffers is the strongest prior-art model for durable additive
cross-language evolution. Terraform/HCL and Kubernetes demonstrate that a
declaration can remain small when providers/controllers own operational
semantics. These precedents argue for a binding layer, not for moving all
behavior into a new language.

## Falsifiers

Reject or narrow the custom kernel if the first ProviderSpec/component slice:

- costs more declaration/generator/provenance code than the baseline;
- does not make provider or invariant changes more local;
- produces semantic drift under golden, mutation, or migration tests;
- takes longer to review than direct code;
- cannot precisely invalidate affected evidence after version changes.

## Next implementation experiment

Implement only the FoodSavr provider boundary on the pinned snapshot:

1. define `GroceryProvider` or `ProviderSpec`;
2. replace the provider switch/direct client construction in
   `ImportService`;
3. retain existing provider clients and behavior;
4. add a fake provider, provider-coverage tests, failure-isolation tests, and
   golden request/output tests;
5. compare L0 and L1 by changed files/lines, test failures, review time,
   assumption count, and declaration-to-code ratio.

Do not introduce recursive L2 composition in this slice. If L1 cannot improve
the seam without excess machinery, that is evidence against a custom kernel.

## Readiness

The research is ready for a small implementation experiment, not for adopting
a language standard. The evidence supports the stack recommendation and
identifies concrete falsifiers, but no generated projection has yet been
compiled or compared behaviorally against a handwritten baseline.
