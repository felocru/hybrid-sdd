#!/usr/bin/env python3
"""Validate Mermaid blocks in Markdown files using Mermaid CLI (mmdc).

Local-only validation. This script is intentionally not wired into CI.

Usage:
    python3 validate_mermaid.py [paths ...]
    python3 validate_mermaid.py specs/ --mmdc mmdc
    python3 validate_mermaid.py specs/ --puppeteer-config puppeteer.json

Requires:
    - Python 3.9+
    - mmdc (Mermaid CLI) 12+ for usecase-beta and C4 diagrams
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

MERMAID_BLOCK = re.compile(r"```mermaid[ \t]*\r?\n(.*?)```", re.DOTALL)


def find_markdown_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_file() and path.suffix.lower() == ".md":
            files.append(path)
        elif path.is_dir():
            files.extend(sorted(path.rglob("*.md")))
        else:
            print(f"warning: path not found or not a Markdown file: {path}", file=sys.stderr)
    return files


def extract_blocks(text: str) -> list[tuple[int, str]]:
    blocks: list[tuple[int, str]] = []
    for match in MERMAID_BLOCK.finditer(text):
        line = text.count("\n", 0, match.start()) + 1
        blocks.append((line, match.group(1)))
    return blocks


def validate_block(
    mmdc: str,
    block: str,
    source: Path,
    line: int,
    puppeteer_config: Path | None,
) -> tuple[bool, str]:
    with tempfile.TemporaryDirectory(prefix="mermaid-check-") as tmp:
        tmp_path = Path(tmp)
        input_file = tmp_path / "diagram.mmd"
        output_file = tmp_path / "diagram.svg"
        input_file.write_text(block, encoding="utf-8")

        command = [mmdc, "-i", str(input_file), "-o", str(output_file)]
        if puppeteer_config:
            command.extend(["-p", str(puppeteer_config)])

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return True, ""

        detail = (result.stderr or result.stdout or "").strip()
        return False, f"{source}:{line}: {detail}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Mermaid blocks in Markdown files using mmdc."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["."],
        help="Markdown files or directories to scan (default: current directory).",
    )
    parser.add_argument(
        "--mmdc",
        default="mmdc",
        help="Path to the Mermaid CLI executable (default: mmdc).",
    )
    parser.add_argument(
        "--puppeteer-config",
        type=Path,
        default=None,
        help="Optional Puppeteer configuration file for mmdc.",
    )
    args = parser.parse_args()

    mmdc = shutil.which(args.mmdc) or (args.mmdc if Path(args.mmdc).is_file() else None)
    if not mmdc:
        print(
            "error: mmdc was not found. Install Mermaid CLI 12+ and try again:\n"
            "  npm install -g @mermaid-js/mermaid-cli",
            file=sys.stderr,
        )
        return 2

    paths = [Path(p) for p in args.paths]
    files = find_markdown_files(paths)
    if not files:
        print("error: no Markdown files found.", file=sys.stderr)
        return 2

    total = 0
    failures: list[str] = []

    for file in files:
        try:
            text = file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            print(f"warning: skipping non-UTF-8 file: {file}", file=sys.stderr)
            continue

        for line, block in extract_blocks(text):
            total += 1
            ok, error = validate_block(
                mmdc=mmdc,
                block=block,
                source=file,
                line=line,
                puppeteer_config=args.puppeteer_config,
            )
            if not ok:
                failures.append(error)

    if failures:
        print(f"\n{len(failures)} of {total} Mermaid block(s) failed:\n", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1

    print(f"OK: {total} Mermaid block(s) validated across {len(files)} Markdown file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
