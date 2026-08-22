# WaveTerm Upstream Pull Requests

Catalog of open pull requests from [wavetermdev/waveterm](https://github.com/wavetermdev/waveterm/pulls)
evaluated for integration into the fork via the `.patch` strategy.

**Last updated:** 2026-08-22
**Total open PRs:** 104

## Legend

- **Risk** — conflict risk if integrated as a `.patch` file:
  - **Zero** — 1 file, <10 lines, no config/schema changes
  - **Low** — 1-2 files, isolated, no overlap with `PATCHED_FILES`
  - **Medium** — touches files we already patch, or touches conflict-prone files (`settingsconfig.go`, `metaconsts.go`, `gotypes.d.ts`)
  - **High** — large, multi-file, touches core files or config schemas
- **.patch fit** — suitability for the revert-then-repatch strategy

## Already integrated

| PR | Title | Size | Files | Branch | Patch file |
|----|----|----|----|----|----|
| [#3420](https://github.com/wavetermdev/waveterm/pull/3420) | Fix bookmark typeahead not rendering suggestions | +4/-4 | `frontend/app/view/webview/webview.tsx` | `dev.patch` | `002-bookmark-typeahead-fix.patch` |
| [#3429](https://github.com/wavetermdev/waveterm/pull/3429) | fix: stop a de-focusing block from re-grabbing focus | +6/-2 | `frontend/app/block/block.tsx` | `dev.patch` | `003-focus-fix.patch` |
| [#3443](https://github.com/wavetermdev/waveterm/pull/3443) | File explorer bookmarks (folder / file / document-position) | +867/-200 | `frontend/app/element/markdown-anchor.test.ts`, `frontend/app/element/markdown-anchor.ts`, … _+20 more_ | `dev.patch` | `004-file-explorer-bookmarks.patch` |

### Tier 1 — Zero risk (pure bugfixes, tiny, single-file)

| PR | Title | Size | Files | Risk | .patch fit |
|----|----|----|----|----|----|
| [#3413](https://github.com/wavetermdev/waveterm/pull/3413) | fix(webview): respect system color scheme for prefers-color-scheme in web blocks | +1/-1 | `emain/emain.ts` | Zero | Excellent |
| [#3419](https://github.com/wavetermdev/waveterm/pull/3419) | fix(wsh): prevent deleteblock from silently ignoring positional arguments | +3/-1 | `cmd/wsh/cmd/wshcmd-deleteblock.go` | Zero | Excellent |
| [#3455](https://github.com/wavetermdev/waveterm/pull/3455) | fix(web): add missing returns after http.Error in handlers | +5/-0 | `pkg/web/web.go` | Zero | Excellent |
| [#3343](https://github.com/wavetermdev/waveterm/pull/3343) | feat(preview): sort directories before files in directory preview | +7/-1 | `frontend/app/view/preview/preview-directory.tsx` | Zero | Excellent |
| [#3404](https://github.com/wavetermdev/waveterm/pull/3404) | wavebase: symlink ~/.config/waveterm for snap users | +9/-0 | `pkg/wavebase/wavebase.go` | Zero | Excellent |

### Tier 2 — Low risk (small, isolated)

| PR | Title | Size | Files | Risk | .patch fit |
|----|----|----|----|----|----|
| [#3186](https://github.com/wavetermdev/waveterm/pull/3186) | ci: enable Windows ARM64 build in GitHub Actions | +5/-4 | `.github/workflows/build-helper.yml`, `Taskfile.yml` | Low | Great |
| [#3339](https://github.com/wavetermdev/waveterm/pull/3339) | Fix Korean IME space handling on Windows | +12/-0 | `frontend/app/view/term/term-model.ts` | Low | Great |
| [#3278](https://github.com/wavetermdev/waveterm/pull/3278) | fix(UI)): ensure terminal theme application via xterm theme setter | +10/-2 | `frontend/app/view/term/termtheme.ts`, `frontend/app/view/term/termwrap.ts` | Low | Great |
| [#2856](https://github.com/wavetermdev/waveterm/pull/2856) | fix: file browser shows newest files first, bump limit to 5000 | +13/-1 | `pkg/wshrpc/wshremote/wshremote_file.go`, `pkg/wshrpc/wshrpctypes_const.go` | Low | Great |
| [#2101](https://github.com/wavetermdev/waveterm/pull/2101) | fix: add WebSocket polyfill for Electron main process | +10/-8 | `frontend/util/wsutil.ts` | Low | Great |
| [#3402](https://github.com/wavetermdev/waveterm/pull/3402) | fix(shellexec): avoid false Snap detection and empty XDG_* vars | +18/-1 | `pkg/shellexec/shellexec.go` | Low | Great |
| [#2840](https://github.com/wavetermdev/waveterm/pull/2840) | Show Caps Lock indicator in SSH password prompt | +25/-4 | `frontend/app/modals/userinputmodal.tsx` | Low | Great |
| [#3182](https://github.com/wavetermdev/waveterm/pull/3182) | properly set argv0 when spawning a process | +31/-0 | `pkg/shellexec/shellexec.go` | Low | Great |
| [#2770](https://github.com/wavetermdev/waveterm/pull/2770) | fix: prevent terminal history duplication on restart | +28/-3 | `frontend/app/view/term/termwrap.ts` | Low | Great |
| [#3264](https://github.com/wavetermdev/waveterm/pull/3264) | fix: serialize IME composition with subsequent keystrokes (#3164) | +39/-2 | `frontend/app/view/term/term-model.ts`, `frontend/app/view/term/termwrap.ts` | Low | Great |
| [#2681](https://github.com/wavetermdev/waveterm/pull/2681) | New tabs inherit working directory from active tab | +36/-6 | `pkg/wcore/workspace.go` | Low | Great |
| [#3476](https://github.com/wavetermdev/waveterm/pull/3476) | Fix DeepSeek multi-turn chat breaking with reasoning_content error | +29/-19 | `pkg/aiusechat/openaichat/openaichat-backend.go`, `pkg/aiusechat/openaichat/openaichat-types.go` | Low | Great |
| [#3406](https://github.com/wavetermdev/waveterm/pull/3406) | fix(term): correctly map Ctrl+[ to ESC on non-US keyboard layouts | +42/-10 | `frontend/app/view/term/term-model.ts`, `frontend/util/keyutil.ts` | Low | Great |
| [#2712](https://github.com/wavetermdev/waveterm/pull/2712) | Improve search functionality | +48/-4 | `frontend/app/element/search.tsx`, `frontend/app/store/keymodel.ts` | Low | Great |
| [#3384](https://github.com/wavetermdev/waveterm/pull/3384) | fix(#3165): OSC 8 hyperlinks not opening in the terminal | +27/-27 | `frontend/app/view/term/termwrap.ts` | Low | Great |

### Tier 3 — Medium risk (overlaps or touches conflict-prone files)

| PR | Title | Size | Files | Risk | .patch fit |
|----|----|----|----|----|----|
| [#3270](https://github.com/wavetermdev/waveterm/pull/3270) | fix minor scroll bug with telemetry required page | +2/-1 | `frontend/app/aipanel/telemetryrequired.tsx`, `frontend/types/gotypes.d.ts` | Medium | Caution — overlaps existing patch |
| [#2461](https://github.com/wavetermdev/waveterm/pull/2461) | Fix/terminal background color detection | +7/-3 | `frontend/app/view/codeeditor/codeeditor.tsx`, `frontend/app/view/preview/preview-edit.tsx`, … _+1 more_ | Medium | Caution — overlaps existing patch |
| [#3407](https://github.com/wavetermdev/waveterm/pull/3407) | Preserve all windows/workspaces on close, not just the last one | +12/-1 | `docs/docs/config.mdx`, `emain/emain-window.ts`, … _+5 more_ | Medium | Caution — overlaps existing patch |
| [#3457](https://github.com/wavetermdev/waveterm/pull/3457) | feat(config): add macOS vibrancy state setting | +17/-0 | `docs/docs/config.mdx`, `emain/emain-window.ts`, … _+4 more_ | Medium | Caution — overlaps existing patch |
| [#2406](https://github.com/wavetermdev/waveterm/pull/2406) | wsh => wave | +18/-1 | `pkg/remote/connutil.go`, `pkg/util/shellutil/shellutil.go`, … _+2 more_ | Medium | Caution |
| [#3308](https://github.com/wavetermdev/waveterm/pull/3308) | add Cmd+, shortcut to open Settings, Esc to close | +24/-0 | `docs/docs/keybindings.mdx`, `frontend/app/element/quicktips.tsx`, … _+1 more_ | Medium | Caution |
| [#3358](https://github.com/wavetermdev/waveterm/pull/3358) | fix: support OAuth/SSO auth flows in webview blocks | +25/-0 | `emain/emain-tabview.ts`, `frontend/app/view/webview/webview.tsx` | Medium | Caution — overlaps existing patch |
| [#3440](https://github.com/wavetermdev/waveterm/pull/3440) | add preview:openfileinnewblock setting to open files in a new block from directory preview | +36/-6 | `docs/docs/config.mdx`, `frontend/app/view/preview/preview-directory.tsx`, … _+5 more_ | Medium | Caution — overlaps existing patch |
| [#3117](https://github.com/wavetermdev/waveterm/pull/3117) | feat: add tab:newtablayout setting for custom new tab layouts | +42/-1 | `pkg/wconfig/settingsconfig.go`, `pkg/wcore/workspace.go`, … _+1 more_ | Medium | Caution — overlaps existing patch |
| [#2858](https://github.com/wavetermdev/waveterm/pull/2858) | fix: terminal scroll preservation on tab switch and alt buffer exit | +40/-4 | `emain/emain-window.ts`, `frontend/app/view/term/osc-handlers.ts`, … _+1 more_ | Medium | Caution |
| [#3478](https://github.com/wavetermdev/waveterm/pull/3478) | fix: serialize concurrent mermaid renders in markdown preview | +32/-14 | `frontend/app/element/markdown.tsx` | Medium | Caution — overlaps existing patch |
| [#3280](https://github.com/wavetermdev/waveterm/pull/3280) | feat: support Windows right-click context menu to open directory | +52/-3 | `emain/emain-window.ts`, `emain/emain.ts`, … _+2 more_ | Medium | Caution |
| [#2678](https://github.com/wavetermdev/waveterm/pull/2678) | Add confirmation dialog before closing tabs | +50/-5 | `frontend/app/modals/confirmclosetab.tsx`, `frontend/app/modals/modalregistry.tsx`, … _+2 more_ | Medium | Caution — overlaps existing patch |
| [#3058](https://github.com/wavetermdev/waveterm/pull/3058) | feat: close window when last terminal exits (term:closeonlasttermclose) | +56/-2 | `frontend/types/gotypes.d.ts`, `pkg/blockcontroller/shellcontroller.go`, … _+3 more_ | Medium | Caution — overlaps existing patch |
| [#2245](https://github.com/wavetermdev/waveterm/pull/2245) | Fix WebSocket utilities and Add OSC 52 clipboard support | +60/-6 | `frontend/app/view/term/termwrap.ts`, `frontend/util/wsutil.ts` | Medium | Caution |
| [#2717](https://github.com/wavetermdev/waveterm/pull/2717) | Fix terminal state loss when switching workspaces | +57/-10 | `emain/emain-window.ts` | Medium | Caution |
| [#3401](https://github.com/wavetermdev/waveterm/pull/3401) | fix(ssh): wrap agent signers to continue to next identity on signing failure | +87/-1 | `pkg/remote/sshclient.go`, `pkg/remote/sshsigners.go` | Medium | Caution |
| [#2742](https://github.com/wavetermdev/waveterm/pull/2742) | Add drag-and-drop file support to terminal | +101/-3 | `emain/preload.ts`, `frontend/app/view/term/term.tsx`, … _+3 more_ | Medium | Caution — overlaps existing patch |
| [#3016](https://github.com/wavetermdev/waveterm/pull/3016) | feat: implement per-block zsh history isolation | +97/-26 | `pkg/util/shellutil/shellintegration/zsh_zshrc.sh`, `pkg/util/shellutil/shellutil.go`, … _+1 more_ | Medium | Caution |
| [#3421](https://github.com/wavetermdev/waveterm/pull/3421) | add ssh agent forwarding support (ForwardAgent / ssh:forwardagent) | +128/-11 | `docs/docs/connections.mdx`, `frontend/types/gotypes.d.ts`, … _+5 more_ | Medium | Caution — overlaps existing patch |
| [#2859](https://github.com/wavetermdev/waveterm/pull/2859) | feat: cmd+click to open file paths in terminal | +160/-0 | `frontend/app/view/term/term-link-provider.ts`, `frontend/app/view/term/termwrap.ts` | Medium | Caution |
| [#3290](https://github.com/wavetermdev/waveterm/pull/3290) | fix: preserve reasoning_content for DeepSeek chat completions | +212/-24 | `pkg/aiusechat/openaichat/openaichat-backend.go`, `pkg/aiusechat/openaichat/openaichat-backend_test.go`, … _+1 more_ | Medium | Caution |
| [#3460](https://github.com/wavetermdev/waveterm/pull/3460) | fix: recover durable SSH sessions stuck falsely-attached after stream timeout (#3439) | +250/-6 | `cmd/test-streammanager/main-test-streammanager.go`, `pkg/jobcontroller/jobcontroller.go`, … _+4 more_ | Medium | Caution |
| [#3152](https://github.com/wavetermdev/waveterm/pull/3152) | fix: prevent "no route for conn:..." errors and add shell path expansion | +354/-0 | `pkg/remote/conncontroller/conncontroller.go`, `pkg/shellexec/shellexec.go`, … _+1 more_ | Medium | Caution |
| [#3066](https://github.com/wavetermdev/waveterm/pull/3066) | Add standalone file suggestion preview and fix PreviewEnv service narrowing | +401/-38 | `frontend/app/suggestion/suggestion.tsx`, `frontend/app/view/preview/preview.tsx`, … _+5 more_ | Medium | Caution |

### Tier 4 — High risk (large, multi-file, features)

| PR | Title | Size | Files | Risk | .patch fit |
|----|----|----|----|----|----|
| [#3408](https://github.com/wavetermdev/waveterm/pull/3408) | fix(term): emit distinct CSI-u sequence for Ctrl+Enter in terminal blocks | +23/-0 | `cmd/generateschema/main-generateschema.go`, `frontend/app/view/term/term-model.ts`, … _+7 more_ | High | Risky |
| [#2835](https://github.com/wavetermdev/waveterm/pull/2835) | Tab background glow on process exit/bell | +174/-3 | `docs/docs/config.mdx`, `frontend/app/tab/tab.scss`, … _+9 more_ | High | Risky |
| [#3004](https://github.com/wavetermdev/waveterm/pull/3004) | Upgrade OSC 16162 `I` to return full ZLE buffer and cursor state | +186/-43 | `aiprompts/wave-osc-16162.md`, `frontend/app/view/term/osc-handlers.test.ts`, … _+6 more_ | High | Risky |
| [#3353](https://github.com/wavetermdev/waveterm/pull/3353) | Add Tab Lock feature: prevent close, lock icon and tab color | +269/-15 | `frontend/app/store/keymodel.ts`, `frontend/app/tab/tab.scss`, … _+12 more_ | High | Risky |
| [#3205](https://github.com/wavetermdev/waveterm/pull/3205) | feat: add quick terminal float window with double-ESC trigger | +292/-18 | `frontend/app/store/global-atoms.ts`, `frontend/app/store/global.ts`, … _+7 more_ | High | Risky |
| [#3086](https://github.com/wavetermdev/waveterm/pull/3086) | Test pr 1 rebased | +339/-5 | `frontend/app/aipanel/aimessage.tsx`, `frontend/app/aipanel/aipanel.tsx`, … _+7 more_ | High | Risky |
| [#3333](https://github.com/wavetermdev/waveterm/pull/3333) | add wsh tab commands (create, rename, focus) | +451/-0 | `cmd/wsh/cmd/wshcmd-tab.go`, `docs/docs/wsh-reference.mdx`, … _+6 more_ | High | Risky |
| [#3070](https://github.com/wavetermdev/waveterm/pull/3070) | Add a whitelisted AI tool definition for Wave config updates | +545/-0 | `pkg/aiusechat/tools_setconfig.go`, `pkg/aiusechat/tools_setconfig_test.go` | High | Risky |
| [#3331](https://github.com/wavetermdev/waveterm/pull/3331) | [codex] Fix terminal IME composition handling | +526/-62 | `Taskfile.yml`, `electron-builder.config.cjs`, … _+22 more_ | High | Risky |
| [#3480](https://github.com/wavetermdev/waveterm/pull/3480) | feat: add configurable keybindings via keybindings.json | +499/-244 | `frontend/app/store/global.ts`, `frontend/app/store/keymodel.ts`, … _+7 more_ | High | Risky |
| [#2238](https://github.com/wavetermdev/waveterm/pull/2238) | Sysinfo: add support for AMD and NVIDIA GPUs | +927/-2 | `docs/GPU_MONITORING.md`, `frontend/app/theme.scss`, … _+5 more_ | High | Risky |
| [#2103](https://github.com/wavetermdev/waveterm/pull/2103) | refactor: enhance AI block UI/UX | +697/-252 | `frontend/app/element/markdown.scss`, `frontend/app/element/markdown.tsx`, … _+4 more_ | High | Risky |
| [#3069](https://github.com/wavetermdev/waveterm/pull/3069) | Make config preview default-aware and adopt a VS Code-style settings layout | +995/-0 | `frontend/app/configui/configvalidation.test.ts`, `frontend/app/configui/configvalidation.ts`, … _+2 more_ | High | Risky |
| [#3184](https://github.com/wavetermdev/waveterm/pull/3184) | feat: add i18n framework with Chinese (zh-CN) localization | +369/-648 | `frontend/app/aipanel/aipanel-contextmenu.ts`, `frontend/app/aipanel/aipanelheader.tsx`, … _+12 more_ | High | Risky |
| [#3293](https://github.com/wavetermdev/waveterm/pull/3293) | Notes widget (w/ syncing backend) | +1158/-12 | `docs/docs/config.mdx`, `frontend/app/block/blockregistry.ts`, … _+23 more_ | High | Risky |
| [#3235](https://github.com/wavetermdev/waveterm/pull/3235) | Add block rename and preview follow terminal features | +647/-563 | `.gitignore`, `CLAUDE.md`, … _+12 more_ | High | Risky |
| [#2763](https://github.com/wavetermdev/waveterm/pull/2763) | add workspace directory feature with shell quoting and tests | +844/-613 | `emain/emain-ipc.ts`, `emain/preload.ts`, … _+16 more_ | High | Risky |
| [#3263](https://github.com/wavetermdev/waveterm/pull/3263) | feat: tab templates and geolocation polyfill for webviews | +968/-593 | `db/migrations-wstore/000012_tabtemplate.down.sql`, `db/migrations-wstore/000012_tabtemplate.up.sql`, … _+17 more_ | High | Risky |
| [#2940](https://github.com/wavetermdev/waveterm/pull/2940) | feat(term): add sixel rendering and propagate terminal pixel size to PTY | +1010/-598 | `frontend/app/view/term/term-model.ts`, `frontend/app/view/term/term.tsx`, … _+11 more_ | High | Risky |
| [#3479](https://github.com/wavetermdev/waveterm/pull/3479) | feat: add Excalidraw diagram editor widget | +2049/-2 | `.gitignore`, `cmd/wsh/cmd/wshcmd-excalidraw.go`, … _+18 more_ | High | Risky |
| [#3399](https://github.com/wavetermdev/waveterm/pull/3399) | Feat/files widget active cwd tree | +1585/-721 | `electron.vite.config.ts`, `frontend/app/block/block.tsx`, … _+27 more_ | High | Risky |
| [#3312](https://github.com/wavetermdev/waveterm/pull/3312) | feat: add three-section VTabBar with working queue and archive queue | +1349/-967 | `.github/workflows/build-helper.yml`, `.github/workflows/publish-release.yml`, … _+22 more_ | High | Risky |
| [#3275](https://github.com/wavetermdev/waveterm/pull/3275) | New Direct Terminal Tsunami SubBlock + TCP over PTY system to forward ports | +3311/-162 | `.gitignore`, `.vscode/settings.json`, … _+59 more_ | High | Risky |
| [#2789](https://github.com/wavetermdev/waveterm/pull/2789) | feat: Tab base directory with VS Code style redesign | +4152/-141 | `CHANGES.md`, `CLAUDE.md`, … _+40 more_ | High | Risky |
| [#3220](https://github.com/wavetermdev/waveterm/pull/3220) | feat(platform): 优化Windows平台路径处理和SSH配置文件支持 | +7925/-371 | `.gitignore`, `.harness/decisions.md`, … _+75 more_ | High | Risky |

## Not applicable

### Documentation only

| PR | Title | Size | Files |
|----|----|----|----|
| [#3477](https://github.com/wavetermdev/waveterm/pull/3477) | docs: add MiniMax AI provider to Wave AI documentation | +55/-0 | `docs/docs/waveai-modes.mdx` |
| [#3265](https://github.com/wavetermdev/waveterm/pull/3265) | docs: add Simplified Chinese README | +171/-3 | `README.ko.md`, `README.md`, … _+2 more_ |
| [#3075](https://github.com/wavetermdev/waveterm/pull/3075) | feat: improve skill scores for waveterm | +36/-965 | `.kilocode/skills/add-config/SKILL.md`, `.kilocode/skills/add-rpc/SKILL.md`, … _+6 more_ |
| [#2218](https://github.com/wavetermdev/waveterm/pull/2218) | Add docs how to configure Docker Model Runner as the AI backend | +22/-1 | `docs/docs/ai-presets.mdx`, `docs/docs/faq.mdx` |

### Dependabot (auto-managed by upstream)

| PR | Title | Size |
|----|----|----|
| [#3474](https://github.com/wavetermdev/waveterm/pull/3474) | Bump js-yaml from 3.14.1 to 3.15.1 | +16/-6 |
| [#3473](https://github.com/wavetermdev/waveterm/pull/3473) | Bump nanoid from 3.3.11 to 3.3.18 | +3/-3 |
| [#3470](https://github.com/wavetermdev/waveterm/pull/3470) | Bump brace-expansion | +22/-22 |
| [#3468](https://github.com/wavetermdev/waveterm/pull/3468) | Bump mermaid from 11.15.0 to 11.16.1 | +27/-27 |
| [#3467](https://github.com/wavetermdev/waveterm/pull/3467) | Bump electron from 41.1.0 to 41.10.3 | +38/-159 |
| [#3465](https://github.com/wavetermdev/waveterm/pull/3465) | Bump fast-uri from 3.1.4 to 3.1.5 | +3/-3 |
| [#3461](https://github.com/wavetermdev/waveterm/pull/3461) | Bump ip-address from 10.2.0 to 10.4.0 | +3/-3 |
| [#3454](https://github.com/wavetermdev/waveterm/pull/3454) | Bump postcss from 8.5.8 to 8.5.25 | +7/-7 |
| [#3451](https://github.com/wavetermdev/waveterm/pull/3451) | Bump builder-util-runtime, electron-updater and electron-builder | +350/-923 |
| [#3450](https://github.com/wavetermdev/waveterm/pull/3450) | Bump app-builder-lib and electron-builder | +348/-877 |
| [#3447](https://github.com/wavetermdev/waveterm/pull/3447) | Bump shell-quote from 1.8.4 to 1.10.0 | +5/-5 |
| [#3398](https://github.com/wavetermdev/waveterm/pull/3398) | Bump golang.org/x/crypto from 0.52.0 to 0.54.0 | +21/-21 |
| [#3397](https://github.com/wavetermdev/waveterm/pull/3397) | Bump github.com/fsnotify/fsnotify from 1.9.0 to 1.10.1 | +3/-3 |
| [#3389](https://github.com/wavetermdev/waveterm/pull/3389) | Bump github.com/invopop/jsonschema from 0.13.0 to 0.14.0 | +9/-19 |
| [#3388](https://github.com/wavetermdev/waveterm/pull/3388) | Bump actions/checkout from 6 to 7 in /.github/workflows | +10/-10 |
| [#3379](https://github.com/wavetermdev/waveterm/pull/3379) | Bump vite from 6.4.2 to 6.4.3 | +7/-7 |
| [#3346](https://github.com/wavetermdev/waveterm/pull/3346) | Bump vitest and @vitest/coverage-istanbul | +256/-453 |
| [#3341](https://github.com/wavetermdev/waveterm/pull/3341) | Bump github.com/junegunn/fzf from 0.65.2 to 0.73.1 | +9/-7 |
| [#3326](https://github.com/wavetermdev/waveterm/pull/3326) | Bump the react-major group across 1 directory with 4 updates | +34/-96 |
| [#3302](https://github.com/wavetermdev/waveterm/pull/3302) | Bump @babel/plugin-transform-modules-systemjs from 7.27.1 to 7.29.7 | +63/-63 |
| [#3229](https://github.com/wavetermdev/waveterm/pull/3229) | Bump actions/upload-pages-artifact from 4 to 5 in /.github/workflows | +1/-1 |
| [#3227](https://github.com/wavetermdev/waveterm/pull/3227) | Bump softprops/action-gh-release from 2 to 3 in /.github/workflows | +1/-1 |
| [#3180](https://github.com/wavetermdev/waveterm/pull/3180) | Bump lodash from 4.17.23 to 4.18.1 | +3/-3 |
| [#3056](https://github.com/wavetermdev/waveterm/pull/3056) | Bump vitest from 3.2.4 to 4.1.0 | +161/-253 |
| [#2952](https://github.com/wavetermdev/waveterm/pull/2952) | Bump actions/upload-artifact from 5 to 7 in /.github/workflows | +3/-3 |
| [#2950](https://github.com/wavetermdev/waveterm/pull/2950) | Bump actions/download-artifact from 4 to 8 in /.github/workflows | +1/-1 |
| [#2422](https://github.com/wavetermdev/waveterm/pull/2422) | Bump github.com/skeema/knownhosts from 1.3.1 to 1.3.2 | +3/-3 |

## File overlap matrix

Files that appear in multiple PRs — integrating one may complicate integrating another:

| File | PRs |
|------|-----|
| `frontend/types/gotypes.d.ts` **(patched)** | [#2763](https://github.com/wavetermdev/waveterm/pull/2763), [#2789](https://github.com/wavetermdev/waveterm/pull/2789), [#2835](https://github.com/wavetermdev/waveterm/pull/2835), [#2940](https://github.com/wavetermdev/waveterm/pull/2940), [#3004](https://github.com/wavetermdev/waveterm/pull/3004), [#3058](https://github.com/wavetermdev/waveterm/pull/3058), [#3086](https://github.com/wavetermdev/waveterm/pull/3086), [#3220](https://github.com/wavetermdev/waveterm/pull/3220), [#3235](https://github.com/wavetermdev/waveterm/pull/3235), [#3263](https://github.com/wavetermdev/waveterm/pull/3263), [#3270](https://github.com/wavetermdev/waveterm/pull/3270), [#3275](https://github.com/wavetermdev/waveterm/pull/3275), [#3293](https://github.com/wavetermdev/waveterm/pull/3293), [#3312](https://github.com/wavetermdev/waveterm/pull/3312), [#3331](https://github.com/wavetermdev/waveterm/pull/3331), [#3333](https://github.com/wavetermdev/waveterm/pull/3333), [#3353](https://github.com/wavetermdev/waveterm/pull/3353), [#3399](https://github.com/wavetermdev/waveterm/pull/3399), [#3407](https://github.com/wavetermdev/waveterm/pull/3407), [#3408](https://github.com/wavetermdev/waveterm/pull/3408), [#3421](https://github.com/wavetermdev/waveterm/pull/3421), [#3440](https://github.com/wavetermdev/waveterm/pull/3440), [#3443](https://github.com/wavetermdev/waveterm/pull/3443), [#3457](https://github.com/wavetermdev/waveterm/pull/3457), [#3479](https://github.com/wavetermdev/waveterm/pull/3479), [#3480](https://github.com/wavetermdev/waveterm/pull/3480) |
| `pkg/wconfig/settingsconfig.go` **(patched)** | [#2789](https://github.com/wavetermdev/waveterm/pull/2789), [#2835](https://github.com/wavetermdev/waveterm/pull/2835), [#3058](https://github.com/wavetermdev/waveterm/pull/3058), [#3117](https://github.com/wavetermdev/waveterm/pull/3117), [#3220](https://github.com/wavetermdev/waveterm/pull/3220), [#3275](https://github.com/wavetermdev/waveterm/pull/3275), [#3293](https://github.com/wavetermdev/waveterm/pull/3293), [#3331](https://github.com/wavetermdev/waveterm/pull/3331), [#3407](https://github.com/wavetermdev/waveterm/pull/3407), [#3408](https://github.com/wavetermdev/waveterm/pull/3408), [#3421](https://github.com/wavetermdev/waveterm/pull/3421), [#3440](https://github.com/wavetermdev/waveterm/pull/3440), [#3443](https://github.com/wavetermdev/waveterm/pull/3443), [#3457](https://github.com/wavetermdev/waveterm/pull/3457), [#3480](https://github.com/wavetermdev/waveterm/pull/3480) |
| `frontend/app/view/term/termwrap.ts` | [#2245](https://github.com/wavetermdev/waveterm/pull/2245), [#2770](https://github.com/wavetermdev/waveterm/pull/2770), [#2789](https://github.com/wavetermdev/waveterm/pull/2789), [#2858](https://github.com/wavetermdev/waveterm/pull/2858), [#2859](https://github.com/wavetermdev/waveterm/pull/2859), [#2940](https://github.com/wavetermdev/waveterm/pull/2940), [#3004](https://github.com/wavetermdev/waveterm/pull/3004), [#3205](https://github.com/wavetermdev/waveterm/pull/3205), [#3220](https://github.com/wavetermdev/waveterm/pull/3220), [#3264](https://github.com/wavetermdev/waveterm/pull/3264), [#3275](https://github.com/wavetermdev/waveterm/pull/3275), [#3278](https://github.com/wavetermdev/waveterm/pull/3278), [#3331](https://github.com/wavetermdev/waveterm/pull/3331), [#3384](https://github.com/wavetermdev/waveterm/pull/3384) |
| `frontend/app/view/term/term-model.ts` | [#2789](https://github.com/wavetermdev/waveterm/pull/2789), [#2940](https://github.com/wavetermdev/waveterm/pull/2940), [#3205](https://github.com/wavetermdev/waveterm/pull/3205), [#3220](https://github.com/wavetermdev/waveterm/pull/3220), [#3264](https://github.com/wavetermdev/waveterm/pull/3264), [#3275](https://github.com/wavetermdev/waveterm/pull/3275), [#3293](https://github.com/wavetermdev/waveterm/pull/3293), [#3331](https://github.com/wavetermdev/waveterm/pull/3331), [#3339](https://github.com/wavetermdev/waveterm/pull/3339), [#3406](https://github.com/wavetermdev/waveterm/pull/3406), [#3408](https://github.com/wavetermdev/waveterm/pull/3408) |
| `frontend/app/store/keymodel.ts` | [#2678](https://github.com/wavetermdev/waveterm/pull/2678), [#2712](https://github.com/wavetermdev/waveterm/pull/2712), [#2789](https://github.com/wavetermdev/waveterm/pull/2789), [#3205](https://github.com/wavetermdev/waveterm/pull/3205), [#3275](https://github.com/wavetermdev/waveterm/pull/3275), [#3308](https://github.com/wavetermdev/waveterm/pull/3308), [#3331](https://github.com/wavetermdev/waveterm/pull/3331), [#3353](https://github.com/wavetermdev/waveterm/pull/3353), [#3399](https://github.com/wavetermdev/waveterm/pull/3399), [#3480](https://github.com/wavetermdev/waveterm/pull/3480) |
| `package-lock.json` | [#2763](https://github.com/wavetermdev/waveterm/pull/2763), [#2940](https://github.com/wavetermdev/waveterm/pull/2940), [#3184](https://github.com/wavetermdev/waveterm/pull/3184), [#3220](https://github.com/wavetermdev/waveterm/pull/3220), [#3235](https://github.com/wavetermdev/waveterm/pull/3235), [#3263](https://github.com/wavetermdev/waveterm/pull/3263), [#3312](https://github.com/wavetermdev/waveterm/pull/3312), [#3331](https://github.com/wavetermdev/waveterm/pull/3331), [#3399](https://github.com/wavetermdev/waveterm/pull/3399), [#3479](https://github.com/wavetermdev/waveterm/pull/3479) |
| `schema/settings.json` | [#2835](https://github.com/wavetermdev/waveterm/pull/2835), [#3058](https://github.com/wavetermdev/waveterm/pull/3058), [#3117](https://github.com/wavetermdev/waveterm/pull/3117), [#3220](https://github.com/wavetermdev/waveterm/pull/3220), [#3275](https://github.com/wavetermdev/waveterm/pull/3275), [#3293](https://github.com/wavetermdev/waveterm/pull/3293), [#3407](https://github.com/wavetermdev/waveterm/pull/3407), [#3408](https://github.com/wavetermdev/waveterm/pull/3408), [#3440](https://github.com/wavetermdev/waveterm/pull/3440), [#3457](https://github.com/wavetermdev/waveterm/pull/3457) |
| `pkg/wconfig/metaconsts.go` | [#2835](https://github.com/wavetermdev/waveterm/pull/2835), [#3058](https://github.com/wavetermdev/waveterm/pull/3058), [#3275](https://github.com/wavetermdev/waveterm/pull/3275), [#3293](https://github.com/wavetermdev/waveterm/pull/3293), [#3407](https://github.com/wavetermdev/waveterm/pull/3407), [#3408](https://github.com/wavetermdev/waveterm/pull/3408), [#3440](https://github.com/wavetermdev/waveterm/pull/3440), [#3457](https://github.com/wavetermdev/waveterm/pull/3457) |
| `pkg/wshrpc/wshserver/wshserver.go` **(patched)** | [#2789](https://github.com/wavetermdev/waveterm/pull/2789), [#3275](https://github.com/wavetermdev/waveterm/pull/3275), [#3293](https://github.com/wavetermdev/waveterm/pull/3293), [#3312](https://github.com/wavetermdev/waveterm/pull/3312), [#3333](https://github.com/wavetermdev/waveterm/pull/3333), [#3399](https://github.com/wavetermdev/waveterm/pull/3399), [#3443](https://github.com/wavetermdev/waveterm/pull/3443), [#3479](https://github.com/wavetermdev/waveterm/pull/3479) |
| `frontend/app/store/wshclientapi.ts` **(patched)** | [#3275](https://github.com/wavetermdev/waveterm/pull/3275), [#3293](https://github.com/wavetermdev/waveterm/pull/3293), [#3312](https://github.com/wavetermdev/waveterm/pull/3312), [#3333](https://github.com/wavetermdev/waveterm/pull/3333), [#3399](https://github.com/wavetermdev/waveterm/pull/3399), [#3443](https://github.com/wavetermdev/waveterm/pull/3443), [#3479](https://github.com/wavetermdev/waveterm/pull/3479) |
| `pkg/wshrpc/wshclient/wshclient.go` **(patched)** | [#3275](https://github.com/wavetermdev/waveterm/pull/3275), [#3293](https://github.com/wavetermdev/waveterm/pull/3293), [#3312](https://github.com/wavetermdev/waveterm/pull/3312), [#3333](https://github.com/wavetermdev/waveterm/pull/3333), [#3399](https://github.com/wavetermdev/waveterm/pull/3399), [#3443](https://github.com/wavetermdev/waveterm/pull/3443), [#3479](https://github.com/wavetermdev/waveterm/pull/3479) |
| `pkg/wshrpc/wshrpctypes.go` **(patched)** | [#2238](https://github.com/wavetermdev/waveterm/pull/2238), [#3275](https://github.com/wavetermdev/waveterm/pull/3275), [#3293](https://github.com/wavetermdev/waveterm/pull/3293), [#3312](https://github.com/wavetermdev/waveterm/pull/3312), [#3333](https://github.com/wavetermdev/waveterm/pull/3333), [#3443](https://github.com/wavetermdev/waveterm/pull/3443), [#3479](https://github.com/wavetermdev/waveterm/pull/3479) |
| `emain/emain-window.ts` | [#2717](https://github.com/wavetermdev/waveterm/pull/2717), [#2858](https://github.com/wavetermdev/waveterm/pull/2858), [#3220](https://github.com/wavetermdev/waveterm/pull/3220), [#3280](https://github.com/wavetermdev/waveterm/pull/3280), [#3407](https://github.com/wavetermdev/waveterm/pull/3407), [#3457](https://github.com/wavetermdev/waveterm/pull/3457) |
| `frontend/app/block/blockregistry.ts` | [#3220](https://github.com/wavetermdev/waveterm/pull/3220), [#3275](https://github.com/wavetermdev/waveterm/pull/3275), [#3293](https://github.com/wavetermdev/waveterm/pull/3293), [#3312](https://github.com/wavetermdev/waveterm/pull/3312), [#3399](https://github.com/wavetermdev/waveterm/pull/3399), [#3479](https://github.com/wavetermdev/waveterm/pull/3479) |
| `frontend/app/view/term/term.tsx` **(patched)** | [#2742](https://github.com/wavetermdev/waveterm/pull/2742), [#2789](https://github.com/wavetermdev/waveterm/pull/2789), [#2940](https://github.com/wavetermdev/waveterm/pull/2940), [#3220](https://github.com/wavetermdev/waveterm/pull/3220), [#3275](https://github.com/wavetermdev/waveterm/pull/3275), [#3331](https://github.com/wavetermdev/waveterm/pull/3331) |
| `package.json` | [#2940](https://github.com/wavetermdev/waveterm/pull/2940), [#3184](https://github.com/wavetermdev/waveterm/pull/3184), [#3220](https://github.com/wavetermdev/waveterm/pull/3220), [#3235](https://github.com/wavetermdev/waveterm/pull/3235), [#3331](https://github.com/wavetermdev/waveterm/pull/3331), [#3479](https://github.com/wavetermdev/waveterm/pull/3479) |
| `pkg/waveobj/metaconsts.go` | [#2789](https://github.com/wavetermdev/waveterm/pull/2789), [#2835](https://github.com/wavetermdev/waveterm/pull/2835), [#3235](https://github.com/wavetermdev/waveterm/pull/3235), [#3275](https://github.com/wavetermdev/waveterm/pull/3275), [#3353](https://github.com/wavetermdev/waveterm/pull/3353), [#3408](https://github.com/wavetermdev/waveterm/pull/3408) |
| `pkg/waveobj/wtypemeta.go` | [#2789](https://github.com/wavetermdev/waveterm/pull/2789), [#2835](https://github.com/wavetermdev/waveterm/pull/2835), [#3235](https://github.com/wavetermdev/waveterm/pull/3235), [#3275](https://github.com/wavetermdev/waveterm/pull/3275), [#3353](https://github.com/wavetermdev/waveterm/pull/3353), [#3408](https://github.com/wavetermdev/waveterm/pull/3408) |
| `docs/docs/config.mdx` | [#2835](https://github.com/wavetermdev/waveterm/pull/2835), [#3293](https://github.com/wavetermdev/waveterm/pull/3293), [#3407](https://github.com/wavetermdev/waveterm/pull/3407), [#3440](https://github.com/wavetermdev/waveterm/pull/3440), [#3457](https://github.com/wavetermdev/waveterm/pull/3457) |
| `frontend/app/modals/modalregistry.tsx` **(patched)** | [#2678](https://github.com/wavetermdev/waveterm/pull/2678), [#3263](https://github.com/wavetermdev/waveterm/pull/3263), [#3293](https://github.com/wavetermdev/waveterm/pull/3293), [#3331](https://github.com/wavetermdev/waveterm/pull/3331), [#3443](https://github.com/wavetermdev/waveterm/pull/3443) |
| `frontend/app/tab/tabbar.tsx` | [#2678](https://github.com/wavetermdev/waveterm/pull/2678), [#2789](https://github.com/wavetermdev/waveterm/pull/2789), [#3263](https://github.com/wavetermdev/waveterm/pull/3263), [#3331](https://github.com/wavetermdev/waveterm/pull/3331), [#3353](https://github.com/wavetermdev/waveterm/pull/3353) |
| `frontend/app/view/preview/preview-directory.tsx` **(patched)** | [#3220](https://github.com/wavetermdev/waveterm/pull/3220), [#3343](https://github.com/wavetermdev/waveterm/pull/3343), [#3399](https://github.com/wavetermdev/waveterm/pull/3399), [#3440](https://github.com/wavetermdev/waveterm/pull/3440), [#3443](https://github.com/wavetermdev/waveterm/pull/3443) |
| `frontend/app/view/term/osc-handlers.ts` | [#2858](https://github.com/wavetermdev/waveterm/pull/2858), [#3004](https://github.com/wavetermdev/waveterm/pull/3004), [#3205](https://github.com/wavetermdev/waveterm/pull/3205), [#3275](https://github.com/wavetermdev/waveterm/pull/3275), [#3399](https://github.com/wavetermdev/waveterm/pull/3399) |
| `frontend/types/custom.d.ts` | [#2742](https://github.com/wavetermdev/waveterm/pull/2742), [#2763](https://github.com/wavetermdev/waveterm/pull/2763), [#2789](https://github.com/wavetermdev/waveterm/pull/2789), [#3205](https://github.com/wavetermdev/waveterm/pull/3205), [#3220](https://github.com/wavetermdev/waveterm/pull/3220) |
| `pkg/blockcontroller/shellcontroller.go` | [#2763](https://github.com/wavetermdev/waveterm/pull/2763), [#2835](https://github.com/wavetermdev/waveterm/pull/2835), [#2940](https://github.com/wavetermdev/waveterm/pull/2940), [#3058](https://github.com/wavetermdev/waveterm/pull/3058), [#3275](https://github.com/wavetermdev/waveterm/pull/3275) |
| `pkg/shellexec/shellexec.go` | [#2940](https://github.com/wavetermdev/waveterm/pull/2940), [#3152](https://github.com/wavetermdev/waveterm/pull/3152), [#3182](https://github.com/wavetermdev/waveterm/pull/3182), [#3402](https://github.com/wavetermdev/waveterm/pull/3402), [#3421](https://github.com/wavetermdev/waveterm/pull/3421) |
| `pkg/wconfig/defaultconfig/settings.json` | [#2835](https://github.com/wavetermdev/waveterm/pull/2835), [#3220](https://github.com/wavetermdev/waveterm/pull/3220), [#3293](https://github.com/wavetermdev/waveterm/pull/3293), [#3331](https://github.com/wavetermdev/waveterm/pull/3331), [#3407](https://github.com/wavetermdev/waveterm/pull/3407) |
| `.gitignore` | [#3220](https://github.com/wavetermdev/waveterm/pull/3220), [#3235](https://github.com/wavetermdev/waveterm/pull/3235), [#3275](https://github.com/wavetermdev/waveterm/pull/3275), [#3479](https://github.com/wavetermdev/waveterm/pull/3479) |
| `emain/preload.ts` | [#2742](https://github.com/wavetermdev/waveterm/pull/2742), [#2763](https://github.com/wavetermdev/waveterm/pull/2763), [#2789](https://github.com/wavetermdev/waveterm/pull/2789), [#3220](https://github.com/wavetermdev/waveterm/pull/3220) |
| `frontend/app/block/blockutil.tsx` | [#3220](https://github.com/wavetermdev/waveterm/pull/3220), [#3312](https://github.com/wavetermdev/waveterm/pull/3312), [#3399](https://github.com/wavetermdev/waveterm/pull/3399), [#3479](https://github.com/wavetermdev/waveterm/pull/3479) |
| `frontend/app/element/markdown.tsx` **(patched)** | [#2103](https://github.com/wavetermdev/waveterm/pull/2103), [#3399](https://github.com/wavetermdev/waveterm/pull/3399), [#3443](https://github.com/wavetermdev/waveterm/pull/3443), [#3478](https://github.com/wavetermdev/waveterm/pull/3478) |
| `frontend/app/store/global.ts` | [#2789](https://github.com/wavetermdev/waveterm/pull/2789), [#3205](https://github.com/wavetermdev/waveterm/pull/3205), [#3275](https://github.com/wavetermdev/waveterm/pull/3275), [#3480](https://github.com/wavetermdev/waveterm/pull/3480) |
| `frontend/app/tab/tab.scss` | [#2789](https://github.com/wavetermdev/waveterm/pull/2789), [#2835](https://github.com/wavetermdev/waveterm/pull/2835), [#3220](https://github.com/wavetermdev/waveterm/pull/3220), [#3353](https://github.com/wavetermdev/waveterm/pull/3353) |
| `frontend/app/tab/tab.tsx` | [#2789](https://github.com/wavetermdev/waveterm/pull/2789), [#2835](https://github.com/wavetermdev/waveterm/pull/2835), [#3312](https://github.com/wavetermdev/waveterm/pull/3312), [#3353](https://github.com/wavetermdev/waveterm/pull/3353) |
| `frontend/app/tab/tabcontextmenu.ts` | [#3184](https://github.com/wavetermdev/waveterm/pull/3184), [#3263](https://github.com/wavetermdev/waveterm/pull/3263), [#3312](https://github.com/wavetermdev/waveterm/pull/3312), [#3353](https://github.com/wavetermdev/waveterm/pull/3353) |
| `frontend/app/view/preview/preview-edit.tsx` **(patched)** | [#2461](https://github.com/wavetermdev/waveterm/pull/2461), [#3312](https://github.com/wavetermdev/waveterm/pull/3312), [#3399](https://github.com/wavetermdev/waveterm/pull/3399), [#3443](https://github.com/wavetermdev/waveterm/pull/3443) |
| `frontend/app/view/preview/preview-model.tsx` **(patched)** | [#2763](https://github.com/wavetermdev/waveterm/pull/2763), [#3235](https://github.com/wavetermdev/waveterm/pull/3235), [#3399](https://github.com/wavetermdev/waveterm/pull/3399), [#3443](https://github.com/wavetermdev/waveterm/pull/3443) |
| `frontend/app/view/webview/webview.tsx` **(patched)** | [#3220](https://github.com/wavetermdev/waveterm/pull/3220), [#3275](https://github.com/wavetermdev/waveterm/pull/3275), [#3358](https://github.com/wavetermdev/waveterm/pull/3358), [#3420](https://github.com/wavetermdev/waveterm/pull/3420) |
| `frontend/app/workspace/widgets.tsx` | [#2789](https://github.com/wavetermdev/waveterm/pull/2789), [#3220](https://github.com/wavetermdev/waveterm/pull/3220), [#3312](https://github.com/wavetermdev/waveterm/pull/3312), [#3399](https://github.com/wavetermdev/waveterm/pull/3399) |
| `pkg/waveobj/wtype.go` | [#2763](https://github.com/wavetermdev/waveterm/pull/2763), [#2940](https://github.com/wavetermdev/waveterm/pull/2940), [#3263](https://github.com/wavetermdev/waveterm/pull/3263), [#3312](https://github.com/wavetermdev/waveterm/pull/3312) |
| `pkg/wconfig/defaultconfig/widgets.json` | [#2763](https://github.com/wavetermdev/waveterm/pull/2763), [#3220](https://github.com/wavetermdev/waveterm/pull/3220), [#3312](https://github.com/wavetermdev/waveterm/pull/3312), [#3399](https://github.com/wavetermdev/waveterm/pull/3399) |
| `pkg/wcore/workspace.go` | [#2681](https://github.com/wavetermdev/waveterm/pull/2681), [#2763](https://github.com/wavetermdev/waveterm/pull/2763), [#3117](https://github.com/wavetermdev/waveterm/pull/3117), [#3312](https://github.com/wavetermdev/waveterm/pull/3312) |
| `CLAUDE.md` | [#2789](https://github.com/wavetermdev/waveterm/pull/2789), [#3220](https://github.com/wavetermdev/waveterm/pull/3220), [#3235](https://github.com/wavetermdev/waveterm/pull/3235) |
| `Taskfile.yml` | [#2789](https://github.com/wavetermdev/waveterm/pull/2789), [#3186](https://github.com/wavetermdev/waveterm/pull/3186), [#3331](https://github.com/wavetermdev/waveterm/pull/3331) |
| `electron-builder.config.cjs` | [#3220](https://github.com/wavetermdev/waveterm/pull/3220), [#3263](https://github.com/wavetermdev/waveterm/pull/3263), [#3331](https://github.com/wavetermdev/waveterm/pull/3331) |
| `emain/emain-ipc.ts` | [#2763](https://github.com/wavetermdev/waveterm/pull/2763), [#2789](https://github.com/wavetermdev/waveterm/pull/2789), [#3220](https://github.com/wavetermdev/waveterm/pull/3220) |
| `emain/emain.ts` | [#3220](https://github.com/wavetermdev/waveterm/pull/3220), [#3280](https://github.com/wavetermdev/waveterm/pull/3280), [#3413](https://github.com/wavetermdev/waveterm/pull/3413) |
| `frontend/app/store/services.ts` | [#2763](https://github.com/wavetermdev/waveterm/pull/2763), [#2789](https://github.com/wavetermdev/waveterm/pull/2789), [#3263](https://github.com/wavetermdev/waveterm/pull/3263) |
| `frontend/app/tab/vtabbar.tsx` | [#3312](https://github.com/wavetermdev/waveterm/pull/3312), [#3331](https://github.com/wavetermdev/waveterm/pull/3331), [#3353](https://github.com/wavetermdev/waveterm/pull/3353) |
| `frontend/app/view/codeeditor/codeeditor.tsx` | [#2461](https://github.com/wavetermdev/waveterm/pull/2461), [#3220](https://github.com/wavetermdev/waveterm/pull/3220), [#3312](https://github.com/wavetermdev/waveterm/pull/3312) |
| `frontend/app/view/preview/preview.tsx` | [#3066](https://github.com/wavetermdev/waveterm/pull/3066), [#3235](https://github.com/wavetermdev/waveterm/pull/3235), [#3399](https://github.com/wavetermdev/waveterm/pull/3399) |
| `frontend/preview/mock/mockwaveenv.ts` | [#3066](https://github.com/wavetermdev/waveterm/pull/3066), [#3205](https://github.com/wavetermdev/waveterm/pull/3205), [#3293](https://github.com/wavetermdev/waveterm/pull/3293) |
| `frontend/tailwindsetup.css` | [#3220](https://github.com/wavetermdev/waveterm/pull/3220), [#3293](https://github.com/wavetermdev/waveterm/pull/3293), [#3312](https://github.com/wavetermdev/waveterm/pull/3312) |
| `frontend/types/waveevent.d.ts` | [#3275](https://github.com/wavetermdev/waveterm/pull/3275), [#3293](https://github.com/wavetermdev/waveterm/pull/3293), [#3479](https://github.com/wavetermdev/waveterm/pull/3479) |
| `frontend/wave.ts` | [#2789](https://github.com/wavetermdev/waveterm/pull/2789), [#3220](https://github.com/wavetermdev/waveterm/pull/3220), [#3480](https://github.com/wavetermdev/waveterm/pull/3480) |
| `pkg/remote/conncontroller/conncontroller.go` | [#3152](https://github.com/wavetermdev/waveterm/pull/3152), [#3220](https://github.com/wavetermdev/waveterm/pull/3220), [#3421](https://github.com/wavetermdev/waveterm/pull/3421) |
| `pkg/tsgen/tsgenevent.go` | [#3275](https://github.com/wavetermdev/waveterm/pull/3275), [#3293](https://github.com/wavetermdev/waveterm/pull/3293), [#3479](https://github.com/wavetermdev/waveterm/pull/3479) |
| `pkg/waveobj/objrtinfo.go` | [#3004](https://github.com/wavetermdev/waveterm/pull/3004), [#3086](https://github.com/wavetermdev/waveterm/pull/3086), [#3293](https://github.com/wavetermdev/waveterm/pull/3293) |
| `pkg/wps/wpstypes.go` | [#3275](https://github.com/wavetermdev/waveterm/pull/3275), [#3293](https://github.com/wavetermdev/waveterm/pull/3293), [#3479](https://github.com/wavetermdev/waveterm/pull/3479) |
| `pkg/wshrpc/wshremote/wshremote_file.go` | [#2856](https://github.com/wavetermdev/waveterm/pull/2856), [#3220](https://github.com/wavetermdev/waveterm/pull/3220), [#3399](https://github.com/wavetermdev/waveterm/pull/3399) |
| `.github/workflows/build-helper.yml` | [#3186](https://github.com/wavetermdev/waveterm/pull/3186), [#3312](https://github.com/wavetermdev/waveterm/pull/3312) |
| `docs/docs/wsh-reference.mdx` | [#3333](https://github.com/wavetermdev/waveterm/pull/3333), [#3479](https://github.com/wavetermdev/waveterm/pull/3479) |
| `electron.vite.config.ts` | [#3399](https://github.com/wavetermdev/waveterm/pull/3399), [#3479](https://github.com/wavetermdev/waveterm/pull/3479) |
| `emain/emain-tabview.ts` | [#3220](https://github.com/wavetermdev/waveterm/pull/3220), [#3358](https://github.com/wavetermdev/waveterm/pull/3358) |
| `emain/preload-webview.ts` | [#3220](https://github.com/wavetermdev/waveterm/pull/3220), [#3275](https://github.com/wavetermdev/waveterm/pull/3275) |
| `frontend/app/aipanel/waveai-model.tsx` | [#3086](https://github.com/wavetermdev/waveterm/pull/3086), [#3275](https://github.com/wavetermdev/waveterm/pull/3275) |
| `frontend/app/block/block.tsx` **(patched)** | [#3399](https://github.com/wavetermdev/waveterm/pull/3399), [#3429](https://github.com/wavetermdev/waveterm/pull/3429) |
| `frontend/app/block/blockframe-header.tsx` | [#3184](https://github.com/wavetermdev/waveterm/pull/3184), [#3235](https://github.com/wavetermdev/waveterm/pull/3235) |
| `frontend/app/store/global-atoms.ts` | [#3205](https://github.com/wavetermdev/waveterm/pull/3205), [#3275](https://github.com/wavetermdev/waveterm/pull/3275) |
| `frontend/app/tab/tabbar.scss` | [#2789](https://github.com/wavetermdev/waveterm/pull/2789), [#3220](https://github.com/wavetermdev/waveterm/pull/3220) |
| `frontend/app/theme.scss` | [#2238](https://github.com/wavetermdev/waveterm/pull/2238), [#3220](https://github.com/wavetermdev/waveterm/pull/3220) |
| `frontend/app/view/term/termutil.ts` | [#2461](https://github.com/wavetermdev/waveterm/pull/2461), [#3220](https://github.com/wavetermdev/waveterm/pull/3220) |
| `frontend/app/view/term/termwrap.test.ts` | [#2940](https://github.com/wavetermdev/waveterm/pull/2940), [#3331](https://github.com/wavetermdev/waveterm/pull/3331) |
| `frontend/app/view/waveconfig/waveconfig-model.ts` | [#2789](https://github.com/wavetermdev/waveterm/pull/2789), [#3480](https://github.com/wavetermdev/waveterm/pull/3480) |
| `frontend/app/workspace/workspace.tsx` | [#2789](https://github.com/wavetermdev/waveterm/pull/2789), [#3220](https://github.com/wavetermdev/waveterm/pull/3220) |
| `frontend/layout/lib/layoutModel.ts` | [#3205](https://github.com/wavetermdev/waveterm/pull/3205), [#3263](https://github.com/wavetermdev/waveterm/pull/3263) |
| `frontend/preview/mock/defaultconfig.ts` **(patched)** | [#3443](https://github.com/wavetermdev/waveterm/pull/3443), [#3480](https://github.com/wavetermdev/waveterm/pull/3480) |
| `frontend/util/keyutil.ts` | [#3331](https://github.com/wavetermdev/waveterm/pull/3331), [#3406](https://github.com/wavetermdev/waveterm/pull/3406) |
| `frontend/util/wsutil.ts` | [#2101](https://github.com/wavetermdev/waveterm/pull/2101), [#2245](https://github.com/wavetermdev/waveterm/pull/2245) |
| `pkg/aiusechat/openaichat/openaichat-backend.go` | [#3290](https://github.com/wavetermdev/waveterm/pull/3290), [#3476](https://github.com/wavetermdev/waveterm/pull/3476) |
| `pkg/aiusechat/openaichat/openaichat-types.go` | [#3290](https://github.com/wavetermdev/waveterm/pull/3290), [#3476](https://github.com/wavetermdev/waveterm/pull/3476) |
| `pkg/remote/sshclient.go` | [#3401](https://github.com/wavetermdev/waveterm/pull/3401), [#3421](https://github.com/wavetermdev/waveterm/pull/3421) |
| `pkg/service/workspaceservice/workspaceservice.go` | [#2763](https://github.com/wavetermdev/waveterm/pull/2763), [#3353](https://github.com/wavetermdev/waveterm/pull/3353) |
| `pkg/util/shellutil/shellintegration/zsh_zshrc.sh` | [#3004](https://github.com/wavetermdev/waveterm/pull/3004), [#3016](https://github.com/wavetermdev/waveterm/pull/3016) |
| `pkg/util/shellutil/shellutil.go` | [#2406](https://github.com/wavetermdev/waveterm/pull/2406), [#3016](https://github.com/wavetermdev/waveterm/pull/3016) |
| `pkg/wavebase/wavebase.go` | [#2406](https://github.com/wavetermdev/waveterm/pull/2406), [#3404](https://github.com/wavetermdev/waveterm/pull/3404) |
| `schema/widgets.json` | [#3220](https://github.com/wavetermdev/waveterm/pull/3220), [#3408](https://github.com/wavetermdev/waveterm/pull/3408) |
