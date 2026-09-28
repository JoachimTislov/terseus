# Approach map

This map expands the research space without selecting a single architecture.
Each approach changes what is considered the primary representation, what AI
does, and how results should be evaluated. The approaches are candidates for
separate experiments; none is evidence for another.

## 1. Model-driven multi-view engineering

**Core idea:** maintain platform-independent models and derive
platform-specific models, code, schemas, and tests through explicit
transformations.

**Useful question:** Does an explicit transformation chain make changes more
understandable and controllable than direct code generation?

**Risks:** model maintenance cost, transformation drift, and forcing domains
into a rigid modeling notation.

**Evaluation emphasis:** semantic fidelity, view consistency, transformation
reversibility, change impact precision, and maintenance effort.

**Sources:** [OMG Model Driven
Architecture](https://www.omg.org/mda/), [Martin Fowler's Language
Workbench](https://martinfowler.com/articles/languageWorkbench.html).

## 2. Provenance-first representations

**Core idea:** treat claims, artifacts, agents, activities, and derivations as
first-class data so every projection and AI proposal has an evidence trail.

**Useful question:** Does provenance improve review and recovery when an
abstraction or generated artifact becomes questionable?

**Risks:** metadata overhead, false confidence in complete-looking graphs,
and difficulty representing informal human knowledge.

**Evaluation emphasis:** trace completeness, provenance accuracy, audit time,
recovery from rejected changes, and ability to identify unsupported claims.

**Source:** [W3C PROV overview](https://www.w3.org/TR/prov-overview/).

## 3. Ontology and knowledge-graph engineering

**Core idea:** extract and maintain concepts and relations from code,
documentation, issues, and operational records in a graph constrained by an
ontology or vocabulary.

**Useful question:** Does a graph expose cross-cutting domain knowledge that
is invisible in language-bound modules and documents?

**Risks:** hallucinated relations, ontology ossification, incomplete
extraction, and expensive expert validation.

**Evaluation emphasis:** precision and recall of claims, consistency,
coverage across artifact types, update latency, and expert correction effort.

**Sources:** [Accelerating Knowledge Graph and Ontology Engineering with
LLMs](https://arxiv.org/abs/2411.09601), [Ontology-guided Knowledge Graph
Construction from Maintenance Short Texts](https://aclanthology.org/2024.kallm-1.8/),
and [Knowledge Graph Construction: Current State and
Challenges](https://doi.org/10.3390/info15080509).

## 4. Inductive library and abstraction learning

**Core idea:** discover reusable functions, concepts, or a small domain
library from solved examples rather than requiring every abstraction to be
declared first.

**Useful question:** Can discovered abstractions reduce repeated work while
remaining interpretable, testable, and easy to reject?

**Risks:** overfitting, opaque or trivial abstractions, benchmark leakage,
and optimizing compression instead of usefulness.

**Evaluation emphasis:** reuse on held-out tasks, compression adjusted for
comprehension, abstraction stability, editability, and regression rate.

**Sources:** [DreamCoder](https://github.com/ellisk42/dreamcoder),
[LILO](https://arxiv.org/abs/2310.19791), and [Metagol](https://github.com/metagol/metagol).

## 5. Programming by example and inductive synthesis

**Core idea:** specify behavior through examples and constraints; infer an
implementation or transformation from those examples.

**Useful question:** Are examples a more accessible and less language-bound
way to communicate domain behavior than prose or signatures alone?

**Risks:** examples under-specify edge cases, inferred behavior can be
surprising, and examples may encode accidental rather than intended rules.

**Evaluation emphasis:** generalization to hidden cases, counterexample
quality, example authoring effort, semantic coverage, and ability to revise
the inferred rule.

**Sources:** [Programming by Examples](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/12/pbe16.pdf)
and the [PROSE research overview](https://www.microsoft.com/en-us/research/project/prose/).

## 6. Formal synthesis and proof-carrying change

**Core idea:** combine a bounded implementation space with executable
specifications, solvers, or proof obligations; AI may propose candidates but
an independent checker decides acceptance.

**Useful question:** Which parts of an abstraction can be made mechanically
safe without making domain expression too costly?

**Risks:** specification burden, solver limits, weak specifications that
prove the wrong thing, and poor support for informal domain knowledge.

**Evaluation emphasis:** invariant coverage, proof or counterexample quality,
false acceptance rate, specification effort, and change locality.

**Sources:** [Sketch](https://people.csail.mit.edu/asolar/SynthesisCourse/Sketch.pdf),
[Rosette](https://plt.cs.northwestern.edu/pkg-build/doc/rosette-guide/),
and [Neurosymbolic Programming](https://doi.org/10.1561/2500000049).

## 7. Repository-scale requirements and change-impact analysis

**Core idea:** connect requirements, architecture, code, tests, and
documentation to identify affected artifacts and propose coordinated
changes.

**Useful question:** Can AI reduce the cost of changing a large system by
finding semantic impact rather than only textual references?

**Risks:** plausible but unsupported links, stale context, missed runtime
coupling, and difficulty evaluating impact completeness.

**Evaluation emphasis:** impact precision/recall, missed dependency severity,
review time, stale-link detection, and regression outcomes.

**Sources:** [LLMs for Requirements Engineering: A Systematic Literature
Review](https://arxiv.org/abs/2509.11446), [Challenges in applying LLMs to
requirements engineering tasks](https://doi.org/10.1017/S2053470124000088),
and [Awesome LLM for Software Engineering](https://github.com/iSEngLab/AwesomeLLM4SE).

## 8. Structured AI workflow compilation

**Core idea:** represent AI work as typed, declarative modules and compile or
optimize the workflow while keeping the surrounding system explicit.

**Useful question:** Does a declarative AI workflow produce more repeatable
and reviewable abstraction work than free-form agent sessions?

**Risks:** optimizing prompts instead of domain meaning, hidden runtime model
dependence, and benchmarks that reward local task success over system quality.

**Evaluation emphasis:** repeatability, calibration, unsupported-claim rate,
human review effort, provider portability, and long-term drift.

**Source:** [DSPy: Compiling Declarative Language Model Calls into
Self-Improving Pipelines](https://arxiv.org/abs/2310.03714).

## 9. Confidence-gated semantic language development

**Core idea:** keep the domain language's grammar, type system, execution
semantics, and side effects deterministic, while using Jev as a bounded
semantic decision primitive for the parts that depend on intent, context, or
domain judgment. A parsed AST and its supporting evidence become Jev's
structured state; independent `Choice`, `Score`, and `Noul` questions produce
typed interpretations that ordinary code combines into a validated
intermediate representation.

This is not a proposal to have a model generate the language or executable
code. It is a hybrid language workbench: parsing and exact constraints reject
invalid programs, while Jev supplies explicit, inspectable judgments such as
intent classification, ambiguity resolution, eligibility, severity, or
mapping a phrase to a closed domain vocabulary. Jev's probabilities and
confidence are preserved as part of the semantic result rather than reduced
to an unexplained yes/no.

**Useful question:** Does placing calibrated, atomic semantic judgments behind
a stable DSL boundary make natural-language domain expressions easier to
author and evolve without weakening traceability or execution safety?

**Proposed workflow:**

1. Define a small, versioned domain vocabulary and grammar. Do not delegate
   lexical analysis, parsing, type checking, authorization, or arithmetic to
   Jev.
2. Parse source into a typed AST and collect the relevant facts, source spans,
   provenance, and unresolved alternatives into structured state.
3. Fan out narrow Jev questions in one request. Each question should address
   one dimension and use a closed `Choice`, ordered `Score`, or binary `Noul`
   contract.
4. Combine answers with ordinary, version-controlled code into a semantic IR.
   Keep coefficients, thresholds, precedence, and side effects in the DSL
   implementation, not in model instructions.
5. Gate behavior by risk: high-confidence interpretations may proceed,
   medium-confidence ones request confirmation or more evidence, and
   low-confidence ones are rejected or sent to human review.
6. Record the model version, question schema, state, probabilities,
   confidence, selected interpretation, and human overrides so a decision can
   be replayed and audited.

**Example scope:** a policy DSL may parse `approve refund when failure is
severe` deterministically, then ask Jev separately to score incident severity,
classify refund eligibility, and detect fraud indicators. The runtime combines
those results with explicit policy thresholds. A low-confidence severity score
must not silently become an approval.

**Risks:** calibrated confidence may still be unsuitable for an unmeasured
domain; a closed vocabulary can encode the wrong ontology; question and
rubric changes can alter language meaning; model drift can change behavior;
and semantic judgments may be mistaken for proof. Network availability,
privacy, latency, and provider dependence also become language-runtime
concerns.

**Evaluation emphasis:** semantic fidelity against expert-reviewed cases,
confidence calibration and selective accuracy, ambiguity and abstention
quality, regression behavior across question/model versions, trace
completeness, authoring and review effort, latency/cost, and the safety of
generated side effects. Compare deterministic rules alone, a general LLM
workflow, and Jev-backed atomic decisions on the same domain tasks. At least
one held-out change should test whether the language remains understandable
and adaptable after its vocabulary or rubric evolves.

**Sources:** [TypeSafe introduction](https://docs.typesafe.ai/introduction),
[TypeSafe confidence](https://docs.typesafe.ai/confidence), [TypeSafe
patterns](https://docs.typesafe.ai/patterns), and [Introducing System One
Models & Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev).

## Selection rule

Do not rank approaches by literature popularity or token reduction. Select a
path for a concrete system slice, hold the task and evaluation constant, and
report both the aggregate score and blocking failures in semantic fidelity or
correctness.
