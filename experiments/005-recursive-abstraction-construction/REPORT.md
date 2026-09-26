# Structured construction report

## Executive summary

Codex and Vibe both produced substantial, self-contained designs for
recursively declaring a multi-tenant notification system. They did not merely
recommend “use a DSL”: they supplied typed recursive schemas, component
libraries, a worked declaration, bounded expansion rules, independent
verification checks, compression estimates, change impact, rejected unsafe
shortcuts, and a concrete implementation slice.

The strongest reusable design principles appearing independently in both
outputs are immutable component references, explicit typed bindings, finite
well-founded recursion, platform-owned idempotency, durable audit obligations,
and deterministic expansion. These are candidate requirements for a future
implementation, not accepted repository conventions.

## Run metrics

| Field | Codex | Vibe |
|---|---|---|
| CLI/model | `codex-cli 0.156.1` / `gpt-5.6-sol` | `vibe 2.25.4` / `mistral-medium-3.5` |
| Exit status | 0 | 0 |
| Wall time | 85.472 s | 45.005 s |
| Final response | 19,489 bytes / 2,287 words | 17,301 bytes / 1,495 words |
| Required sections | 9/9 | 9/9 |
| Final JSON appendix | valid | valid |
| Token telemetry | 14,493 input; 4,533 output; 112 reasoning | unavailable |
| Final SHA-256 | `989b59a5183a8f88f2c2d414c57eed1c54f611c06af6b22db4866a399a2232ec` | `6fbb432460fc2c81e0fc7382d3c32c4455d842e18252dfab0630946dd026aed6` |

## What the models constructed

Codex proposed a recursive `Component` with child components, wires,
constraints, and evidence, plus `tenant`, `ingress`, `policy`, `delivery`,
`escalation`, and `audit` library entries. Its worked declaration expands
bounded escalation into a deterministic graph and defines six checks,
including an explicit provider-path idempotency check and stale evidence
invalidation.

Vibe proposed atomic/composite components with typed ports, immutable
references, evidence subject digests, and a lexicographic termination measure.
Its worked declaration adds a durable outbox intent/audit boundary,
tenant-taint checks, and a vertical first implementation slice that defers
real providers while validating their declarations.

Both outputs explicitly reject unbounded retry/escalation, untyped maps,
implicit type-inference wiring, and provider-owned idempotency. Those
rejections are particularly valuable because they turn abstraction design
into constrained engineering rather than surface-level syntax compression.

## Compression result

The agents produced meaningful but non-comparable hand-counted ratios:

- Codex: approximately 224 expanded lines / 39 compact lines = 5.7:1;
  approximately 2,980 / 640 whitespace-token estimate = 4.7:1.
- Vibe: 21 repeated behavioral lines / 6 compact lines = 3.5:1;
  76 / 17 whitespace-token estimate = 4.47:1.

The values should not be treated as semantic compression scores. The next
implementation must generate both forms from one canonical declaration,
count with one tokenizer, and compare behavior with executable invariants.

## Build recommendation

The most useful next implementation checkpoint is a small offline prototype:

1. Define `Component`, `Port`, `Binding`, `Constraint`, and `Evidence`.
2. Store immutable component versions in a registry.
3. Expand nested composites deterministically with a finite recursion measure.
4. Run pure checkers for types, tenant isolation, idempotency, retry bounds,
   audit completeness, and termination.
5. Execute one `InvoiceOverdue` or equivalent event through a fake provider and
   durable outbox.
6. Add mutation tests for each rejected abstraction and re-run checks after a
   provider/escalation change.

Acceptance should require byte-stable expansion, one logical send under
concurrent duplicate input, bounded attempts, no tenant-tainted crossovers,
complete correlated audit records, and rejection of unguarded cycles.

## Interpretation boundary

This run demonstrates that headless agents can produce a concrete abstraction
candidate with reusable recursive parts and a plausible build sequence. It
does not demonstrate implementation correctness, semantic equivalence of the
compact form, production suitability, or generalization to other domains.
