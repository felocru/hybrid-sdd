# Release v0.2.0

## Publicar

1. Usa el repositorio `felocru/hybrid-sdd`.
2. Crea o verifica el tag `v0.2.0` y el GitHub Release.
3. Sube a ese release:

```text
dist/hybrid-methodology-0.2.0.zip
dist/hybrid-sdt-0.2.0.zip
dist/hybrid-sdd-0.2.0.zip
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
e4d61208ada0a5086ab08fd36074aee0cb9667c24931ee11e20242ef0c9452c5  hybrid-methodology-0.2.0.zip
d5a550c69e574191d7da7bbbda2f7ab9d54acabd5b6ce4ce609f37ffe3d8942b  hybrid-sdt-0.2.0.zip
63c9d857e1b8a16f7ca8dc57bdf48ffe1be9020c879c2397265244f60e175498  hybrid-sdd-0.2.0.zip
```
