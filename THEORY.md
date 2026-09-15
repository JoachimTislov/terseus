# Theory

## The proposition, stated as neutrally as possible

Software expression has repeatedly moved toward higher abstraction --
assembly to 3GL, 3GL to 4GL/DSL -- each step trading generality for
concision in some bounded domain. The proposition this repo is scoped
around: an AI system might let that process happen *continuously and
per-project*, rather than only through hand-designed, centrally-maintained
languages (SQL, Terraform's HCL, etc.). Instead of a language designer
deciding in advance what a domain's vocabulary should be, the AI observes
or is given a domain's recurring patterns and helps bootstrap a smaller,
verified vocabulary for expressing them -- gradually replacing verbose,
repeated 3GL syntax with concise, reusable keywords, the way Theseus's
ship is replaced plank by plank while remaining seaworthy throughout.

That's the ambition. It is not obviously achievable, and prior art in
every adjacent field suggests specific ways it fails. This document
doesn't resolve those; it names them.

## Two axes that keep recurring, independent of each other

**Axis 1 -- where does the model operate?**
- *At the vocabulary/syntax layer*: the model interprets looser,
  natural-language-adjacent input and decides what it means. This is the
  Controlled Natural Language lineage (Basic English -> COBOL -> SBVR/ACE)
  -- see PRIOR_ART.md. Ambiguity resolution happens *inside* the model's
  interpretation of the request.
- *At a bounded, pre-typed hole inside an already-formal structure*: the
  vocabulary, types, and contracts are fixed by a human-authored schema;
  the model only fills a narrow, verifiable gap. This is the Sketch /
  DSPy / LMQL lineage. Ambiguity is supposed to be structurally
  impossible by the time the model is invoked, because the hole's
  contract is unambiguous.

These are not points on a spectrum so much as different bets about where
correctness risk should live. Any concrete design has to pick, per
layer of the system, which one it's doing -- and stay honest about which
one it's actually doing, since it's easy to describe axis 1 systems using
axis 2 language.

**Axis 2 -- what triggers a new abstraction?**
- *Manual curation*: a person decides "this repeated pattern deserves a
  keyword" and defines it.
- *Statistical/automatic discovery*: the system notices recurring
  patterns across a corpus (one codebase, or many) and proposes an
  abstraction.
- *Reactive-only*: abstractions exist because someone already declared
  them; the system's only job is re-verifying/re-synthesizing when the
  declaration changes, never inventing new vocabulary on its own.

Nothing in prior art (surveyed below) does automatic discovery well at
the level of whole reusable abstractions with verified contracts --
most systems that generate code from a compact spec require the compact
spec to already exist, hand-authored.

## Known historical tension: compressing vocabulary has a track record, and it's mixed

Basic English (1930s), COBOL's original "English-like" pitch, SBVR, and
Attempto Controlled English all attempted some version of "let a
restricted vocabulary carry formal meaning." None fully displaced formal
syntax for serious systems despite decades of dedicated effort -- see
PRIOR_ART.md for specifics. Dijkstra's structural argument (EWD667) is
worth carrying forward as a live objection rather than a historical
footnote: formal strictness is not friction on top of the "real" content
of a program, it's what makes it possible to rule out nonsense. A
vocabulary compressed enough to be genuinely concise risks either (a)
smuggling back in exactly the ambiguity formalism exists to remove, or
(b) becoming a formal grammar wearing a human-language costume, which
doesn't actually reduce anything except surface appearance.

## Known empirical finding (not hypothetical): verification strength is target-dependent

A single, verified empirical result from `experiments/001-domainkit`:
a synthesized implementation that satisfied a Python `eval`-based
property test (dynamically typed, so a boolean field could silently
receive a value of the wrong type and still "pass") was *rejected
outright* by a Go compiler checking the identical contract, because Go's
static types don't allow it. This means the strength of "verification"
in any version of this idea is not fixed -- it depends on what target's
type discipline is checking the contract, and a system that only ever
verifies against one, loosely-typed target may be silently accepting
things a second target would catch for free. This is stated here as a
finding to design around, not a solved problem.

## The open measurement question

"Minimize total words/tokens/syntax" is stated as the goal but has not
been shown to be the right proxy for what actually matters (lower cost
to build, understand, and maintain a system correctly). It's possible to
reduce token count by increasing semantic density per token, which could
just as easily *increase* the cognitive distance between an engineer and
what their system does -- the opposite of a stated goal from earlier
discussion of this idea (engineers should stay close to what's produced).
This tension is not resolved anywhere in prior art surveyed here, and is
listed explicitly in OPEN_QUESTIONS.md rather than assumed away.
