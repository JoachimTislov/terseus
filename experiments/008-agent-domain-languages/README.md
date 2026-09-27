# 008 — Agent domain languages (consolidated 008/009, 6x6 matrix)

The standalone ANL experiment from 008 is consolidated here as the first
language in a broader comparison. Its typed capability graph, relation-specific
cycle rules, deterministic summaries, and local mutation are retained in
`agentlangs/anl.py` and `samples/anl/`. This experiment asks the broader
question: if "declare structure, never encode order" is the rule, how many
*distinct semantic centers* can agent coordination documents have before one
is forced to smuggle workflow back in? Six domain languages, one shared
harness, six sub-experiments each: a 36-cell matrix, all of which must pass.
Stdlib-only Python, JSON documents, no dependencies.

## Hypothesis

Six different semantic centers — a capability graph, a schema-contract set, a
provenance record, a policy rule set, a decision table, and a desired-state
resource model — can all express nontrivial incident-triage meaning for
agents without ever encoding order, triggers, or steps, and each can be given
a validator, a deterministic summary, and a bounded mutation whose diff stays
local to the edit. If any center cannot stay workflow-free for a realistic
task, or cannot be validated deterministically, the hypothesis is falsified
for that center.

## The six semantic centers

| Key | Language | Semantic center | Inspired by | Escape hatch |
|---|---|---|---|---|
| `anl` | Agent Network Language (baseline from 008) | typed capability graph: agents, capabilities, evidence, five typed relations | RDF/SHACL-shaped capability ontologies | free-text `note` on any record; unevidenced capabilities are legal gaps |
| `scl` | Schema Contract Language | typed record contracts with single inheritance (`extends`) and cross-references (`ref`) | OpenAPI 3.1 / JSON Schema 2020-12 | `x-` prefixed extension objects, shape-validated only |
| `pvl` | Provenance Vocabulary Language | past-tense derivation and responsibility records over one namespace | W3C PROV-DM | free-form `attributes` string maps on entities |
| `pdl` | Policy Decision Language | unordered decision assertions; conflict is an error, never precedence | OPA / Rego | free-text `note`; `cites` entries are free strings |
| `dtl` | Decision Table Language | unordered constraint rows with an explicit hit policy | OMG DMN decision tables | the `-` wildcard cell; `note`/`cites` on rules |
| `drl` | Desired-state Resource Language | desired vs observed state with computed drift over a dependency DAG | Kubernetes / HCL | free-form `labels`/`annotations`; `evidence` is a free string |

What is deliberately absent from **every** language: steps, sequences,
triggers, `next`/`then`, priorities-as-order, and any key that tells a
consumer *when* something runs. Each module's validator rejects a shared
forbidden-key vocabulary (`step`, `order`, `next`, `then`, `before`, `after`,
`trigger`, `sequence`, and where relevant `priority`/`command`/`script`/`run`).
DTL additionally rejects DMN's `First` and `Rule Order` hit policies by
design, because there row position carries meaning — exactly the leakage
this experiment forbids.

## The six sub-experiments (per language)

1. **declaration** — the sample loads, validates, and yields a deterministic
   summary (unique, ordered, keyed lines; re-running must be byte-identical).
2. **invalid-input validation** — every `invalid_*.json` case must be rejected
   with the expected located error (SHACL-report style: sorted, focused
   error strings, never a single opaque message).
3. **mutation/locality** — the diff of `sample.json` vs `mutated.json`
   summaries must equal the module's declared `MUTATION_SPEC` exactly;
   nothing outside the declared neighborhood may move.
4. **projection/rendering** — a deterministic alternative rendering (DOT,
   OpenAPI-style block, chain-of-custody table, readable policy text,
   markdown tables, kubectl-describe text) containing declared markers.
5. **provenance/evidence trace** — a deterministic trace for the declared
   target (capability evidence, field origin, derivation closure, decision
   cites, table evaluation chain, drift with blockers/waiters).
6. **practical-fit scorecard** — six criteria scored 0..3, with `observed`
   entries recomputing from measured metrics and `judgment` entries marked
   as such.

A failing sub-experiment raises; the harness never fabricates a pass.

## Research findings and URLs

`RESEARCH.md` holds the full study (primary sources fetched 2026-09-27,
facts separated from judgments, confidence levels recorded). Summary:

- **OpenAPI 3.1 / JSON Schema 2020-12** — https://spec.openapis.org/oas/v3.1.0,
  https://json-schema.org/draft/2020-12/json-schema-core — specification
  extensions (`x-` objects) are the sanctioned home for unanticipated meaning;
  assertion and annotation vocabularies are separate. Taken by SCL.
- **W3C PROV-DM** — https://www.w3.org/TR/prov-dm/ — entity/activity/agent
  with generation, usage, derivation, attribution, delegation; a deliberately
  small core. Taken by PVL; derivation cycles are rejected as contradictory.
- **OPA / Rego** — https://www.openpolicyagent.org/docs/latest/policy-language/ —
  policy as assertions on data; complete rules that disagree are errors
  (`eval_conflict_error`), not precedence. Taken by PDL (unordered rules,
  conflict = error, one optional default).
- **OMG DMN** — https://www.omg.org/spec/DMN/ (hit-policy reference:
  https://docs.cibseven.org/manual/1.0/reference/dmn/decision-table/hit-policy/) —
  hit policies decide how many rows may match; Unique/Priority/Collect stay
  order-free, First and Rule Order do not. Taken (and bounded) by DTL.
- **Kubernetes / HCL** — https://kubernetes.io/docs/concepts/architecture/controller/,
  https://kubernetes.io/docs/concepts/overview/kubernetes-api/,
  https://developer.hashicorp.com/terraform/language — controllers move
  observed state toward declared desired state; the document contains no
  steps. The strongest empirical evidence that coordination documents need
  not encode order. Taken by DRL.
- **RDF / SHACL** — https://www.w3.org/TR/rdf11-concepts/,
  https://www.w3.org/TR/shacl/ — typed graphs with structural constraints;
  validation reports as located, sorted violations. Taken by the ANL baseline
  and by this harness's error shape.

## Reading the practical-fit scores

Each scorecard totals 0..18 over six criteria (grounding,
referential integrity, escape-hatch usage, workflow leakage,
explainability, edit locality). Interpretation rules:

- **observed** entries are recomputed from the document by the harness
  itself (e.g. evidence coverage fractions, forbidden-key counts) — those
  scores are measurements of the *samples*, not of the language in the wild.
- **judgment** entries are explicit design judgments (Vibe's, not Astra's —
  Astra was unavailable for this experiment); they carry no user-study
  evidence and are marked as such in every note.
- A low grounding score means "this sample has unevidenced entities", which
  is a *legal, surfaced state* by design — not a defect. The scorecard
  rewards visibility of gaps, not their absence.
- Totals are not comparable across languages as a ranking: the semantic
  centers are different instruments. Use them to ask "which observed
  guarantees does each language give me on a real file", nothing more.

## Limitations and falsifiers

Limitations (what 36/36 does *not* establish):

- No agent ever consumed one of these documents; utility for AI-assisted
  change is argued, not demonstrated.
- The scorecard's judgment criteria are unaudited design opinions; only the
  observed criteria are measured, and only on the shipped samples.
- Each language closes over a single document; no cross-document imports,
  no SHACL-style shapes/data split.
- Mutation locality is demonstrated once per language (one shipped
  mutation), not exhaustively over all possible edits.

Falsifiers — the hypothesis or implementation fails if:

- any nontrivial incident-triage task cannot be expressed in one of the six
  centers without smuggling order (sequence fields, `then`, triggers,
  priorities-as-order, First/Rule-Order hit policies) into the document;
- any validator rejects a legal document (e.g. mutual critique in ANL,
  an evidence-less DRL resource) or accepts one that breaks the center's
  meaning (escalation loop, derivation cycle, dependency cycle, unique-hit
  overlap, disagreeing policy rules);
- any legal nontrivial edit produces summary changes outside the edited
  neighborhood beyond the declared `MUTATION_SPEC` scope;
- any summary, projection, trace, or scorecard output is nondeterministic.

## Files

- `agentlangs/` — one self-contained module per language (`anl`, `scl`,
  `pvl`, `pdl`, `dtl`, `drl`), plus `errors.py` (located error type),
  `harness.py` (the six sub-experiments and the 6x6 runner), and `cli.py`.
- `samples/<lang>/sample.json` — the valid document (incident-472 triage).
- `samples/<lang>/mutated.json` — one bounded mutation for sub-experiment 3.
- `samples/<lang>/invalid_*.json` — rejection cases; wrappers with
  `document` and `expect_error` (the located error substring that must
  appear in the raised `ValidationError`).
- `test_matrix.py` — parameterized pytest suite over the full matrix.
- `RESEARCH.md` — the gathered practical intelligence with URLs.

The former standalone experiment-008 files are intentionally not duplicated:
ANL's behavior and fixtures live only in this consolidated directory, and the
site visualization reads the same canonical ANL samples.

## Agent CRUD

The ANL slice also exposes document-level CRUD operations. They are pure
transformations: each operation validates the input and output, create/update
reject unknown capabilities, and delete rejects agents still referenced by
relations. This keeps mutations safe without introducing workflow semantics.

```bash
python3 -m agentlangs.cli agent create \
  --file samples/anl/sample.json --id reviewer --type human \
  --capability claim-verification --out /tmp/anl-created.json
python3 -m agentlangs.cli agent read \
  --file /tmp/anl-created.json --id reviewer --out /tmp/reviewer.json
python3 -m agentlangs.cli agent update \
  --file /tmp/anl-created.json --id reviewer --type llm \
  --note "automated reviewer" --out /tmp/anl-updated.json
python3 -m agentlangs.cli agent delete \
  --file /tmp/anl-updated.json --id reviewer --out /tmp/anl-deleted.json
```

## Commands

Run the full matrix (exit 0 iff 36/36 pass):

```
python3 -m agentlangs.cli
```

One language only, JSON report, or output to a file:

```
python3 -m agentlangs.cli --language dtl
python3 -m agentlangs.cli --format json
python3 -m agentlangs.cli --out report.json --format json
```

Run the tests (the same matrix, parameterized, plus every invalid case):

```
python3 -m pytest test_matrix.py -q
```

The pytest suite executes `harness.run_all()` (asserting exactly 36 passes),
runs every sub-experiment individually, and rejects every `invalid_*.json`
document with its declared error.
