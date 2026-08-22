#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Fix: stop a de-focusing block from re-grabbing focus.

When clicking from one web block to another, both webviews become
unresponsive because the de-focusing block re-grabs DOM and logical
focus (webview-focus flap). The fix adds guards so the de-focusing
block only acts when it actually has focus.

Ref: wavetermdev/waveterm#3429

Idempotent: exits 0 if the fix is already present.

Usage:
    uv run --script .github/scripts/apply_focus_fix.py
"""
import sys
from pathlib import Path

BLOCK_TSX = Path("frontend/app/block/block.tsx")

if not BLOCK_TSX.exists():
    print(f"⚠️  {BLOCK_TSX} not found — skipping focus fix")
    sys.exit(0)

content = BLOCK_TSX.read_text()

# Idempotency: the fix adds "isFocused && focusWithin" pattern
if "if (!focusWithin && isFocused)" in content:
    print(f"✅ focus fix already present in {BLOCK_TSX}")
    sys.exit(0)

# Apply the patch
OLD = """        const focusWithin = focusedBlockId() == nodeModel.blockId;
        if (!focusWithin) {
            setFocusTarget();
        }
        if (!isFocused) {
            nodeModel.focusNode();
        }"""

NEW = """        const focusWithin = focusedBlockId() == nodeModel.blockId;
        // blockClicked is state and lags one commit, so this effect also runs when the block is
        // losing focus. In that case DOM focus already moved to another block (focusWithin is false)
        // and isFocused is false. Without these guards the de-focusing block re-grabs both DOM and
        // logical focus, which makes two web blocks fight over focus indefinitely (webview-focus flap).
        if (!focusWithin && isFocused) {
            setFocusTarget();
        }
        if (!isFocused && focusWithin) {
            nodeModel.focusNode();
        }"""

if OLD not in content:
    print(f"❌ pattern not found in {BLOCK_TSX} — upstream may have changed it")
    sys.exit(1)

BLOCK_TSX.write_text(content.replace(OLD, NEW, 1))
print(f"✅ patched {BLOCK_TSX}")
