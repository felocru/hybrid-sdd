---
description: Genera la suite de aceptación/E2E/carga para la feature activa en contexto aislado.
agent: sdt-tester
subagent: true
---

Genera la suite de aceptación para la feature activa.

1. Lee `.specify/feature.json`, ubica el `spec.md` y los `contracts/` de esa feature.
2. Lee la sección de testing de `.specify/memory/constitution.md`.
3. Genera las pruebas de aceptación API, E2E y carga en `tests/acceptance/`.
4. Traza cada CA de `spec.md` a al menos una prueba y deja la matriz en `tests/acceptance/README.md`.
5. No leas `plan.md`, `data-model.md`, `tasks.md` ni `src/main/`.
6. No edites `spec.md`, `contracts/`, `plan.md`, `tasks.md` ni código de producción.
7. Ejecuta la suite con el comando declarado en `AGENTS.md`. No asumas Maven, npm ni otra tecnología; si el comando no está definido, pregunta.
8. Los fallos en rojo son esperados. Reporta resultados y supuestos.
9. No congeles la suite: QA/PO la revisan y el humano hace el commit dedicado.
