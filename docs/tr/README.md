TR (Test Rationale)
===================

Purpose
-------
TR is a structured record of *test design decisions and scenario rationale*.
It captures *why* a test exists, *what scenario* it validates, and *what
reasoning* drove the test engineer to imagine that scenario — not just
*what* the test does mechanically.

Where a DR records why the implementation was designed a certain way,
a TR records why the tests were designed a certain way: which risks they
mitigate, which user behaviors they simulate, and which failure modes
they guard against.

A TR is not a test plan, a test report, or a bug ticket.
It is a durable record of test design reasoning.


Relationship to ADR and DR
--------------------------
TRs are children of DRs:

```
ADR-0008  (architecture decision)
  └── DR-0008-0001  (design rationale)
        ├── EIR-0008-0001-0001  (investigation record)
        ├── TR-0008-0001-0001   (test rationale)
        ├── TR-0008-0001-0002   (another test rationale)
        └── RET-0008-0001-0001  (after action record)
```

A TR always traces back to a DR, and through the DR to an ADR.
Use `0000` for the DR segment for rare ADR-level cross-cutting tests.


Numbering Convention
--------------------

Format: `TR-XXXX-YYYY-ZZZZ-<short-title>.md`

- `XXXX` = Parent ADR number (4 digits, zero-padded)
- `YYYY` = Parent DR number (4 digits, zero-padded)
- `ZZZZ` = Sequential TR number within that DR (4 digits, zero-padded)
- `<short-title>` = Kebab-case descriptive slug

Reserved values:
- `XXXX = 0000` — standalone TR with no parent ADR
- `YYYY = 0000` — ADR-level TR with no specific parent DR

Examples:
```
TR-0004-0001-0001-task-state-transition-boundaries.md
TR-0000-0000-0001-cross-role-message-delivery-smoke.md
```

Rules:
- All TRs live in a single directory: `docs/tr/`
- IDs are immutable once assigned
- ZZZZ is monotonically increasing per parent DR
- Do not rename old TRs; supersede them instead


TR Lifecycle
------------

- Draft         : scenario identified, rationale not yet reviewed
- Active        : test rationale is current and tests exist for it
- Outdated      : system has evolved; test scenario no longer applies
- Superseded    : replaced by a newer TR (must reference the new ID)

A TR is never deleted. History is preserved.


Standard TR Format
------------------

Minimal mandatory sections:

1. Title (with full TR ID)
2. Status
3. Parent DR (and parent ADR)
4. Scenario Description
5. Test Design Rationale
6. Expected Behavior
7. Risk Addressed


TR Template
-----------

```markdown
# TR-XXXX-YYYY-ZZZZ: <Test Scenario Title>

## Status
Draft | Active | Outdated | Superseded by TR-XXXX-YYYY-ZZZZ

## Parent DR
DR-XXXX-YYYY: <DR Title>

## Parent ADR
ADR-XXXX: <ADR Title>

## Scenario Description
Describe the usage scenario or failure mode this test targets.

## Test Design Rationale
Explain *why* this test was designed this way.

## Expected Behavior
Describe what correct system behavior looks like.

## Risk Addressed
What could go wrong if this test did not exist?

## Test Cases (optional)
## Boundary Conditions (optional)
## Related
```


Authoring Guidelines
--------------------

- Focus on *why this scenario matters*, not on test mechanics
- Include the failure mode that inspired the scenario
- A TR should allow a future engineer to say:
  "Now I understand why this test exists and what breaks without it."


End of File
-----------
