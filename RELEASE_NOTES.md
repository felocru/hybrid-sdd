# Hybrid SDD v0.1.0

Primera versión del preset, la extensión SDT y el bundle de la Metodología Híbrida de Desarrollo para GitHub Spec Kit.

## Componentes

- **Preset `hybrid-methodology` 0.1.0**: plantillas y addendas híbridas.
- **Extensión `hybrid-sdt` 0.1.0**: aceptación en contexto aislado y setup del subagente.
- **Bundle `hybrid-sdd` 0.1.0**: composición de preset + extensión.

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

- `hybrid-methodology-0.1.0.zip`
- `hybrid-sdt-0.1.0.zip`
- `hybrid-sdd-0.1.0.zip`
- `SHA256SUMS`
