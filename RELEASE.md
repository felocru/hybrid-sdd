# Release v0.2.3

## Publicar

1. Usa el repositorio `felocru/hybrid-sdd`.
2. Crea o verifica el tag `v0.2.3` y el GitHub Release.
3. Sube a ese release:

```text
dist/hybrid-methodology-0.2.3.zip
dist/hybrid-sdt-0.2.3.zip
dist/hybrid-sdd-0.2.3.zip
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
51eeb68d0c641c9145af499e6cc94b67095f1780ac94f7ec4f86f542281b68e7  hybrid-methodology-0.2.3.zip
17430331e79fa2100e883c2f91d8a8fa5c71f02e0b120cdd65234ee6617d2536  hybrid-sdt-0.2.3.zip
dba2b9a4718c0490d264c2b5274265989c5b156de82218beb748fb25df2a7305  hybrid-sdd-0.2.3.zip
```
