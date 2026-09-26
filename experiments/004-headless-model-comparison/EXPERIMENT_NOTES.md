# Experiment 004: headless Codex and Vibe report generation

## Question

Can two non-interactive coding agents analyze the same Terseus repository
prompt and produce a structured, evidence-linked proposal for a next
Path C experiment, while preserving enough execution metadata for an
independent review?

This is a calibration experiment for headless workflow observability. It does
not establish that either model is generally better, that either proposal is
correct, or that the proposed follow-up experiment should be accepted.

## Fixed input

`PROMPT.md` was passed unchanged to both runners. The prompt required a
read-only repository analysis, seven named report sections, a machine-readable
JSON appendix, a 1,500-word limit, no network access, and no claim that an
experiment had been run.

## Runners and controls

| Runner | Version | Model | Invocation controls |
|---|---|---|---|
| Codex | `codex-cli 0.156.1` | `gpt-5.6-sol` | `exec --json --ephemeral`, read-only sandbox |
| Vibe | `vibe 2.25.4` | `mistral-medium-3.5` | programmatic JSON output, 16-turn cap, auto-approve, trusted workdir |

Both runs used `/home/joachim/projects/terseus`, the same prompt, and no
requested file edits. Raw event streams, final messages, stderr, exit status,
and wall-clock timing are retained under `artifacts/`.

## Results

| Metric | Codex | Vibe |
|---|---:|---:|
| Exit status | 0 | 0 |
| Wall time | 74.280 s | 34.294 s |
| Final report words | 1,021 | 1,495 |
| Required headings | present | present |
| JSON appendix | present | present |
| Input tokens | 176,175 | unavailable in exported JSON |
| Output tokens | 3,251 | unavailable in exported JSON |
| Reasoning tokens | 525 | unavailable in exported JSON |
| Event records | 16 | 28 |
| Files modified | 0 | 0 |

Both runners complied with the word limit after separating Vibe's short
progress message from its final response. Codex produced a focused benchmark
centered on citation-preservation and unsupported-claim detection; Vibe
produced a similar unsupported-claim audit. Vibe's JSON export
contains reasoning, message, and tool-effect records, but no token or cost
usage fields; those metrics are therefore intentionally reported as
unavailable.

The two proposals converge on a useful candidate follow-up: freeze recorded
AI proposals, build a human-adjudicated claim inventory, and measure
unsupported-claim detection, false positives, review time, and inter-rater
agreement. This convergence is an observation about these two outputs, not
independent evidence that the design is valid.

## Evidence and limitations

The final reports cite `FOUNDATION.md`, `PATHS.md`, `OPEN_QUESTIONS.md`,
research registry files, and prior experiment notes. The reports should be
audited before being added to the research registry. Neither run independently
verifies the proposed thresholds or demonstrates human review performance.

The experiment is not a fair model-quality benchmark: model families,
runtime implementations, telemetry availability, and effective context
handling differ. Timing is also environment-dependent. Vibe's captured report
and Codex's report mentions the in-progress Vibe artifact directory; these are
review findings, not silently corrected outputs.

## Reproduction

From the repository root:

```sh
codex exec --json --ephemeral -C "$PWD" -s read-only \
  -o artifacts/codex-last-message.txt < PROMPT.md > artifacts/codex-events.jsonl

vibe -p "$(cat PROMPT.md)" --output json --max-turns 16 \
  --auto-approve --workdir "$PWD" --trust > artifacts/vibe-output.json
```

Record CLI versions, model configuration, exit status, wall time, stderr,
final-message hashes, and usage fields when the runner exports them. Never
copy API keys or other credentials into the artifacts.
