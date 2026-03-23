DR (Design Rationale)
=====================

Purpose
-------
DR is a structured record of *implementation-level* design decisions.
Where an ADR captures *which direction the system takes* at the
architectural level, a DR captures *how and why a specific piece was
built the way it was* — the rationale behind patterns, abstractions,
data-structure choices, and trade-offs made for scalability,
portability, or maintainability.

A DR is not a tutorial, code comment, or changelog entry.
It is a durable record that lets future engineers (human or agent)
understand why the implementation looks the way it does.


Relationship to ADR
-------------------
DRs are children of ADRs. Every DR traces back to the architectural
decision it implements. If no specific ADR exists, the reserved parent
ID `0000` is used (see Numbering below).

```
ADR-0008  (architecture decision)
  └── DR-0008-0001  (design rationale implementing part of ADR-0008)
  └── DR-0008-0002  (another design rationale under ADR-0008)
```


Numbering Convention
--------------------

Format: `DR-XXXX-YYYY-<short-title>.md`

- `XXXX` = Parent ADR number (4 digits, zero-padded)
- `YYYY` = Sequential DR number within that ADR (4 digits, zero-padded)
- `<short-title>` = Kebab-case descriptive slug

Reserved values:
- `XXXX = 0000` — standalone DR with no parent ADR

Examples:
```
DR-0008-0001-three-layer-directory-layout.md
DR-0000-0001-json-over-yaml-for-entity-cards.md
```

Rules:
- All DRs live in a single directory: `docs/dr/`
- IDs are immutable once assigned
- YYYY is monotonically increasing per parent ADR
- Filenames must be stable and descriptive
- Do not rename old DRs; supersede them instead


DR Lifecycle
------------

Each DR has a status that reflects its lifecycle:

- Draft         : work in progress, not yet reviewed
- Active        : rationale is current and reflects the implementation
- Outdated      : implementation has evolved; rationale no longer accurate
- Superseded    : replaced by a newer DR (must reference the new ID)

A DR is never deleted. History is preserved.


Standard DR Format
------------------

Minimal mandatory sections:

1. Title (with full DR ID)
2. Status
3. Parent ADR
4. Context
5. Design Decision
6. Rationale
7. Consequences


DR Template
-----------

```markdown
# DR-XXXX-YYYY: <Design Decision Title>

## Status
Draft | Active | Outdated | Superseded by DR-XXXX-ZZZZ

## Parent ADR
ADR-XXXX: <ADR Title>
(Use ADR-0000 if no parent ADR exists)

## Context
Describe the implementation challenge or design problem.

## Design Decision
State the implementation design choice clearly.

## Rationale
Explain *why* this design was chosen over alternatives.

## Consequences
Describe the effects of this design choice.

## Alternatives Considered (optional)

## Related
- Parent ADR link
- Related DRs
- Child EIRs (if any)
- Child RETs (after action records, if any)
```


Authoring Guidelines
--------------------

- Write from the engineer's perspective
- Focus on trade-offs, not just the chosen path
- Include concrete examples where they clarify the rationale
- Reference specific code paths, modules, or files when relevant
- A DR should allow a future engineer to say:
  "Now I understand why this code looks this way."


End of File
-----------
