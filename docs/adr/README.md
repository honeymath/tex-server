ADR (Architecture Decision Record)
=================================

Purpose
-------
ADR is a lightweight, structured way to record important engineering and
architecture decisions. It captures *why* a decision was made, not just
*what* was done, so that future humans and agents can reconstruct the
reasoning under the original constraints.

ADR files are not design documents, logs, or tutorials.
They are durable records of decisions that affect system evolution.


Directory Structure
-------------------

```
docs/
  adr/
    0001-<short-decision-title>.md
    0002-<short-decision-title>.md
    summary/
      0001-<short-decision-title>.md    ← Chinese summary
```

Rules:
- All ADRs live in a single directory: docs/adr/
- Each ADR has a monotonically increasing numeric ID
- IDs are immutable once assigned
- Filenames must be stable and descriptive
- Do not rename old ADRs; supersede them instead


ADR Lifecycle
-------------

Each ADR has a status that reflects its lifecycle:

- Proposed     : drafted, not yet accepted
- Accepted     : decision is in effect
- Deprecated   : decision is no longer recommended
- Superseded   : replaced by a newer ADR (must reference the new ID)

An ADR is never deleted. History is preserved.


Standard ADR Format
-------------------

Minimal mandatory sections:

1. Title
2. Status
3. Context
4. Decision
5. Consequences

Optional but strongly recommended sections are listed below.


ADR Template
------------

```markdown
# ADR-XXXX: <Decision Title>

## Status
Proposed | Accepted | Deprecated | Superseded by ADR-YYYY

## Context
Describe the situation that led to this decision.

Include:
- The problem being solved
- Relevant background
- Constraints (technical, organizational, time, migration, cost)
- Why this decision matters

Avoid implementation details unless they are constraints.

## Decision
State the decision clearly and concisely.

This section should be short and unambiguous.
It answers: "What did we decide?"

## Consequences
Describe the effects of this decision.

Include:
- Positive consequences
- Negative consequences
- Known risks or technical debt
- Operational or maintenance impact
```


Optional Sections
-----------------

## Alternatives Considered
List meaningful alternatives that were evaluated.

For each alternative:
- Brief description
- Why it was not chosen

## Reversibility
Describe how hard this decision is to undo.

## Related
References to related material:
- Other ADRs, DRs, RETs, AAs
- Pull requests, issues
- External references


Authoring Guidelines
--------------------

- Write ADRs in neutral, factual language
- Avoid justifying decisions with authority ("X said so")
- Capture trade-offs explicitly
- Prefer clarity over completeness
- Assume the reader has no access to prior conversations

An ADR should allow a future reader to say:
"I disagree, but I understand why this was done."


End of File
-----------
