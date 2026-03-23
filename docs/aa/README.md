AA (Architecture Analysis)
==========================

Purpose
-------
AA is a structured record of *external system architecture analysis*.
It captures the reverse-engineered design story of a library, protocol,
framework, or external service — what the creators likely decided at the
architecture level and why.

Where an ADR records YOUR architectural decisions, an AA records your
understanding of THEIR architectural decisions.

An AA is not a tutorial, a comparison table, or a recommendation.
It is a durable record that lets future engineers (human or agent)
understand an external system's architecture without re-analyzing it
from scratch.


When to Write an AA
-------------------
Write an AA whenever a team member spends more than 30 minutes
understanding an external system's design. If you are merely reading
docs to call an API, you do not need an AA. If you are reconstructing
the design philosophy behind the API, you do.

Decision heuristic:
- "I'm recording OUR decision" → write an ADR
- "I'm analyzing THEIR system" → write an AA


Relationship to the Decision Chain
-----------------------------------
The Analysis chain (AA → DA → TA) is independent from the Decision
chain (ADR → DR → EIR / TR). They may cross-reference each other:

- An AA may **inspire** an ADR (analyzing MCP leads to a protocol decision)
- An ADR may **motivate** an AA (deciding to adopt React triggers analysis)
- Cross-references use: `See AA-0001` or `Motivated by ADR-0012`

```
AA-0001  (architecture analysis of external system X)
  └── DA-0001-0001  (design analysis of component Y within X)
        └── TA-0001-0001-0001  (test analysis of how X tests Y)
```


Numbering Convention
--------------------

Format: `AA-XXXX-<short-title>.md`

- `XXXX` = Sequential number (4 digits, zero-padded)
- `<short-title>` = Kebab-case descriptive slug

Numbering is independent from ADR (AA-0001 and ADR-0001 are unrelated).

Examples:
```
AA-0001-mcp-protocol-architecture.md
AA-0002-react-fiber-reconciliation.md
AA-0003-latex-toolchain-compilation-pipeline.md
```

Rules:
- All AAs live in a single directory: `docs/aa/`
- IDs are immutable once assigned
- XXXX is monotonically increasing
- Filenames must be stable and descriptive
- Do not rename old AAs; supersede them instead


AA Lifecycle
------------

Each AA has a status that reflects its lifecycle:

- Draft         : analysis in progress, not yet reviewed
- Active        : analysis is current and reflects the analyzed system's state
- Outdated      : the analyzed system has evolved; analysis no longer accurate
- Superseded    : replaced by a newer analysis (must reference the new ID)

An AA is never deleted. History is preserved.


Standard AA Format
------------------

Minimal mandatory sections:

1. Title (with full AA ID)
2. Status
3. System Under Analysis
4. Architecture Overview
5. Key Design Decisions (inferred)
6. Trade-offs Observed
7. Implications for Our System


AA Template
-----------

```markdown
# AA-XXXX: <System Name> — Architecture Analysis

## Status
Draft | Active | Outdated | Superseded by AA-YYYY

## System Under Analysis
- Name and version analyzed
- Official documentation links
- Date of analysis

## Architecture Overview
Describe the system's high-level architecture as you understand it.

Include:
- Major components and their responsibilities
- Communication patterns between components
- Key boundaries and interfaces

## Key Design Decisions (Inferred)
What decisions did the creators likely make, and why?

For each inferred decision:
- What the decision appears to be
- What evidence supports this inference
- What trade-off it represents

## Trade-offs Observed
What did the system gain and lose from its design?

## Implications for Our System
How does this understanding affect our own architecture or decisions?

## Open Questions (optional)
Aspects of the system's design that remain unclear.

## Related
- Child DAs (component-level analyses)
- ADRs motivated by this analysis
- External references
```


Authoring Guidelines
--------------------

- Write as a reverse-engineering exercise, not a review or judgment
- Distinguish between observed facts and inferred reasoning
- Be explicit about uncertainty: "likely", "appears to", "evidence suggests"
- Include version numbers — external systems evolve
- An AA should allow a future reader to say:
  "Now I understand how this system works and why it was built this way."


End of File
-----------
