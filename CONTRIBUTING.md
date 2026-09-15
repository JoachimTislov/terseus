# Contributing

This repo is a living reference scaffold, not a shipped artifact -- most
"contributions" are additions to a document, not code. The one structural
rule (from `README.md`): anything added should cite which `PRIOR_ART.md`
entry it extends or diverges from, and which `OPEN_QUESTIONS.md` item it's
taking a position on, if any.

For work following the initial direction, also state which isolated path in
`PATHS.md` the change belongs to. Do not combine paths implicitly: a format,
metric, or AI workflow needs a new experiment before it is reused across
paths.

## Adding to PRIOR_ART.md

New entries go under the existing category that fits, or a new numbered
category if none fits. Each entry: one paragraph, neutral description (no
"this is better than X"), and a real link. No copyrighted text pasted in
-- paraphrase, don't quote.

## Adding to OPEN_QUESTIONS.md

Append, don't renumber existing items (so references to "#6" elsewhere
stay valid). A question gets removed only when it's actually been
resolved by an experiment or a cited external result -- move it to
`CHANGELOG.md` under the release that resolved it rather than deleting it
outright.

## Adding a new experiment

Create `experiments/NNN-short-name/` (zero-padded, sequential) with its
own `EXPERIMENT_NOTES.md` following the same shape as `001-domainkit`'s:
what it actually tested, what it found, and -- just as important -- what
it did *not* test and shouldn't be assumed to generalize from. An
experiment is a calibration point, not a proposal for the next one.

## Versioning and releases

Progress is tracked through releases in `CHANGELOG.md`, using a
version scheme adapted from SemVer for a theory/reference repo rather
than a software package:

- **MAJOR** -- the core proposition in `THEORY.md` is fundamentally
  reframed (not just clarified).
- **MINOR** -- a new experiment is added, an open question is resolved
  (see above) and moved to the changelog, or a new prior-art *category*
  (not just an entry) is added.
- **PATCH** -- individual prior-art entries added/corrected, wording
  fixes, an open question rephrased without being resolved.

Each release gets a tag matching its `CHANGELOG.md` heading (e.g.
`v0.1.0`). Cut a release when a batch of changes reaches a stable
resting point -- there's no cadence requirement.
