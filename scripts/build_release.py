#!/usr/bin/env python3
"""Build the hybrid Spec Kit release artifacts and catalogs.

Usage:
    python3 scripts/build_release.py
    python3 scripts/build_release.py --repo owner/repo --tag v0.1.0

Without --repo, it builds the preset/extension/bundle zips and SHA256SUMS.
With --repo, it also generates the three catalogs for GitHub Releases.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
CATALOG = ROOT / "catalog"
PRESET = ROOT / "preset"
EXTENSION = ROOT / "extension" / "hybrid-sdt"
BUNDLE = ROOT / "bundle"

VERSION = "0.1.0"
PRESET_ID = "hybrid-methodology"
EXTENSION_ID = "hybrid-sdt"
BUNDLE_ID = "hybrid-sdd"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def zip_dir(source: Path, destination: Path) -> None:
    with zipfile.ZipFile(destination, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(source).as_posix())


def build_bundle() -> Path:
    result = subprocess.run(
        [
            "specify",
            "bundle",
            "build",
            "--path",
            str(BUNDLE),
            "--output",
            str(DIST),
        ],
        text=True,
        capture_output=True,
    )
    if result.returncode != 0:
        raise SystemExit(result.stderr.strip() or result.stdout.strip())
    artifact = DIST / f"{BUNDLE_ID}-{VERSION}.zip"
    if not artifact.is_file():
        raise SystemExit(f"No se generó {artifact}")
    return artifact


def catalog_entry(
    *,
    name: str,
    description: str,
    author: str,
    repo: str,
    tag: str,
    filename: str,
    digest: str,
    kind: str,
) -> dict:
    base = f"https://github.com/{repo}/releases/download/{tag}/{filename}"
    entry = {
        "name": name,
        "id": "",
        "version": VERSION,
        "description": description,
        "author": author,
        "repository": f"https://github.com/{repo}",
        "download_url": base,
        "sha256": digest,
        "license": "Internal",
        "requires": {"speckit_version": ">=1.2.3"},
        "tags": ["hybrid", "sdd", "sdt"],
        "verified": False,
    }
    if kind == "preset":
        entry["id"] = PRESET_ID
        entry["provides"] = {"templates": 4, "commands": 5}
    elif kind == "extension":
        entry["id"] = EXTENSION_ID
        entry["category"] = "process"
        entry["effect"] = "read-write"
        entry["provides"] = {"commands": 2, "hooks": 0}
    else:
        entry["id"] = BUNDLE_ID
        entry["role"] = "developer"
        entry["provides"] = {
            "extensions": 1,
            "presets": 1,
            "steps": 0,
            "workflows": 0,
        }
    return entry


def write_catalog(kind: str, entry: dict, repo: str, tag: str) -> Path:
    path = CATALOG / f"{kind}s.json"
    payload = {
        "schema_version": "1.0",
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "catalog_url": f"https://raw.githubusercontent.com/{repo}/main/catalog/{kind}s.json",
        kind + "s": {entry["id"]: entry},
    }
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return path


def write_release(repo: str, tag: str, hashes: dict[str, str]) -> None:
    preset = f"hybrid-methodology-{VERSION}.zip"
    extension = f"hybrid-sdt-{VERSION}.zip"
    bundle = f"hybrid-sdd-{VERSION}.zip"
    release = ROOT / "RELEASE.md"
    release.write_text(
        f"""# Release v{VERSION}

## Publicar

1. Crea el repositorio `{repo}`.
2. Crea el tag `{tag}` y un GitHub Release.
3. Sube a ese release:

```text
dist/{preset}
dist/{extension}
dist/{bundle}
```

4. Confirma que `catalog/` esté en la rama `main`.
5. Verifica que los catálogos sean accesibles por HTTPS.

## Instalar desde catálogo

```bash
specify preset catalog add https://raw.githubusercontent.com/{repo}/main/catalog/presets.json \\
  --name hybrid-catalog --install-allowed

specify extension catalog add https://raw.githubusercontent.com/{repo}/main/catalog/extensions.json \\
  --name hybrid-catalog --install-allowed

specify bundle catalog add https://raw.githubusercontent.com/{repo}/main/catalog/bundles.json \\
  --policy install-allowed --id hybrid-catalog

specify bundle install {BUNDLE_ID}
```

Después del bundle:

```text
/speckit.hybrid-sdt.setup
```

## SHA-256

```text
{hashes[preset]}  {preset}
{hashes[extension]}  {extension}
{hashes[bundle]}  {bundle}
```
""",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", help="owner/repo de GitHub")
    parser.add_argument("--tag", default=f"v{VERSION}")
    args = parser.parse_args()

    DIST.mkdir(parents=True, exist_ok=True)
    CATALOG.mkdir(parents=True, exist_ok=True)

    preset_zip = DIST / f"{PRESET_ID}-{VERSION}.zip"
    extension_zip = DIST / f"{EXTENSION_ID}-{VERSION}.zip"

    zip_dir(PRESET, preset_zip)
    zip_dir(EXTENSION, extension_zip)
    bundle_zip = build_bundle()

    hashes = {
        preset_zip.name: sha256(preset_zip),
        extension_zip.name: sha256(extension_zip),
        bundle_zip.name: sha256(bundle_zip),
    }

    (DIST / "SHA256SUMS").write_text(
        "".join(f"{digest}  {name}\n" for name, digest in hashes.items()),
        encoding="utf-8",
    )

    if not args.repo:
        print("Zips y SHA256SUMS generados en", DIST)
        print("Falta --repo owner/repo para generar los catálogos.")
        return 0

    repo = args.repo.strip().strip("/")
    entries = {
        "preset": catalog_entry(
            name="Metodología Híbrida de Desarrollo",
            description="Plantillas y addendas híbridas para especificación, plan y tareas.",
            author="Metodología Híbrida",
            repo=repo,
            tag=args.tag,
            filename=preset_zip.name,
            digest=hashes[preset_zip.name],
            kind="preset",
        ),
        "extension": catalog_entry(
            name="Hybrid SDT",
            description="Suite de aceptación y setup del subagente tester.",
            author="Metodología Híbrida",
            repo=repo,
            tag=args.tag,
            filename=extension_zip.name,
            digest=hashes[extension_zip.name],
            kind="extension",
        ),
        "bundle": catalog_entry(
            name="Hybrid SDD",
            description="Bundle de la Metodología Híbrida: preset y extensión SDT.",
            author="Metodología Híbrida",
            repo=repo,
            tag=args.tag,
            filename=bundle_zip.name,
            digest=hashes[bundle_zip.name],
            kind="bundle",
        ),
    }

    for kind, entry in entries.items():
        path = write_catalog(kind, entry, repo, args.tag)
        print(f"Catálogo: {path}")

    write_release(repo, args.tag, hashes)
    print(f"Release: {ROOT / 'RELEASE.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
