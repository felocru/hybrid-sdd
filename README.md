# Hybrid SDD

Adaptación de **GitHub Spec Kit** a la **Metodología Híbrida de Desarrollo** (Scrum + SDD + SDT + agentes).

Incluye:

- **Preset `hybrid-methodology` v0.1.0**: plantillas y addendas para `spec.md`, `plan.md`, `tasks.md` y `data-model.md`.
- **Extensión `hybrid-sdt` v0.1.0**: comando de aceptación en contexto aislado y setup del subagente `sdt-tester`.
- **Bundle `hybrid-sdd` v0.1.0**: composición del preset y la extensión.

## Instalación desde catálogo

```bash
specify preset catalog add https://raw.githubusercontent.com/felocru/hybrid-sdd/main/catalog/presets.json \
  --name hybrid-catalog --install-allowed

specify extension catalog add https://raw.githubusercontent.com/felocru/hybrid-sdd/main/catalog/extensions.json \
  --name hybrid-catalog --install-allowed

specify bundle catalog add https://raw.githubusercontent.com/felocru/hybrid-sdd/main/catalog/bundles.json \
  --policy install-allowed --id hybrid-catalog

specify bundle install hybrid-sdd
```

Después del bundle, instala el agente una vez:

```text
/speckit.hybrid-sdt.setup
```

El bundle no copia `.opencode/agents/sdt-tester.md`; el comando de setup lo instala desde la extensión.

## Instalación local

```bash
specify preset add --dev ./preset --priority 5
specify extension add ./extension/hybrid-sdt --dev
/speckit.hybrid-sdt.setup
```

## Comandos

| Comando | Propósito |
| :--- | :--- |
| `/speckit.constitution` | Constitución del proyecto con C4 L1/L2 |
| `/speckit.specify` | Especificación de negocio con casos de uso, flujos, estados y CA |
| `/speckit.plan` | Plan técnico con C4 L3, secuencia, clases y contratos |
| `/speckit.tasks` | Tareas de Build y caja blanca |
| `/speckit.hybrid-sdt.setup` | Instala el subagente `sdt-tester` |
| `/speckit.hybrid-sdt.sdt-test` | Genera la suite de aceptación en contexto aislado |

En el piloto existen alias `/hybrid.setup` y `/hybrid.sdt-test`; los nombres canónicos de la extensión son los `speckit.hybrid-sdt.*`.

## Separación de documentos

| Archivo | Propósito |
| :--- | :--- |
| `constitution.md` | Principios, arquitectura global, restricciones y gates |
| `spec.md` | Caso de uso, reglas de negocio, flujos, estados y CA |
| `plan.md` | C4 L3, secuencia, clases y decisiones técnicas |
| `data-model.md` | ER, entidades, campos y constraints |
| `tasks.md` | Tareas de Build y caja blanca |
| `contracts/` | Contratos técnicos de API/UI |
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
│   ├── hybrid-methodology-0.1.0.zip
│   ├── hybrid-sdt-0.1.0.zip
│   ├── hybrid-sdd-0.1.0.zip
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
python3 scripts/build_release.py --repo felocru/hybrid-sdd --tag v0.1.0
```

El primer comando genera los zips. El segundo genera los catálogos y `RELEASE.md`.

## Estado

- Preset, extensión y bundle en `v0.1.0`.
- Validación Mermaid local con `mmdc` 12+.
- La validación semántica de las especificaciones se hace con subagentes independientes.
- El workflow `hybrid-sdd` es la siguiente fase.

## Advertencias

- Las plantillas son una extensión de Spec Kit para agregarles diagramas de software.
- El bundle no incrusta el preset, la extensión ni el agente; los componentes se resuelven desde catálogos o instalación previa.
- `AGENTS.md` contiene los comandos operativos de pruebas; la constitución no los duplica.
