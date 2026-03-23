# docs/issues/

Structured issue documents produced during codebase analysis.

## Purpose

When someone audits a codebase and identifies problems, the findings are
recorded here as structured issue documents with evidence, affected files,
severity, and recommended target state.

## Format

```
docs/issues/
└── <YYYY-MM-DD-HH-MM-SS>/
    └── <issue-name>.md
```

Each issue document includes:
- Affected files with line references
- Code evidence (excerpts demonstrating the problem)
- Severity classification
- Target state description
- Related ADRs or knowledge entries
