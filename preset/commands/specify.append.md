## Hybrid Methodology Specification Rules

### Before writing

Identify the actors, the main flow, alternate and exception flows, business rules, stateful entities, and non-functional requirements. If a material ambiguity changes scope or behavior, stop and ask; do not invent a rule.

### Specification content

The specification MUST include:

- A use case diagram in Mermaid `usecase-beta` (Mermaid 12+), with every actor declared explicitly.
- For each user story: a 2-3 line Intent, Why this priority, Independent Test, and one activity/flow diagram in Mermaid `flowchart`.
- A state diagram (`stateDiagram-v2`) for each entity with a meaningful lifecycle.
- Acceptance scenarios in Given/When/Then Markdown, each with a stable, globally unique `CA-n` id (CA-1, CA-2, ...).
- Functional requirements, non-functional requirements specific to the use case, edge cases, key entities, measurable success criteria, and assumptions.

### Quality rules

- The specification is technology-agnostic: no languages, frameworks, databases, APIs, or implementation details.
- Prose is complementary: do not restate diagram steps.
- Rules that diagrams cannot express belong in Requirements or Edge Cases.
- Do not use Gherkin syntax or `.feature` files.
- Do not create executable acceptance artifacts here; acceptance tests are the tester's responsibility.
- Do not add diagram formats beyond those listed.
