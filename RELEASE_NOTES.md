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
