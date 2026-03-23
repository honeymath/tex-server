TA (Test Analysis)
==================

Purpose
-------
TA is a structured record of *external system test strategy analysis*.
It captures how an external system tests itself — what testing approaches
are used, what coverage philosophy is applied, and why the test
architecture was likely designed that way.

Where a TR records why YOUR tests exist, a TA records your understanding
of why THEIR tests exist.

A TA is not a test report or quality assessment.
It is a durable record of reverse-engineered testing strategy understanding.


Relationship to AA and DA
--------------------------
TAs are children of DAs, forming the third level of the analysis chain:

```
AA-0001  (architecture analysis)
  └── DA-0001-0001  (design analysis)
        └── TA-0001-0001-0001  (test analysis)
        └── TA-0001-0001-0002  (another test analysis)
```

A TA always traces back through a DA to an AA.
If no specific DA exists, use `0000` for the DA segment.


Numbering Convention
--------------------

Format: `TA-XXXX-YYYY-ZZZZ-<short-title>.md`

- `XXXX` = Grandparent AA number (4 digits, zero-padded)
- `YYYY` = Parent DA number within that AA (4 digits, zero-padded)
- `ZZZZ` = Sequential TA number within that DA (4 digits, zero-padded)
- `<short-title>` = Kebab-case descriptive slug

Reserved values:
- `YYYY = 0000` — TA linked directly to an AA, no parent DA
- `XXXX = 0000` — standalone TA with no parent AA

Examples:
```
TA-0001-0001-0001-mcp-tool-invocation-unit-test-strategy.md
TA-0000-0000-0001-react-testing-library-philosophy.md
```

Rules:
- All TAs live in a single directory: `docs/ta/`
- IDs are immutable once assigned
- ZZZZ is monotonically increasing per parent DA
- Do not rename old TAs; supersede them instead


TA Lifecycle
------------

- Draft         : analysis in progress
- Active        : analysis is current
- Outdated      : the analyzed test strategy has evolved
- Superseded    : replaced by a newer TA (must reference the new ID)

A TA is never deleted. History is preserved.


Standard TA Format
------------------

Minimal mandatory sections:

1. Title (with full TA ID)
2. Status
3. Parent DA (and grandparent AA)
4. Test Strategy Overview
5. Coverage Philosophy (Inferred)
6. Test Tooling
7. Implications for Our Testing


TA Template
-----------

```markdown
# TA-XXXX-YYYY-ZZZZ: <Test Strategy Title>

## Status
Draft | Active | Outdated | Superseded by TA-XXXX-YYYY-WWWW

## Parent
- AA-XXXX: <System Name>
- DA-XXXX-YYYY: <Component Name>
(Use 0000 placeholders for standalone analyses)

## Test Strategy Overview
Describe how the external system tests the component under analysis.

## Coverage Philosophy (Inferred)
What testing philosophy does the system appear to follow?
(e.g., unit-heavy, integration-focused, property-based, snapshot, etc.)

## Test Tooling
What test frameworks, assertion libraries, or custom tooling are used?

## Implications for Our Testing
How does this understanding inform our own test strategy?

## Related
- Parent DA and AA links
- Related TAs
- TRs in the Decision chain that were influenced by this analysis
```


Authoring Guidelines
--------------------

- Focus on the "why" of the testing strategy, not just the "what"
- Note gaps in coverage as well as strengths
- Be specific about versions of test tooling
- A TA should allow a future engineer to say:
  "Now I understand how they test this and why, and what we can learn from it."


End of File
-----------
