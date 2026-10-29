# Discovery and evidence

Use this reference before creating a new page or when an existing page rests on unclear assumptions.

## Readiness test

A reference-quality page requires all six conditions:

1. **Bounded subject:** one concept, system, flow, state space, place, comparison, or production concern can be named precisely.
2. **Reader and purpose:** the intended audience and the understanding or decision the page should support are known.
3. **Structural material:** the important entities and at least one meaningful relationship, rule, sequence, or spatial fact are supported.
4. **Concrete instance:** a real or user-approved example exercises the model.
5. **Boundary:** exclusions and material that belongs on another page are understood.
6. **Truth status:** confirmed facts, supplied decisions, observations, assumptions, and unknowns can be distinguished.

If conditions 1–3 are missing, stay in discovery. If 4–6 are incomplete, offer an exploration only when useful and label it clearly. Do not use polish to disguise missing design information.

## Autonomous mode (no human to ask)
Often you run inside a harness, a background task or a one-shot prompt with nobody to answer. Then do not stop at questions:
1. **Mine the project first:** list and read `README`, `STATUS`, plan/research/workstream folders, fact files, prior pages. Extract nouns, verbs, quantities, dates and decisions with their file paths.
2. Build an **evidence table** (`claim | value | source file | label`) using the labels below, and keep it beside the page (`evidence.md` or in the handoff). Numbers come from sources; a missing number is `Assumed` (dashed on the page, flagged) or left out, never invented to fill a box.
3. Convert each blocking question into an **Open** item placed near the element it affects, choose the most defensible reading, and deliver an **exploration** page. Promote to **reference** only when readiness conditions 1-6 hold.
4. Report the open questions and assumptions first in the handoff so a human can redirect in one reply.
5. **If every number is assumed** (no source exists), say so once in the masthead status ("exploration: all values assumed") and the footer, and reserve dashed outlines for what differs from that default; otherwise every box is dashed and the dash stops meaning anything. Show numbers as ranges or round figures, and keep the evidence table (`A1...An`) so a human can replace them one by one.

## Title test and page contract
Write the title and the contract sentence before drawing: *This page helps [audience] understand or decide [specific thing] by showing [relationships].* Librande: if you cannot fill in the title, stop [23:25]. A title that names a topic ("Production") fails; one that states the job ("From order to delivery: where time and cost accumulate") passes.

## Adaptive question bank

Inspect available material first. Ask only unresolved questions whose answers would change the information model or visual grammar. Group tightly related questions; do not administer this as a generic form.

### Contract

- What single thing should this page explain?
- Who will use it, and what should they understand, decide, implement, or discuss afterward?
- Is this an exploratory thinking surface or a reference the team may rely on?

### Evidence

- Which existing documents, behavior, requirements, research, or decisions are authoritative?
- Which parts are confirmed, proposed, disputed, or unknown?
- What concrete example best represents normal use?

### Model

- What people, objects, resources, screens, modules, or places participate?
- What does each one do, exchange, contain, or affect?
- What triggers the system, and what result ends or repeats it?
- What changes over time or between states?
- Which quantities, timing rules, permissions, or constraints matter?
- What feedback tells an actor what happened?

### Exceptions

- What happens when the normal path fails, pauses, reverses, or is skipped?
- Which edge case exposes a weakness or important tradeoff?
- What must never happen?

### Boundary and medium

- What belongs on a different page or in supporting detail?
- Will the page be printed, displayed on a wall, reviewed on screen, or edited in a workshop?
- Which source format must remain editable, and what visual language or assets already exist?

## Evidence labels

Use provenance during modeling even if the final page does not show every label:

- **Observed:** demonstrated in a working product, research, or measured behavior.
- **Specified:** explicitly required in an authoritative source.
- **Decided:** confirmed by the responsible person or team.
- **Proposed:** a candidate awaiting approval.
- **Assumed:** necessary to continue but not yet supported.
- **Open:** unresolved and intentionally left undecided.

Never convert `Proposed`, `Assumed`, or `Open` material into neutral-looking reference content.

## Discovery outcome

When the page is not ready, return:

- the proposed page subject and purpose;
- what the available evidence already establishes;
- the smallest set of blocking questions;
- the likely visual grammar, marked tentative;
- which answers would make the page ready.

This is productive design work. Do not render a decorative placeholder merely to appear finished.
