# Recursive abstraction construction benchmark

This is a design-and-construction task, not a request for general advice.
Do not modify repository files, use network access, or claim that the design
has been implemented or verified. Produce a self-contained artifact that a
human engineer could build upon.

## System to declare

Design a reusable declaration for a multi-tenant notification platform with
these core parts:

- tenants have users and notification preferences;
- applications emit typed events;
- policies select channels and templates from events and preferences;
- deliveries execute through providers with retries and idempotency;
- an audit stream records every decision and delivery outcome.

The system must support a new tenant, a new channel provider, and a composite
workflow in which a failed delivery triggers an escalation notification. A
composite workflow is itself a reusable component and may contain nested
components recursively.

## Required output

Return exactly these sections:

1. `System boundary and invariants`
2. `Recursive declaration model`
3. `Reusable component library`
4. `Worked declaration`
5. `Expansion and verification`
6. `Compression accounting`
7. `Change test`
8. `Failure modes and unresolved decisions`
9. `Build-ready next slice`

The artifact must include all of the following:

- a minimal typed schema for `Component`, `Port`, `Input`, `Output`,
  `Constraint`, `Evidence`, and nested composition;
- a grammar or canonical JSON/YAML shape for declaring a component;
- at least five reusable components, with at least two being recursive or
  compositional;
- one complete worked declaration for the notification platform, including
  tenant, event, policy, delivery, retry, escalation, and audit behavior;
- a deterministic expansion from the compact declaration into an explicit
  implementation plan or pseudocode;
- independent checks for type compatibility, idempotency, retry bounds,
  tenant isolation, audit completeness, and recursive termination;
- a baseline verbose representation and a compact representation of the same
  behavior, with token/line counts and a plainly stated compression ratio;
- a change test adding a new provider and changing escalation policy, with
  affected components and stale evidence identified;
- at least three deliberately rejected abstractions and why they are unsafe;
- a concrete next implementation slice with files, interfaces, tests, and
  acceptance criteria.

## Quality constraints

Prefer explicit semantics over clever syntax. Distinguish declarations from
generated projections. Every non-obvious abstraction must state its contract,
inputs, outputs, invariants, and evidence. Mark any invented syntax as
illustrative. Do not use a language model as an implicit verifier. Keep the
answer under 3,000 words, and include a final fenced JSON object with keys
`components`, `recursive_rules`, `invariants`, `baseline`, `compact`,
`compression`, `change_test`, `rejections`, and `next_slice`.
