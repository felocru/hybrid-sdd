# Hybrid SDD

Adaptación de **GitHub Spec Kit** a la **Metodología Híbrida de Desarrollo** (Scrum + SDD + SDT + agentes), compatible con **OpenCode** y **Antigravity CLI (`agy`)**.

Incluye:

- **Preset `hybrid-methodology` v0.3.0**: plantillas y addendas para `spec.md`, `plan.md`, `tasks.md`, `data-model.md` y `ui-contract.md`.
- **Extensión `hybrid-sdt` v0.3.0**: comando de aceptación en contexto aislado y setup del subagente `sdt-tester` para OpenCode y Antigravity.
- **Bundle `hybrid-sdd` v0.3.0**: composición del preset y la extensión.

## Requisitos previos

- Spec Kit CLI `1.2.3` o superior.
- **OpenCode** o **Antigravity CLI (`agy` `1.0.0+` / Antigravity IDE `2.0.0+`)**.
- Ejecuta la instalación desde el directorio padre del proyecto. Cambia `mi-proyecto` por el nombre que quieras.

## Instalación en un comando

### Con Antigravity CLI (`agy`)

```bash
specify init mi-proyecto --integration agy && \
cd mi-proyecto && \
specify preset catalog add https://raw.githubusercontent.com/felocru/hybrid-sdd/main/catalog/presets.json --name hybrid-catalog --install-allowed && \
specify extension catalog add https://raw.githubusercontent.com/felocru/hybrid-sdd/main/catalog/extensions.json --name hybrid-catalog --install-allowed && \
specify bundle catalog add https://raw.githubusercontent.com/felocru/hybrid-sdd/main/catalog/bundles.json --policy install-allowed --id hybrid-catalog && \
specify bundle install hybrid-sdd
```

Después, dentro de `agy`:

```text
/speckit-hybrid-sdt-setup
```

### Con OpenCode

```bash
specify init mi-proyecto --integration opencode && \
cd mi-proyecto && \
specify preset catalog add https://raw.githubusercontent.com/felocru/hybrid-sdd/main/catalog/presets.json --name hybrid-catalog --install-allowed && \
specify extension catalog add https://raw.githubusercontent.com/felocru/hybrid-sdd/main/catalog/extensions.json --name hybrid-catalog --install-allowed && \
specify bundle catalog add https://raw.githubusercontent.com/felocru/hybrid-sdd/main/catalog/bundles.json --policy install-allowed --id hybrid-catalog && \
specify bundle install hybrid-sdd
```

Después, dentro de OpenCode:

```text
/speckit.hybrid-sdt.setup
```

Los `catalog add` son por proyecto: esta cadena los registra y deja el bundle instalado. El setup autodetecta los arneses instalados (`.opencode/` y/o `.agents/`) y copia la definición correspondiente del subagente `sdt-tester`.

## Instalación local (desarrollo)

Desde la raíz de tu proyecto Spec Kit, apuntando al checkout de este repositorio:

```bash
specify preset add --dev /ruta/a/hybrid-sdd/preset --priority 5
specify extension add /ruta/a/hybrid-sdd/extension/hybrid-sdt --dev
bash .specify/extensions/hybrid-sdt/scripts/install-agent.sh
```

También puedes invocar el comando de setup dentro de tu arnés (`/speckit-hybrid-sdt-setup` en Antigravity o `/speckit.hybrid-sdt.setup` en OpenCode) o forzar el destino con `--target opencode|agy|all`.

## Comandos

Spec Kit compila los mismos comandos en `.opencode/commands/speckit.*.md` para OpenCode y en `.agents/skills/speckit-*/SKILL.md` para Antigravity CLI:

| OpenCode | Antigravity CLI | Propósito |
| :--- | :--- | :--- |
| `/speckit.constitution` | `/speckit-constitution` | Constitución del proyecto con C4 L1/L2 |
| `/speckit.specify` | `/speckit-specify` | Especificación de negocio con casos de uso, flujos, estados y CA |
| `/speckit.plan` | `/speckit-plan` | Plan técnico con C4 L3, secuencia, clases y contratos |
| `/speckit.tasks` | `/speckit-tasks` | Tareas de Build y caja blanca |
| `/speckit.implement` | `/speckit-implement` | Implementación Build y pruebas de caja blanca |
| `/speckit.hybrid-sdt.setup` | `/speckit-hybrid-sdt-setup` | Instala el subagente `sdt-tester` |
| `/speckit.hybrid-sdt.sdt-test` | `/speckit-hybrid-sdt-sdt-test` | Genera la suite de aceptación en contexto aislado |

En el piloto existen alias `/hybrid.setup` y `/hybrid.sdt-test`; los nombres canónicos de la extensión son los `speckit.hybrid-sdt.*`.

## Flujo recomendado en Antigravity CLI con `Orchestrator (Neon)`

En Antigravity CLI (`agy`), selecciona **`Orchestrator (Neon)`** como modelo de la sesión (`/model`):

1. **Planificación, decisiones y validación (`Gemini 4 Neon`)**: analiza cada comando (`/speckit-specify`, `/speckit-plan`, `/speckit-tasks`, `/speckit-hybrid-sdt-sdt-test`, `/speckit-implement`), resuelve ambigüedades con el humano y valida los resultados contra los gates de la metodología.
2. **Implementación Build + caja blanca (`Gemini 4 Hydrogen`)**: cuando Neon aprueba el plan de ejecución de `/speckit-implement`, el arnés delega automáticamente la escritura de código y pruebas unitarias/integración/ArchUnit/contrato a **Gemini 4 Hydrogen**; si algo falla repetidamente o falta una decisión, el control vuelve a Neon.
3. **Pruebas de aceptación en contexto aislado (`sdt-tester`)**: al ejecutar `/speckit-hybrid-sdt-sdt-test`, el Orquestador no genera ni ejecuta las pruebas directamente ni comparte `plan.md`, `data-model.md`, `tasks.md`, `design/` o `src/main/`; delega al subagente `sdt-tester` (`.agents/agents/sdt-tester/agent.md`, con `model: inherit` y `commandExecutionPolicy: sandbox`), quien corre con ventana de contexto limpia leyendo únicamente `.specify/feature.json`, `spec.md`, `contracts/`, la sección de testing de `constitution.md`, `AGENTS.md` y `tests/acceptance/`. Al finalizar el subagente, el Orquestador valida con `git status` que solo se haya escrito en `tests/acceptance/`, verifica la matriz `CA-n -> test` en `tests/acceptance/README.md` y entrega la suite en rojo para revisión QA/PO y commit dedicado.

## Separación de documentos

| Archivo | Propósito |
| :--- | :--- |
| `constitution.md` | Principios, arquitectura global, restricciones y gates |
| `spec.md` | Caso de uso, reglas de negocio, flujos, estados y CA |
| `plan.md` | C4 L3, secuencia, clases y decisiones técnicas |
| `data-model.md` | ER, entidades, campos y constraints |
| `tasks.md` | Tareas de Build y caja blanca |
| `contracts/` | Contratos técnicos de API |
| `contracts/ui-contract.md` | Fuente única de identificadores de UI (Principio VI): tabla canónica para tester, Build y diseño |
| `design/` | Referencia visual congelada del diseño, exportada durante el plan |
| `AGENTS.md` | Manual operativo del agente: comandos de build/test y entorno |

La constitución es normativa. `AGENTS.md` es operativo y no debe contradecirla.

## Estructura del repositorio

```text
.
├── README.md
├── RELEASE.md
├── catalog/
│   ├── presets.json
│   ├── extensions.json
│   └── bundles.json
├── templates/
├── commands/
├── preset/
├── extension/
│   └── hybrid-sdt/
├── bundle/
├── dist/
│   ├── hybrid-methodology-0.3.0.zip
│   ├── hybrid-sdt-0.3.0.zip
│   ├── hybrid-sdd-0.3.0.zip
│   └── SHA256SUMS
├── scripts/
│   ├── build_release.py
│   ├── validate_mermaid.py
│   └── validate_overrides.py
└── pilot/
```

## Desarrollo

```bash
python3 scripts/build_release.py
python3 scripts/build_release.py --repo felocru/hybrid-sdd --tag v0.3.0
```

El primer comando genera los zips. El segundo genera los catálogos y `RELEASE.md`.

## Estado

- Preset, extensión y bundle en `v0.3.0`: soporte dual **OpenCode + Antigravity CLI (`agy`)**, con subagente `sdt-tester` por arnés y delegación aislada compatible con `Orchestrator (Neon)` + `Hydrogen`.
- Validación Mermaid local con `mmdc` 12+.
- La validación semántica de las especificaciones se hace con subagentes independientes.
- El workflow `hybrid-sdd` es la siguiente fase.

## Advertencias

- Las plantillas son una extensión de Spec Kit para agregarles diagramas de software.
- El bundle no incrusta el preset, la extensión ni el agente; los componentes se resuelven desde catálogos o instalación previa.
- `AGENTS.md` contiene los comandos operativos de pruebas; la constitución no los duplica.
