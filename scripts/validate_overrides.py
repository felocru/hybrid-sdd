#!/usr/bin/env python3
"""Validate the artifacts produced by the hybrid Spec Kit overrides.

The checker is intentionally structural. It verifies that the templates and
command addenda produce the expected sections, diagrams, traceability ids, and
Build/tester separation. It does not replace the human review of whether the
content is semantically correct.

Usage:
    python3 validate_overrides.py --project /path/to/project
    python3 validate_overrides.py --project /path/to/project --stage spec
    python3 validate_overrides.py --project /path/to/project --mmdc mmdc --strict

Exit codes:
    0  no hard failures (warnings may exist unless --strict)
    1  at least one hard failure, or warnings with --strict
    2  the project or feature directory could not be resolved
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

PASS = "PASS"
FAIL = "FAIL"
WARN = "WARN"
SKIP = "SKIP"

HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.M)
MERMAID_RE = re.compile(r"```mermaid[ \t]*\r?\n(.*?)```", re.S | re.I)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)

STACK_TERMS = [
    "vaadin",
    "spring boot",
    "spring data",
    "postgresql",
    "hibernate",
    "jpa",
    "maven",
    "junit",
    "playwright",
    "testcontainers",
    "java 25",
    "openapi",
]

STOP_LABELS = {
    "inicio",
    "fin",
    "start",
    "end",
    "sí",
    "si",
    "no",
    "yes",
    "ok",
    "error",
}


class Report:
    def __init__(self) -> None:
        self.rows: list[dict[str, str]] = []

    def add(self, status: str, area: str, check: str, detail: str = "") -> None:
        self.rows.append(
            {"status": status, "area": area, "check": check, "detail": detail}
        )

    def count(self, status: str) -> int:
        return sum(1 for row in self.rows if row["status"] == status)

    def has_fail(self) -> bool:
        return self.count(FAIL) > 0

    def print_table(self) -> None:
        areas: list[str] = []
        for row in self.rows:
            if row["area"] not in areas:
                areas.append(row["area"])

        for area in areas:
            print(f"\n[{area}]")
            for row in self.rows:
                if row["area"] != area:
                    continue
                line = f"  {row['status']:4}  {row['check']}"
                if row["detail"]:
                    line += f" — {row['detail']}"
                print(line)

        print("\nResumen:")
        print(f"  PASS: {self.count(PASS)}")
        print(f"  WARN: {self.count(WARN)}")
        print(f"  FAIL: {self.count(FAIL)}")
        print(f"  SKIP: {self.count(SKIP)}")

    def to_dict(self) -> dict[str, object]:
        return {
            "rows": self.rows,
            "summary": {
                "pass": self.count(PASS),
                "warn": self.count(WARN),
                "fail": self.count(FAIL),
                "skip": self.count(SKIP),
            },
        }


def read_text(path: Path) -> str | None:
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def headings(text: str) -> list[tuple[int, int, str]]:
    return [
        (match.start(), len(match.group(1)), match.group(2).strip())
        for match in HEADING_RE.finditer(text)
    ]


def get_section(text: str, title_pattern: str) -> str:
    """Return a heading and its body, stopping at the next same/higher heading."""
    entries = headings(text)
    for index, (start, level, title) in enumerate(entries):
        if not re.search(title_pattern, title, re.I):
            continue
        end = len(text)
        for next_start, next_level, _ in entries[index + 1 :]:
            if next_level <= level:
                end = next_start
                break
        return text[start:end]
    return ""


def has_section(text: str, title_pattern: str) -> bool:
    return bool(get_section(text, title_pattern))


def mermaid_blocks(text: str) -> list[str]:
    return [match.group(1) for match in MERMAID_RE.finditer(text)]


def diagram_kind(block: str) -> str:
    for line in block.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("%%"):
            return stripped.split()[0]
    return ""


def diagrams_of(text: str, kind: str) -> list[str]:
    return [block for block in mermaid_blocks(text) if diagram_kind(block) == kind]


def has_diagram(text: str, kind: str) -> bool:
    return bool(diagrams_of(text, kind))


def strip_mermaid(text: str) -> str:
    return MERMAID_RE.sub("", text)


def strip_comments(text: str) -> str:
    return HTML_COMMENT_RE.sub("", text)


def body_of(section: str) -> str:
    lines = section.splitlines()
    return "\n".join(lines[1:]) if lines else ""


def check_text_absent(
    report: Report, area: str, text: str, pattern: str, label: str
) -> None:
    if re.search(pattern, text, re.I):
        report.add(FAIL, area, f"No debe aparecer {label}")
    else:
        report.add(PASS, area, f"No aparece {label}")


def check_required_sections(
    report: Report,
    area: str,
    text: str,
    sections: list[tuple[str, str]],
) -> None:
    for label, pattern in sections:
        if has_section(text, pattern):
            report.add(PASS, area, f"Sección presente: {label}")
        else:
            report.add(FAIL, area, f"Falta la sección: {label}")


def parse_stories(spec: str) -> list[tuple[str, str]]:
    entries = headings(spec)
    stories: list[tuple[str, str]] = []
    for index, (start, level, title) in enumerate(entries):
        if not re.match(r"User Story\s+\d+", title, re.I):
            continue
        end = len(spec)
        for next_start, next_level, next_title in entries[index + 1 :]:
            if next_level < level:
                end = next_start
                break
            if next_level == level and re.match(
                r"User Story\s+\d+", next_title, re.I
            ):
                end = next_start
                break
        stories.append((title, spec[start:end]))
    return stories


def extract_flowchart_labels(block: str) -> list[str]:
    labels: list[str] = []
    pattern = re.compile(
        r"(?:\[\[|\[\(|\(\[|\[|\(|\{)([^\[\]\(\)\{\}]+)(?:\]\]|\)\]|\]\)|\]|\)|\})"
    )
    for match in pattern.finditer(block):
        label = re.sub(r"<br\s*/?>", " ", match.group(1), flags=re.I)
        label = re.sub(r"\s+", " ", label).strip().strip("\"'")
        if len(label) < 4 or label.lower() in STOP_LABELS:
            continue
        labels.append(label)
    return sorted(set(labels))


def check_spec(feature: Path, report: Report) -> None:
    spec = read_text(feature / "spec.md")
    if spec is None:
        report.add(FAIL, "spec.md", "El archivo existe")
        return
    report.add(PASS, "spec.md", "El archivo existe")

    check_required_sections(
        report,
        "spec.md",
        spec,
        [
            ("User Scenarios & Testing", r"^User Scenarios & Testing"),
            ("Requirements", r"^Requirements\b"),
            ("Success Criteria", r"^Success Criteria"),
            ("Assumptions", r"^Assumptions$"),
            ("Use Case Diagram", r"^Use Case Diagram$"),
            ("Edge Cases", r"^Edge Cases$"),
            ("Functional Requirements", r"^Functional Requirements$"),
            (
                "Non-Functional Requirements",
                r"^Non-Functional Requirements$",
            ),
            ("Key Entities", r"^Key Entities"),
            ("State Diagram", r"^State Diagram$"),
            ("Measurable Outcomes", r"^Measurable Outcomes$"),
        ],
    )

    use_case = get_section(spec, r"^Use Case Diagram$")
    if use_case:
        blocks = diagrams_of(use_case, "usecase-beta")
        if blocks:
            report.add(PASS, "spec.md", "Diagrama de casos de uso usecase-beta")
            block = blocks[0]
            if re.search(r"^\s*actor\s+", block, re.M):
                report.add(PASS, "spec.md", "El diagrama de casos de uso declara actores")
            else:
                report.add(
                    FAIL,
                    "spec.md",
                    "El diagrama de casos de uso no declara actores",
                )
            if "systemBoundary" in block:
                report.add(PASS, "spec.md", "El diagrama delimita el sistema")
            else:
                report.add(
                    WARN,
                    "spec.md",
                    "El diagrama de casos de uso no usa systemBoundary",
                )
        else:
            report.add(
                FAIL,
                "spec.md",
                "Falta un bloque Mermaid usecase-beta en Use Case Diagram",
            )

    stories = parse_stories(spec)
    if not stories:
        report.add(FAIL, "spec.md", "Hay al menos una User Story con prioridad")
    else:
        report.add(
            PASS,
            "spec.md",
            "User Stories detectadas",
            f"{len(stories)} historia(s)",
        )

    for title, story in stories:
        short = re.sub(r"\s+", " ", title)[:70]
        if re.search(r"\*\*Intent\*\*", story, re.I):
            report.add(PASS, "spec.md", f"Intent presente: {short}")
        else:
            report.add(FAIL, "spec.md", f"Falta Intent: {short}")

        if re.search(r"\*\*Why this priority\*\*", story, re.I):
            report.add(PASS, "spec.md", f"Prioridad justificada: {short}")
        else:
            report.add(WARN, "spec.md", f"Falta Why this priority: {short}")

        if re.search(r"\*\*Independent Test\*\*", story, re.I):
            report.add(PASS, "spec.md", f"Independent Test presente: {short}")
        else:
            report.add(WARN, "spec.md", f"Falta Independent Test: {short}")

        flow_blocks = diagrams_of(story, "flowchart")
        if flow_blocks:
            report.add(PASS, "spec.md", f"Diagrama de actividad: {short}")
        else:
            report.add(
                FAIL,
                "spec.md",
                f"Falta el diagrama de actividad flowchart: {short}",
            )

        scenario_ids = re.findall(r"\bCA-(\d+)\b", story)
        if scenario_ids:
            report.add(
                PASS,
                "spec.md",
                f"Criterios de aceptación con id CA: {short}",
                ", ".join(f"CA-{number}" for number in sorted(set(scenario_ids))),
            )
        else:
            report.add(
                FAIL,
                "spec.md",
                f"Los Acceptance Scenarios no tienen id CA-n: {short}",
            )

        given = re.search(r"\*\*(Given|Dado)\*\*", story, re.I)
        when = re.search(r"\*\*(When|Cuando)\*\*", story, re.I)
        then = re.search(r"\*\*(Then|Entonces)\*\*", story, re.I)
        if given and when and then:
            report.add(PASS, "spec.md", f"Formato Given/When/Then: {short}")
        else:
            report.add(
                FAIL,
                "spec.md",
                f"Falta el formato Given/When/Then: {short}",
            )

    ca_definitions = re.findall(r"\*\*CA-(\d+)\*\*", spec)
    duplicate_ca = sorted(
        {number for number in ca_definitions if ca_definitions.count(number) > 1},
        key=int,
    )
    if duplicate_ca:
        report.add(
            FAIL,
            "spec.md",
            "Hay ids CA duplicados; deben ser globales y únicos",
            ", ".join(f"CA-{number}" for number in duplicate_ca),
        )
    else:
        report.add(PASS, "spec.md", "Ids CA únicos")

    all_ca_ids = sorted(set(re.findall(r"\bCA-(\d+)\b", spec)), key=int)
    if len(all_ca_ids) >= 3:
        report.add(
            PASS,
            "spec.md",
            "Cantidad de criterios de aceptación",
            f"{len(all_ca_ids)} CA",
        )
    elif all_ca_ids:
        report.add(
            WARN,
            "spec.md",
            "Pocos criterios de aceptación para el CU piloto",
            f"{len(all_ca_ids)} CA; se esperaban al menos 3",
        )
    else:
        report.add(FAIL, "spec.md", "No hay criterios de aceptación CA-n")

    state = get_section(spec, r"^State Diagram$")
    if state:
        blocks = diagrams_of(state, "stateDiagram-v2")
        if blocks:
            transitions = len(re.findall(r"-->", blocks[0]))
            if transitions >= 2:
                report.add(
                    PASS,
                    "spec.md",
                    "Diagrama de estados con transiciones",
                    f"{transitions} transiciones",
                )
            else:
                report.add(
                    FAIL,
                    "spec.md",
                    "El diagrama de estados no tiene al menos 2 transiciones",
                )
        else:
            report.add(
                FAIL,
                "spec.md",
                "Falta un bloque Mermaid stateDiagram-v2 en State Diagram",
            )

    fr_count = len(re.findall(r"\bFR-\d+\b", spec))
    if fr_count >= 3:
        report.add(PASS, "spec.md", "Requisitos funcionales FR-n", f"{fr_count} FR")
    else:
        report.add(
            FAIL,
            "spec.md",
            "Se esperaban al menos 3 requisitos funcionales FR-n",
            f"{fr_count} FR",
        )

    nfr_count = len(re.findall(r"\bNFR-\d+\b", spec))
    if nfr_count >= 1:
        report.add(
            PASS,
            "spec.md",
            "Requisitos no funcionales NFR-n",
            f"{nfr_count} NFR",
        )
    else:
        report.add(FAIL, "spec.md", "No hay requisitos no funcionales NFR-n")

    sc_count = len(re.findall(r"\bSC-\d+\b", spec))
    if sc_count >= 2:
        report.add(
            PASS,
            "spec.md",
            "Criterios de éxito medibles SC-n",
            f"{sc_count} SC",
        )
    else:
        report.add(
            FAIL,
            "spec.md",
            "Se esperaban al menos 2 criterios de éxito SC-n",
            f"{sc_count} SC",
        )

    edge = get_section(spec, r"^Edge Cases$")
    edge_bullets = len(re.findall(r"^\s*-\s+\S", body_of(edge), re.M))
    if edge_bullets >= 2:
        report.add(
            PASS,
            "spec.md",
            "Edge cases documentados",
            f"{edge_bullets} casos",
        )
    elif edge_bullets == 1:
        report.add(WARN, "spec.md", "Solo hay un edge case")
    else:
        report.add(FAIL, "spec.md", "No hay edge cases")

    entities = get_section(spec, r"^Key Entities")
    entity_bullets = len(re.findall(r"^\s*-\s+\*\*.+?\*\*", body_of(entities), re.M))
    if entity_bullets >= 1:
        report.add(
            PASS,
            "spec.md",
            "Entidades clave declaradas",
            f"{entity_bullets} entidad(es)",
        )
    else:
        report.add(FAIL, "spec.md", "No hay entidades clave")

    check_text_absent(report, "spec.md", spec, r"\bgherkin\b", "Gherkin")
    check_text_absent(report, "spec.md", spec, r"\.feature\b", ".feature")

    if re.search(
        r"^\s*(Feature|Scenario|Scenario Outline|Background|Examples)\s*:",
        spec,
        re.M,
    ):
        report.add(
            FAIL,
            "spec.md",
            "El spec usa palabras clave de Gherkin; debe quedarse en Given/When/Then Markdown",
        )
    else:
        report.add(PASS, "spec.md", "Sin sintaxis Gherkin en el spec")

    placeholders = [
        "[FEATURE NAME]",
        "[###-feature-name]",
        "[DATE]",
        "[Brief Title]",
        "[initial state]",
        "[action]",
        "[expected outcome]",
        "[Entity 1]",
        "[specific capability]",
        "$ARGUMENTS",
    ]
    found_placeholders = [token for token in placeholders if token in spec]
    if found_placeholders:
        report.add(
            FAIL,
            "spec.md",
            "Quedaron placeholders de plantilla en spec.md",
            ", ".join(found_placeholders),
        )
    else:
        report.add(PASS, "spec.md", "Sin placeholders de plantilla en spec.md")

    clarifications = len(re.findall(r"\[NEEDS CLARIFICATION", spec))
    if clarifications > 3:
        report.add(
            FAIL,
            "spec.md",
            "Hay más de 3 NEEDS CLARIFICATION",
            f"{clarifications} marcadores",
        )
    elif clarifications:
        report.add(
            WARN,
            "spec.md",
            "El spec conserva NEEDS CLARIFICATION",
            f"{clarifications} marcador(es); resolver con /speckit.clarify",
        )
    else:
        report.add(PASS, "spec.md", "Sin NEEDS CLARIFICATION")

    found_stack = [
        term
        for term in STACK_TERMS
        if re.search(rf"\b{re.escape(term)}\b", spec, re.I)
    ]
    if found_stack:
        report.add(
            FAIL,
            "spec.md",
            "El spec debe ser agnóstico a la tecnología",
            "términos encontrados: " + ", ".join(found_stack),
        )
    else:
        report.add(PASS, "spec.md", "Sin términos de stack en el spec")

    flowchart_blocks: list[str] = []
    for _, story in stories:
        flowchart_blocks.extend(diagrams_of(story, "flowchart"))
    labels: list[str] = []
    for block in flowchart_blocks:
        labels.extend(extract_flowchart_labels(block))
    labels = sorted(set(labels))
    prose = strip_comments(strip_mermaid(spec)).lower()
    repeated = [label for label in labels if label.lower() in prose]
    if labels and len(repeated) / len(labels) >= 0.7:
        report.add(
            WARN,
            "spec.md",
            "Posible duplicación texto/diagrama (heurística)",
            f"{len(repeated)}/{len(labels)} etiquetas también aparecen en prosa; revisar manualmente",
        )
    else:
        report.add(
            PASS,
            "spec.md",
            "Sin duplicación evidente texto/diagrama (heurística)",
        )


def check_plan(feature: Path, report: Report) -> None:
    plan = read_text(feature / "plan.md")
    if plan is None:
        report.add(FAIL, "plan.md", "El archivo existe")
        return
    report.add(PASS, "plan.md", "El archivo existe")

    check_required_sections(
        report,
        "plan.md",
        plan,
        [
            ("Summary", r"^Summary$"),
            ("Technical Context", r"^Technical Context$"),
            ("Constitution Check", r"^Constitution Check$"),
            ("C4 Level 3 (Components)", r"^Architecture.*C4 Level 3"),
            ("Sequence Diagram", r"^Sequence Diagram$"),
            ("Domain Model — Class Diagram", r"^Domain Model.*Class Diagram"),
            ("Contracts", r"^Contracts$"),
            ("Project Structure", r"^Project Structure$"),
            ("Complexity Tracking", r"^Complexity Tracking$"),
        ],
    )

    c4 = get_section(plan, r"^Architecture.*C4 Level 3")
    if c4:
        blocks = diagrams_of(c4, "C4Component")
        if blocks:
            report.add(PASS, "plan.md", "Diagrama C4 L3 C4Component")
            block = blocks[0]
            components = re.findall(r"\bComponent(?:Db)?\s*\(", block)
            relationships = re.findall(r"\b(?:Rel|BiRel)\s*\(", block)
            if len(components) >= 2:
                report.add(
                    PASS,
                    "plan.md",
                    "C4 L3 declara componentes",
                    f"{len(components)} componentes",
                )
            else:
                report.add(
                    FAIL,
                    "plan.md",
                    "C4 L3 debe declarar al menos 2 componentes",
                    f"{len(components)} componentes",
                )
            if len(relationships) >= 1:
                report.add(
                    PASS,
                    "plan.md",
                    "C4 L3 declara relaciones",
                    f"{len(relationships)} relaciones",
                )
            else:
                report.add(FAIL, "plan.md", "C4 L3 no declara relaciones")
        else:
            report.add(
                FAIL,
                "plan.md",
                "Falta un bloque Mermaid C4Component en C4 Level 3",
            )

    sequence = get_section(plan, r"^Sequence Diagram$")
    if sequence:
        blocks = diagrams_of(sequence, "sequenceDiagram")
        if blocks:
            messages = len(re.findall(r"->>|-->>", blocks[0]))
            if messages >= 3:
                report.add(
                    PASS,
                    "plan.md",
                    "Diagrama de secuencia con llamadas",
                    f"{messages} mensajes",
                )
            else:
                report.add(
                    FAIL,
                    "plan.md",
                    "El diagrama de secuencia tiene menos de 3 mensajes",
                    f"{messages} mensajes",
                )
        else:
            report.add(
                FAIL,
                "plan.md",
                "Falta un bloque Mermaid sequenceDiagram",
            )

    domain = get_section(plan, r"^Domain Model.*Class Diagram")
    if domain:
        blocks = diagrams_of(domain, "classDiagram")
        if blocks:
            block = blocks[0]
            classes = len(re.findall(r"^\s*class\s+\w+", block, re.M))
            relations = len(re.findall(r"-->|--|\.\.>", block))
            if classes >= 2 and relations >= 1:
                report.add(
                    PASS,
                    "plan.md",
                    "Diagrama de clases de dominio",
                    f"{classes} clases, {relations} relaciones",
                )
            else:
                report.add(
                    FAIL,
                    "plan.md",
                    "El class diagram debe tener al menos 2 clases y 1 relación",
                    f"{classes} clases, {relations} relaciones",
                )
        else:
            report.add(
                FAIL,
                "plan.md",
                "Falta un bloque Mermaid classDiagram",
            )

    for kind, label in [
        ("erDiagram", "ER"),
        ("stateDiagram-v2", "diagrama de estados"),
        ("C4Context", "C4 L1"),
        ("C4Container", "C4 L2"),
    ]:
        if has_diagram(plan, kind):
            report.add(
                FAIL,
                "plan.md",
                f"plan.md no debe duplicar el {label}; vive en otro artefacto",
            )
        else:
            report.add(PASS, "plan.md", f"Sin {label} duplicado en plan.md")

    if not (feature / "data-model.md").is_file():
        report.add(FAIL, "plan.md", "data-model.md no fue generado por el plan")

    contracts = feature / "contracts"
    contract_files = (
        [path for path in contracts.rglob("*") if path.is_file()]
        if contracts.is_dir()
        else []
    )
    if contract_files:
        report.add(
            PASS,
            "plan.md",
            "Contratos presentes en contracts/",
            f"{len(contract_files)} archivo(s)",
        )
    else:
        report.add(
            FAIL,
            "plan.md",
            "El plan debe generar al menos un contrato en contracts/",
        )
    if re.search(r"contracts/", plan, re.I):
        report.add(PASS, "plan.md", "plan.md enlaza a contracts/")
    else:
        report.add(WARN, "plan.md", "plan.md no enlaza explícitamente a contracts/")

    for name in ("research.md", "quickstart.md"):
        if (feature / name).is_file():
            report.add(PASS, "plan.md", f"{name} generado por el plan")
        else:
            report.add(WARN, "plan.md", f"{name} no fue generado")

    placeholders = [
        "__SPECKIT_COMMAND_PLAN__",
        "[FEATURE]",
        "[DATE]",
        "[link]",
        "[###-feature-name]",
        "[###-feature]",
        "[e.g.",
        "[current need]",
        "[why 3 projects insufficient]",
        "[Document the selected structure",
        "[REMOVE IF UNUSED]",
        "[2-3 lines:",
    ]
    found = [token for token in placeholders if token in plan]
    if found:
        report.add(
            FAIL,
            "plan.md",
            "Quedaron placeholders de plantilla en plan.md",
            ", ".join(found),
        )
    else:
        report.add(PASS, "plan.md", "Sin placeholders de plantilla en plan.md")

    if "NEEDS CLARIFICATION" in plan:
        report.add(
            WARN,
            "plan.md",
            "plan.md conserva NEEDS CLARIFICATION; el plan debe resolverlas",
        )
    else:
        report.add(PASS, "plan.md", "Sin NEEDS CLARIFICATION en plan.md")

    constitution_check = get_section(plan, r"^Constitution Check$")
    if constitution_check:
        body = strip_comments(body_of(constitution_check)).strip()
        if "Gates determined based on constitution file" in body:
            report.add(
                FAIL,
                "plan.md",
                "Constitution Check quedó con el texto de ejemplo de la plantilla",
            )
        elif len([line for line in body.splitlines() if line.strip()]) < 2:
            report.add(
                WARN,
                "plan.md",
                "Constitution Check parece vacío",
            )
        else:
            report.add(PASS, "plan.md", "Constitution Check completado")

    summary = get_section(plan, r"^Summary$")
    summary_lines = [
        line
        for line in strip_comments(body_of(summary)).splitlines()
        if line.strip()
    ]
    if len(summary_lines) > 6:
        report.add(
            WARN,
            "plan.md",
            "Summary demasiado largo; la addenda pide 2-3 líneas",
            f"{len(summary_lines)} líneas",
        )
    else:
        report.add(PASS, "plan.md", "Summary compacto")

    technical = get_section(plan, r"^Technical Context$")
    missing_stack = [
        term
        for term in ("Java", "Spring", "Vaadin", "PostgreSQL")
        if term.lower() not in technical.lower()
    ]
    if missing_stack:
        report.add(
            WARN,
            "plan.md",
            "Technical Context no menciona parte del stack esperado",
            ", ".join(missing_stack),
        )
    else:
        report.add(PASS, "plan.md", "Technical Context con el stack esperado")

    structure = get_section(plan, r"^Project Structure$")
    if "src/" in structure or "tests/" in structure:
        report.add(PASS, "plan.md", "Project Structure con rutas reales")
    else:
        report.add(WARN, "plan.md", "Project Structure sin rutas src/ o tests/")


def check_data_model(feature: Path, report: Report) -> None:
    data_model = read_text(feature / "data-model.md")
    if data_model is None:
        report.add(FAIL, "data-model.md", "El archivo existe")
        return
    report.add(PASS, "data-model.md", "El archivo existe")

    check_required_sections(
        report,
        "data-model.md",
        data_model,
        [
            ("Entities", r"^Entities$"),
            ("Entity-Relationship Diagram", r"^Entity-Relationship Diagram$"),
            ("Fields and Constraints", r"^Fields and Constraints$"),
            ("Validation Rules", r"^Validation Rules$"),
        ],
    )

    er = get_section(data_model, r"^Entity-Relationship Diagram$")
    if er:
        blocks = diagrams_of(er, "erDiagram")
        if blocks:
            report.add(PASS, "data-model.md", "Diagrama ER erDiagram")
            block = blocks[0]
            relationships = len(re.findall(r"\|\|--o\{|\}o--\|\||\|\|--\|\|", block))
            entity_blocks = len(re.findall(r"^\s*[A-Z][A-Z0-9_]*\s*\{", block, re.M))
            if relationships >= 1:
                report.add(
                    PASS,
                    "data-model.md",
                    "El ER declara relaciones",
                    f"{relationships} relación(es)",
                )
            else:
                report.add(FAIL, "data-model.md", "El ER no declara relaciones")
            if entity_blocks >= 2:
                report.add(
                    PASS,
                    "data-model.md",
                    "El ER declara entidades",
                    f"{entity_blocks} entidades",
                )
            else:
                report.add(
                    WARN,
                    "data-model.md",
                    "El ER declara menos de 2 entidades",
                    f"{entity_blocks} entidades",
                )
        else:
            report.add(
                FAIL,
                "data-model.md",
                "Falta un bloque Mermaid erDiagram",
            )

    for kind, label in [
        ("classDiagram", "class diagram de dominio"),
        ("stateDiagram-v2", "diagrama de estados"),
        ("sequenceDiagram", "diagrama de secuencia"),
        ("C4Component", "C4 L3"),
    ]:
        if has_diagram(data_model, kind):
            report.add(
                FAIL,
                "data-model.md",
                f"data-model.md no debe duplicar el {label}",
            )
        else:
            report.add(
                PASS,
                "data-model.md",
                f"Sin {label} duplicado en data-model.md",
            )

    table_rows = [
        line
        for line in data_model.splitlines()
        if line.strip().startswith("|") and line.count("|") >= 4
    ]
    if len(table_rows) >= 4:
        report.add(
            PASS,
            "data-model.md",
            "Tabla de campos y constraints",
            f"{len(table_rows)} filas",
        )
    else:
        report.add(
            FAIL,
            "data-model.md",
            "Falta la tabla de campos y constraints",
            f"{len(table_rows)} filas",
        )

    if re.search(r"^\s*\|\s*Entity\s*\|", data_model, re.M | re.I):
        report.add(PASS, "data-model.md", "La tabla tiene columna Entity")
    else:
        report.add(WARN, "data-model.md", "La tabla no tiene columna Entity")

    state_transitions = get_section(data_model, r"^State Transitions$")
    if state_transitions and re.search(r"spec\.md", state_transitions, re.I):
        report.add(
            PASS,
            "data-model.md",
            "State Transitions referencia el diagrama de spec.md",
        )
    else:
        report.add(
            WARN,
            "data-model.md",
            "Falta la referencia a spec.md en State Transitions",
        )

    placeholders = [
        "ENTITY_A",
        "ENTITY_B",
        "[Entity 1]",
        "[Entity 2]",
        "[FEATURE]",
        "[What it represents",
        "[Rule that cannot",
    ]
    found = [token for token in placeholders if token in data_model]
    if found:
        report.add(
            FAIL,
            "data-model.md",
            "Quedaron placeholders de plantilla en data-model.md",
            ", ".join(found),
        )
    else:
        report.add(
            PASS,
            "data-model.md",
            "Sin placeholders de plantilla en data-model.md",
        )


def task_lines(text: str) -> list[str]:
    return [
        line.strip()
        for line in text.splitlines()
        if re.match(r"^\s*-\s*\[\s*\]\s*T", line)
    ]


def check_tasks(project: Path, feature: Path, report: Report) -> None:
    tasks = read_text(feature / "tasks.md")
    if tasks is None:
        report.add(FAIL, "tasks.md", "El archivo existe")
        return
    report.add(PASS, "tasks.md", "El archivo existe")

    check_required_sections(
        report,
        "tasks.md",
        tasks,
        [
            ("Acceptance Suite Precondition", r"^Acceptance Suite Precondition$"),
            ("Test Policy", r"^Test Policy$"),
            ("Setup", r"^Phase 1:\s*Setup"),
            ("Foundational", r"^Phase 2:\s*Foundational"),
            ("User Story phase", r"^Phase \d+.*User Story"),
            ("Polish", r"^Phase .*Polish|^Polish"),
            ("Dependencies & Execution Order", r"^Dependencies & Execution Order$"),
            ("Implementation Strategy", r"^Implementation Strategy$"),
        ],
    )

    task_line_list = task_lines(tasks)
    if len(task_line_list) >= 5:
        report.add(
            PASS,
            "tasks.md",
            "Cantidad de tareas",
            f"{len(task_line_list)} tareas",
        )
    else:
        report.add(
            FAIL,
            "tasks.md",
            "Se esperaban al menos 5 tareas ejecutables",
            f"{len(task_line_list)} tareas",
        )

    valid_tasks: list[str] = []
    invalid_tasks: list[str] = []
    for line in task_line_list:
        if re.match(r"^-\s*\[\s*\]\s*T\d+\b", line):
            valid_tasks.append(line)
        else:
            invalid_tasks.append(line)
    if invalid_tasks:
        report.add(
            FAIL,
            "tasks.md",
            "Hay tareas con formato inválido (se espera - [ ] T001 ...)",
            invalid_tasks[0][:100],
        )
    else:
        report.add(PASS, "tasks.md", "Formato de tareas T-nnn correcto")

    task_ids = [re.match(r"^-\s*\[\s*\]\s*(T\d+)", line).group(1) for line in valid_tasks]
    duplicates = sorted({task_id for task_id in task_ids if task_ids.count(task_id) > 1})
    if duplicates:
        report.add(
            FAIL,
            "tasks.md",
            "Hay ids de tarea duplicados",
            ", ".join(duplicates),
        )
    else:
        report.add(PASS, "tasks.md", "Ids de tarea únicos")

    with_path = [
        line
        for line in valid_tasks
        if re.search(r"`[^`]+`", line)
        or re.search(r"(?:src|tests|specs)/", line)
        or re.search(r"[\w.-]+\.(?:java|kt|ts|tsx|js|py|sql|yaml|yml|xml|md)", line)
    ]
    if valid_tasks and len(with_path) / len(valid_tasks) >= 0.8:
        report.add(
            PASS,
            "tasks.md",
            "Las tareas incluyen rutas de archivo",
            f"{len(with_path)}/{len(valid_tasks)}",
        )
    else:
        report.add(
            WARN,
            "tasks.md",
            "Varias tareas no incluyen una ruta de archivo",
            f"{len(with_path)}/{len(valid_tasks)}",
        )

    categories = {
        "unit": r"\bunit(?: test|aria)?\b|prueba unitaria",
        "integration": r"\bintegration\b|integración",
        "architecture": r"\barch(?:itecture|unit)\b|arquitectura",
        "contract": r"\bcontract tests?\b|pruebas? de contrato",
    }
    found_categories = []
    for name, pattern in categories.items():
        if any(re.search(pattern, line, re.I) for line in valid_tasks):
            found_categories.append(name)
    if found_categories:
        report.add(
            PASS,
            "tasks.md",
            "Tareas de caja blanca presentes",
            ", ".join(found_categories),
        )
    else:
        report.add(
            FAIL,
            "tasks.md",
            "No hay tareas de pruebas de caja blanca (unit/integration/architecture/contract)",
        )
    missing_categories = [name for name in categories if name not in found_categories]
    if missing_categories:
        report.add(
            WARN,
            "tasks.md",
            "Faltan categorías de caja blanca de la política",
            ", ".join(missing_categories),
        )

    banned_patterns = [
        r"\bacceptance test",
        r"\bprueba de aceptación",
        r"\bacceptance suite\b",
        r"\be2e test",
        r"\bend-to-end test",
        r"\bend to end test",
        r"\bplaywright test",
        r"\bprueba e2e",
        r"\bload test",
        r"\bprueba de carga",
        r"\bk6\b",
        r"tests/acceptance/",
    ]

    def is_acceptance_task(line: str) -> bool:
        low = line.lower()
        # Dependency/configuration setup is Build infrastructure, not an
        # acceptance/E2E authoring task, even if it mentions Playwright.
        if any(term in low for term in ("dependenc", "configur", "pom.xml", "build.gradle")):
            return False
        return any(re.search(pattern, low) for pattern in banned_patterns)

    bad_tasks = [line for line in valid_tasks if is_acceptance_task(line)]
    if bad_tasks:
        report.add(
            FAIL,
            "tasks.md",
            "tasks.md contiene tareas de aceptación/E2E/carga",
            bad_tasks[0][:120],
        )
    else:
        report.add(
            PASS,
            "tasks.md",
            "Sin tareas de aceptación/E2E/carga en tasks.md",
        )

    tdd_lines = []
    for line in tasks.splitlines():
        low = line.lower()
        if any(term in low for term in ("test-first", "tests first", "tdd", "test primero")):
            if not any(neg in low for neg in ("no ", "not ", "sin ", "do not", "avoid")):
                tdd_lines.append(line.strip())
    if tdd_lines:
        report.add(
            WARN,
            "tasks.md",
            "Posible imposición de test-first/TDD",
            tdd_lines[0][:120],
        )
    else:
        report.add(PASS, "tasks.md", "Sin imposición de test-first/TDD")

    precondition = get_section(tasks, r"^Acceptance Suite Precondition$")
    if precondition:
        if "tests/acceptance/" in precondition:
            report.add(
                PASS,
                "tasks.md",
                "La precondición referencia tests/acceptance/",
            )
        else:
            report.add(
                WARN,
                "tasks.md",
                "La precondición no referencia tests/acceptance/",
            )
        if re.search(r"^-\s*\[\s*\]\s*T\d+", precondition, re.M):
            report.add(
                FAIL,
                "tasks.md",
                "La precondición de aceptación contiene tareas T-nnn",
            )
        else:
            report.add(
                PASS,
                "tasks.md",
                "La precondición de aceptación no es una tarea",
            )

    spec = read_text(feature / "spec.md") or ""
    story_numbers = sorted({int(number) for number in re.findall(r"User Story\s+(\d+)", spec, re.I)})
    for number in story_numbers:
        if f"[US{number}]" in tasks:
            report.add(
                PASS,
                "tasks.md",
                f"Tareas etiquetadas para US{number}",
            )
        else:
            report.add(
                FAIL,
                "tasks.md",
                f"No hay tareas etiquetadas [US{number}]",
            )

    if "[P]" in tasks:
        report.add(PASS, "tasks.md", "Marcadores de paralelismo [P] presentes")
    else:
        report.add(WARN, "tasks.md", "No hay tareas paralelizables [P]")

    placeholders = [
        "TXXX",
        "[TaskID]",
        "[Story]",
        "[Brief Title]",
        "[FEATURE NAME]",
        "[Title]",
        "[Brief description]",
        "[How to verify]",
        "[domain rule]",
        "[repository/adapter]",
        "[endpoint]",
        "[layer rule]",
        "[Entity]",
        "[path]",
    ]
    found = [token for token in placeholders if token in tasks]
    if found:
        report.add(
            FAIL,
            "tasks.md",
            "Quedaron placeholders de plantilla en tasks.md",
            ", ".join(found),
        )
    else:
        report.add(PASS, "tasks.md", "Sin placeholders de plantilla en tasks.md")


def check_preset(project: Path, report: Report) -> None:
    preset = project / ".specify" / "presets" / "hybrid-methodology"
    if (preset / "preset.yml").is_file():
        report.add(PASS, "preset", "Preset hybrid-methodology instalado")
    else:
        report.add(
            FAIL,
            "preset",
            "No está instalado .specify/presets/hybrid-methodology/preset.yml",
        )
        return

    expected_templates = {
        "spec-template.md": ["usecase-beta", "stateDiagram-v2", "CA-1"],
        "plan-template.md": ["C4Component", "sequenceDiagram", "classDiagram"],
        "tasks-template.md": [
            "Acceptance Suite Precondition",
            "White-Box Tests",
        ],
        "data-model-template.md": ["erDiagram"],
    }
    for name, markers in expected_templates.items():
        path = preset / "templates" / name
        if not path.is_file():
            report.add(FAIL, "preset", f"Falta la plantilla {name}")
            continue
        text = path.read_text(encoding="utf-8")
        missing = [marker for marker in markers if marker not in text]
        if missing:
            report.add(
                FAIL,
                "preset",
                f"La plantilla {name} no contiene la sección híbrida",
                ", ".join(missing),
            )
        else:
            report.add(PASS, "preset", f"Plantilla híbrida: {name}")

    core_constitution = project / ".specify" / "templates" / "constitution-template.md"
    if core_constitution.is_file():
        core_text = core_constitution.read_text(encoding="utf-8")
        if "[PROJECT_NAME]" in core_text and "[PRINCIPLE_1_NAME]" in core_text:
            report.add(
                PASS,
                "preset",
                "Plantilla core de constitución intacta",
            )
        else:
            report.add(
                WARN,
                "preset",
                "La plantilla core de constitución no parece ser la original",
            )
    else:
        report.add(
            FAIL,
            "preset",
            "Falta .specify/templates/constitution-template.md (core)",
        )

    expected_commands = {
        "speckit.constitution.md": "Hybrid Methodology Constitution Rules",
        "speckit.specify.md": "Hybrid Methodology Specification Rules",
        "speckit.plan.md": "Hybrid Methodology Plan Rules",
        "speckit.tasks.md": "Hybrid Methodology Task Rules",
        "speckit.implement.md": "Hybrid Methodology Implementation Rules",
    }
    commands_dir = project / ".opencode" / "commands"
    for name, marker in expected_commands.items():
        path = commands_dir / name
        if not path.is_file():
            report.add(FAIL, "preset", f"Falta el comando compuesto {name}")
            continue
        if marker in path.read_text(encoding="utf-8"):
            report.add(PASS, "preset", f"Reglas híbridas aplicadas: {name}")
        else:
            report.add(
                FAIL,
                "preset",
                f"El comando {name} no contiene sus reglas híbridas",
            )


def check_constitution(project: Path, report: Report) -> None:
    constitution_path = project / ".specify" / "memory" / "constitution.md"
    constitution = read_text(constitution_path)
    if constitution is None:
        report.add(FAIL, "constitution.md", "El archivo existe")
        return
    report.add(PASS, "constitution.md", "El archivo existe")

    check_required_sections(
        report,
        "constitution.md",
        constitution,
        [
            (
                "C4 Level 1 (System Context)",
                r"C4 Level 1|C4 Nivel 1",
            ),
            (
                "C4 Level 2 (Containers)",
                r"C4 Level 2|C4 Nivel 2",
            ),
            (
                "Technical Constraints and Platform Standards",
                r"^Technical Constraints and Platform Standards$|^Restricciones T[eé]cnicas",
            ),
            (
                "Workflow and Gates",
                r"^Workflow and Gates$|^Flujo de Trabajo y Puertas$",
            ),
            ("Governance", r"^Governance$|^Gobernanza$"),
        ],
    )

    c4_context = get_section(
        constitution,
        r"C4 Level 1|C4 Nivel 1",
    )
    if c4_context:
        if diagrams_of(c4_context, "C4Context"):
            report.add(PASS, "constitution.md", "Diagrama C4 L1 C4Context")
        else:
            report.add(FAIL, "constitution.md", "Falta un bloque C4Context")

    c4_container = get_section(
        constitution,
        r"C4 Level 2|C4 Nivel 2",
    )
    if c4_container:
        if diagrams_of(c4_container, "C4Container"):
            report.add(PASS, "constitution.md", "Diagrama C4 L2 C4Container")
        else:
            report.add(FAIL, "constitution.md", "Falta un bloque C4Container")

    principles = re.findall(
        r"^###\s+(I|II|III|IV|V|VI)\.\s+\S",
        constitution,
        re.M,
    )
    if len(principles) >= 5:
        report.add(
            PASS,
            "constitution.md",
            "Principios de la plantilla híbrida presentes",
            f"{len(principles)} principios",
        )
    elif len(principles) >= 4:
        report.add(
            WARN,
            "constitution.md",
            "Faltan principios de la plantilla híbrida",
            f"{len(principles)}/5",
        )
    else:
        report.add(
            FAIL,
            "constitution.md",
            "No se encontraron los principios de la plantilla híbrida",
            f"{len(principles)}/5",
        )

    forbidden = [
        (r"/speckit\.", "comandos /speckit.*"),
        (r"\bpresets?\b", "presets"),
        (r"\baddendas?\b", "addendas"),
        (
            r"Preservaci[oó]n del N[uú]cleo|Core Preservation",
            "principio de preservación del núcleo",
        ),
    ]
    found_forbidden = [
        label for pattern, label in forbidden if re.search(pattern, constitution, re.I)
    ]
    if found_forbidden:
        report.add(
            FAIL,
            "constitution.md",
            "La constitución describe mecánica de la herramienta",
            ", ".join(found_forbidden),
        )
    else:
        report.add(
            PASS,
            "constitution.md",
            "Sin mecánica de la herramienta en la constitución",
        )

    if re.search(r"Spec Kit", constitution, re.I):
        report.add(
            WARN,
            "constitution.md",
            "La constitución menciona Spec Kit; debería ser agnóstica a la herramienta",
        )
    else:
        report.add(PASS, "constitution.md", "Sin mención de Spec Kit")

    mermaid_ci = []
    for line in constitution.splitlines():
        low = line.lower()
        if "mermaid" not in low:
            continue
        if "pipeline" not in low and not re.search(r"\bci\b", low):
            continue
        if any(
            term in low
            for term in ("local", "no se añade", "no se valida", "no se ejecuta")
        ):
            continue
        mermaid_ci.append(line.strip())

    if mermaid_ci:
        report.add(
            FAIL,
            "constitution.md",
            "La validación Mermaid debe ser local, no en CI",
            mermaid_ci[0][:160],
        )
    else:
        report.add(
            PASS,
            "constitution.md",
            "Validación Mermaid local, sin requisito de CI",
        )

    placeholders = [
        "[PROJECT_NAME]",
        "[PRINCIPLE_1_NAME]",
        "[PRINCIPLE_1_DESCRIPTION]",
        "[CONSTITUTION_VERSION]",
        "[RATIFICATION_DATE]",
        "[LAST_AMENDED_DATE]",
    ]
    found = [token for token in placeholders if token in constitution]
    generic = re.findall(
        r"\[(?:PRINCIPLE|SECTION|GOVERNANCE)_[A-Z0-9_]+\]",
        constitution,
    )
    if found or generic:
        report.add(
            FAIL,
            "constitution.md",
            "Quedaron placeholders de plantilla en constitution.md",
            ", ".join(sorted(set(found + generic))),
        )
    else:
        report.add(
            PASS,
            "constitution.md",
            "Sin placeholders de plantilla en constitution.md",
        )


def check_cross(project: Path, feature: Path, report: Report) -> None:
    skip_parts = {".git", "target", "node_modules", ".specify", "build", "dist"}
    feature_files = []
    for path in project.rglob("*.feature"):
        if any(part in skip_parts for part in path.parts):
            continue
        feature_files.append(path)
    if feature_files:
        report.add(
            FAIL,
            "transversal",
            "No debe haber archivos .feature",
            f"{len(feature_files)} archivo(s), por ejemplo {feature_files[0].name}",
        )
    else:
        report.add(PASS, "transversal", "Sin archivos .feature")

    gherkin_hits = []
    for name in ("spec.md", "plan.md", "data-model.md", "tasks.md"):
        text = read_text(feature / name)
        if text and re.search(r"\bgherkin\b", text, re.I):
            gherkin_hits.append(name)
    if gherkin_hits:
        report.add(
            FAIL,
            "transversal",
            "Los artefactos no deben mencionar Gherkin",
            ", ".join(gherkin_hits),
        )
    else:
        report.add(PASS, "transversal", "Los artefactos no mencionan Gherkin")

    acceptance_dir = project / "tests" / "acceptance"
    if acceptance_dir.is_dir():
        files = [path for path in acceptance_dir.rglob("*") if path.is_file()]
        if files:
            report.add(
                WARN,
                "transversal",
                "tests/acceptance/ tiene archivos antes de que Build implemente",
                f"{len(files)} archivo(s); los comandos specify/plan/tasks no deben generarlo",
            )
        else:
            report.add(
                PASS,
                "transversal",
                "tests/acceptance/ existe pero está vacío",
            )
    else:
        report.add(
            PASS,
            "transversal",
            "Los comandos no generaron tests/acceptance/",
        )

    checklist = feature / "checklists" / "requirements.md"
    if checklist.is_file():
        report.add(PASS, "transversal", "Checklist de calidad del spec generado")
    else:
        report.add(
            WARN,
            "transversal",
            "No se generó checklists/requirements.md con /speckit.specify",
        )

    feature_json = project / ".specify" / "feature.json"
    if feature_json.is_file():
        report.add(PASS, "transversal", ".specify/feature.json presente")
    else:
        report.add(
            WARN,
            "transversal",
            ".specify/feature.json ausente; los comandos posteriores pueden no ubicar la feature",
        )


def check_mermaid(feature: Path, report: Report, mmdc: str | None) -> None:
    if not mmdc:
        report.add(
            SKIP,
            "Mermaid",
            "Validación Mermaid no ejecutada; usa --mmdc mmdc",
        )
        return

    script = Path(__file__).resolve().with_name("validate_mermaid.py")
    if not script.is_file():
        report.add(
            FAIL,
            "Mermaid",
            "No se encontró validate_mermaid.py junto a este verificador",
        )
        return

    try:
        proc = subprocess.run(
            [sys.executable, str(script), str(feature), "--mmdc", mmdc],
            capture_output=True,
            text=True,
            timeout=600,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        report.add(FAIL, "Mermaid", "No se pudo ejecutar el validador", str(exc))
        return

    output = (proc.stdout or "").strip().splitlines()
    detail = output[-1] if output else (proc.stderr or "").strip()[-200:]
    if proc.returncode == 0:
        report.add(PASS, "Mermaid", "Todos los bloques Mermaid renderizan", detail)
    else:
        report.add(
            FAIL,
            "Mermaid",
            "Hay bloques Mermaid que no renderizan",
            detail,
        )


def resolve_feature(project: Path, feature_arg: str | None) -> Path | None:
    if feature_arg:
        path = Path(feature_arg)
        if not path.is_absolute():
            path = project / path
        path = path.resolve()
        return path if path.is_dir() else None

    feature_json = project / ".specify" / "feature.json"
    if feature_json.is_file():
        try:
            data = json.loads(feature_json.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            data = {}
        relative = data.get("feature_directory")
        if isinstance(relative, str) and relative:
            path = (project / relative).resolve()
            if path.is_dir():
                return path

    specs = project / "specs"
    if not specs.is_dir():
        return None
    candidates = sorted(
        path
        for path in specs.iterdir()
        if path.is_dir() and (path / "spec.md").is_file()
    )
    if len(candidates) == 1:
        return candidates[0]
    if candidates:
        return max(candidates, key=lambda path: path.stat().st_mtime)
    return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Valida los artefactos generados por el preset híbrido de Spec Kit."
    )
    parser.add_argument(
        "--project",
        default=".",
        help="Raíz del proyecto Spec Kit (por defecto: el directorio actual).",
    )
    parser.add_argument(
        "--feature",
        help="Directorio de la feature, relativo al proyecto o absoluto.",
    )
    parser.add_argument(
        "--stage",
        choices=("spec", "plan", "tasks", "all"),
        default="all",
        help="Hasta dónde validar (por defecto: all).",
    )
    parser.add_argument(
        "--mmdc",
        help="Ruta al ejecutable mmdc para validar los diagramas Mermaid.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Trata los WARN como fallos.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emite el resultado en JSON en lugar de tabla.",
    )
    args = parser.parse_args()

    project = Path(args.project).expanduser().resolve()
    if not project.is_dir():
        print(f"ERROR: no existe el proyecto {project}", file=sys.stderr)
        return 2

    feature = resolve_feature(project, args.feature)
    if feature is None:
        print(
            "ERROR: no se encontró una feature. Ejecuta /speckit.specify primero "
            "o pasa --feature specs/NNN-nombre.",
            file=sys.stderr,
        )
        return 2

    report = Report()
    check_preset(project, report)
    check_constitution(project, report)
    check_spec(feature, report)
    if args.stage in ("plan", "tasks", "all"):
        check_plan(feature, report)
        check_data_model(feature, report)
    if args.stage in ("tasks", "all"):
        check_tasks(project, feature, report)
    check_cross(project, feature, report)
    check_mermaid(feature, report, args.mmdc)

    failed = report.has_fail() or (args.strict and report.count(WARN) > 0)

    if args.json:
        payload = report.to_dict()
        payload["project"] = str(project)
        payload["feature"] = str(feature)
        payload["stage"] = args.stage
        payload["ok"] = not failed
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print("=== Validación de overrides híbridos ===")
        print(f"Proyecto: {project}")
        print(f"Feature:  {feature}")
        print(f"Etapa:    {args.stage}")
        report.print_table()
        print()
        if failed:
            print("Estado: NO APTO")
            print("Corrige los FAIL (y los WARN si usaste --strict) y vuelve a ejecutar.")
        elif report.count(WARN) > 0:
            print("Estado: APTO CON ADVERTENCIAS")
            print("Revisa los WARN manualmente antes de cerrar la validación.")
        else:
            print("Estado: APTO")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
