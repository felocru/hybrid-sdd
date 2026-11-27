#!/usr/bin/env bash
set -euo pipefail

EXT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_ROOT="$(pwd)"
TARGET=""

usage() {
  echo "Uso: bash install-agent.sh [--target opencode|agy|all]" >&2
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --target)
      if [ "$#" -lt 2 ]; then
        echo "ERROR: --target requiere un valor (opencode, agy o all)." >&2
        usage
        exit 1
      fi
      TARGET="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "ERROR: argumento no reconocido: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [ ! -d "$PROJECT_ROOT/.specify" ]; then
  echo "ERROR: ejecuta este comando desde la raíz del proyecto Spec Kit." >&2
  exit 1
fi

install_opencode=false
install_agy=false

if [ -n "$TARGET" ]; then
  case "$TARGET" in
    opencode) install_opencode=true ;;
    agy) install_agy=true ;;
    all)
      install_opencode=true
      install_agy=true
      ;;
    *)
      echo "ERROR: --target inválido '$TARGET'. Usa opencode, agy o all." >&2
      exit 1
      ;;
  esac
else
  INTEGRATION_JSON="$PROJECT_ROOT/.specify/integration.json"
  if [ -f "$INTEGRATION_JSON" ]; then
    if command -v python3 >/dev/null 2>&1; then
      detected="$(python3 - "$INTEGRATION_JSON" <<'PY'
import json, sys
try:
    data = json.load(open(sys.argv[1], encoding="utf-8"))
except Exception:
    sys.exit(0)
items = set(data.get("installed_integrations") or [])
for key in ("integration", "default_integration"):
    val = data.get(key)
    if isinstance(val, str) and val:
        items.add(val)
print(" ".join(sorted(items)))
PY
)"
      for item in $detected; do
        [ "$item" = "opencode" ] && install_opencode=true
        [ "$item" = "agy" ] && install_agy=true
      done
    else
      grep -q '"opencode"' "$INTEGRATION_JSON" && install_opencode=true
      grep -q '"agy"' "$INTEGRATION_JSON" && install_agy=true
    fi
  fi

  [ -d "$PROJECT_ROOT/.opencode" ] && install_opencode=true
  [ -d "$PROJECT_ROOT/.agents" ] && install_agy=true
fi

if [ "$install_opencode" = false ] && [ "$install_agy" = false ]; then
  echo "ERROR: no se detectó ninguna integración OpenCode (.opencode/) ni Antigravity (.agents/)." >&2
  echo "Ejecuta de nuevo especificando --target opencode, --target agy o --target all." >&2
  exit 1
fi

if [ "$install_opencode" = true ]; then
  mkdir -p "$PROJECT_ROOT/.opencode/agents"
  cp "$EXT_DIR/agents/opencode/sdt-tester.md" "$PROJECT_ROOT/.opencode/agents/sdt-tester.md"
  echo "sdt-tester instalado en .opencode/agents/sdt-tester.md"
fi

if [ "$install_agy" = true ]; then
  mkdir -p "$PROJECT_ROOT/.agents/agents/sdt-tester"
  cp "$EXT_DIR/agents/agy/sdt-tester.md" "$PROJECT_ROOT/.agents/agents/sdt-tester/agent.md"
  echo "sdt-tester instalado en .agents/agents/sdt-tester/agent.md"
fi
