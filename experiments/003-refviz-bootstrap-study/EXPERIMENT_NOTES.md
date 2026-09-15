# Experiment 003: bootstrapping RefViz

## Selected system

This study uses [`RefViz`](https://github.com/JoachimTislov/RefViz) as a
pinned submodule at `../003-refviz-bootstrap`. RefViz is complementary to
AI-VCS: it exposes code structure and references, making it suitable for
testing whether domain representations improve understanding and change
impact in an existing Go system.

The submodule is independently versioned. This study does not edit its source.

## Common benchmark

Apply the same maintenance task to each isolated path: identify the affected
concepts and references for one small RefViz feature, propose a change, and
apply one follow-up requirement change. Use the same repository snapshot,
task statement, time budget, and evaluator instructions.

Score each criterion from 0 to 4:

| Criterion | 0 | 2 | 4 |
|---|---|---|---|
| Semantic fidelity | misses core meaning | captures main intent with gaps | preserves intent, constraints, and alternatives |
| Flexibility | hard-coded to one case | handles expected variation | supports novel requirements without redesign |
| Change resilience | widespread unexplained breakage | impact is partly identified | precise impact and controlled update |
| Correctness | invalid or unverified output | tests pass but gaps remain | independent checks cover stated invariants |
| Maintainability | increases hidden coupling | understandable with effort | reduces cognitive and change burden |
| Traceability | no claim/evidence links | partial links | every material output is explainable |
| Reviewability | opaque or excessive review | review is feasible | decisions and uncertainty are immediately clear |
| Reproducibility | cannot repeat result | repeatable with setup | deterministic artifacts and recorded inputs |

Report the total out of 32, each dimension separately, elapsed human review
time, edits after the initial proposal, and unsupported claims. A high total
does not override a zero in correctness or semantic fidelity; report those as
blocking failures.

## Isolated paths

- **Path A:** an open domain record of RefViz concepts, references,
  constraints, examples, and unresolved alternatives; no AI proposal and no
  code generation.
- **Path B:** two traceable projections from the fixed record: a change-impact
  map and a maintenance specification; no AI proposal generation.
- **Path C:** an AI-generated structured change proposal with affected claims,
  expected references, uncertainty, and validation plan; human acceptance is
  mandatory.

Store each path's inputs, outputs, score sheet, rejected proposals, and
conclusion in its own directory. Do not combine conclusions until all paths
use the same benchmark and independent review.

## External references

- [RefViz](https://github.com/JoachimTislov/RefViz) — selected system and
  reference-graph context.
- [W3C PROV](https://www.w3.org/TR/prov-overview/) — provenance vocabulary.
- [OMG DMN](https://www.omg.org/spec/DMN/) — portable decision
  representations.
- [Language Workbench](https://martinfowler.com/articles/languageWorkbench.html)
  — domain-language and projection practice.
- [Protocol Buffers](https://protobuf.dev/overview/) — evolution and
  multi-language projection precedent.
- [DSPy](https://arxiv.org/abs/2310.03714) — declarative AI pipeline
  precedent.
- [Sketch](https://people.csail.mit.edu/asolar/SynthesisCourse/Sketch.pdf)
  and [Rosette](https://plt.cs.northwestern.edu/pkg-build/doc/rosette-guide/)
  — bounded synthesis and verification precedents.

These sources inform the benchmark vocabulary and separations; none defines
the result in advance.
