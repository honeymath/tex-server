DA (Design Analysis)
====================

Purpose
-------
DA is a structured record of *component-level analysis* within an external
system. Where an AA captures the architecture-level "what and why" of an
external system, a DA zooms into a specific component, pattern, data
structure, algorithm, or API convention and analyzes how it works and why
it was likely designed that way.

A DA is not a usage guide or API reference.
It is a durable record of reverse-engineered design understanding at the
component level.


Relationship to AA
------------------
DAs are children of AAs. Every DA traces back to the architecture analysis
of the system it belongs to. If no specific AA exists, the reserved parent
ID `0000` is used.

```
AA-0001  (architecture analysis of system X)
  └── DA-0001-0001  (design analysis of component Y)
  └── DA-0001-0002  (design analysis of component Z)
```


Numbering Convention
--------------------

Format: `DA-XXXX-YYYY-<short-title>.md`

- `XXXX` = Parent AA number (4 digits, zero-padded)
- `YYYY` = Sequential DA number within that AA (4 digits, zero-padded)
- `<short-title>` = Kebab-case descriptive slug

Reserved values:
- `XXXX = 0000` — standalone DA with no parent AA

Examples:
```
DA-0001-0001-mcp-tool-invocation-protocol.md
DA-0001-0002-mcp-resource-subscription-model.md
DA-0000-0001-react-hooks-closure-semantics.md
```

Rules:
- All DAs live in a single directory: `docs/da/`
- IDs are immutable once assigned
- YYYY is monotonically increasing per parent AA
- Do not rename old DAs; supersede them instead


DA Lifecycle
------------

- Draft         : analysis in progress
- Active        : analysis is current
- Outdated      : the analyzed component has evolved
- Superseded    : replaced by a newer DA (must reference the new ID)

A DA is never deleted. History is preserved.


Standard DA Format
------------------

Minimal mandatory sections:

1. Title (with full DA ID)
2. Status
3. Parent AA
4. Component Under Analysis
5. Design Pattern / Mechanism
6. Inferred Rationale
7. Implications


DA Template
-----------

```markdown
# DA-XXXX-YYYY: <Component Name> — Design Analysis

## Status
Draft | Active | Outdated | Superseded by DA-XXXX-ZZZZ

## Parent AA
AA-XXXX: <System Name>
(Use AA-0000 if no parent AA exists)

## Component Under Analysis
Identify the specific component, module, or pattern being analyzed.

## Design Pattern / Mechanism
Describe how this component works at the design level.

Include:
- Data structures used
- Algorithms or patterns employed
- Interface contracts
- State management approach

## Inferred Rationale
Why was it likely designed this way?

Include:
- Performance considerations
- Compatibility constraints
- Historical evolution (if traceable)
- Trade-offs made

## Implications
How does this understanding affect our use of or building upon this component?

## Related
- Parent AA link
- Child TAs (test analyses)
- Related DAs under the same AA
- DRs in the Decision chain that depend on this understanding
```


Authoring Guidelines
--------------------

- Focus on one component or pattern per DA
- Distinguish observation from inference
- Include code examples or API excerpts where they clarify the design
- Reference specific versions, files, or documentation sections
- A DA should allow a future engineer to say:
  "Now I understand how this component works and why."


End of File
-----------
