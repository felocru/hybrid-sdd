# Release v0.1.0

## Publicar

1. Repositorio: `felocru/hybrid-sdd`.
2. Release: `v0.1.0` (https://github.com/felocru/hybrid-sdd/releases/tag/v0.1.0).
3. Sube a ese release:

```text
dist/hybrid-methodology-0.1.0.zip
dist/hybrid-sdt-0.1.0.zip
dist/hybrid-sdd-0.1.0.zip
```

4. Confirma que `catalog/` esté en la rama `main`.
5. Verifica que los catálogos sean accesibles por HTTPS.

## Instalar desde catálogo

```bash
specify preset catalog add https://raw.githubusercontent.com/felocru/hybrid-sdd/main/catalog/presets.json \
  --name hybrid-catalog --install-allowed

specify extension catalog add https://raw.githubusercontent.com/felocru/hybrid-sdd/main/catalog/extensions.json \
  --name hybrid-catalog --install-allowed

specify bundle catalog add https://raw.githubusercontent.com/felocru/hybrid-sdd/main/catalog/bundles.json \
  --policy install-allowed --id hybrid-catalog

specify bundle install hybrid-sdd
```

Después del bundle:

```text
/speckit.hybrid-sdt.setup
```

## SHA-256

```text
ffb7e47917250f41b3a3c96cc6177f55ce884147e1f4fcbf4e8a30aa93d3de23  hybrid-methodology-0.1.0.zip
75a7a5903f0ef6a99e9413f26cccd9423f98e8be2a7e6c392099ba7a1c70e789  hybrid-sdt-0.1.0.zip
70f0b14e1e46dde3c4a01ec9bc17815247b9da29f331dc87612bff03773e325f  hybrid-sdd-0.1.0.zip
```
