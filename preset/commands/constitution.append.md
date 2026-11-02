## Hybrid Methodology Constitution Rules

### Constitution content

Before drafting or updating the constitution, confirm with the user:

- project name and scope;
- stack and database;
- ratification date and constitution version.

Do not infer these values silently. If a value is genuinely undecided, record an explicit `TODO(<FIELD>)` item and justify it in the governance notes.

Define exactly these five principles, in this order:

- **I. Spec-First** — every feature starts with a specification; technology decisions belong in the plan, not in the specification.
- **II. Diagram-First for Flows and States** — flows, states, and architecture are described primarily with Mermaid diagrams; prose captures intent, rules, validation, edge cases, non-functional requirements, and acceptance criteria without repeating the diagram.
- **III. Acceptance-First (SDT)** — the acceptance suite is written and frozen before implementation starts; it is owned by the isolated tester role and is not part of the Build task list.
- **IV. Isolated Test Context** — the tester reads the specification, contracts, and testing rules only; it does not read the plan, data model, or source. Build never edits the acceptance suite.
- **V. Traceability** — every acceptance criterion maps to at least one acceptance test; every contract operation maps to a criterion or a documented internal obligation. No orphan tests and no untested acceptance criteria.

The constitution MUST include:

- **Architecture Context — C4 Level 1 (System Context)** with a Mermaid `C4Context` diagram.
- **Architecture Context — C4 Level 2 (Containers)** with a Mermaid `C4Container` diagram.
- **Architecture Maintenance Rule**: C4 L1/L2 change only when the system boundary, an external system, or a container changes; they are constitutional amendments between Sprints. C4 L3 is documented in the feature plan; C4 L4 is not used.
- **Technical Constraints and Platform Standards**: global stack, architecture patterns, coding rules, and security/compliance rules.
- **Workflow and Gates**: only the four human gates:
  1. Specification approved by the Product Owner and QA.
  2. Technical plan approved by the Tech Lead.
  3. Acceptance suite generated, reviewed, and frozen by QA and the Product Owner.
  4. Sprint Review with the Product Owner and stakeholders.

  Implementation MUST NOT start until gate 3 is complete.
- **Governance**: amendment procedure, SemVer policy, compliance review, version, ratification date, and last-amended date.

The constitution is project governance: principles, global architecture, constraints, quality standards, gates, and amendment rules. It does not contain operating instructions for the agent or the development toolchain, and it does not describe a command-by-command workflow.

### Filling mechanics (instructions for you, not constitution content)

- Keep the template's heading hierarchy.
- Replace its generic sections with the sections listed above; do not duplicate them.
- Write in Spanish and keep the section headings in Spanish.
- Replace every placeholder and remove template comments before writing.
- Verify that no `[ALL_CAPS_IDENTIFIER]` remains, except intentionally deferred items explicitly justified in the governance notes.
