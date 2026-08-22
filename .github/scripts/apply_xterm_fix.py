#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Re-apply the xterm macOptionClickForcesSelection fix to term.tsx.

Idempotent: exits 0 if the fix is already present.

Usage:
    uv run --script .github/scripts/apply_xterm_fix.py
"""
import sys
from pathlib import Path

TERM_TSX = Path("frontend/app/view/term/term.tsx")

if not TERM_TSX.exists():
    print(f"⚠️  {TERM_TSX} not found — skipping xterm fix")
    sys.exit(0)

content = TERM_TSX.read_text()

if "macOptionClickForcesSelection: termMacOptionIsMeta" in content:
    print(f"✅ xterm fix already present in {TERM_TSX}")
    sys.exit(0)

OLD = "                macOptionIsMeta: termMacOptionIsMeta,"
NEW = """                macOptionIsMeta: termMacOptionIsMeta,
                  // When macOptionIsMeta is enabled, also set macOptionClickForcesSelection=true.
                  // Without this, xterm.js still activates column-select mode (crosshair cursor)
                  // when holding Option, because shouldColumnSelect() checks
                  // macOptionClickForcesSelection independently of macOptionIsMeta.
                  // See: xterm.js SelectionService.ts#shouldColumnSelect()
                  macOptionClickForcesSelection: termMacOptionIsMeta,"""

if OLD not in content:
    print(f"Pattern not found in {TERM_TSX} — the file structure may have changed.")
    sys.exit(1)

TERM_TSX.write_text(content.replace(OLD, NEW, 1))
print(f"✅ Patched {TERM_TSX}")
