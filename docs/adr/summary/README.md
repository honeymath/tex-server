# summary/

Human-readable Chinese-language summaries of ADR documents.

## Rules

- **Language**: Chinese (中文)
- **Tone**: Storytelling (讲故事), may be humorous
- **Length**: 5–15 sentences
- **Naming**: 1:1 mapping with parent document (same filename)
- **Goal**: A reader who reads only the summary can say: "我知道这个文件在讲什么了。"

## Content requirements

- What problem or decision was made
- What was decided and why
- Why it matters
- One sentence on what would break if this were reversed

## What summaries are NOT

- Not translations of the full document
- Not technical specifications
- Not approval-gated (anyone can write or update them)

## Example

Parent: `docs/adr/0001-decision-name.md`
Summary: `docs/adr/summary/0001-decision-name.md`
