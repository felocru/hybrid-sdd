# Release v0.3.0

## Publicar

1. Usa el repositorio `felocru/hybrid-sdd`.
2. Crea o verifica el tag `v0.3.0` y el GitHub Release.
3. Sube a ese release:

```text
dist/hybrid-methodology-0.3.0.zip
dist/hybrid-sdt-0.3.0.zip
dist/hybrid-sdd-0.3.0.zip
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
937ac5ed452b554a5d9470ebcb6e0b34d8834ce5c86549b09e62af2284924356  hybrid-methodology-0.3.0.zip
a9df66eebc6bf936b18a4d548bff7a4220b4b00bbff5b950c6e41d3554e4af4f  hybrid-sdt-0.3.0.zip
854f6f9a366a700e6e239a825daa6bdc4112a171a82f058ae7b3f479e9cb0e8e  hybrid-sdd-0.3.0.zip
```
