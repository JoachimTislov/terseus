# Foundation

Terseus explores how AI can help people construct and evolve abstractions in
large systems. It is not an attempt to enclose the design space in a new
programming language or to make one generated implementation authoritative.

## Research position

Important domain knowledge is usually split between source code, documents,
tickets, tests, operational practice, and people. A standard programming
language can implement part of that knowledge, but it is not a sufficient
place to preserve concepts, constraints, alternatives, rationale, and
relationships across a changing system.

This project therefore investigates an open representation layer:

- domain concepts, relationships, constraints, examples, decisions, and
  unresolved alternatives remain expressible independently of one target
  language;
- implementations, APIs, tests, documentation, and operational artifacts are
  projections that can be generated, inspected, replaced, and compared;
- AI proposes connections, transformations, and abstractions, while people
  retain authority over important decisions;
- every useful proposal must remain traceable to its evidence and claims.

The goal is not merely fewer tokens. A successful abstraction makes a large
system easier to understand, verify, change, and coordinate without losing
meaning.

## Experiment contract

Every experiment should preserve:

1. the domain inputs and available knowledge;
2. the intermediate representation being tested;
3. generated and hand-written projections;
4. links between domain claims and projections;
5. human decisions, including rejected or unresolved proposals;
6. evidence about correctness, clarity, adaptability, and change effort.

Experiments must state what they do not establish. AI output is a proposal,
not proof. Whenever possible, the core path must run without an API key and
the experiment must include at least one meaningful change after initial
construction.

`experiments/001-domainkit` is retained as a narrow calibration point for
typed contracts and multi-target synthesis. It is not the prescribed
architecture for the broader research direction.
