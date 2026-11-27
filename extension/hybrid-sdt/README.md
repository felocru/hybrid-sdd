# Hybrid SDT

Extensión de Spec Kit para el bucle externo de aceptación, compatible con **OpenCode** y **Antigravity CLI (`agy`)**.

## Comandos

- `speckit.hybrid-sdt.setup` (`/speckit-hybrid-sdt-setup` en Antigravity): instala el subagente `sdt-tester` en `.opencode/agents/sdt-tester.md` y/o `.agents/agents/sdt-tester/agent.md` según los arneses detectados.
- `speckit.hybrid-sdt.sdt-test` (`/speckit-hybrid-sdt-sdt-test` en Antigravity): genera la suite de aceptación/E2E/carga en contexto aislado delegando en `@sdt-tester`.

## Instalación

```bash
specify extension add hybrid-sdt --dev ./extension/hybrid-sdt
```

Después de instalar, ejecuta una vez dentro del arnés:

- En Antigravity CLI: `/speckit-hybrid-sdt-setup`
- En OpenCode: `/speckit.hybrid-sdt.setup`

O directamente en terminal desde la raíz del proyecto:

```bash
bash .specify/extensions/hybrid-sdt/scripts/install-agent.sh [--target opencode|agy|all]
```

El setup es explícito: no hay hook que lo ejecute en cada `/speckit.tasks`.

## Notas

- Spec Kit no instala subagentes nativos de `.opencode/agents/` ni `.agents/agents/` al instalar una extensión; `install-agent.sh` copia la definición específica de cada arnés (`agents/opencode/sdt-tester.md` o `agents/agy/sdt-tester.md`).
- En Antigravity CLI (`Orchestrator`), el Orquestador (`Gemini 4 Neon`) delega `/speckit-hybrid-sdt-sdt-test` a `@sdt-tester` en un contexto limpio (sin pasar `plan.md`, `data-model.md`, `tasks.md`, `design/` ni `src/main/`) y al finalizar valida que los cambios se limiten a `tests/acceptance/` y exista la matriz `CA-n -> test`.
- Las reglas de testing viven en la constitución y `AGENTS.md`; el comando y el agente son agnósticos a la tecnología.
