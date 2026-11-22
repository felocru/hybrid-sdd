# Release v0.2.2

## Publicar

1. Usa el repositorio `felocru/hybrid-sdd`.
2. Crea o verifica el tag `v0.2.2` y el GitHub Release.
3. Sube a ese release:

```text
dist/hybrid-methodology-0.2.2.zip
dist/hybrid-sdt-0.2.2.zip
dist/hybrid-sdd-0.2.2.zip
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
d24522439310a3fa974b1134c8841c0ad1def24cc2eb60d96a913f70c5779491  hybrid-methodology-0.2.2.zip
b7dad221e56bbb5b97de1af706fcfa0c76b2bef27824e045a865b11f197db986  hybrid-sdt-0.2.2.zip
354bfb8fa6d07a0eeeb179b1c632964920d709385eaeb1d4f69fd6ff17c6e0a7  hybrid-sdd-0.2.2.zip
```
