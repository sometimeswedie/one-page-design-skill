# Visual grammars

Select the smallest grammar that makes the subject's important relationships visible. The grammar follows the information model; it is not a house style. Combine at most two primary grammars unless their connection is itself the subject. Once chosen, build it from a recipe in [layout-recipes.md](layout-recipes.md) (swimlane, cycle, value chain, supply chain, factory flow, anatomy, space-time, matrix, composite).

| Relationship to explain | Primary grammar | Useful encodings |
|---|---|---|
| Repeated behavior or value creation | Loop | Circular path, stages, reinforcing or balancing feedback |
| Transformation from input to outcome | Flow | Left-to-right pipeline, branching decisions, labeled arrows |
| Change over time | Timeline or storyboard | Frames, milestones, state snapshots, before/after contrast |
| Components and dependencies | System map | Nodes, bounded groups, directional edges, interface labels |
| Categories against shared dimensions | Matrix | Rows/columns, cells, heat or status marks, highlighted gaps |
| Levels, ownership, or containment | Hierarchy | Nested regions, tree, layers, relative scale |
| Physical or navigational experience | Spatial map | Zones, paths, landmarks, proximity, annotated environment |
| States and transitions | State diagram | Distinct states, triggers, transition conditions, failure paths |
| Composition of an object or interface | Annotated anatomy | Central illustration, callouts, magnified details |
| Competing forces or tradeoffs | Spectrum or tension map | Axes, opposing poles, target zone, examples |

Forms Librande actually used, mapped to grammars: **flowchart** (flow or loop; "do this first if new" [26:14]), **matrix solved top-down** (matrix [33:42]), **storyboard with time marks** (timeline [27:52]), **space + time chart** (Minard/Spore; timeline with a quantity axis [28:38]), **spatial map with expected level/timing** (spatial map [15:02]), **abstract-system page** (system map of atoms [17:44]), **unit/module relationship page** (system map [31:39]), **object with callouts** (annotated anatomy [25:19]).

Do not select a loop merely because behavior repeats, a matrix merely because categories exist, or a storyboard merely because screens exist. Choose the form that exposes the decision-relevant relationship most clearly.

## Anchor, tiers and reading path (the talk's default composition)
- A **central anchor** (product, place, loop, or one key figure) draws people in; callouts and layers reveal around it [24:19], [30:10]. Use it when the subject has an anchor. It is template residue only when the centred object encodes nothing.
- **Three tiers:** tier 1 is readable from across the room (title, anchor, stage heads), tier 2 at arm's length (labels), tier 3 leaning in (annotations, units, sources) [46:15]. Make the tiers visibly different in size; a page with five similar sizes has no hierarchy.
- **Reading path:** eye lands on title and anchor, follows the process order, ends on the exception or the decision. Left-to-right for sequence, top-to-bottom for portrait journeys; lanes and bands align stage columns so several diagrams read as one model.
- **White space is content:** it separates tiers and gives pencil room. Fill it only with something that encodes information.

## Shape test: the diagram's shape is part of the design
Ask of every layout: *does the shape of the space match the shape of the information?* Librande's units in rock-paper-scissors corners allowed three choices; the same units as sliders along edges allowed tunable ranges [32:58]-[33:42]. A radial layout can lie by folding a spectrum like a fan so distant things look adjacent [39:06]. A table with more than two dimensions or a diagram that will not fit is a signal that the model or metaphor is wrong, not that the type should shrink [36:23], [37:42]. Re-shape (axes, sliders, vectors, splitting) before polishing.

## Quantity encodings (put numbers into geometry)
Width = duration or flow volume; height = cost or capacity; thickness of a band = quantity over time (Minard [13:16]); position = order or ownership; colour = category; outline style = evidence status; badge = exception. State the unit and scale on the page. Do not encode a number only in text when geometry can carry it.

## Hybrid patterns

Use a hybrid only when the connection between forms is itself important.

- **Anchor + loop:** A central object or promise surrounded by the repeated experience it creates.
- **Journey + states:** A timeline whose frames show meaningful state changes.
- **Map + flow:** A spatial layout overlaid with movement, information, or resource paths.
- **System map + matrix:** A relationship model paired with a compact coverage or responsibility table.
- **Anatomy + feedback:** An annotated object with a small input-response-feedback loop.

## Visual argument rules

- Give the most important idea the most visual weight.
- Make the natural reading order agree with the process order.
- Use spatial distance to express conceptual distance.
- Use the same shape for the same kind of thing.
- Use color for categories, status, ownership, or flow, not mood alone.
- Label connectors with verbs when the relationship is not self-evident.
- Show examples at the point where they clarify a rule.
- Place uncertainty near the element it affects instead of collecting every caveat in a detached footnote.
- Break visual consistency deliberately when an exception breaks the system rule.
- Show a concrete instance inside or beside the abstraction so the model can be checked.

## Semantic encoding audit

For each prominent visual device, name its meaning:

| Device | Must encode |
|---|---|
| Position | sequence, hierarchy, proximity, ownership, or another stated relationship |
| Size | importance, quantity, duration, capacity, or another stated magnitude |
| Color | category, state, ownership, confidence, or another consistent distinction |
| Shape | entity type, state type, or another recurring role |
| Connector | direction, transfer, dependency, causality, transition, or another labeled relation |
| Boundary | scope, containment, responsibility, phase, or another grouping rule |
| Repetition | recurrence, equivalence, cadence, alternatives, or comparable instances |

If a device has no semantic answer, simplify or remove it. Aesthetic choices may remain, but they must not masquerade as information.

**One channel, one meaning.** A device carries one meaning on a page. Node outline dash = evidence status; connector dash = flow type; accent colour = the single thing the page exists to show. When a second meaning needs a channel, use a different one (weight, fill, hatch, icon, label). Check in grayscale that two meanings do not collapse into the same look.

## Common failures

- **Posterized prose:** paragraphs placed inside colored boxes.
- **Diagram wallpaper:** many arrows that do not encode clear relationships.
- **False certainty:** invented values or unlabeled assumptions presented as facts.
- **Equal-weight soup:** every object has the same size, color, and emphasis.
- **Decorative metaphor:** attractive imagery that obscures the actual system.
- **Miniature encyclopedia:** comprehensive coverage made unreadable through compression.
- **Orphan legend:** symbols appear before their meaning can be inferred or found.
- **Generic loop:** a circular sequence imposed on behavior without meaningful feedback or recurrence.
- **Card collage:** independent facts placed in rounded containers without a spatial relationship.
- **Slogan substitution:** motivational language stands in for rules, examples, or evidence.
- **Template residue:** numbered sections, equal columns, centered hero objects, or decorative badges recur despite having no subject-specific meaning (a central anchor that carries the subject is not residue).
- **Polished uncertainty:** unresolved ideas are presented with the visual authority of confirmed design.
- **Ugly connectors:** diagonal lines mixed with elbows, arrows that pass through unrelated nodes, floating endpoints, several arrowhead styles (see the connector toolkit in `layout-recipes.md`).
- **Inconsistent icon family:** mixed stroke weights, fills and styles, or decorative icons with no label.
- **Tiny type to fit more:** shrinking text to avoid cutting content; Librande: below roughly 4 pt print type, forget it [46:31].

## Anti-slop test

Before delivery, ask:

1. Could this exact composition describe an unrelated product after replacing the nouns? If yes, redesign it.
2. Would flattening the page into bullets lose little meaning? If yes, the visual model is too weak.
3. Are any headings slogans that conceal an undecided rule? Replace them with concrete language.
4. Do cards, colors, numbers, icons, and arrows each encode something consistent? Remove those that do not.
5. Does the page contain a real example, a meaningful exception, and enough detail to challenge the model? Add them before polishing.
