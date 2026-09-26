# Structured comparison report

## Executive summary

Both headless runs completed successfully and returned the requested
seven-section proposal without modifying repository files. They independently
converged on an offline human audit of unsupported claims in recorded AI
proposals. Both final responses were within the requested word limit; Codex
exposed token telemetry, while Vibe's exported JSON did not expose token or
cost telemetry.

This is an execution and observability result, not a model leaderboard.

## Run metadata

| Field | Codex | Vibe |
|---|---|---|
| CLI | `codex-cli 0.156.1` | `vibe 2.25.4` |
| Model | `gpt-5.6-sol` | `mistral-medium-3.5` |
| Prompt | `PROMPT.md` (same bytes) | `PROMPT.md` (same bytes) |
| Sandbox/approval | read-only sandbox | auto-approved tools |
| Exit status | 0 | 0 |
| Wall time | 74.280 s | 34.294 s |
| Final report size | 8,703 bytes / 1,021 words | 11,016 bytes / 1,495 words |
| Final report SHA-256 | `55f776d76b847f4046e4866517809f62d8cbc48872f09c12534dfb91fc74eb0b` | `8dfb08b545a8e26470f6727c5423949e0a1fcca7ed568012980f96e2acc0016b` |

## Telemetry

Codex reported 176,175 input tokens, 141,184 cached input tokens, 3,251
output tokens, and 525 reasoning output tokens in its `turn.completed` event.
Its JSONL stream contained 16 records: one thread start, one turn start, one
turn completion, five item starts, and eight item completions.

Vibe's JSON export contained 28 records: three messages, six reasoning
records, and 19 effects. It did not contain token, cost, or latency fields
inside the export; wall time was measured externally with epoch-nanosecond
timestamps. The Vibe session metadata identifies the active model as
`mistral-medium-3.5` from the Mistral provider.

## Content comparison

| Criterion | Codex | Vibe |
|---|---|---|
| Required structure | all headings present | all headings present |
| Proposed focus | citation-preservation audit | claim-inventory and provenance-rubric audit |
| No-API-key design | yes | yes |
| Human acceptance preserved | yes | yes |
| Explicit limitations | yes | yes |
| Word-limit compliance | yes | yes |
| Unsupported claims | no run claimed; design caveats stated | no run claimed; design caveats stated |

The common proposal is a plausible candidate for a later experiment:
construct an adjudicated claim inventory for frozen AI outputs, compare
review conditions with and without provenance structure, and report recall,
false-positive rate, citation validity, review time, and inter-rater
agreement. Human reviewers must accept the corpus and ground truth before
this becomes evidence.

## Artifacts

- `PROMPT.md` — frozen input.
- `artifacts/codex-events.jsonl` — Codex event telemetry.
- `artifacts/codex-last-message.txt` — Codex final response.
- `artifacts/vibe-output.json` — Vibe JSON event export.
- `artifacts/vibe-last-message.txt` — extracted Vibe response text.
- `artifacts/*-run-metadata.json`, `*-time.json`, `*-exit-status`, and
  `*-stderr.log` — execution metadata.

## Interpretation boundary

The runs show that the shared prompt is reproducible enough to yield
structured outputs and that telemetry differs materially between tools. They
do not show which model is more capable, whether either proposal is correct,
or whether the follow-up benchmark improves human review. The unavailable Vibe usage counters are a concrete workflow limitation that
should be addressed in future headless runs.
