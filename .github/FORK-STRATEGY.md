# Fork Maintenance Strategy

This fork of [wavetermdev/waveterm](https://github.com/wavetermdev/waveterm) is kept
mergeable with upstream using a **revert-then-repatch** strategy.

## Branch model

| Branch | Tracks | Purpose |
|--------|--------|---------|
| `main` | Latest upstream release tag (e.g. `v0.14.5`) | Stable — well-tested patches only |
| `dev`  | `upstream/main` (latest development) | Unstable — experimental patches welcome |

## What lives where

### Tier 1: Config files (NOT in this repo)

User-level config lives in `~/.config/waveterm/` and is managed via dotfiles:

- `settings.json`, `connections.json`, `widgets.json`
- `termthemes.json`, `backgrounds.json`, `waveai.json`
- `presets/ai.json`, `bookmarks.json`

**Never commit these to the fork.** They're user-specific and would conflict.

### Tier 2: External plugins (NOT in this repo)

Plugins like `wave-term-tabs` are separate repos, built independently and loaded
via `widgets.json` at runtime. They don't touch the WaveTerm source tree.

### Tier 3: Source patches (in this repo)

Actual changes to upstream source files. These are the only things that risk
merge conflicts. Each patch has:

1. **A PEP 723 script** in `.github/scripts/` that applies the patch idempotently
2. **An entry in `PATCHED_FILES`** in the sync workflow env var
3. **A re-apply step** in `.github/workflows/sync-upstream-and-fix.yml`

Current patches:

| Patch | Script | File | Branch |
|-------|--------|------|--------|
| xterm cursor fix | `apply_xterm_fix.py` | `frontend/app/view/term/term.tsx` | `main` + `dev` |
| bookmark typeahead fix | `apply_bookmark_fix.py` | `frontend/app/view/webview/webview.tsx` | `dev` only |

## How the sync works

The `sync-upstream-and-fix.yml` workflow runs daily at 07:00 UTC (or manually):

```
1. Revert all PATCHED_FILES to upstream's version → commit
2. Merge upstream (normal merge, no strategy override)
3. If merge conflicts on non-patched files → FAIL LOUDLY
4. Re-apply each patch via `uv run --script .github/scripts/apply_*.py`
5. If a patch script's pattern doesn't match → FAIL LOUDLY
6. Push the updated branch
```

### Why revert-then-repatch instead of `--strategy-option=theirs`?

`--strategy-option=theirs` silently lets upstream overwrite custom patches.
The revert-then-repatch approach:

- **Guarantees patches are always re-applied** on the latest upstream code
- **Fails loudly** if upstream changed the surrounding code (pattern mismatch)
- **Fails loudly** if there are conflicts on files we don't patch
- **Never silently drops** a custom change

## Adding a new patch

1. **Write the patch script** as a PEP 723 file in `.github/scripts/`:

   ```python
   #!/usr/bin/env -S uv run --script
   # /// script
   # requires-python = ">=3.11"
   # dependencies = []
   # ///
   """Fix: <description>. Idempotent. Ref: <upstream issue/PR>"""
   import sys
   from pathlib import Path

   TARGET = Path("path/to/file.tsx")
   content = TARGET.read_text()

   # Idempotency check
   if "unique marker string from the patch" in content:
       print(f"✅ already patched in {TARGET}")
       sys.exit(0)

   # Apply patch
   OLD = "exact string to find"
   NEW = "replacement string"
   if OLD not in content:
       print(f"❌ pattern not found in {TARGET} — upstream may have changed it")
       sys.exit(1)
   TARGET.write_text(content.replace(OLD, NEW, 1))
   print(f"✅ patched {TARGET}")
   ```

2. **Add the file to `PATCHED_FILES`** in `.github/workflows/sync-upstream-and-fix.yml`

3. **Add re-apply + commit steps** to the relevant job(s) in the workflow

4. **Apply the patch manually** to the branch (`uv run --script .github/scripts/apply_*.py`)

5. **Commit and push**

## Rules

- **Never edit upstream files directly** — always via a patch script
- **Never use `--strategy-option=theirs`** — it silently drops changes
- **Keep patches minimal** — one logical change per script
- **Make scripts idempotent** — check if the patch is already present
- **Fail loudly** — `sys.exit(1)` with a clear message if patterns don't match
- **Test locally** before pushing: `uv run --script .github/scripts/apply_*.py`
