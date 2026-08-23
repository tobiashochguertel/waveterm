# Fork Maintenance Strategy

This fork of [wavetermdev/waveterm](https://github.com/wavetermdev/waveterm) is kept
mergeable with upstream using a **revert-then-repatch** strategy.

## Branch model

| Branch | Tracks | Purpose |
|--------|--------|---------|
| `main` | Latest upstream release tag (e.g. `v0.14.5`) | Stable — well-tested patches only |
| `dev.patch` | `upstream/main` (latest development) | Unstable — experimental patches welcome |

## Upstream PR catalog

An automated catalog of open upstream PRs is maintained at
[`.github/UPSTREAM-PRS.md`](./PR-CATALOG.md) — see
[`PR-CATALOG.md`](./PR-CATALOG.md) for full documentation of the generator,
config options, and the `waveterm-prs` viewer CLI.

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

1. **A `.patch` file** in `.github/patches/` (named `NNN-description.patch`)
2. **An entry in `PATCHED_FILES`** in the sync workflow env var (modified files only — new files don't need listing)
3. **An entry in `ALREADY_INTEGRATED`** in `.github/scripts/generate_upstream_prs.py` (for the PR catalog)

Patches are applied by `.github/scripts/apply_patches.sh`, which loops over
all `.patch` files in `.github/patches/` in alphabetical order.

Current patches:

| Patch | Patch file | Files | Branch |
|-------|-----------|-------|--------|
| xterm cursor fix | `001-xterm-cursor-fix.patch` | `frontend/app/view/term/term.tsx` | `main` + `dev.patch` |
| bookmark typeahead fix | `002-bookmark-typeahead-fix.patch` | `frontend/app/view/webview/webview.tsx` | `dev.patch` only |
| focus fix | `003-focus-fix.patch` | `frontend/app/block/block.tsx` | `dev.patch` only |
| file explorer bookmarks | `004-file-explorer-bookmarks.patch` | 22 files (see PR #3443) | `dev.patch` only |
| ssh agent forwarding | `005-ssh-agent-forwarding.patch` | 7 files (see PR #3421) | `dev.patch` only |
| ssh durable session recovery | `006-ssh-durable-session-recovery.patch` | 6 files (see PR #3460) | `dev.patch` only |
| ssh agent signer failover | `007-ssh-agent-signer-failover.patch` | 2 files (see PR #3401) | `dev.patch` only |
| ssh caps lock indicator | `008-ssh-capslock-indicator.patch` | `frontend/app/modals/userinputmodal.tsx` | `dev.patch` only |

## How the sync works

The `sync-upstream-and-fix.yml` workflow runs daily at 07:00 UTC (or manually).
It syncs both branches in parallel — `main` from the latest upstream release
tag, `dev.patch` from `upstream/main`.

### The revert-then-repatch sequence

For each branch, the workflow executes these steps:

```bash
# 1. Fetch upstream
git remote add upstream https://github.com/wavetermdev/waveterm.git
git fetch upstream --tags --quiet

# 2. Determine what to merge
#    main:       latest upstream release tag (e.g. v0.14.5)
#    dev.patch:  upstream/main

# 3. Skip if already up to date
git merge-base --is-ancestor "$UPSTREAM_SHA" HEAD  # → nothing to do

# 4. Revert all PATCHED_FILES to upstream's version, then commit
#    This removes our custom changes from the working tree so the merge
#    won't conflict on those files.
.github/scripts/revert_patched_files.sh "$UPSTREAM_SHA" "$MERGE_REF"
#    → git checkout "$UPSTREAM_SHA" -- <each patched file>
#    → git commit -m "chore: revert patched files to upstream …"

# 5. Merge upstream (normal merge, no strategy override)
git merge "$MERGE_REF" --no-edit -m "chore: merge upstream …"
#    If this conflicts on non-patched files → FAIL LOUDLY (merge --abort, exit 1)

# 6. Re-apply all patches via apply_patches.sh
.github/scripts/apply_patches.sh
#    For each .github/patches/*.patch:
#      - If git apply --reverse --check passes → already applied, skip
#      - If git apply --check passes → git apply, continue
#      - Otherwise → FAIL LOUDLY (exit 1)

# 7. Commit the re-applied patches
git add frontend/ pkg/
git commit -m "fix: re-apply custom patches after upstream merge …"

# 8. Push
git push origin <branch>
```

### Why revert-then-repatch instead of `--strategy-option=theirs`?

`--strategy-option=theirs` silently lets upstream overwrite custom patches.
The revert-then-repatch approach:

- **Guarantees patches are always re-applied** on the latest upstream code
- **Fails loudly** if upstream changed the surrounding code (`git apply` fails)
- **Fails loudly** if there are conflicts on files we don't patch
- **Never silently drops** a custom change

### Helper scripts

| Script | Purpose |
|--------|---------|
| `.github/scripts/revert_patched_files.sh` | Checks out each `PATCHED_FILES` entry from the upstream SHA, commits the revert |
| `.github/scripts/apply_patches.sh` | Loops over `.github/patches/*.patch`, applies each with idempotency check |

## Adding a new patch

### 1. Find the PR and generate the `.patch` file

```bash
# Fetch the PR branch
git remote add upstream https://github.com/wavetermdev/waveterm.git  # if not already present
git fetch upstream pull/<PR_NUMBER>/head:pr-<PR_NUMBER>

# Find the merge base (the commit the PR was based on)
MERGE_BASE=$(git merge-base pr-<PR_NUMBER> upstream/main)

# Generate the patch
git diff "$MERGE_BASE"..pr-<PR_NUMBER> > .github/patches/NNN-description.patch
```

### 2. Test the patch applies cleanly

```bash
# Dry-run
git apply --check .github/patches/NNN-description.patch

# Apply for real
git apply .github/patches/NNN-description.patch

# Verify the build
npm run build:dev          # frontend
go build ./pkg/...         # backend
go test ./pkg/...          # tests

# Verify idempotency (reverse check should pass)
git apply --reverse --check .github/patches/NNN-description.patch

# Verify apply_patches.sh works with the new patch
.github/scripts/apply_patches.sh
```

### 3. Add modified files to `PATCHED_FILES`

In `.github/workflows/sync-upstream-and-fix.yml`, add each **modified** file
(not new files — those don't exist in upstream and don't need reverting) to
the `PATCHED_FILES` env var:

```yaml
env:
  PATCHED_FILES: |
    frontend/app/view/term/term.tsx
    frontend/app/view/webview/webview.tsx
    ...
    path/to/new/modified/file.tsx   # ← add here
```

### 4. Register the PR in the catalog

In `.github/scripts/generate_upstream_prs.py`, add an entry to
`ALREADY_INTEGRATED`:

```python
ALREADY_INTEGRATED = {
    ...
    <PR_NUMBER>: ("PR title", "dev.patch", "NNN-description.patch"),
}
```

If the PR touches files that are frequently changed in upstream or hold config
schemas, also add them to `CONFLICT_PRONE_FILES`.

### 5. Update the workflow commit message

In `.github/workflows/sync-upstream-and-fix.yml`, add the new patch to the
"Commit patches" step message and the summary step, so the workflow output
lists all patches applied.

### 6. Commit and push

```bash
git add -A
git commit -m "feat: integrate PR #<NNN> <description> via .patch"
git push origin dev.patch
```

## Rules

- **Never edit upstream files directly** — always via a `.patch` file
- **Never use `--strategy-option=theirs`** — it silently drops changes
- **Keep patches minimal** — one logical change per `.patch` file
- **Name patches with zero-padded numbers** — `NNN-description.patch` (applied in alphabetical order)
- **Only list modified files in `PATCHED_FILES`** — new files don't need reverting
- **Test locally** before pushing: `git apply --check`, `npm run build:dev`, `go build ./pkg/...`
- **Verify idempotency** — `git apply --reverse --check` must pass (so `apply_patches.sh` can detect already-applied patches)
