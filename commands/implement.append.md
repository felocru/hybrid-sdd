---
description: Execute the implementation plan by processing and executing all tasks defined in tasks.md
model: opencode-go/deepseek-v4.1-flash#max
subagent: true
---

## Hybrid Methodology Implementation Rules

### Before starting

Verify that the acceptance suite is frozen in `tests/acceptance/` and that `tasks.md` contains only Build implementation and white-box tasks. If the suite is missing or `tasks.md` contains acceptance tasks, stop and report the inconsistency; do not proceed.

### Execution rules

- Execute the Build tasks in dependency order and keep the task checkoff and progress reporting.
- Write and run white-box tests (unit, integration with Testcontainers, ArchUnit, contract) during or after implementation; no test-first requirement.
- Do not run, edit, regenerate, or reorder the acceptance suite from `tasks.md`.
- If a white-box test fails, fix the implementation.
- If the acceptance suite fails, report it; do not modify the suite.
- Acceptance verification happens after implementation and is not a Build task.

### UI identifiers and visual reference

- Implement UI identifiers (`name`, `id`, accessible labels, ARIA roles, `data-testid`) verbatim from the canonical identifiers table in `contracts/ui-contract.md`. Do not invent, rename, or silently "fix" identifiers; if a row is wrong or missing, report it and stop for that screen.
- The visual reference is the frozen snapshot in `specs/[###-feature]/design/`, not the live design file or its MCP. Compare the built screens against those images; the contract wins over the image.
- If you cannot read images natively, spawn a subagent with an image-capable model to verify the built UI against `design/` and the accessibility rules of the UI contract.
- Mismatches are reported, never resolved silently on either side.
