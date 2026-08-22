# WaveTerm Upstream Pull Requests

Catalog of open pull requests from [wavetermdev/waveterm](https://github.com/wavetermdev/waveterm/pulls)
evaluated for integration into the fork via the `.patch` strategy.

**Last updated:** 2026-08-22

## Legend

- **Risk** — conflict risk if integrated as a `.patch` file:
  - **Zero** — 1 file, <10 lines, no config/schema changes
  - **Low** — 1-2 files, isolated, no overlap with `PATCHED_FILES`
  - **Medium** — touches files we already patch, or touches conflict-prone files (`settingsconfig.go`, `metaconsts.go`)
  - **High** — large, multi-file, touches core files or config schemas
- **.patch fit** — suitability for the revert-then-repatch strategy:
  - **Excellent** — tiny, single-file, pure bugfix
  - **Great** — small, isolated, low conflict risk
  - **Good** — viable but slightly larger or touches shared files
  - **Caution** — overlaps existing patches or touches conflict-prone files
  - **Risky** — large, multi-file, high maintenance burden

## Already integrated

| PR | Title | Size | Files | Branch | Patch file |
|----|-------|------|-------|--------|------------|
| #3429 | fix: stop a de-focusing block from re-grabbing focus | +6/-2 | 1 (`block.tsx`) | `dev.patch` | `003-focus-fix.patch` |
| #3420 | Fix bookmark typeahead not rendering suggestions | +4/-4 | 1 (`webview.tsx`) | `dev.patch` | `002-bookmark-typeahead-fix.patch` |
| (custom) | fix(term): disable crosshair cursor when macOptionIsMeta | +5/-0 | 1 (`term.tsx`) | `main` + `dev.patch` | `001-xterm-cursor-fix.patch` |

## Recommended for integration

### Tier 1 — Zero risk (pure bugfixes, tiny, single-file)

| PR | Title | Size | Files | Risk | .patch fit |
|----|-------|------|-------|------|------------|
| #3455 | fix(web): add missing returns after http.Error in handlers | +5/-0 | 1 (`pkg/web/web.go`) | Zero | Excellent |
| #3419 | fix(wsh): prevent deleteblock from silently ignoring positional arguments | +3/-1 | 1 (`cmd/wsh/cmd/wshcmd-deleteblock.go`) | Zero | Excellent |
| #3413 | fix(webview): respect system color scheme for prefers-color-scheme in web blocks | +1/-1 | 1 (`emain/emain.ts`) | Zero | Excellent |

### Tier 2 — Low risk (small, isolated)

| PR | Title | Size | Files | Risk | .patch fit |
|----|-------|------|-------|------|------------|
| #3343 | feat(preview): sort directories before files in directory preview | +7/-1 | 1 (`preview-directory.tsx`) | Low | Great |
| #3478 | fix: serialize concurrent mermaid renders in markdown preview | +32/-14 | 1 (`markdown.tsx`) | Low | Great |
| #3406 | fix(term): correctly map Ctrl+[ to ESC on non-US keyboard layouts | +42/-10 | 2 (`term-model.ts`, `keyutil.ts`) | Low | Great |
| #3476 | Fix DeepSeek multi-turn chat breaking with reasoning_content error | +29/-19 | 2 (Go backend) | Low | Great |
| #3308 | add Cmd+, shortcut to open Settings, Esc to close | +24/-0 | 3 (incl. docs) | Low | Good |
| #3384 | fix(#3165): OSC 8 hyperlinks not opening in the terminal | +27/-27 | 1 (`termwrap.ts`) | Low | Good |
| #3402 | fix(shellexec): avoid false Snap detection and empty XDG_* vars | +18/-1 | 1 (`shellexec.go`) | Low | Good |
| #3404 | wavebase: symlink ~/.config/waveterm for snap users | +9/-0 | 1 (`wavebase.go`) | Low | Good |
| #3339 | Fix Korean IME space handling on Windows | +12/-0 | 1 (`term-model.ts`) | Low | Good |

### Tier 3 — Medium risk (overlaps or touches conflict-prone files)

| PR | Title | Size | Files | Risk | .patch fit |
|----|-------|------|-------|------|------------|
| #3358 | fix: support OAuth/SSO auth flows in webview blocks | +25/-0 | 2 (incl. `webview.tsx`) | Medium | Caution — overlaps `002-bookmark-typeahead-fix.patch` |
| #3401 | fix(ssh): wrap agent signers to continue to next identity on signing failure | +87/-1 | 2 (`sshclient.go` + new file) | Medium | Caution — touches core SSH code |
| #3407 | Preserve all windows/workspaces on close, not just the last one | +12/-1 | 7 (incl. `settingsconfig.go`, `metaconsts.go`) | Medium | Caution — config schema changes |
| #3457 | feat(config): add macOS vibrancy state setting | +17/-0 | 6 (incl. `settingsconfig.go`, `metaconsts.go`) | Medium | Caution — config schema changes |

### Tier 4 — High risk (large, multi-file, features)

| PR | Title | Size | Files | Risk | .patch fit |
|----|-------|------|-------|------|------------|
| #3460 | fix: recover durable SSH sessions stuck falsely-attached after stream timeout | +250/-6 | 6 | High | Risky |
| #3421 | add ssh agent forwarding support (ForwardAgent / ssh:forwardagent) | +128/-11 | 7 (incl. `settingsconfig.go`) | High | Risky |
| #3440 | add preview:openfileinnewblock setting | +36/-6 | 7 (incl. `settingsconfig.go`, `metaconsts.go`) | High | Risky |
| #3408 | fix(term): emit distinct CSI-u sequence for Ctrl+Enter | +23/-0 | 9 (incl. `settingsconfig.go`, `metaconsts.go`) | High | Risky |
| #3480 | feat: add configurable keybindings via keybindings.json | +499/-244 | 9 (incl. `settingsconfig.go`) | High | Risky |
| #3333 | add wsh tab commands (create, rename, focus) | +451/-0 | 8 | High | Risky |
| #3353 | Add Tab Lock feature: prevent close, lock icon and tab color | +269/-15 | 14 | High | Risky |
| #3331 | [codex] Fix terminal IME composition handling | +526/-62 | 24 (incl. `term.tsx`, `termwrap.ts`) | High | Risky — overlaps `001-xterm-cursor-fix.patch` |
| #3443 | File explorer bookmarks (folder / file / document-position) | +867/-200 | 22 | High | Risky |
| #3399 | Feat/files widget active cwd tree | +1585/-721 | 29 | High | Risky |
| #3312 | feat: add three-section VTabBar with working queue and archive queue | +1349/-967 | 24 | High | Risky |
| #3479 | feat: add Excalidraw diagram editor widget | +2049/-2 | 20 | High | Risky — new widget, better as external plugin |

## Not applicable

### Documentation only

| PR | Title | Size | Files |
|----|-------|------|-------|
| #3477 | docs: add MiniMax AI provider to Wave AI documentation | +55/-0 | 1 (`docs/docs/waveai-modes.mdx`) |

### Dependabot (auto-managed by upstream)

| PR | Title | Size |
|----|-------|------|
| #3474 | Bump js-yaml from 3.14.1 to 3.15.1 | +16/-6 |
| #3473 | Bump nanoid from 3.3.11 to 3.3.18 | +3/-3 |
| #3470 | Bump brace-expansion | +22/-22 |
| #3468 | Bump mermaid from 11.15.0 to 11.16.1 | +27/-27 |
| #3467 | Bump electron from 41.1.0 to 41.10.3 | +38/-159 |
| #3465 | Bump fast-uri from 3.1.4 to 3.1.5 | +3/-3 |
| #3461 | Bump ip-address from 10.2.0 to 10.4.0 | +3/-3 |
| #3454 | Bump postcss from 8.5.8 to 8.5.25 | +7/-7 |
| #3451 | Bump builder-util-runtime, electron-updater and electron-builder | +350/-923 |
| #3450 | Bump app-builder-lib and electron-builder | +348/-877 |
| #3447 | Bump shell-quote from 1.8.4 to 1.10.0 | +5/-5 |
| #3398 | Bump golang.org/x/crypto from 0.52.0 to 0.54.0 | +21/-21 |
| #3397 | Bump github.com/fsnotify/fsnotify from 1.9.0 to 1.10.1 | +3/-3 |
| #3389 | Bump github.com/invopop/jsonschema from 0.13.0 to 0.14.0 | +9/-19 |
| #3388 | Bump actions/checkout from 6 to 7 in /.github/workflows | +10/-10 |
| #3379 | Bump vite from 6.4.2 to 6.4.3 | +7/-7 |
| #3346 | Bump vitest and @vitest/coverage-istanbul | +256/-453 |
| #3341 | Bump github.com/junegunn/fzf from 0.65.2 to 0.73.1 | +9/-7 |
| #3326 | Bump the react-major group across 1 directory with 4 updates | +34/-96 |

## File overlap matrix

Files that appear in multiple PRs — integrating one may complicate integrating another:

| File | PRs |
|------|-----|
| `frontend/app/view/webview/webview.tsx` | #3420 (integrated), #3358 |
| `frontend/app/view/term/term.tsx` | custom (integrated), #3331 |
| `frontend/app/view/term/term-model.ts` | #3406, #3339, #3408, #3331 |
| `frontend/util/keyutil.ts` | #3406, #3331 |
| `frontend/app/view/term/termwrap.ts` | #3384, #3331 |
| `pkg/wconfig/settingsconfig.go` | #3480, #3440, #3421, #3408, #3407, #3457, #3331 |
| `pkg/wconfig/metaconsts.go` | #3480, #3440, #3408, #3407, #3457 |
| `frontend/types/gotypes.d.ts` | #3480, #3479, #3443, #3440, #3421, #3408, #3407, #3353, #3333, #3331, #3312 |
| `frontend/app/store/keymodel.ts` | #3480, #3308, #3353, #3331, #3399 |
| `frontend/app/view/preview/preview-directory.tsx` | #3343, #3443, #3399 |
| `pkg/remote/sshclient.go` | #3421, #3401 |
| `pkg/shellexec/shellexec.go` | #3421, #3402 |
