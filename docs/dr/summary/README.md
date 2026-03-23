# summary/

Human-readable Chinese-language summaries of DR documents.

## Rules

- **Language**: Chinese (中文)
- **Tone**: Storytelling (讲故事), may be humorous
- **Length**: 5–15 sentences
- **Naming**: 1:1 mapping with parent document (same filename)
- **Goal**: A reader who reads only the summary can say: "我知道这个文件在讲什么了。"

## Content requirements

- What implementation challenge was addressed
- What design was chosen and why
- Why it matters
- One sentence on what would break if this design were reversed

## What summaries are NOT

- Not translations of the full document
- Not technical specifications
- Not approval-gated (anyone can write or update them)

## Example

Parent: `docs/dr/DR-0008-0001-design-name.md`
Summary: `docs/dr/summary/DR-0008-0001-design-name.md`
