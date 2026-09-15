# Initial paths

These paths are deliberately isolated. Each asks a different question and
may produce a different representation. A result in one path must not be
treated as evidence for the others.

## Path A — domain knowledge as an open record

**Question:** Can concepts, relationships, constraints, examples, decisions,
and unresolved alternatives be represented without making a programming
language the source of truth?

**Smallest useful study:** Take one modest domain and write its knowledge as
an inspectable record containing typed claims, prose context, examples,
references, and alternatives. Ask independent reviewers to reconstruct the
domain and identify missing meaning.

**Evidence:** reconstruction accuracy, disagreement visibility, ease of
editing, and whether the record remains useful when implementation choices
change.

**Not testing:** code generation, AI quality, or whether the representation
should become a standard language.

**External references:** OMG's [Decision Model and
Notation](https://www.omg.org/spec/DMN/) demonstrates a portable decision
model with notation and an executable expression layer. W3C's
[PROV-O overview](https://www.w3.org/TR/prov-overview/) provides a model for
describing entities, activities, and agents involved in producing artifacts.
Both are precedents, not dependencies or proposed formats for Terseus.

## Path B — projections and traceability

**Question:** Can several implementation artifacts be projections of domain
claims while remaining inspectable, replaceable, and traceable?

**Smallest useful study:** From the same fixed domain record, create two
different projections (for example an API contract and a test/documentation
set). Link each meaningful output to the claims it implements, then make one
domain change and inspect the impact.

**Evidence:** coverage of claims, stale-link detection, impact precision,
reviewer ability to explain changes, and effort to replace one projection.

**Not testing:** whether one target language is better, or whether generated
code is more concise.

**External references:** Martin Fowler's
[Language Workbench](https://martinfowler.com/articles/languageWorkbench.html)
describes domain-specific languages and tooling as a family of projection
techniques. The [Protocol Buffers overview](https://protobuf.dev/overview/)
is a production precedent for one schema producing artifacts in multiple
languages with explicit evolution rules.

## Path C — AI as a bounded change proposer

**Question:** Can AI propose useful abstractions and changes while keeping
human authority, provenance, and failure visible?

**Smallest useful study:** Give an AI the domain record, existing projections,
and one requested change. Require a structured proposal containing affected
claims, proposed edits, projected artifacts, uncertainty, and evidence. A
human accepts, edits, or rejects it.

**Evidence:** useful proposal rate, unsupported-claim rate, review time,
change-resilience, and whether rejected proposals remain understandable.

**Not testing:** autonomous system ownership, model capability in general, or
formal correctness without an independent verifier.

**External references:** [DSPy](https://arxiv.org/abs/2310.03714) is a
precedent for declarative language-model modules compiled into pipelines.
[Sketch](https://people.csail.mit.edu/asolar/SynthesisCourse/Sketch.pdf)
and [Rosette](https://plt.cs.northwestern.edu/pkg-build/doc/rosette-guide/)
are precedents for bounded synthesis and verification. Terseus uses these
references to separate proposal generation from acceptance, not to prescribe
their implementations.

## Isolation rule

Each path gets its own inputs, artifacts, evaluation, and conclusion. Do not
merge a format from Path A into Path B, or an AI result from Path C into a
claim about representation quality, without a new experiment that tests the
combination directly.
