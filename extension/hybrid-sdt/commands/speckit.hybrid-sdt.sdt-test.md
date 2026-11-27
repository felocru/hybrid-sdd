---
description: Genera la suite de aceptación/E2E/carga para la feature activa en contexto aislado.
agent: sdt-tester
model: opencode-go/glm-5.3#max
subagent: true
---

## Protocolo de aislamiento y delegación (Orquestador / agente principal)

- Si ya estás ejecutando dentro del subagente `sdt-tester` (por ejemplo, invocado directamente por el arnés en OpenCode), omite este protocolo y ejecuta directamente las `Instrucciones del tester aislado`.
- Si eres el agente principal u Orquestador (por ejemplo, Antigravity CLI ejecutando `/speckit-hybrid-sdt-sdt-test`):
  1. **NO** escribas ni ejecutes la suite de aceptación tú mismo.
  2. **NO** leas ni resumas `plan.md`, `data-model.md`, `tasks.md`, `research.md`, `quickstart.md`, `design/` ni `src/main/` en el prompt del subagente.
  3. Lee únicamente `.specify/feature.json` para obtener la ruta de la feature activa (si falta, pregunta al usuario y detente).
  4. Delega la tarea al subagente `sdt-tester` en contexto aislado usando `invoke_subagent` con `TypeName: "sdt-tester"` y `Model: "inherit"` (cuando estés en `Orchestrator`, la invocación desde el ejecutor Hydrogen hereda Hydrogen; el Orquestador planifica, delega y valida).
     - Si el tipo `sdt-tester` no estuviera registrado en la sesión actual, verifica si existe `.agents/agents/sdt-tester/agent.md` (si falta, ejecuta `bash .specify/extensions/hybrid-sdt/scripts/install-agent.sh` primero) y créalo en la sesión con `define_subagent` (`EnableWriteTools: true`, `EnableMCPTools: false`, `EnableSubagentTools: false`) cargando las instrucciones de `.agents/agents/sdt-tester/agent.md`.
  5. Entrega al subagente un prompt mínimo con **únicamente** la ruta de la feature activa y las `Instrucciones del tester aislado`, sin historial previo ni contexto técnico de implementación.
  6. **Validación del Orquestador al recibir el reporte del subagente**:
     - Ejecuta `git status --short` y verifica que solo haya archivos nuevos o modificados dentro de `tests/acceptance/`. Si se modificó cualquier otro archivo (`spec.md`, `contracts/`, `plan.md`, `tasks.md`, `src/main/`, etc.), repórtalo como violación de aislamiento.
     - Verifica que exista `tests/acceptance/README.md` con la matriz `CA-n -> test` cubriendo todos los `CA-n` declarados en `spec.md`.
     - Confirma que la suite de aceptación corrió en rojo y presenta el resumen al humano para revisión de QA/PO y commit dedicado (Gate 3). No hagas commit automático.

## Instrucciones del tester aislado

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
