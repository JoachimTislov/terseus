# Research — 008 agent domain languages

**Provenance of this research:** Astra was unavailable for this experiment, so the
independent design/research perspective was provided by Vibe (the Mistral CLI
agent) itself. Everything below is **Vibe research**, not Astra research. Primary
sources were fetched directly with `curl` on 2026-09-27; a web-search connector
was used to locate secondary sources. No text was copied from any source; all
statements are short paraphrases written for this document. Quoted fragments are
brief (under ~25 words) and attributed.

## Method

Each topic below records: URLs, **observed facts** (read directly from a fetched
page), **design judgments** (this experiment's interpretation, argued), and
**unverified claims** (secondary-source snippets not opened or not fully read).
Confidence: high = read in a fetched primary source; medium = corroborated by
two independent secondary sources or one authoritative vendor page; low = single
secondary source or snippet.

---

## 1. OpenAPI 3.1 and JSON Schema draft 2020-12

URLs (fetched 2026-09-27, HTTP 200):

- https://spec.openapis.org/oas/v3.1.0
- https://json-schema.org/draft/2020-12/json-schema-core

Observed facts:

- The OpenAPI Specification "defines a standard, programming language-agnostic
  interface description for HTTP APIs" that lets "both humans and computers …
  discover and understand the capabilities of a service" without reading source
  code or watching network traffic.
- The OAS has a dedicated "Specification Extensions" clause: vendors may add
  fields whose names begin with the `x-` prefix. Extension objects are the
  sanctioned mechanism for meaning the core spec does not model.
- JSON Schema 2020-12 "uses keywords to assert constraints on JSON instances or
  annotate those instances": the spec separates an assertion vocabulary
  (machine-checkable constraints) from an annotation vocabulary (carried, not
  enforced).

Design judgments:

- The `x-` escape hatch is the single most load-bearing practical idea here: a
  language can stay small if unanticipated meaning has a sanctioned, clearly
  marked place to live. This experiment requires every candidate language to have
  one.
- OpenAPI documents are consumed by code generators, linters, diff tools, and
  humans; the format succeeded because it is declarative, machine-validatable,
  and diff-friendly. Evidence-linkage and human readability are separate axes
  and must be scored separately.

Confidence: high.

## 2. W3C PROV-DM

URL (fetched 2026-09-27, HTTP 200):

- https://www.w3.org/TR/prov-dm/ (W3C Recommendation, 30 April 2013)

Observed facts:

- PROV-DM distinguishes **core structures** ("the essence of provenance") from
  **extended structures**; the core is deliberately small.
- Three primary kinds: an **entity** is "a physical, digital, conceptual, or
  other kind of thing with some fixed aspects"; an **activity** is something
  that "occurs over a period of time and acts upon or with entities" (consuming,
  transforming, generating); an **agent** "bears some form of responsibility"
  for an activity, an entity, or another agent's activity.
- Core relations include **generation** ("the completion of production of a new
  entity by an activity"), **usage** ("the beginning of the act of utilizing
  entities"), **derivation** (transformation/update/construction of a new
  entity based on a pre-existing one), **attribution**, and **delegation**
  (`actedOnBehalfOf`, with an optional qualifying activity).

Design judgments:

- PROV is the reference answer to "what does a provenance-first language look
  like": no workflow at all, only records of what used what and what produced
  what. A provenance language for agents (PVL in this experiment) can be a
  small subset of PROV-DM with JSON syntax.
- Derivation implies temporal precedence (a derived entity did not exist before
  its source), so a derivation cycle is contradictory and should be rejected at
  validation time. This is our reading of the model's intent, not a sentence in
  the spec: judgment.

Confidence: high (facts); medium (cycle judgment).

## 3. OPA / Rego

URLs:

- https://www.openpolicyagent.org/docs/latest/policy-language/ (fetched
  2026-09-27, HTTP 200)
- https://docs.styra.com/opa/errors/eval-conflict-error/complete-rules-must-not-produce-multiple-outputs (search snippet; page not opened)

Observed facts:

- From the OPA docs: "Rego queries are assertions on data" that "can be used to
  define policies and make decisions about whether data violates the expected
  state of your system." Rego is described as letting you "express desired
  rules and decisions as code."
- Rego's rules are not an imperative sequence; policy is evaluated as queries
  over input and data documents.

Unverified claims (secondary snippets, not opened):

- Complete rules that take the same input and produce unequal output raise
  `eval_conflict_error` ("complete rules must not produce multiple outputs").
  Two independent sources (Styra docs snippet, Snyk article snippet) describe
  this error, and Snyk describes how unresolvable conditions evaluate to
  undefined rather than false. Both were search snippets only.

Design judgments:

- The decisive practical constraint for a policy language: **conflicts must be
  errors, not precedence**. If two matching rules disagreeing silently produced
  a winner by rule order, order would smuggle workflow back in. PDL adopts:
  unordered rules, disagreement = error, one optional default rule (mirroring
  the `default` keyword described in Rego documentation).

Confidence: high (facts); medium (conflict/default semantics).

## 4. DMN decision tables

URLs (both fetched 2026-09-27, HTTP 200):

- https://www.omg.org/spec/DMN/ (spec landing page)
- https://docs.cibseven.org/manual/1.0/reference/dmn/decision-table/hit-policy/
  (CIB seven / Camunda DMN engine reference, DMN 1.x compatible)

Observed facts:

- OMG describes DMN as "a standardized bridge" between business decision
  requirements and the automation of those decisions in processes.
- Hit policies define "how many rules of a decision table can be satisfied and
  which of the satisfied rules are included in the decision table result."
  Single-hit policies (Unique, Any, First) return at most one satisfied rule;
  multi-hit policies (Rule Order, Collect) can return several. Under Unique,
  "if more than one rule is satisfied, the Unique hit policy is violated."
  Collect supports aggregators (e.g. sum).
- A First hit policy returns the output of the **first** rule that matches:
  rule order in the document carries meaning.

Design judgments:

- A decision table is workflow-free at its core (rows are unordered
  constraints) **except** for `First` and `Rule Order` hit policies, where row
  position carries meaning. That is exactly the boundary this experiment cares
  about: DTL therefore supports only Unique, Priority, and Collect, and
  rejects First and Rule Order by design.
- Static overlap checking is feasible for enumerated inputs (cells are either a
  value or the `-` wildcard), so Unique-policy violations are detectable at
  validation time, not just at evaluation time. Judgment, derived from the
  semantics above.

Confidence: high.

## 5. Kubernetes and HCL desired-state resources

URLs (fetched 2026-09-27, HTTP 200):

- https://kubernetes.io/docs/concepts/architecture/controller/
- https://kubernetes.io/docs/concepts/overview/kubernetes-api/
- https://developer.hashicorp.com/terraform/language

Observed facts:

- Kubernetes controllers are "control loops that watch the state of your
  cluster, then make or request changes where needed"; the docs use a
  thermostat analogy where a controller moves the **current state** toward the
  **desired state**. The document declares desired state; reconciliation is
  performed by an external loop.
- Custom resources let you "declaratively define how the API server should
  provide your chosen resource API."
- The Terraform docs describe its configuration language as "declarative,
  describing an intended goal rather than the steps to reach that goal," and
  state that "the ordering of blocks and the files they are organized into are
  generally not significant; Terraform only considers implicit and explicit
  relationships between resources."

Design judgments:

- Desired-state documents answer the workflow question empirically: the most
  widely deployed infrastructure languages contain **no steps at all** — only
  goals plus dependencies, with convergence done by an external controller.
  This is the strongest available evidence that agentic coordination documents
  need not encode order.
- The `spec`/`status` split (declared intent vs observed reality, with drift
  computed, never asserted as a plan) gives DRL its semantic center.

Confidence: high.

## 6. Capability / ontology graphs (RDF, SHACL)

URLs (fetched 2026-09-27, HTTP 200):

- https://www.w3.org/TR/rdf11-concepts/
- https://www.w3.org/TR/shacl/

Observed facts:

- RDF graphs are sets of triples whose elements may be IRIs, blank nodes, or
  datatyped literals; any RDF graph can be represented as a directed labeled
  graph.
- SHACL defines **shapes** with constraint components (e.g. `sh:closed`,
  `sh:minCount`, node-kind constraints), **targets** selecting which nodes a
  shape applies to, and a **validation report** structure with `sh:conforms`
  and `sh:result` entries carrying focus nodes and severity levels.

Design judgments:

- A typed agent/capability graph (ANL, the baseline of this experiment) is a
  small capability ontology: nodes with types, typed edges, and rules about
  edge shapes. SHACL's validation-report shape (list of violations with focus
  nodes and severities) is the practical model for this harness's error
  reporting: every rejection is a list of located, sorted error strings.
- SHACL shows constraints and data live in separate documents (shapes graph vs
  data graph); this experiment's languages instead close each language over
  its own document to keep single-file portability. Trade-off, judgment.

Confidence: high.

---

## How the findings constrain the six languages

| Research topic | Language in this experiment | What was taken | What was rejected |
|---|---|---|---|
| OpenAPI / JSON Schema | SCL (contract language) | `x-` extension objects; assertion vs annotation split | runtime/endpoint vocabulary (not needed) |
| W3C PROV-DM | PVL (provenance language) | entity/activity/agent + generation/usage/derivation/attribution/delegation subset | PROV's full extended structures; RDF syntax |
| OPA / Rego | PDL (policy language) | unordered rules, assertions on data, conflict = error, one default rule | Rego's expression power (only structured conditions) |
| DMN | DTL (decision tables) | Unique/Priority/Collect hit policies, `-` wildcard cells, annotations | First and Rule Order hit policies (row order carries meaning) |
| Kubernetes / HCL | DRL (desired-state resources) | desired/observed split, computed drift, depends_on DAG, labels/annotations | imperative apply steps, controllers in-document |
| RDF / SHACL | ANL baseline + this harness | typed graph with per-relation structural rules (from 008); SHACL-style located validation errors | shapes/data split; open-world semantics |

Design judgment, marked as such: the mapping above is Vibe's selection, not a
mechanical consequence of the sources. The alternatives (e.g. taking SHACL
shapes as a seventh language, or PROV-N text syntax) were rejected to keep the
matrix at exactly six languages with distinct semantic centers.

## Unverified / not pursued

- Camunda's own docs (docs.camunda.org) were unreachable from this environment
  on 2026-09-27 (connection refused); the CIB seven mirror of the same DMN
  engine documentation was used instead.
- The exact wording of Rego's `default` keyword semantics was taken from the
  fetched OPA policy-language page plus a search snippet; the Styra error page
  was not opened.
- No claims are made about production adoption rates, parser performance, or
  real-world incident tooling integration of any candidate language. No source
  was read that measures agent use of such languages; that is exactly what the
  scorecard sub-experiment does **not** claim to measure.
