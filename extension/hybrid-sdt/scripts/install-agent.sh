#!/usr/bin/env bash
set -euo pipefail

EXT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PROJECT_ROOT="$(pwd)"

if [ ! -d "$PROJECT_ROOT/.specify" ]; then
  echo "ERROR: ejecuta este comando desde la raíz del proyecto Spec Kit." >&2
  exit 1
fi

mkdir -p "$PROJECT_ROOT/.opencode/agents"
cp "$EXT_DIR/agents/sdt-tester.md" "$PROJECT_ROOT/.opencode/agents/sdt-tester.md"
echo "sdt-tester instalado en .opencode/agents/"
