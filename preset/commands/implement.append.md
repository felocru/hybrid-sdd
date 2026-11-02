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
