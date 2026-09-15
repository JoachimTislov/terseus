# Prior Art

Organized by which piece of the problem each category addresses. None of
these were built with this repo's proposition in mind -- each solves a
narrower, adjacent problem well, which is exactly why they're useful
reference points rather than competitors.

## 1. Concise keywords bound to hand-written implementation (no AI)

**Robot Framework** -- test cases are written as tabular "keywords"
(action words); each keyword is backed by library code written in
Python, Java, or .NET. This is the clearest production precedent for
"a small, concise vocabulary layer sitting on top of a real
implementation layer, written the traditional way."
https://robotframework.org/ ; overview of the keyword-driven approach:
https://www.apriorit.com/qa-blog/569-keyword-driven-testing-robot-framework

**Cucumber / Gherkin** -- `Given/When/Then` steps in natural-language-like
syntax map to hand-written step definitions in the target language. Step
definitions are the binding layer; Gherkin is the concise vocabulary.
https://cucumber.io/docs/gherkin/

## 2. Schema-first, deterministic code generation across a chosen stack

**JHipster / JDL (JHipster Domain Language)** -- a compact
entity-and-relationship definition language that generates a complete,
working application (Spring Boot backend, a chosen frontend framework,
database migrations) across a fixed, developer-selected set of
frameworks. The closest full-pipeline analog to a "concise domain
language that outputs real 3GL apps," minus any AI/synthesis step --
everything is deterministic templating.
https://www.jhipster.tech/jdl/ ; walkthrough:
https://medium.com/jhipster/create-full-microservice-stack-using-jhipster-domain-language-under-30-minutes-ecc6e7fc3f77

**Ent (entgo.io)** -- a Go entity framework where you declare a schema
(types + relations) as code, and it generates strongly-typed,
graph-aware Go code (queries, migrations) mechanically. Types-as-source-
of-truth, no synthesis involved.
https://entgo.io/

**Prisma** -- a declarative schema (`schema.prisma`) describing types and
relations, from which a type-safe client is generated for use across
several languages/ecosystems. Same "types are structure, generate
mechanically" principle as Ent, aimed at a different ecosystem.
https://www.prisma.io/docs

**Protocol Buffers / gRPC** -- an Interface Definition Language (`.proto`)
is the single source of truth; `protoc` generates client and server code
in many languages (Go, Python, Java, C++, Rust, TypeScript, and others)
from one definition. The strongest existing precedent for "one
declarative source, many idiomatic target-language outputs, generated
independently per target rather than translated between targets."
Field-number-based schema evolution is also the most battle-tested
answer anywhere in this list to the versioning/ossification question in
OPEN_QUESTIONS.md #5.
https://protobuf.dev/overview/ ; https://grpc.io/docs/what-is-grpc/introduction/

## 3. Declarative infrastructure with pluggable, hand-written providers

**Terraform / HCL** -- HCL is a declarative configuration language;
`resource` blocks describe desired state, and the actual work of
reaching that state is implemented by provider plugins, most of them
written in Go by HashiCorp or third parties. This is the closest
real-world analog to a "bindings" layer: the declarative language never
implements behavior itself, it only references a hand-written provider
that does.
https://developer.hashicorp.com/terraform/language

**Kubernetes Custom Resource Definitions (CRDs) + controllers** --
CRDs let you declare a new, domain-specific YAML vocabulary; a
hand-written controller (typically Go) watches for that vocabulary and
reconciles real infrastructure to match. Same shape as Terraform's
provider model, applied to a running system instead of a one-time
provisioning step.
https://kubernetes.io/docs/concepts/extend-kubernetes/api-extension/custom-resources/

**Ansible + modules** -- YAML playbooks are the declarative vocabulary;
modules (mostly Python) are the hand-written implementation layer each
YAML task binds to.
https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html

## 4. Cross-language / cross-platform compilation

**Haxe** -- a strictly-typed source language whose compiler targets many
other *languages* (JavaScript, C++, C#, Java/JVM, Python, Lua, PHP), not
just machine platforms. Haxe's own documentation is explicit that this
requires keeping the language fairly minimal to accommodate the target
set, and still needs per-target escape hatches when the abstraction
leaks -- direct evidence for the "any language" ambition's actual cost.
https://haxe.org/documentation/introduction/

**LLVM IR** and **WebAssembly** -- both solve the *platform* half of
"any platform and language" by compiling to one shared low-level
representation and letting each backend/runtime handle final lowering.
Neither attempts cross-*language* source generation the way Haxe or
protobuf do -- worth keeping platform-targeting and language-targeting
as genuinely separate problems (see THEORY.md's related note from an
earlier discussion in this project's history).
https://llvm.org/docs/LangRef.html ; https://webassembly.org/

## 5. Language workbenches / language-oriented programming

**Martin Fowler's "Language Workbench" concept** -- names the general
pattern of building tooling (editors, projections, compilers) around a
custom DSL as a first-class discipline, rather than an ad hoc
side-project. Useful as the umbrella term for everything in categories
2-4 above.
https://martinfowler.com/bliki/LanguageWorkbench.html ;
https://martinfowler.com/articles/languageWorkbench.html

**JetBrains MPS** and **Xtext** -- mature, general-purpose tools for
building exactly this kind of custom DSL + generator, independent of any
one domain. Worth studying their extension/versioning mechanisms
directly rather than re-deriving them.

**Racket's `#lang`** -- treats "define a new language with its own
syntax, compiled down to Racket" as a core, first-class language
feature rather than an external tool -- one of the few examples where
creating a new small language is a routine, cheap operation instead of a
major undertaking.

## 6. Controlled natural language (the "subset of human words" lineage)

**Basic English** (1930s), **COBOL**'s original "English-like syntax so
business people can read/write it" pitch, **SBVR** (Semantics of
Business Vocabulary and Rules, an OMG standard), and **Attempto
Controlled English (ACE)** all attempted some version of restricting
natural language into a formally unambiguous subset. A 2015 survey
traces this as a continuous, decades-long research thread across
industry, government, and academia, still without a settled answer on
whether a genuinely general-purpose controlled language is viable at
scale.

**Dijkstra, EWD667 ("On the foolishness of 'natural language
programming'")** -- the standing structural objection: formal
strictness isn't friction to be removed from the "real" content of a
program, it's what makes it possible to rule out nonsense. Worth reading
as a live counter-argument, not a historical curiosity, whenever a
design leans on "closer to natural language" as a selling point.

## 7. LLM calls embedded into a language's execution/constraint semantics

**LMQL** (Beurer-Kellner, Fischer, Vechev; PLDI 2023) -- "Language Model
Programming": constraints declared in the language compile into
token-level generation control, rather than being checked after the
fact on returned text. https://arxiv.org/abs/2212.06094

**DSPy** (Khattab et al.) -- treats LM calls as typed, declarative
modules in a program graph, optimized by a compiler rather than
hand-tuned as prompt strings. Important distinction from this project's
scope: DSPy's compiled output still calls an LLM every time the program
runs; it optimizes a pipeline that keeps the model in the runtime path.
https://arxiv.org/abs/2310.03714

**Constrained/structured decoding engines** -- Outlines, Guidance,
XGrammar, llguidance: libraries that mask invalid tokens during
generation so output is guaranteed to match a grammar or schema, rather
than being validated and retried after the fact. Actively evolving as
of 2026, with meaningful performance differences between engines. This
is a different mechanism from LMQL/DSPy (token-level constraint vs.
program-level typed modules) solving an adjacent problem (guaranteed
syntactic validity vs. guaranteed semantic correctness).
https://github.com/Saibo-creator/Awesome-LLM-Constrained-Decoding is a
maintained index of this space.

## 8. Program synthesis with typed holes

**Sketch** (Solar-Lezama) and **Rosette** -- write a program with
explicit "holes"; a solver fills them against a specification. The
direct intellectual ancestor of "human writes the scaffold, an automated
process fills bounded, verified gaps," predating LLMs by roughly two
decades.

**Neurosymbolic programming** (Chaudhuri, Ellis, Polozov, Singh,
Solar-Lezama, Yue; Foundations and Trends in Programming Languages,
2021) -- the theoretical argument that a language's structural
restrictions make a neural/learned component's contribution trustworthy
and composable, rather than being overhead to eliminate once the
learned component is "good enough." doi.org/10.1561/2500000049

## 9. LLM synthesis gated by formal specification/verification (closest existing work to this project's actual novel core)

**spec2code** (Sevenhuijsen, Etemadi, Nyberg et al.) -- combines LLM
code generation with formal-verification "critics," evaluated on
industrial embedded automotive case studies at Scania; produced
compiling, and in some cases formally verified, code from specifications
alone without iterative backprompting or fine-tuning in its first
feasibility study.

**VeCoGen** -- automates generating formally verified C code with LLMs,
same "synthesize, then prove or reject" shape as a Sketch-style pipeline,
applied to a real verifier instead of property-based testing.

**SpecGen, KBSpec, and related 2025-2026 work** on LLM-driven formal
specification generation (for Java/JML, C/ACSL, and Dafny) consistently
report that getting a model to produce specifications precise enough to
verify against is still an open, actively-researched problem, not a
solved one -- directly relevant to OPEN_QUESTIONS.md #6.

**GitHub Spec Kit** (2026) -- a recent, actively developed toolkit for
spec-driven, agentic development. Close in spirit to "the schema is the
source of truth, an agent fills the gaps," worth a direct look for how
it handles the same territory this project is scoped around.
https://github.com/github/spec-kit

## 10. Low-code/model-driven platforms with a code escape hatch

**Mendix**, **OutSystems** (established enterprise low-code platforms)
and **Amplication** (open-source; define a data model, get a generated
Node.js backend with an escape hatch to hand-written code) all occupy
the "visual/declarative model generates real, editable code" space
commercially. Worth studying their escape-hatch design (how a developer
drops from the generated layer into hand-written code without losing
the ability to regenerate) as a direct precedent for how `bindings`-style
overrides should behave at scale.
