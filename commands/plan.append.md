## Hybrid Methodology Plan Rules

### Before writing

Read the approved specification and the project constitution. Resolve the technical context, constitution gates, and any material ambiguity before designing. If a gap changes scope or behavior, stop and ask; do not invent requirements.

### Plan content

The plan MUST include:

- Summary of 2-3 lines.
- Technical Context: stack, dependencies, storage, testing, constraints, and scale.
- Constitution Check with explicit gates.
- C4 Level 3 (Components) in Mermaid `C4Component` for this feature. C4 L1/L2 belong to the constitution; do not duplicate them.
- One sequence diagram (`sequenceDiagram`) for the key technical flow.
- One domain class diagram (`classDiagram`) for domain entities and relationships.
- Links to contracts in `contracts/`; do not inline the full contract.
- Project Structure and Complexity Tracking.
- `data-model.md` with an ER diagram (`erDiagram`), entities, fields, relationships, constraints, and validation rules.

### Quality rules

- Keep the summary and technical context compact; do not repeat diagrams in prose.
- If the feature does not change components, reference the relevant C4 L2 container instead of inventing a component diagram.
- Keep the domain class diagram and the ER diagram as separate views: domain behavior vs persistence.
- Do not put the ER or the state diagram in `plan.md`.
- Validate Mermaid diagrams locally before considering the plan complete; do not add CI validation.
