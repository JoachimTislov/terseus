# Independent subagent report

## Executive summary

An independent subagent repeated the abstraction-level review against the
three pinned public repositories without network access, file modifications,
or test execution. Its recommendation is **L1 typed reusable components as the
common kernel**, scoped differently per project:

- `common-tools`: a narrow `RemoteFileSystem` port; retain the concrete CLI
  and reject L2.
- `lite-jnc`: typed compiler phases and an intermediate representation; defer
  L2 until language semantics, error behavior, and a real backend stabilize.
- `foodsavr`: typed domain ports, normalized inventory models, and injected
  grocery providers; reject recursive declarations for now.

This independently agrees with the primary agents that a universal L2
representation would obscure behavior. It is more conservative than the
primary reports by rejecting even the proposed FoodSavr L2 provider-spec seam
until the underlying provider and data boundaries are stable.

## Evidence reviewed

### common-tools

- `ftp/ftp_client.py`: `main()` constructs `ftpretty`, reads environment
  configuration, calls recursive `delete_remote_directory()`, and uploads
  through `upload_dir()`.
- `ftp/test_ftp_client.py`: flag parsing, recursive upload, deletion, and
  mocked connection lifecycle tests.
- `ftp/doc.md`: trailing-slash and deployment environment requirements.

The subagent identified the concrete weakness as direct `ftpretty` coupling
and broad exception handling in recursive deletion, not lack of a DSL.

### lite-jnc

- `parser/lexer.go` and `parser/parser.go`: mutable parser state and partial
  state-machine semantics.
- `parser/types.go`: typed but mostly unexported AST structures.
- `spec/spec.go`: small `Runner` seam.
- `compiler/compiler.go`, `compiler/x86-64-ELF.go`,
  `transpiler/transpiler.go`, `transpiler/go.go`: target and emitter seams,
  but incomplete implementations.
- `README.md`, `Status.md`, and `parser/lexer_internal_test.go`: documented
  TODOs, partial status, and no active lexer test coverage.

The subagent identified a typed IR/frontend/backend boundary as the missing
abstraction, while rejecting declarative lexer or parser generation.

### foodsavr

- `lib/interfaces/`: `IRepository`, `IService`, `IProductRepository`, and
  `IAuthService`.
- `lib/injection.dart`, `lib/register_module.dart`, and
  `lib/service_locator.dart`: existing dependency-injection seam.
- `lib/models/product_model.dart`: overloaded product/inventory structure.
- `lib/services/product_service.dart`: barcode, repository, shelf-life, and
  external-data coupling.
- `lib/features/third_party_integration/services/import_service.dart`:
  provider enum and direct client construction.
- `lib/utils/product_add_helper.dart`: nested scan → lookup → persistence →
  collection → UI workflow.
- `doc/implementation/product-architecture-refactor.md`: proposed but
  unimplemented split into registry product, inventory item, and shopping-list
  item.

The subagent identifies L1 data and provider boundaries as the priority before
any recursive declaration layer.

## Independent scores

Scores are 0–4 estimates under the same six dimensions: semantic fidelity,
extensibility, change locality, verification, reviewability, and compression.
Totals are shown only to make the ranking explicit.

| Project | L0 | L1 | L2 | Recommended |
|---|---:|---:|---:|---|
| common-tools | 18 | **19** | 12 | L1 port around concrete CLI |
| lite-jnc | 16 | **19** | 11 | L1 typed phases and IR |
| foodsavr | 16 | **20** | 12 | L1 domain/provider ports |

The scores are not runtime measurements. The subagent did not run project
tests or builds.

## Stress-test findings

- Adding an SFTP/alternate transport exposes direct `ftpretty` coupling in
  `ftp/ftp_client.py`; a small port is sufficient, while L2 is not.
- Adding a lite-jnc backend is currently blocked more by incomplete emitters
  and unstable AST/IR contracts than by missing declaration syntax.
- Adding FoodSavr providers requires replacing enum switches and direct client
  construction in `ImportService`; adding inventory semantics crosses
  `Product`, repositories, services, and views.
- Nested workflows already exist concretely in `ProductAddHelper`; the useful
  abstraction is an explicit typed service workflow, not a recursive DSL.

## Recommended kernel

The subagent's reusable kernel is intentionally smaller than the L2 proposals:

1. typed capability ports;
2. immutable, non-overloaded input/output data shapes;
3. provider registry/factory;
4. explicit sequential workflow composition;
5. boundary fakes and invariant tests.

Recursive declaration should stop at stable seams. It should not replace
parser state machines, UI trees, migrations, or external-provider behavior.

## Follow-up slices

- `common-tools`: add `RemoteFileSystem`, pure traversal/path joining, and fake
  provider tests.
- `lite-jnc`: export a small IR, adapt the parser to it, add an `Emitter`
  interface, and test a fake emitter.
- `foodsavr`: add `GroceryProvider`, inject a provider list into
  `ImportService`, remove the provider switch, and test failure isolation.

## Limitations

The report is based on pinned source snapshots and did not execute tests,
analyzers, builds, or dependencies. Some repository documentation describes
intended rather than implemented architecture. Provider APIs, Firebase, and
FTP behavior were inferred from call sites and mocks. The report therefore
supports an abstraction-boundary decision, not a claim of implementation
correctness.
