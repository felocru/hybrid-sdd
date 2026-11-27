# Hybrid SDD v0.3.0

Soporte dual para **Antigravity CLI (`agy`)** y **OpenCode** manteniendo la fuente única de comandos y el aislamiento estricto de la Metodología Híbrida.

## Qué cambia

- **Subagente `sdt-tester` por arnés**:
  - `extension/hybrid-sdt/agents/opencode/sdt-tester.md` (sin cambios funcionales para OpenCode).
  - `extension/hybrid-sdt/agents/agy/sdt-tester.md` con frontmatter nativo de Antigravity (`subagent: true`, `mainAgent: false`, `model: inherit`, `commandExecutionPolicy: sandbox`).
- **`install-agent.sh` multi-arnés**: autodetecta `.specify/integration.json`, `.opencode/` y `.agents/` (o acepta `--target opencode|agy|all`) para instalar `.opencode/agents/sdt-tester.md` y/o `.agents/agents/sdt-tester/agent.md`.
- **Comandos portables**:
  - `speckit.hybrid-sdt.setup` instruye explícitamente la ejecución del script de instalación sin depender de sintaxis exclusiva de OpenCode.
  - `speckit.hybrid-sdt.sdt-test` agrega el protocolo explícito de delegación aislada para el Orquestador en Antigravity (`invoke_subagent` a `sdt-tester` sin pasar `plan.md`, `data-model.md`, `tasks.md`, `design/` ni `src/main/`, y validación posterior de `tests/acceptance/` y matriz `CA-n -> test`), manteniendo el frontmatter de OpenCode.
- **Validador**: `scripts/validate_overrides.py` valida comandos híbridos tanto en `.opencode/commands/` como en `.agents/skills/speckit-*/SKILL.md`.
- **Documentación**: guía de uso con `Orchestrator (Neon)` + `Hydrogen` + `sdt-tester` en Antigravity CLI.

## Componentes

- **Preset `hybrid-methodology` 0.3.0**: bump de versión única del bundle (sin cambios funcionales respecto a 0.2.3).
- **Extensión `hybrid-sdt` 0.3.0**: soporte dual OpenCode + Antigravity CLI (`agy`).
- **Bundle `hybrid-sdd` 0.3.0**: composición actualizada.

---

# Hybrid SDD v0.2.3

`/speckit.implement` se ejecuta como **subagente con `opencode-go/deepseek-v4.1-flash#max`** de forma durable: el frontmatter del `implement.append.md` viaja en el preset y la composición lo usa como frontmatter de mayor prioridad (los `scripts` se heredan del comando base). Antes, cualquier frontmatter local del comando se perdía en cada `preset update` / `bundle update`.

Nota de composición: los demás comandos (`specify`, `plan`, `tasks`, `constitution`) y el tester (`sdt-test`, `glm-5.3#max`) no cambian.

## Componentes

- **Preset `hybrid-methodology` 0.2.3**: frontmatter con `model` + `subagent` para `speckit.implement`.
- **Extensión `hybrid-sdt` 0.2.3**: sin cambios funcionales (bump de versión única del bundle).
- **Bundle `hybrid-sdd` 0.2.3**: composición actualizada.

---

# Hybrid SDD v0.2.2

`/speckit.plan` crea el diseño cuando no existe: para features con UI, tras redactar el `ui-contract` y antes de congelarlo, el plan genera las pantallas en la herramienta de diseño vía MCP (capas nombradas con los identificadores canónicos) y exporta la referencia congelada en PNG+SVG. El diseño es un artefacto derivado del contrato; los huecos que surjan al maquetar se corrigen primero en el contrato.

Antes: si no existía diseño, el plan lo saltaba y dejaba la columna "Capa" como pendiente. Ahora solo queda pendiente si la herramienta de diseño no está disponible.

## Componentes

- **Preset `hybrid-methodology` 0.2.2**: `plan.append` con la ruta from-scratch; export PNG+SVG documentado.
- **Extensión `hybrid-sdt` 0.2.2**: sin cambios funcionales (bump de versión única del bundle).
- **Bundle `hybrid-sdd` 0.2.2**: composición actualizada.

---

# Hybrid SDD v0.2.1

El subagente tester (`speckit.hybrid-sdt.sdt-test` y `sdt-tester`) usa por defecto `opencode-go/glm-5.3#max` en lugar de `glm-5.3-flash#max`. Sin cambios funcionales en el preset respecto a 0.2.0.

## Componentes

- **Preset `hybrid-methodology` 0.2.1**: idéntico a 0.2.0 (bump de versión para mantener la versión única del bundle).
- **Extensión `hybrid-sdt` 0.2.1**: modelo por defecto `glm-5.3#max` en comando y subagente.
- **Bundle `hybrid-sdd` 0.2.1**: composición actualizada.

---

# Hybrid SDD v0.2.0

Contrato de UI con **identificadores canónicos** como fuente única de identidad para el tester aislado, el Build y el diseño (Principio VI de la constitución).

## Qué cambia

- **Preset `hybrid-methodology` 0.2.0**
  - Nueva plantilla `ui-contract-template.md`: `contracts/ui-contract.md` con tabla de identificadores canónicos (ruta, elemento, `name`/`id`, etiqueta accesible, rol ARIA, `data-testid` opcional y nombre de capa del diseño).
  - `plan.append.md`: el ui-contract es obligatorio en features con UI; si ya existe un diseño (p. ej. Penpot vía su MCP de plugin), el plan importa y reconcilia los nombres de capa antes de congelar el contrato (el contrato canoniza, el diseño adopta) y exporta la referencia visual congelada a `specs/[###-feature]/design/`.
  - `implement.append.md`: el Build implementa los identificadores verbatim del contrato y verifica visualmente contra `design/` (no contra el diseño en vivo); sin lectura de imagen nativa, usa un subagente con un modelo que sí pueda leer imágenes.
  - `constitution.append.md`: nuevo **Principio VI — Single Source of UI Identity**.
  - `plan-template.md`: la sección Contracts distingue API, UI e `design/`.
- **Extensión `hybrid-sdt` 0.2.0**
  - El tester aislado deriva sus selectores exclusivamente de la tabla canónica y no consulta el diseño ni su MCP; si la tabla falta, reporta el bloqueo en vez de inventar identificadores.
- **Bundle `hybrid-sdd` 0.2.0**: composición actualizada de preset y extensión.
- **Validador**: `validate_overrides.py` exige la plantilla `ui-contract-template` instalada y valida que cada `contracts/ui-contract.md` tenga la sección de identificadores canónicos con filas de datos y sin duplicados.

## Componentes

- **Preset `hybrid-methodology` 0.2.0**: plantillas y addendas híbridas.
- **Extensión `hybrid-sdt` 0.2.0**: aceptación en contexto aislado y setup del subagente.
- **Bundle `hybrid-sdd` 0.2.0**: composición de preset + extensión.

## Instalación

```bash
specify preset catalog add https://raw.githubusercontent.com/felocru/hybrid-sdd/main/catalog/presets.json \
  --name hybrid-catalog --install-allowed

specify extension catalog add https://raw.githubusercontent.com/felocru/hybrid-sdd/main/catalog/extensions.json \
  --name hybrid-catalog --install-allowed

specify bundle catalog add https://raw.githubusercontent.com/felocru/hybrid-sdd/main/catalog/bundles.json \
  --policy install-allowed --id hybrid-catalog

specify bundle install hybrid-sdd
```

Después:

```text
/speckit.hybrid-sdt.setup
```

## Assets

- `hybrid-methodology-0.2.0.zip`
- `hybrid-sdt-0.2.0.zip`
- `hybrid-sdd-0.2.0.zip`
- `SHA256SUMS`

---

# Hybrid SDD v0.1.0

Primera versión del preset, la extensión SDT y el bundle de la Metodología Híbrida de Desarrollo para GitHub Spec Kit.

## Componentes

- **Preset `hybrid-methodology` 0.1.0**: plantillas y addendas híbridas.
- **Extensión `hybrid-sdt` 0.1.0**: aceptación en contexto aislado y setup del subagente.
- **Bundle `hybrid-sdd` 0.1.0**: composición de preset + extensión.
