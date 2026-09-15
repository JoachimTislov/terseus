# Terseus

An open-source experiment repository for discovering how AI can help people
build and evolve abstractions in large systems.

The project is not about enclosing possibilities in a new programming
language. Domain knowledge is often distributed across source code,
documentation, tests, operations, and people. Terseus investigates whether an
open representation layer can keep that knowledge connected while producing
inspectable, replaceable projections for different implementations.

A reference scaffold for an open research direction, not a proposed final
answer:

> Can an AI system be used to progressively identify, verify, and reuse
> abstractions across languages and frameworks -- so that the total
> words/tokens/syntax needed to express a system shrinks over time --
> without collapsing into either an unverifiable black box, or a
> lowest-common-denominator DSL that can't say anything interesting?

This repo does not pick an architecture, a target language, a metric for
"concise," or a synthesis strategy. It exists to hold the research position,
the tensions around it, and reproducible experiments:

1. **`FOUNDATION.md`** -- the open representation position and the artifact
   contract every experiment should follow.
2. **`PATHS.md`** -- three isolated initial paths for domain records,
   projections/traceability, and AI-assisted change proposals.
3. **`PRIOR_ART.md`** -- a wide, categorized survey of existing systems
   that already occupy some corner of this problem, so any future design
   decision starts from what's been tried, not from a blank page.
4. **`THEORY.md`** and **`OPEN_QUESTIONS.md`** -- the actual tensions and
   unresolved design axes this idea sits on, stated as neutrally as
   possible, several of which pull in opposite directions.

`experiments/001-domainkit/` holds an earlier, unrelated exploratory
prototype (schema -> contract-verified synthesis -> multi-target wiring)
that came out of a different conversation thread. It's included as one
labeled data point -- what it tried, what it found, what it didn't
resolve -- not as the template the rest of this project should follow.
Nothing here commits to repeating its choices (bindings + fallback
synthesis + hash-cached rebuilds was one specific answer to a much
narrower question than the one this repo is scoped around).

## Layout

```
terseus/
  README.md              <- you are here
  THEORY.md               core proposition + the design axes it forces
  OPEN_QUESTIONS.md        unresolved tensions, kept as a live list
  PRIOR_ART.md             categorized survey with links
  experiments/
    001-domainkit/         one earlier prototype, labeled, not prescriptive
```

## How to use this

If a next step gets decided later, it should cite which prior-art entry
it's extending, borrowing from, or deliberately diverging from, and which
open question it's taking a position on. That's the only structural rule
this scaffold imposes.

## Status

Current release: **v0.1.0** — see `CHANGELOG.md` for what's in it.
Progress is tracked through tagged releases rather than an open-ended
commit history; `CONTRIBUTING.md` defines what bumps each version number
and how to add a prior-art entry, an open question, or a new experiment.

## License

MIT — see `LICENSE`.
