EIR (Engineering Investigation Record)
======================================

Purpose
-------
EIR is a structured record of *engineering investigation and exploration*.
It captures the process of trying approaches, hitting walls, evaluating
alternatives, and arriving at (or failing to arrive at) a working solution.

Where a DR records *why the implementation was designed a certain way*,
an EIR records *the journey of figuring it out* — including dead ends,
unexpected behaviors, and lessons learned along the way.

An EIR is not a bug report, a log, or a postmortem.
It is a durable record of engineering exploration that prevents future
engineers from repeating the same investigation.


Relationship to ADR and DR
--------------------------
EIRs are children of DRs, forming the third level of the decision
traceability chain:

```
ADR-0008  (architecture decision)
  └── DR-0008-0001  (design rationale)
        ├── EIR-0008-0001-0001  (investigation record)
        ├── EIR-0008-0001-0002  (another investigation)
        ├── TR-0008-0001-0001   (test rationale)
        └── RET-0008-0001-0001  (after action record)
```

An EIR always traces back through a DR to an ADR.
If no specific DR exists, use `0000` for the DR segment.
If no specific ADR exists either, use `0000` for both.


Numbering Convention
--------------------

Format: `EIR-XXXX-YYYY-ZZZZ-<short-title>.md`

- `XXXX` = Grandparent ADR number (4 digits, zero-padded)
- `YYYY` = Parent DR number within that ADR (4 digits, zero-padded)
- `ZZZZ` = Sequential EIR number within that DR (4 digits, zero-padded)
- `<short-title>` = Kebab-case descriptive slug

Reserved values:
- `YYYY = 0000` — EIR linked directly to an ADR, no parent DR
- `XXXX = 0000` — standalone EIR with no parent ADR

Examples:
```
EIR-0008-0001-0001-symlink-vs-copy-for-shared-files.md
EIR-0000-0000-0001-claude-code-hook-stderr-buffering.md
```

Rules:
- All EIRs live in a single directory: `docs/eir/`
- IDs are immutable once assigned
- ZZZZ is monotonically increasing per parent DR
- Do not rename old EIRs; supersede them instead


EIR Lifecycle
-------------

Each EIR has a status that reflects its lifecycle:

- Open          : investigation is in progress
- Resolved      : investigation concluded with a finding or solution
- Inconclusive  : investigation did not reach a clear conclusion
- Superseded    : replaced by a newer EIR (must reference the new ID)

An EIR is never deleted. History is preserved.


Standard EIR Format
-------------------

Minimal mandatory sections:

1. Title (with full EIR ID)
2. Status
3. Parent DR (and grandparent ADR)
4. Investigation Goal
5. What Was Tried
6. Findings
7. Outcome


EIR Template
------------

```markdown
# EIR-XXXX-YYYY-ZZZZ: <Investigation Title>

## Status
Open | Resolved | Inconclusive | Superseded by EIR-XXXX-YYYY-WWWW

## Parent
- ADR-XXXX: <ADR Title>
- DR-XXXX-YYYY: <DR Title>
(Use 0000 placeholders for standalone investigations)

## Investigation Goal
What question were you trying to answer?

## What Was Tried
Describe each approach attempted, in chronological order.

## Findings
Summarize the key technical insights discovered.

## Outcome
State the conclusion clearly.

## Dead Ends (optional)
Approaches confirmed non-viable.

## Related
- Parent DR and ADR links
- Related EIRs
- External references
```


Authoring Guidelines
--------------------

- Write in chronological order of investigation
- Be brutally specific: include error messages, version numbers, OS details
- Do not editorialize — record what happened
- A failed investigation is still valuable — document it fully
- An EIR should allow a future engineer to say:
  "Someone already tried this. Here is what they found."


End of File
-----------
