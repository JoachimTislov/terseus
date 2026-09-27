# Deep research — 008 agent domain languages (six-language matrix)

**Provenance of this research.** This report is **Vibe research** (the Mistral CLI
agent), **not Astra** — Astra was unavailable for this experiment, so every
selection, weighting, and interpretation below is Vibe's. Primary sources were
fetched directly with `curl` on 2026-09-27: the first ten URLs earlier in the day
(recorded in `RESEARCH.md`), the six new ones for this report in a second batch.
All HTTP 200 unless noted. Every statement is a short paraphrase written for this
document; the few quoted fragments are under ~25 words and attributed. Nothing
was copied at length from any source.

**What this report does not establish.** The six validators, deterministic
summaries, and bounded mutations pass in a harness. **These findings do not prove agent utility.** No AI agent has consumed any of these documents;
usefulness for agent-assisted change is argued from precedent, not measured.
The report separates three kinds of statement throughout:

- **Observed fact** — read directly in a fetched source.
- **Design judgment** — this experiment's interpretation, argued, not sourced.
- **Unverified claim** — secondary snippet or background knowledge, not opened.

Confidence scale: **high** = read in a fetched primary source; **medium** =
authoritative vendor page or claim corroborated but not opened this run;
**low** = single snippet.

---

## 1. Executive summary

The experiment tests one rule — *declare structure, never encode order* — across
six semantic centers for agent coordination documents: ANL (typed capability
graph), SCL (schema contracts), PVL (provenance records), PDL (policy rules),
DTL (decision tables), DRL (desired-state resources). This deep-research pass
adds six sources to the earlier ten: MCP, A2A, NIST AI RMF, OpenTelemetry GenAI
conventions, Temporal, and the MAST multi-agent failure study.

- **Strongest supporting evidence remains the desired-state world.** Kubernetes
  controllers move observed state toward declared intent, and Terraform states
  that block and file order are generally not significant. The most widely
  deployed infrastructure languages contain no steps at all — coordination
  documents do not need to encode order to be industrially useful.
- **The boundary is now sharper.** DMN's `First` and Rule Order hit policies,
  where row position carries meaning, are exactly the leakage this experiment
  forbids, and Temporal demonstrates the opposite design taken seriously:
  durable workflows are code with explicit sequencing, replay-safe by
  construction. Order has a legitimate home — in a runtime engine, not in a
  coordination document.
- **Interoperability is converging on JSON documents plus JSON-RPC.** MCP
  (tools, resources, prompts over JSON-RPC 2.0) and A2A (opaque agents,
  Agent Card discovery, task lifecycle) together cover tool and agent
  interop. A2A's Agent Card is itself a declarative capability document —
  direct overlap with ANL, and an emission target rather than a rival.
- **Observability vocabulary for agents already exists.** The OpenTelemetry
  semantic-convention registry hosts Generative AI groups including agent
  spans and an MCP group. The languages' trace outputs should emit these
  names rather than invent new ones.
- **The MAST study is both a motivation and a caution.** It catalogs 14
  failure modes across three categories — system design issues, inter-agent
  misalignment, task verification — and finds multi-agent gains on popular
  benchmarks are often minimal. Two of its three categories are what
  pre-runtime validation can surface; its results also warn that adding
  structure is not proven to help performance.

**Bottom line (design judgment):** the six centers remain distinct,
workflow-free, and validator-checkable, and the new sources strengthen the
declarative-data / runtime-workflow split without suggesting a seventh center
is required. But the central open question — whether agents actually work
better with these documents — is untouched, and only experiment E1 below can
touch it.

---

## 2. Source table (16 authoritative URLs)

Fetched 2026-09-27 unless noted. Classification: **direct** = materially shaped
a language in this experiment; **adjacent** = informs vocabulary, safety, or
interop without dictating a language; **counterexample** = deliberately encodes
what the experiment forbids, taken as evidence about where that thing belongs.

| # | Source | URL | Observed fact (paraphrase) | Practical implication | Conf. | Class |
|---|---|---|---|---|---|---|
| 1 | OpenAPI 3.1.0 | https://spec.openapis.org/oas/v3.1.0 | Language-agnostic description of HTTP APIs; a dedicated extensions clause sanctions `x-` prefixed fields for meaning the core does not model. | A small core plus a clearly marked escape hatch beats a kitchen-sink schema; SCL's `x-` rule is standard practice, not invention. | high | direct |
| 2 | JSON Schema draft 2020-12 core | https://json-schema.org/draft/2020-12/json-schema-core | Separates an assertion vocabulary (machine-checkable constraints) from an annotation vocabulary (carried, not enforced). | Contracts can carry human-facing meaning without pretending it is enforced; SCL keeps the two lists distinct. | high | direct |
| 3 | W3C PROV-DM | https://www.w3.org/TR/prov-dm/ | Small core: entity, activity, agent; generation, usage, derivation, attribution, delegation; extended structures kept separate. | A provenance language needs no workflow — only what used what and what produced what. PVL is a PROV subset with JSON syntax. | high | direct |
| 4 | OPA / Rego policy language | https://www.openpolicyagent.org/docs/latest/policy-language/ | Rego expresses policy as queries and assertions over data, not an imperative sequence. | Policy rules can be unordered if disagreement is an error rather than silent precedence; PDL adopts this plus one optional default. | high | direct |
| 5 | OMG DMN | https://www.omg.org/spec/DMN/ | A standardized bridge between decision requirements and their automation in processes. | Decision tables are the one DMN piece an agent stack needs; the process layer around them is out of scope here. | high | direct |
| 6 | DMN hit policies (CIB seven manual, Camunda-compatible) | https://docs.cibseven.org/manual/1.0/reference/dmn/decision-table/hit-policy/ | Hit policy decides how many rows may match and which reach the result; `Unique` is violated if more than one row matches; `First` returns the first matching row; `Collect` supports aggregators. | Unique/Priority/Collect stay order-free; First and Rule Order make row position meaningful. DTL supports the first three and rejects the last two by design. | high (mirror caveat, see §10) | direct |
| 7 | Kubernetes controller architecture | https://kubernetes.io/docs/concepts/architecture/controller/ | Controllers are control loops that watch state and move the current state toward the declared desired state. | The document declares intent; an external loop converges. DRL's spec/status split and computed drift come from here. | high | direct |
| 8 | Terraform language docs | https://developer.hashicorp.com/terraform/language | The language is declarative — it describes an intended goal, not steps; block and file ordering are generally not significant, only relationships are. | The single strongest one-sentence precedent for order-free coordination documents. | high | direct |
| 9 | RDF 1.1 concepts | https://www.w3.org/TR/rdf11-concepts/ | A graph is a set of triples (IRIs, blank nodes, literals), representable as a directed labeled graph. | ANL is a small typed graph; no entailment regime or global names are needed for this experiment. | high | adjacent |
| 10 | W3C SHACL | https://www.w3.org/TR/shacl/ | Shapes carry constraint components and targets; the validation report lists violations with focus nodes and severities (`sh:conforms`, `sh:result`). | The harness error model: every rejection is a sorted list of located violations, never one opaque message. | high | direct |
| 11 | MCP specification, version 2025-06-18 | https://modelcontextprotocol.io/specification/2025-06-18 | Open protocol connecting LLM applications to external data and tools; JSON-RPC 2.0; hosts, clients, servers; servers offer prompts, resources, tools; client/server capability negotiation; RFC 2119 keywords; explicit security and trust-and-safety sections; inspired by the Language Server Protocol. | Tool/context interop has settled on JSON-RPC plus schema-shaped JSON. SCL fields project cleanly onto MCP tool input schemas; the harness never needs to speak the wire protocol. | high | adjacent |
| 12 | A2A protocol (v1.0) | https://a2a-protocol.org/latest/ | Open standard for communication between opaque agent applications; positions MCP for tools/data and A2A for agent-to-agent; core concepts include agent discovery (Agent Card), task lifecycle, streaming/async, extensions and bindings; the site announces A2A joining the Agentic AI Foundation. | The Agent Card is itself a declarative capability document: ANL overlaps it and should emit it, not compete with it. Agent-to-agent meaning beyond discovery stays at runtime. | high (landing and navigation read; normative sections not opened — overlap claim is a design judgment) | adjacent |
| 13 | NIST AI Risk Management Framework | https://www.nist.gov/itl/ai-risk-management-framework | Voluntary framework, released January 26, 2023, via an open consensus process; companion Playbook, Roadmap, and Crosswalk; a Generative AI Profile (NIST AI 600-1) released July 26, 2024; the page states AI RMF 1.0 is being revised under the White House AI Action Plan. | Safety claims must map onto a public framework rather than an invented one; §6 maps this experiment's invariants to the RMF's four functions. | high (page); medium (four-function breakdown, background knowledge not refetched) | adjacent |
| 14 | OpenTelemetry GenAI semantic conventions | https://opentelemetry.io/docs/specs/semconv/gen-ai/ | The Generative AI conventions live in the semantic-convention registry (1.44.0 observed), including a Generative AI agent-spans group, a Model Context Protocol group, and provider-specific spans (Anthropic, Bedrock, Azure, OpenAI). | Telemetry names for agents already exist; trace sub-experiments should emit OTel attributes rather than mint vocabulary. The page itself is a "Moved" stub — the registry reorganized, a live example of vocabulary churn. | high (existence and group names; individual attributes not read) | adjacent |
| 15 | Temporal Python SDK developer guide | https://docs.temporal.io/develop/python | Durable orchestration written as code: workflow, activity, and worker primitives with explicit ordering, timeouts, cancellation, versioning; a "Durable AI" section lists integrations with many current agent frameworks (LangGraph, OpenAI Agents SDK, Pydantic AI, Google ADK, and others). | The deliberate counterexample: sequencing fully encoded, replay-safe, in code — and the industry is actively wiring agent frameworks into it. This is evidence for the split, not against it: order belongs in a durable engine, not a coordination document. | high | counterexample |
| 16 | MAST — "Why Do Multi-Agent LLM Systems Fail?" (arXiv 2503.13657) | https://arxiv.org/abs/2503.13657 | 1600+ annotated traces across 7 popular multi-agent frameworks; a taxonomy of 14 failure modes in 3 categories (system design issues, inter-agent misalignment, task verification), built from 150 traces with expert annotators, inter-annotator kappa 0.88; notes that performance gains from multi-agent designs on popular benchmarks are often minimal. | Two of three MAST categories are exactly what pre-runtime document validation can surface. The paper is also a standing caution: structure is not proven to improve outcomes. | high (abstract and metadata; full text not read) | adjacent |

---

## 3. Comparison to all six languages

The table restates the original mapping and adds the pressure each new source
puts on a language. Selections are **design judgments** — Vibe's, argued below,
not mechanical consequences of the sources.

| Language | Semantic center | Taken from direct sources | Rejected | New pressure from this run |
|---|---|---|---|---|
| **ANL** | Typed capability graph: agents, capabilities, evidence, five typed relations | RDF/SHACL-shaped typed graph; SHACL-style located validation reports | RDF's global naming and open-world entailment; shapes/data split | A2A's Agent Card covers a subset of the same ground (identity, skills); ANL should emit one. OTel agent spans define the trace vocabulary |
| **SCL** | Typed record contracts, single `extends`, cross-references | OpenAPI `x-` extensions; JSON Schema assertion/annotation split | Runtime, endpoints, servers vocabulary | MCP tool input schemas are JSON Schema — SCL's field types project almost mechanically |
| **PVL** | Past-tense derivation and responsibility records | PROV-DM entity/activity/agent; generation, usage, derivation, attribution, delegation | PROV extended structures; RDF syntax | OTel spans cover runtime traces; PVL remains the at-rest, post-hoc record. MAST's inter-agent misalignment category is what PVL should make auditable |
| **PDL** | Unordered policy assertions; conflict is an error | Rego's assertions-over-data; one optional default | Rego's expression power (structured conditions only) | MCP's authorization section and NIST Govern function give external hooks for what a policy is *for* |
| **DTL** | Unordered constraint rows with explicit hit policy | DMN Unique/Priority/Collect; `-` wildcard cells; annotations | `First` and Rule Order hit policies (row order carries meaning) | None of the new sources touch decision tables; DTL's boundaries were already set by the DMN evidence |
| **DRL** | Desired vs observed state, computed drift over a dependency DAG | Kubernetes desired-state reconciliation and spec/status split; Terraform's order-insensitivity | Imperative apply steps; in-document controllers | Temporal is the counterexample anchor: DRL declares *what should hold*, Temporal encodes *how and when to act*. The Temporal docs' agent-framework integrations show the runtime side is healthy and crowded |

Per-language notes on the new sources (all **design judgments**):

- **ANL and A2A.** The Agent Card answers discovery — who exists, what skills,
  what endpoints — which is ANL's `agent` and `capability` layer. ANL's extra
  value is evidence linkage and relation-typed critique/escalation structure,
  which Agent Cards do not carry. Emitting a Card from an ANL document is cheap
  and testable (E2 below); treating A2A as a rival would be a category error.
- **SCL and MCP.** MCP tool input schemas are ordinary JSON Schema. A projection
  from SCL contracts to tool input schemas loses SCL's `extends` and `cites`
  (annotations travel, inheritance does not). That is acceptable: projections
  should be lossy views, never the storage format.
- **PVL and OTel.** OTel agent spans describe events as they happen; PVL
  records what already happened, under one namespace, with derivation closure.
  They are complementary layers of the same audit story (E4 below maps one onto
  the other without renaming).
- **PDL and NIST.** "Conflict is an error, never precedence" is a governance
  statement, and it maps to the RMF's Govern function; visible evidence gaps
  map to Measure. The mapping is Vibe's judgment — NIST neither knows about
  nor endorses this experiment.
- **DTL.** Unchanged by this run. Its hit-policy boundary (Unique/Priority/
  Collect in; First/Rule Order out) is the cleanest falsifiable line in the
  whole matrix.
- **DRL and Temporal.** The strongest structural conclusion of this pass: DRL
  documents say what converged state should hold; Temporal workflows say what
  to do, in what order, with retries. The two are designed to coexist, and the
  Temporal ecosystem's rapid absorption of agent frameworks suggests the
  runtime-order side will remain well served by existing engines — a reason
  *not* to build ordering into agent coordination documents.

---

## 4. What belongs in declarative data vs runtime workflow

**Dividing rule (design judgment):** if removing an element changes *what is
true* about the system, it belongs in the document; if removing it changes only
*when or how* things happen, it belongs in the runtime.

Belongs in declarative data (all six languages stay here):

- Who exists and what it can do — agents, capabilities, skills (ANL).
- What shape a record must have — contracts, field types, inheritance (SCL).
- What was used, derived, and who was responsible — provenance (PVL).
- What is permitted, forbidden, required — policy assertions (PDL).
- What conclusion follows from which conditions — decision constraints (DTL).
- What state should hold, and what depends on what — desired state (DRL).
- Invariants, validation reports, evidence and citations, escape-hatch fields.

Belongs in runtime workflow (none of the six languages encode this):

- Sequencing, steps, `next`/`then`, triggers, timers.
- Retries, timeouts, cancellation, compensation, backpressure.
- Transport, negotiation, streaming, task lifecycles (MCP and A2A live here —
  and notably, their *static* artifacts, tool schemas and Agent Cards, are
  themselves declarative documents).
- Reconciliation loops (Kubernetes controllers), replay engines (Temporal),
  and the execution of a DTL evaluation or a PDL decision.

**Temporal as counterexample, used properly.** Temporal's answer to ordering is
to make order a first-class, durable, replay-safe program. That is correct for
execution and wrong for coordination documents: encoding order in a document
fixes it at authorship time, hides it from validators, and makes every replay
of the document a claim about a future that has not happened. The experiment's
position is not "order is bad" but "order is runtime state" — **design
judgment**, consistent with the Kubernetes/Terraform evidence and with
Temporal's own separation of workflow code from the state it manages.

---

## 5. Interoperability vocabulary

A shared crosswalk so consumers of one language can recognize the concept in
another and in the external standards. All cell-to-cell equivalences are
**design judgments** except where sourced.

| Concept | ANL | SCL | PVL | PDL | DTL | DRL | External anchor |
|---|---|---|---|---|---|---|---|
| Agent / actor | `agent` | — (out of scope) | `agent` records | — | — | — | A2A Agent Card principal; OTel service/resource |
| Tool / capability | `capability` | contract fields | — | — | — | — | MCP tool; A2A skill |
| Data / resource | `evidence` | field types | `entity` | input data | input columns | `evidence` string | MCP resource; RDF entity |
| Input contract | relation constraints | `contract` + `extends` | — | condition structure | column types | field schema | JSON Schema (MCP tool input schema) |
| Decision | — | — | — | rule decision | table output | — | DMN decision |
| Rule / policy | relation rules | validation rules | — | `rule` | table row | drift policy | Rego rule |
| Provenance record | `evidence` links | `cites` | all PVL records | `cites` | `cites` | `evidence` | PROV entity/activity/agent |
| Desired state | — | — | — | — | — | `desired` vs `observed` | Kubernetes spec/status |
| Validation report | harness errors | harness errors | harness errors | harness errors | harness errors | harness errors | SHACL `sh:result` shape |
| Escape hatch | `note` | `x-` objects | `attributes` | `note` | `-` cell, `note` | `labels`/`annotations` | OpenAPI `x-`; K8s annotations |
| Drift | — | — | — | — | — | computed drift | controller reconciliation |
| Verification / audit | evidence coverage | field origin | derivation closure | cite trace | evaluation chain | blockers/waiters | OTel GenAI agent spans; NIST Measure |

**Design judgment:** the crosswalk shows the six centers are not redundant —
no row is fully covered by two languages, and no language covers two rows'
external anchors alone. It also defines the projection targets for E2: ANL →
A2A Agent Card + MCP tool descriptions; SCL → JSON Schema; every trace → OTel
GenAI attributes.

---

## 6. Provenance / safety invariants

Structural invariants enforced by validators today, with their anchors. The
NIST mapping in parentheses is Vibe's (the RMF neither knows of nor endorses
this experiment; the four functions are cited from background knowledge —
medium confidence).

1. **Derivation acyclicity (PVL).** A derivation cycle is contradictory because
   derivation implies temporal precedence. Anchored in PROV-DM's model
   (judgment on the cycle reading; the spec does not say it in one sentence).
2. **Delegation well-formedness (PVL).** `performed_by` must reference an
   existing agent; delegation must reference an existing activity. PROV
   `actedOnBehalfOf` with qualifying activity.
3. **Past-tense only (PVL).** No pending or future records; a provenance
   document is an audit of what happened, never a plan. (NIST Measure.)
4. **Conflicts are errors (PDL).** Two matching rules that disagree raise an
   error; there is no rule-order precedence. Mirrors Rego's conflict error for
   complete rules (medium confidence — snippet-verified, Styra page not opened).
5. **At most one default (PDL).** A single optional default rule; two defaults
   are an error, and a default with unconditional rules is an error.
6. **Hit-policy honesty (DTL).** Only Unique, Priority, Collect; `First` and
   Rule Order rejected because row position carries meaning. Unique-policy
   overlap is detectable at validation time for enumerated inputs (judgment,
   derived from the CIB seven semantics).
7. **Dependency acyclicity (DRL).** The `depends_on` graph must be a DAG;
   drift is computed, never asserted as a plan. (NIST Manage.)
8. **Referential integrity and inheritance sanity (SCL).** No dangling `ref`,
   no `extends` cycles, single inheritance. (NIST Map — the document is the
   inventory of what exists and how it relates.)
9. **Relation-typed structure rules (ANL).** Per-relation cycle rules: mutual
   critique cycles are legal (symmetric), escalation chains must not loop
   (asymmetric), duplicate relations are errors.
10. **Forbidden-key vocabulary (all six).** Every validator rejects `step`,
    `order`, `next`, `then`, `before`, `after`, `trigger`, `sequence` (plus
    language-specific additions). This is syntactic; it cannot catch semantic
    smuggling — see failure mode F1. (NIST Govern.)
11. **Evidence gaps are legal and surfaced (all six).** Unevidenced entities
    are reported, never fatal and never hidden; the scorecard rewards
    visibility of gaps, not their absence.
12. **Deterministic validation reports (harness).** SHACL-shaped: sorted,
    located, keyed error strings; reruns byte-identical.

---

## 7. Practical failure modes

How this design fails in practice, with detection ideas. The first three are
**design judgments** informed by MAST's observed categories.

- **F1 — Workflow smuggling.** The forbidden-key scan is syntactic; meaning
  can still be smuggled through priority-as-order, numeric ordering fields
  under other names, or Agent-Card-like position-dependent lists. Detection:
  adversarial review rounds; add semantic lints (e.g., flag any list whose
  elements carry rank-like fields). MAST's system-design category is the
  field evidence that bad structure is a top failure source.
- **F2 — Escape-hatch abuse.** `x-` and `note` fields are meant for rare,
  unanticipated meaning; in practice they can become load-bearing and
  unvalidated, dissolving the language into folklore. Detection: audit escape-
  hatch usage frequency; promote anything recurring into the typed core.
- **F3 — Validation theater.** 36/36 green while documents carry junk: free-
  string `cites` full of dead references, `attributes` maps nobody reads.
  Detection: grounding metrics (already computed for scorecards) plus MAST-
  style trace audits.
- **F4 — Inter-agent misalignment (MAST category).** Two teams' documents
  drift on shared vocabulary; nothing catches it because each language closes
  over one document. Detection: cross-document consistency checks — requires
  E3.
- **F5 — Vocabulary churn.** Observed this run: the OTel GenAI page is a
  "Moved" stub into a reorganized registry; A2A announced a foundation move;
  NIST states AI RMF 1.0 is in revision. Projections onto external
  vocabularies rot faster than the languages. Detection: pin versions in
  emitted artifacts and smoke-test against live registries.
- **F6 — Evidence rot.** Evidence and citation strings go stale; validators
  check shape, never liveness. Detection: liveness at read time, out of band;
  never in the validator (judgment — keeping validation offline and
  deterministic is worth more than freshness).
- **F7 — Mirror dependency.** Camunda's own docs were unreachable on
  2026-09-27; the CIB seven mirror served the DMN hit-policy semantics. A
  mirror can drift from the engine. Detection: verify one normative example
  against a live engine at the next opportunity.
- **F8 — Nondeterminism regression.** Any set-iteration or dict-order leak in
  summary generation breaks the byte-identical guarantee silently. Detection:
  the rerun check already in the harness; keep summaries keyed and sorted.

---

## 8. Prioritized next experiments

Ordered by expected information gain per unit of work; all are Vibe proposals.

1. **E1 — Agent-consumption trial (highest priority).** Same incident-triage
   task, run by an LLM agent three ways: no document, plain prose brief, and
   each language's document. Measure task success, edit locality requests,
   and error recovery. This is the only experiment that can say anything about
   agent utility; everything else sharpens validity.
2. **E2 — Interop projections.** Emit an A2A Agent Card and MCP tool input
   schemas (JSON Schema) from one ANL/SCL document; validate the emitted
   artifacts against the official schemas; round-trip. Tests the §5 crosswalk
   without adding runtime.
3. **E3 — Cross-document closure.** Add imports/refs across files. Prediction
   (design judgment): mutation locality degrades, and the cost is measurable —
   that measurement itself is the result; it would bound the single-document
   trade-off the languages currently make.
4. **E4 — OTel trace mapping.** Map each language's trace output onto
   OpenTelemetry GenAI agent-span attribute names; check nothing needs new
   vocabulary. If new names are needed, the §5 anchor claim is weakened.
5. **E5 — Negative-control mutation corpus.** Generate many random legal
   mutations per language and measure summary churn beyond each
   `MUTATION_SPEC`. Locality is currently demonstrated once per language.
6. **E6 — MAST-aligned fault injection.** Run a two-agent setup and inject
   failures from the three MAST categories; check whether pre-runtime
   validation catches design and misalignment faults before runtime does.
7. **E7 — Judgment-criteria audit.** Blind re-scoring of the scorecard's
   judgment entries by a second reviewer; measure agreement. Cheapest check on
   the experiment's most-audited weakness.

---

## 9. Falsifiers

The hypothesis or implementation fails if any of these occurs:

1. Any nontrivial incident-triage task cannot be expressed in one of the six
   centers without smuggling order (sequence fields, `then`, triggers,
   priorities-as-order, First/Rule-Order hit policies) into the document.
2. Any validator rejects a legal document, or accepts one that breaks its
   center's meaning (escalation loop, derivation cycle, dependency cycle,
   unique-hit overlap, disagreeing policy rules, dangling reference).
3. Any legal nontrivial edit produces summary changes outside the declared
   `MUTATION_SPEC` neighborhood.
4. Any summary, projection, trace, or scorecard output is nondeterministic.
5. E1 shows no measurable benefit over a no-document baseline for all six
   languages — the utility claim dies (the validity claims above survive it).
6. E2/E4 show meaning lost in projection to MCP, A2A, or OTel vocabularies —
   the interoperability-vocabulary claim dies.
7. An external standard ships a coordination-document format that covers one
   of the six centers (for example, an A2A extension carrying typed critique
   or evidence) — that language becomes redundant and should be retired.

---

## 10. Limitations

- **Agent utility is unproven.** No agent consumed any of these documents in
  any test. The scorecard's observed entries measure the shipped samples, not
  the wild; its judgment entries are unaudited opinions.
- **Vibe, not Astra.** The independent-design perspective this experiment
  normally gets from Astra was unavailable; Vibe authored languages, research,
  and scorecards, a self-confirmation risk that E7 partially addresses.
- **Single-document closure.** No cross-document imports, no SHACL-style
  shapes/data split; inter-agent misalignment (MAST) is unaddressed by design.
- **One mutation per language.** Locality is demonstrated once per center, not
  over the edit space.
- **Source caveats.** Camunda's own docs were unreachable (mirror used). The
  Rego conflict-error semantics and the NIST four-function breakdown are
  medium confidence (snippets / background knowledge; pages not opened). The
  MAST paper was read at abstract level only. A2A's full normative spec
  sections were not read, only its landing page, navigation, and tutorials
  index. The ecosystem observed here (MCP 2025-06-18, A2A v1.0 under a new
  foundation, OTel registry mid-reorganization, NIST RMF under revision) is
  moving quickly; every adjacent-source fact has a shelf life measured in
  months.
- **Paraphrase policy.** All content is paraphrased; brief attributed quotes
  are under ~25 words. No copyrighted text was copied.

---

## 11. Ledger of design judgments and unverified claims

**Design judgments** (Vibe's; argued in place, not sourced): the six-center
matrix itself; rejecting First/Rule-Order hit policies; derivation-cycle
rejection as a *reading* of PROV-DM; conflict-is-error as a governance stance;
the declarative/runtime dividing rule in §4; "order is runtime state"; the §5
crosswalk equivalences; the NIST invariant mapping; the ANL→Agent Card overlap
claim; E-prioritization; predictions in E3.

**Unverified claims** (flagged, with plan): Rego complete-rule conflict error
behavior (snippet-level; open the Styra page); NIST four-function breakdown
(background knowledge; fetch NIST AI 100-1); MAST category details beyond the
abstract (fetch full text); A2A Agent Card field-level contents (open the
spec); OTel agent-span attribute specifics (open the registry group).
