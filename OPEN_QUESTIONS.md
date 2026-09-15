# Open Questions

A running list. Nothing here is answered by this repo -- each is a
decision some future design will have to make explicitly, and should be
able to point back to which prior-art entry informed it.

1. **Hole-filling vs. interpretation.** Where exactly is the line between
   "the model fills a bounded, pre-typed gap" and "the model interprets
   under-specified intent"? Every controlled-natural-language project
   claims to do the former and arguably drifts into the latter as soon as
   its vocabulary gets expressive enough to be useful (see THEORY.md,
   Axis 1).

2. **Unit of abstraction.** Is the right granularity a single keyword
   (a verb bound to a contract), a whole module, or a vertical slice
   spanning multiple layers (schema + logic + interface)? Prior art picks
   very different points on this: Robot Framework keywords are small and
   composable; JHipster's JDL entities are closer to whole modules.

3. **Top-down vs. bottom-up abstraction discovery.** Should a human
   declare "this deserves a keyword" ahead of time, or should the system
   mine recurring patterns from an existing corpus (possibly across many
   unrelated projects) and propose candidates? No surveyed system does
   the latter well at the level of verified, reusable abstractions --
   worth confirming this is still true before assuming it's solved.

4. **Is token count the right metric at all?** See THEORY.md's "open
   measurement question." A metric that rewards density over
   traceability could optimize for the wrong thing entirely.

5. **Ossification and versioning.** Once a keyword is standardized and
   consumed by multiple projects, how does its contract change without
   breaking everyone downstream? Every standard (SQL, HTTP, protobuf's
   field-number discipline) has had to solve this explicitly -- protobuf's
   answer (numbered fields, additive-only evolution) is one concrete
   precedent worth studying directly rather than re-deriving from
   scratch.

6. **Contract-language expressiveness ceiling.** How expressive does a
   contract language need to be before it's useful for real domains with
   real invariants (balances, multi-field constraints, state machines
   with more than two states) -- and at what point does the contract
   language itself become a second thing to learn, undermining the
   "fewer words" goal it was meant to serve?

7. **Should verification deliberately span multiple type disciplines?**
   Given the empirical finding in THEORY.md (a statically-typed target
   caught a defect a dynamically-typed one missed), is it worth treating
   "verify against at least one statically-typed target" as a design
   principle regardless of what's actually being shipped, purely as a
   contract sanity check? Or was this incidental to one narrow example
   and not worth generalizing?

8. **Who owns a keyword's meaning once it exists?** Standardizing
   `complete` or `checkout` within a domain schema is a form of
   governance, not just engineering. Business-rules and CNL projects
   (SBVR in particular) ran into organizational versions of this before
   they ran into technical ones -- worth reading their retrospectives for
   the failure mode, not just the technical spec.
