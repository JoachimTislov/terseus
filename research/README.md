# Research registry

This directory is the machine-readable registry behind the static research
site. It is intentionally versioned in Git.

## Versioning and lifecycle

Approach definitions are immutable snapshots. A semantic change creates a new
`version` record; an iteration always records the exact approach version it
tested. Project iterations also pin the target repository commit, so results
can be reproduced against the same system.

Iteration states are:

- `proposed` — scoped but not started;
- `testing` — evidence is being collected;
- `concluded` — reviewed evidence supports a local conclusion;
- `collided` — this path reached a materially shared or contradictory finding;
- `archived` — repeated evidence makes the approach unsuitable for this scope;
- `blocked` — a concrete dependency prevents evaluation.

An approach is never deleted. Archived versions remain visible with their
evidence and can be revived as a new version for a different scope.

## Required iteration record

Each record needs `project`, `approach`, `approach_version`, `scope`, `commit`,
`state`, and `result`. Add benchmark scores only after evidence is collected.
Use typed `relations` (`converges_with`, `contradicts`, `shares_evidence`, or
`supersedes`) to make path interactions explicit. Research questions and
their approach relationships are maintained in `OPEN_QUESTIONS.md`.
