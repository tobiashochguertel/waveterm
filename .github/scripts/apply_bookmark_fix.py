#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Re-apply the bookmark typeahead fix to webview.tsx.

Fixes:
1. Convert fetchBookmarkSuggestions from a regular method to an arrow
   function field so `this` stays bound when passed as a callback.
2. Fix the "Open bookmarks.json" button path from presets/bookmarks.json
   to the correct bookmarks.json at the config directory root.

Idempotent: exits 0 if the fix is already present.

Ref: wavetermdev/waveterm#3420

Usage:
    uv run --script .github/scripts/apply_bookmark_fix.py
"""
import sys
from pathlib import Path

WEBVIEW_TSX = Path("frontend/app/view/webview/webview.tsx")

if not WEBVIEW_TSX.exists():
    print(f"⚠️  {WEBVIEW_TSX} not found — skipping bookmark fix")
    sys.exit(0)

content = WEBVIEW_TSX.read_text()

if "fetchBookmarkSuggestions = async" in content:
    print(f"✅ bookmark fix already present in {WEBVIEW_TSX}")
    sys.exit(0)

# Fix 1: Convert method to arrow function field
OLD_METHOD = """    async fetchBookmarkSuggestions(
        query: string,
        reqContext: SuggestionRequestContext
    ): Promise<FetchSuggestionsResponse> {"""
NEW_ARROW = """    fetchBookmarkSuggestions = async (
        query: string,
        reqContext: SuggestionRequestContext
    ): Promise<FetchSuggestionsResponse> => {"""

if OLD_METHOD not in content:
    print("fetchBookmarkSuggestions method pattern not found — may already be fixed or file structure changed.")
    sys.exit(1)
content = content.replace(OLD_METHOD, NEW_ARROW, 1)

# Fix 2: Close the arrow function with semicolon instead of brace
OLD_RETURN = """        return result;
    }

    handleUrlWrapperMouseOver"""
NEW_RETURN = """        return result;
    };

    handleUrlWrapperMouseOver"""

if OLD_RETURN not in content:
    print("Closing brace pattern not found — may already be fixed.")
    sys.exit(1)
content = content.replace(OLD_RETURN, NEW_RETURN, 1)

# Fix 3: Fix bookmarks.json path
OLD_PATH = "${env.electron.getConfigDir()}/presets/bookmarks.json"
NEW_PATH = "${env.electron.getConfigDir()}/bookmarks.json"
content = content.replace(OLD_PATH, NEW_PATH)

WEBVIEW_TSX.write_text(content)
print(f"✅ Patched {WEBVIEW_TSX}")
