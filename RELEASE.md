# Release v0.2.1

## Publicar

1. Usa el repositorio `felocru/hybrid-sdd`.
2. Crea o verifica el tag `v0.2.1` y el GitHub Release.
3. Sube a ese release:

```text
dist/hybrid-methodology-0.2.1.zip
dist/hybrid-sdt-0.2.1.zip
dist/hybrid-sdd-0.2.1.zip
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
76466fc95d2fd198fa155891acc9fa9c67017d5f9bddd63a534eb983ec91d537  hybrid-methodology-0.2.1.zip
d413e4fc2e88114db69577171f27a689c609a0fddebb78ba884e2ce596118e42  hybrid-sdt-0.2.1.zip
da0dfeb86c3e90ba9279c56b39c49a7e833701720bd4ceca9124ad2b755647b7  hybrid-sdd-0.2.1.zip
```
