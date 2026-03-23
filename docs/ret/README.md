RET (After Action Record)
==========================

Purpose
-------
RET is a structured record of *execution experience* tied to a specific
architecture or design decision. It captures what actually happened when
a decision was implemented, how reality deviated from the plan, and what
was learned — the backward-looking complement to the forward-looking
Decision chain.

Where a DR records "why was it built this way" (before or during),
a RET records "what happened when we built it this way" (after).

A RET is not a failure record (ADR-0003), not a personal retrospective,
and not a changelog entry. It is a durable after-action record linked
to a specific decision in the traceability chain.


Relationship to ADR and DR
--------------------------
RETs are children of DRs, forming part of the third level of the
decision traceability chain alongside EIRs and TRs:

```
ADR-XXXX  (architecture decision)
  └── DR-XXXX-YYYY  (design rationale)
        ├── EIR-XXXX-YYYY-ZZZZ  (investigation record)
        ├── TR-XXXX-YYYY-ZZZZ   (test rationale)
        └── RET-XXXX-YYYY-ZZZZ  (after action record)
```

A RET traces back through a DR to an ADR.
- Use `YYYY = 0000` for ADR-level reflection (no specific DR).
- Use `XXXX = 0000` for standalone after-action records with no parent ADR.


Numbering Convention
--------------------

Format: `RET-XXXX-YYYY-ZZZZ-<short-title>.md`

- `XXXX` = Grandparent ADR number (4 digits, zero-padded)
- `YYYY` = Parent DR number within that ADR (4 digits, zero-padded)
- `ZZZZ` = Sequential RET number within that DR (4 digits, zero-padded)
- `<short-title>` = Kebab-case descriptive slug

Reserved values:
- `YYYY = 0000` — RET linked directly to an ADR, no parent DR
- `XXXX = 0000` — standalone RET with no parent ADR

Examples:
```
RET-0008-0002-0001-symlink-approach-required-three-iterations.md
RET-0012-0000-0001-cross-repo-deployment-first-attempt.md
RET-0000-0000-0001-remember-skill-rollout-lessons.md
```

Rules:
- All RETs live in a single directory: `docs/ret/`
- IDs are immutable once assigned
- ZZZZ is monotonically increasing per parent DR
- Do not rename old RETs; supersede them instead


RET Lifecycle
-------------

Each RET has a status that reflects its lifecycle:

- Draft         : after-action record in progress, not yet reviewed
- Active        : record is current and reflects actual execution experience
- Outdated      : the context has evolved; lessons may no longer apply
- Superseded    : replaced by a newer RET (must reference the new ID)

A RET is never deleted. History is preserved.


Standard RET Format
-------------------

Minimal mandatory sections:

1. Title (with full RET ID)
2. Status
3. Parent DR (and grandparent ADR)
4. Execution Summary
5. Deviations
6. Observations
7. Lesson


RET Template
------------

```markdown
# RET-XXXX-YYYY-ZZZZ: <After Action Title>

## Status
Draft | Active | Outdated | Superseded by RET-XXXX-YYYY-WWWW

## Parent
- ADR-XXXX: <ADR Title>
- DR-XXXX-YYYY: <DR Title>
(Use 0000 placeholders for standalone records)

## Execution Summary
What was the plan, and what actually happened?

## Deviations
Where did reality diverge from the plan, and why?

## Observations
What worked well? What didn't? What was surprising?

## Lesson
> <One-sentence actionable takeaway.>

## Peer Comments (optional)
Append-only area for other roles to add structured feedback:

### [role-name] YYYY-MM-DD
<Comment text>

## Related
- Parent DR and ADR links
- Related RETs, EIRs, or TRs
- External references
```


Authoring Guidelines
--------------------

- Write as an honest retrospective — capture reality, not the ideal
- Focus on the gap between plan and execution
- Include specific, actionable lessons — not vague "be more careful"
- The Lesson blockquote should be scannable as a standalone takeaway
- Other roles may append Peer Comments with provenance (role + date)
- A RET should allow a future engineer to say:
  "Someone already tried this approach. Here is what they learned."


End of File
-----------
