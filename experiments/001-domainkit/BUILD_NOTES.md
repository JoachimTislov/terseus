# domainkit -- a minimal proof of concept

**The idea being tested:** the domain schema (types, keywords, relations,
contracts, interface) is the only hand-authored source of truth. An LLM is
only ever trusted to fill in a *pre-typed hole* -- the body of one keyword's
function, whose name, signature, and contract are fixed. It is never asked
to interpret intent from natural language, and its output is never accepted
just because it looks plausible: it has to survive property-based testing
against the contract first. If it fails, it's rejected with a concrete
counterexample and re-synthesized (or you fix the contract, if the contract
itself was wrong).

This is deliberately small. It exists to make the mechanism concrete enough
to argue about, not to be a real system.

## Run it

```bash
pip install -r requirements.txt
python main.py          # synthesize + verify every keyword, write generated_impls.py
python app.py            # http://localhost:5050 -- a UI generated from schema.yaml
```

With no `ANTHROPIC_API_KEY` set, `main.py` uses `MockSynthesizer`, a tiny
deterministic heuristic standing in for an LLM, so you can see the whole
pipeline run without an API key. Set `ANTHROPIC_API_KEY` and it switches to
`AnthropicSynthesizer` automatically, which really calls the model and feeds
back the counterexample on a failed attempt.

## What's actually being demonstrated

1. **schema.yaml is the only place intent is expressed**, and it's fully
   declarative: types, a keyword's subject/object, and a `requires`/
   `ensures` contract. Nothing else in the pipeline may introduce a field,
   a relation, or change a contract's meaning.
2. **Standardization, not per-call interpretation.** `complete` means one
   thing, defined once, in this domain. Every task that gets `complete`d
   goes through the exact same verified function -- there's no
   re-negotiation of meaning at each call site.
3. **The LLM's blast radius is the size of a hole, not the size of a
   system.** It can only affect one function body, under one contract,
   and its output is either verified or discarded -- see
   `contracts.py::verify_contract` and the rejection test in the repo
   history (a deliberately wrong `complete` implementation gets caught
   with a concrete counterexample, not waved through).
4. **The interface doesn't duplicate the rules.** `app.py` reads the same
   `requires`/`ensures` to decide whether a button click is even allowed,
   so the UI can't drift out of sync with the domain model.

## How this maps to the concepts we discussed

- **LMQL** (Beurer-Kellner et al., PLDI 2023, arxiv.org/abs/2212.06094) --
  embeds constraints directly into the language's execution rather than
  parsing free text after the fact. Here, the contract plays that role:
  it's not documentation, it's an executable gate.
- **DSPy** (Khattab et al., arxiv.org/abs/2310.03714) -- treats LM calls as
  typed, declarative modules in a program graph rather than hardcoded
  prompt strings. `synth.py`'s `synthesize()` interface is that idea
  reduced to its smallest possible unit: one typed hole per keyword.
- **Neurosymbolic programming** (Chaudhuri et al., 2021,
  doi.org/10.1561/2500000049) -- argues a language's structural
  restrictions are what make a neural component's contribution
  trustworthy and reusable, not friction to remove. `schema.yaml`'s type
  system is exactly that restriction.
- **Sketch / program synthesis with holes** (Solar-Lezama) -- the
  intellectual ancestor of this whole pattern: you write the scaffold,
  the solver (or here, the LLM + verifier) fills bounded gaps.
- Deliberately *not* used: controlled natural language / ACE-style
  "subset of English" as the interface for expressing logic. That's a
  different, older idea (and one with a rockier track record -- see our
  earlier discussion) about who writes the schema, not how the schema
  gets implemented. This project keeps intent expression fully formal
  (YAML + typed contracts) and only lets the LLM operate inside that
  formality.

## Honest limitations (read before extending this)

- `eval()` is used for contract expressions for brevity. It's sandboxed
  with an empty `__builtins__`, but it's not a real expression language --
  a production version needs a proper parser (a tiny grammar over
  `subject.field`, comparisons, `and`/`or`/`not`) so contracts can't
  reference anything outside the schema, full stop.
- Verification here is randomized property testing, not a proof. It's
  good at catching wrong implementations (see the rejection demo) but
  it's not a soundness guarantee the way an SMT-backed tool like Sketch
  or Rosette would give you. That's the natural "make this real" next
  step: compile `requires`/`ensures` to Z3 constraints and either prove
  the synthesized function correct or find a counterexample deterministically.
- Relations are shallow (one level of nesting, capped depth for random
  generation). A real version needs proper multiplicity (one-to-many,
  many-to-many) and referential integrity, not just "a field that points
  at another type."
- The interface is intentionally the least interesting part of this repo
  -- it exists to prove the contract can gate the UI, not to be a real
  frontend.

## Second increment: bounded multi-target synthesis + reactive re-verification

The first version of this repo required a hand-written provider before a
keyword could exist for a given target. This increment removes that
requirement while keeping everything else's guarantees:

- **`targets:` in schema.yaml bounds the LLM's output space.** Only the
  languages/frameworks declared there are ever generated for -- this is
  the "prevent ambiguous output" constraint: the model doesn't choose a
  language or a style, the schema does.
- **Bindings are now an optional override, not a requirement.** `complete`
  and `assign` still wire to the hand-written providers (`providers/`).
  `reopen` has no binding at all -- it's synthesized directly for *both*
  Python and Go, verified independently in each, with no shared source
  between the two implementations.
- **Types are generated mechanically** (`domainkit/targetlang.py`,
  `generate_go_types`), never synthesized -- they're structure, not
  logic, so there's nothing non-deterministic about them.
- **Reactive, content-hashed synthesis.** `compile_targets.py` hashes
  each keyword's `(subject, object, requires, ensures, target style)`.
  Unchanged keywords are never re-synthesized or re-verified on a
  rebuild -- run it twice with no schema edits and you'll see "unchanged
  -- reusing cached verified implementation" for `reopen` on both
  targets. Edit a contract and only that keyword's synthesis re-runs. A
  failed verification never overwrites a previously-verified
  implementation.
- **The Go verifier is now generated from the schema too**
  (`domainkit/verify_go_gen.py`) -- no hand-written per-keyword Go test
  code. Any new keyword gets a working verifier the moment it's declared.

### A real finding from building this, not a hypothetical

While testing the reactive re-synthesis, an intentionally bad contract
(`ensures: "not subject.title"`, a string field) was fed through both
targets. **Python's `eval`-based verifier accepted it** -- the
synthesizer wrote `subject.title = False`, and `not False` is truthy
regardless of the field's declared type, so the property test passed on
a value of the wrong type entirely. **Go's compiler rejected the same
contract outright**, because `Title` is statically `string` and can't
hold a `bool`. Cross-language verification caught a defect that a
single-language pipeline let straight through. This is a direct,
concrete argument for the "replace `eval` with a real parsed, typed
expression language" item in the limitations list above -- it's not a
theoretical nicety, it's the difference between catching a bad contract
immediately and shipping it.

## Natural next steps, roughly in order of ambition

1. Replace `eval()` with a real parsed contract language (small grammar,
   maybe 50-100 lines with a parser generator).
2. Replace random-testing verification with an SMT-backed check (Z3 via
   `z3-solver`) for a real correctness guarantee instead of a probabilistic one.
3. Add a second domain (something with more interesting relations --
   multiplicities, cascading contracts across related types) to see where
   the "standardized keyword" idea starts to strain.
4. This is where a Go rewrite would make sense given your existing stack
   (refviz, ai-native-vcs) -- the schema compiler and verifier are a
   natural fit for Go's type system, and it'd let you reuse tooling
   across projects.
