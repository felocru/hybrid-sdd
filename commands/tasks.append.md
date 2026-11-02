## Hybrid Methodology Task Rules

### Before writing

Read the approved specification, plan, data model, and contracts. Identify the user stories and their priorities. Record the acceptance suite as a precondition, not as a task.

### Task content

`tasks.md` MUST contain:

- An Acceptance Suite Precondition at the top: the suite is generated and frozen by the isolated tester role before implementation, lives in `tests/acceptance/`, maps every CA to at least one test, and is not modified by Build.
- Only Build implementation and white-box tasks: unit, integration with Testcontainers, architecture with ArchUnit, and contract tests.
- The phases: Setup, Foundational, one phase per user story in priority order, and Polish.
- Tasks in the format `- [ ] TNNN [P?] [USn?] Description with file path`.
- Dependencies and execution order, plus parallel examples per user story.

### Quality rules

- Do not create acceptance, E2E, or load-test tasks in `tasks.md`.
- Do not impose test-first for white-box tests; they may be written during or after implementation.
- Every task must be immediately executable by Build and include a concrete file path.
- The acceptance precondition is a gate, not a task.
