# Experiment 005: recursive abstraction construction

## Question

Can headless coding agents move beyond describing an abstraction strategy and
construct a concrete, recursively composable declaration for a multi-part
system, while making compression, contracts, verification, and change impact
explicit enough for an engineer to build upon?

This is a construction calibration point. It is not evidence that the
declaration is executable, that the proposed compression preserves semantics,
or that either model is generally superior.

## Fixed task

`PROMPT.md` gave both runners the same notification-platform domain and
required a typed recursive schema, reusable components, a worked declaration,
deterministic expansion, independent checks, baseline/compact compression
accounting, a change test, rejected abstractions, and a build-ready next
slice. The agents were instructed not to modify files, use network access, or
claim implementation or verification.

## Runners

| Runner | Version | Model | Controls |
|---|---|---|---|
| Codex | `codex-cli 0.156.1` | `gpt-5.6-sol` | ephemeral JSONL execution, read-only sandbox |
| Vibe | `vibe 2.25.4` | `mistral-medium-3.5` | JSON output, 24-turn cap, auto-approve, trusted workdir |

## Results

| Metric | Codex | Vibe |
|---|---:|---:|
| Exit status | 0 | 0 |
| Wall time | 85.472 s | 45.005 s |
| Final response words | 2,287 | 1,495 |
| Required sections | 9/9 | 9/9 |
| Valid final JSON appendix | yes | yes |
| Input tokens | 14,493 | unavailable |
| Cached input tokens | 11,136 | unavailable |
| Output tokens | 4,533 | unavailable |
| Reasoning output tokens | 112 | unavailable |
| Event records | 16 | 3 exported messages/reasoning records |
| Files modified | 0 | 0 |

Both outputs are significant build-on artifacts. Each defines recursive
components, typed ports, constraints, evidence, bounded recursion, a
notification-platform declaration, verification checks, compression
accounting, a provider/escalation change, rejected unsafe abstractions, and a
concrete implementation slice.

Codex's design emphasizes explicit `Evidence`, digest invalidation, provider
path guards, and a 17-node bounded expansion. Vibe's design emphasizes
well-founded measures, tenant-tainted execution, an outbox boundary, and a
vertical first slice. Their independent overlap is strongest around:

- immutable versioned component references;
- explicit ports and bindings rather than type-only inference;
- recursive composition guarded by a finite decreasing measure;
- platform-owned idempotency;
- in-band or durable audit obligations;
- deterministic expansion as a projection, not the source declaration;
- stale evidence after dependency or parameter changes.

## Compression and construction findings

Codex reports a 17-node expanded graph versus a 39-line compact declaration,
approximately 5.7:1 by lines and 4.7:1 by its hand-counted token estimate.
Vibe reports a repeated behavioral baseline of 21 lines/76 whitespace tokens
versus 6 lines/17 tokens, 3.50:1 by lines and 4.47:1 by tokens. These counts
are illustrative and hand-counted, not independently generated or semantic
equivalence proofs. Both agents correctly warn that contract and evidence
metadata reduce apparent compression and that compression is not sufficient
if it increases cognitive distance.

The most buildable common next slice is a parser and registry for immutable
component versions, deterministic recursive expansion, and pure checkers for
types, tenant isolation, idempotency, retry bounds, audit completeness, and
termination. A vertical fake-provider path should then test the declaration
against actual execution boundaries.

## Limitations

Neither output was compiled or executed. The syntax is explicitly
illustrative, and the claimed line/token ratios were not independently
recomputed from a canonical baseline. Vibe emitted additional illustrative
JSON blocks before its final appendix; the final appendix is valid, but a
strict consumer should extract the last block or require a single JSON
document. The two model families had different telemetry availability and
runtime behavior, so this is not a capability ranking.

## Reproduction

```sh
codex exec --json --ephemeral -C "$PWD" -s read-only \
  -o artifacts/codex-last-message.txt < PROMPT.md > artifacts/codex-events.jsonl

vibe -p "$(cat PROMPT.md)" --output json --max-turns 24 \
  --auto-approve --workdir "$PWD" --trust > artifacts/vibe-output.json
```

Raw streams, extracted final responses, timing, versions, exit statuses,
stderr, hashes, and metrics are retained in `artifacts/`. No credentials are
stored.
