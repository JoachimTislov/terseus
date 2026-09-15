# Experiment 001: domainkit (folded in from an earlier, narrower thread)

## What this was actually testing

A much narrower question than this repo's scope: given a schema (types,
keywords, contracts, per-target bindings), can an LLM's contribution be
confined to a bounded, verified hole -- falling back to hand-written
providers where they exist -- and can that stay reactive (only
re-synthesizing when the schema's content actually changes) across more
than one target language?

## What it found (see BUILD_NOTES.md for the full account)

- Yes, within a very small contract grammar (boolean flips, single
  field-to-field equality): synthesis + verification worked
  independently across two targets with zero shared source between them.
- The verification mechanism's strength depends entirely on the target's
  own type discipline -- a Python (dynamically typed) verifier accepted
  a contract a Go (statically typed) compiler correctly rejected. This
  is the empirical finding cited in THEORY.md.
- The contract language (Python `eval` on a handful of string patterns)
  was the load-bearing simplification the whole prototype depended on,
  and was flagged from the start as the piece least likely to survive
  contact with a real domain.

## What it did not test, and shouldn't be assumed to generalize

- Automatic discovery of new keywords (Open Question #3) -- every
  keyword here was hand-declared, never mined or proposed.
- Any measurement of whether the resulting schema was actually more
  concise, in any meaningful sense, than writing the target code by hand
  (Open Question #4) -- two toy domains with two or three keywords each
  is not evidence either way.
- Governance or versioning of a keyword once multiple consumers depend
  on it (Open Question #5, #8) -- there was only ever one consumer.
- Anything beyond a boolean-flip/equality contract grammar -- real
  invariants (a bounded numeric field, a multi-step state machine) were
  explicitly out of scope and are exactly where Open Question #6 lives.

Treat this as one calibration point on the "bounded hole-filling,
reactive to a declarative source" axis (THEORY.md, Axis 1/2), not as a
recommended starting architecture for whatever comes next.
