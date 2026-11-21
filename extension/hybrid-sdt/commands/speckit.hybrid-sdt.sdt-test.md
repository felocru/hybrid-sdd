---
description: Genera la suite de aceptación/E2E/carga para la feature activa en contexto aislado.
agent: sdt-tester
model: opencode-go/glm-5.3-flash#max
subagent: true
---

Genera la suite de aceptación para la feature activa.

1. Lee `.specify/feature.json`, ubica el `spec.md` y los `contracts/` de esa feature.
2. Lee la sección de testing de `.specify/memory/constitution.md`.
3. Si la feature tiene UI, deriva los selectores exclusivamente de la tabla de identificadores canónicos de `contracts/ui-contract.md`: rol + etiqueta accesible, o `data-testid` cuando la tabla lo declare. No inventes selectores ni consultes el diseño ni su MCP.
4. Si la feature tiene UI y falta `contracts/ui-contract.md` o su tabla canónica, repórtalo como bloqueo y pregunta; no generes la suite de UI con identificadores inventados.
5. Genera las pruebas de aceptación API, E2E y carga en `tests/acceptance/`.
6. Traza cada CA de `spec.md` a al menos una prueba y deja la matriz en `tests/acceptance/README.md`.
7. No leas `plan.md`, `data-model.md`, `tasks.md` ni `src/main/`; tampoco el diseño ni `design/`.
8. No edites `spec.md`, `contracts/`, `plan.md`, `tasks.md` ni código de producción.
9. Ejecuta la suite con el comando declarado en `AGENTS.md`. No asumas Maven, npm ni otra tecnología; si el comando no está definido, pregunta.
10. Los fallos en rojo son esperados. Reporta resultados y supuestos.
11. No congeles la suite: QA/PO la revisan y el humano hace el commit dedicado.
