# Browser Widget — Research: Current State & The Challenge

**Branch:** `feature/browser-widget`
**Date:** 2026-08-24
**Status:** Research phase

---

## Summary

WaveTerm's browser functionality is built on Electron's `<webview>` tag — a
DOM element that embeds Chromium web content. Electron officially
**recommends not using this tag** due to ongoing architectural instability in
Chromium's webview implementation. This document maps the current wiring,
explains why it's a maintenance liability, and surveys alternative approaches.

---

## Current State: How the browser is wired

### Architecture overview

```
┌─────────────────────────────────────────────────────┐
│  Renderer Process (React)                           │
│                                                     │
│  blockregistry.ts                                   │
│    "web" → WebViewModel                             │
│    "tsunami" → TsunamiViewModel (extends WebViewModel)│
│    "help" → HelpViewModel (extends WebViewModel)    │
│                                                     │
│  WebViewModel (webview.tsx)                         │
│    ├── URL bar, nav buttons, search, bookmarks      │
│    ├── Media controls (mute, play/pause)            │
│    ├── Zoom control                                 │
│    ├── Partition/session management                 │
│    └── <webview> tag (Electron DOM element)         │
│         ├── src={url}                               │
│         ├── preload={preload-webview.cjs}           │
│         ├── partition={session partition}           │
│         └── useragent={custom UA}                  │
└──────────────────────┬──────────────────────────────┘
                       │ IPC
┌──────────────────────▼──────────────────────────────┐
│  Main Process (Electron)                            │
│                                                     │
│  emain-tabview.ts                                   │
│    webPreferences: { webviewTag: true }             │
│    did-attach-webview → setWindowOpenHandler        │
│                                                     │
│  emain-builder.ts                                   │
│    webPreferences: { webviewTag: true }             │
│                                                     │
│  emain-web.ts                                       │
│    getWebContentsByBlockId()                        │
│    webGetSelector() — execute JS in webview         │
│                                                     │
│  emain-ipc.ts                                       │
│    clear-webview-storage handler                    │
│    get-webview-preload handler                      │
│                                                     │
│  preload-webview.ts (injected into every webview)   │
│    Image context menu → IPC                         │
│    Mouse button 3/4 → back/forward navigation       │
└─────────────────────────────────────────────────────┘
```

### Key files

| File | Lines | Role |
|------|-------|------|
| `frontend/app/view/webview/webview.tsx` | 1135 | Main webview component + `WebViewModel` class |
| `frontend/app/view/webview/webviewenv.ts` | — | Webview environment abstraction |
| `frontend/app/block/blockregistry.ts` | 65 | Registers `"web"` → `WebViewModel` |
| `frontend/app/view/tsunami/tsunami.tsx` | ~306 | `TsunamiViewModel extends WebViewModel` (WaveApp) |
| `frontend/app/view/helpview/helpview.tsx` | ~123 | `HelpViewModel extends WebViewModel` (docs) |
| `emain/preload-webview.ts` | 39 | Preload script injected into webviews |
| `emain/emain-web.ts` | 65 | Backend web content operations |
| `emain/emain-tabview.ts` | 395 | Tab view with `webviewTag: true` |
| `emain/emain-builder.ts` | 135 | Window builder with `webviewTag: true` |
| `emain/emain-ipc.ts` | — | IPC handlers for webview storage, preload |

### Electron APIs used by the webview

The `<webview>` tag in `webview.tsx` (line 1110) uses these Electron
`WebviewTag` APIs:

**Navigation:** `loadURL()`, `goBack()`, `goForward()`, `reload()`, `stop()`,
`getURL()`, `canGoBack()`, `canGoForward()`, `clearHistory()`

**Focus/Input:** `focus()`, `getWebContentsId()`, `setAudioMuted()`,
`isAudioMuted()`

**Zoom:** `setZoomFactor()`, `getZoomFactor()`

**DevTools:** `openDevTools()`, `closeDevTools()`, `isDevToolsOpened()`

**Search:** `findInPage()`, `stopFindInPage()`

**JavaScript execution:** `executeJavaScript()`

**Events (13 listeners):** `did-frame-navigate`, `did-navigate-in-page`,
`did-navigate`, `did-start-loading`, `did-stop-loading`, `new-window`,
`did-fail-load`, `focus`, `blur`, `dom-ready`, `media-started-playing`,
`media-paused`, `found-in-page`

### Webview attributes

```tsx
<webview
    id="webview"
    className="webview"
    ref={model.webviewRef}
    src={metaUrlInitial}
    data-blockid={model.blockId}
    data-webcontentsid={webContentsId}
    preload={getWebviewPreloadUrl(env)}
    allowpopups="true"
    partition={webPartition}
    useragent={userAgent}
/>
```

### Session/partition handling

Partitions isolate cookies and storage between webviews:

1. **TsunamiViewModel** — sets `partitionOverride = atom("tsunami:${blockId}")`
   for per-app isolation
2. **Block metadata** — `web:partition` meta key allows custom partitions
3. **Default** — Electron's default session (shared)

Storage clearing via `clearCookiesAndStorage()` → IPC →
`wc.session.clearStorageData()` in main process.

### Existing patches touching the webview

| Patch | File | Change |
|-------|------|--------|
| `002-bookmark-typeahead-fix.patch` | `webview.tsx` | Fixed bookmark suggestions + config path |
| `003-focus-fix.patch` | `block.tsx` | Fixed focus flapping between multiple webview blocks |

Both patches touch files now in `PATCHED_FILES`, meaning any webview refactor
must account for the revert-then-repatch sync workflow.

### Classes extending WebViewModel

**TsunamiViewModel** (`frontend/app/view/tsunami/tsunami.tsx`):
- Extends `WebViewModel` for WaveApp embedding
- Hides navigation bar
- Custom partition: `tsunami:${blockId}`
- Adds shell process status tracking
- Custom settings menu (filters out nav items)

**HelpViewModel** (`frontend/app/view/helpview/helpview.tsx`):
- Extends `WebViewModel` for documentation viewer
- Fixed homepage URL to docsite
- Simplified navigation (no URL input)
- Custom icon and name

Any replacement for `WebViewModel` must preserve these extension points or
provide equivalent mechanisms.

---

## The Challenge: Why the current wiring is a maintenance issue

### 1. Electron officially recommends against `<webview>`

From the [Electron webview-tag docs](https://github.com/electron/electron/blob/main/docs/api/webview-tag.md):

> Electron's `webview` tag is based on Chromium's `webview`, which is
> undergoing dramatic architectural changes. This impacts the stability of
> `webviews`, including rendering, navigation, and event routing. We
> currently recommend to **not use the `webview` tag** and to consider
> alternatives, like `iframe`, a `WebContentsView`, or an architecture that
> avoids embedded content altogether.

From the [Electron web-embeds tutorial](https://github.com/electron/electron/blob/main/docs/tutorial/web-embeds.md):

> WebViews are based on Chromium's WebViews and are **not explicitly
> supported by Electron**. We do not guarantee that the WebView API will
> remain available in future versions of Electron.

### 2. No removal timeline, but ongoing instability

Electron maintainers stated in [issue #34356](https://github.com/electron/electron/issues/34356):

> "As of this time, there aren't any plans to remove `webviewTag` on
> Electron's side"

However, the tag is built on Chromium's `<webview>` which is undergoing
"dramatic architectural changes." This means:

- **Rendering bugs** may appear with Chromium upgrades
- **Event routing** may change between Electron versions
- **Navigation behavior** may shift
- No guarantee the API will remain stable

### 3. Known bugs not present in alternatives

From [Electron issue #18187](https://github.com/electron/electron/issues/18187):

> "There's a fair number of bugs in webviews right now... Most of these
> aren't present in BrowserView, so you definitely want to use that instead
> if it's at all possible to do so."

### 4. Security configuration is minimal

The current webview has:
- `allowpopups="true"` — allows popup windows
- No explicit `sandbox` setting
- No explicit `contextIsolation` setting
- No explicit `nodeIntegration` setting (defaults to disabled)

While webviews run in a separate process with node integration disabled by
default, the lack of explicit security settings is a concern. An
ESLint rule
([no-electron-enable-webview-tag](https://nick2bad4u.github.io/eslint-plugin-SDL-2/docs/rules/no-electron-enable-webview-tag))
exists specifically to flag `webviewTag: true` as a security concern.

### 5. Deep coupling across processes

The webview is wired across three layers:

1. **Renderer** — `WebViewModel` manages the `<webview>` DOM element and all
   user interactions (URL bar, nav, search, zoom, media)
2. **Main process** — `emain-tabview.ts` enables `webviewTag: true`,
   `emain-web.ts` provides backend operations, `emain-ipc.ts` handles storage
3. **Preload** — `preload-webview.ts` is injected into every webview for
   context menus and mouse navigation

Replacing the `<webview>` tag requires changes in all three layers, plus
updating `TsunamiViewModel` and `HelpViewModel` which extend it.

### 6. Fork maintenance impact

Two of our 8 patches touch webview-related files:
- `002-bookmark-typeahead-fix.patch` — modifies `webview.tsx`
- `003-focus-fix.patch` — modifies `block.tsx` (focus handling for webviews)

Any upstream changes to the webview component risk conflicting with these
patches. The sync workflow reverts and re-applies them, but if upstream
significantly refactors the webview (e.g., migrates to `WebContentsView`),
our patches may no longer apply.

---

## Alternative approaches surveyed

### A. Electron `WebContentsView` (Electron 30+)

[Docs](https://github.com/electron/electron/blob/main/docs/api/web-contents-view.md) |
[Migration guide](https://github.com/electron/website/blob/main/blog/migrate-to-webcontentsview.md)

**What it is:** Electron's recommended replacement for both `<webview>` and
the deprecated `BrowserView`. A main-process view that displays web content,
aligned with Chromium's Views API.

**Pros:**
- Official Electron recommendation — future-proof
- More stable than `<webview>` (tracks Chromium Views API directly)
- Full `WebContents` access (same as `BrowserWindow`)
- Supports `BaseWindow` + multiple `WebContentsView` pattern
- Already available in WaveTerm's Electron 41.1.0

**Cons:**
- **Main process only** — not a DOM element, requires IPC coordination for
  positioning relative to React/DOM content
- More complex positioning (programmatic bounds vs CSS)
- Requires architectural refactor: webview logic moves from renderer to main
- Breaking change for `TsunamiViewModel` and `HelpViewModel` extension pattern

**Migration scope:** Large. Would require rewriting `WebViewModel` to
coordinate with a main-process `WebContentsView` instead of rendering a
`<webview>` DOM element.

### B. CEF (Chromium Embedded Framework)

[Project](https://github.com/chromiumembedded/cef) |
[Docs](https://chromiumembedded.github.io/cef/)

**What it is:** A standalone framework for embedding Chromium in C/C++
applications. Production-ready, 100M+ installed instances.

**Pros:**
- Full Chromium feature parity
- Stable C/C++ API with ABI compatibility
- LTS branches with extended security support

**Cons:**
- **Cannot run alongside Electron** — both bundle Chromium, would conflict
- Would require a separate native process + IPC bridge
- ~150-250 MB additional binary size
- Electron already IS Chromium — adding CEF duplicates the engine
- No practical examples of CEF embedded in Electron

**Verdict:** Not viable for embedding within Electron. Would mean replacing
Electron entirely.

### C. Playwright (pixel streaming)

[Screencast API](https://playwright.dev/docs/api/class-screencast) |
[Example project](https://github.com/matyascimbulka/browser-live-view-example)

**What it is:** Browser automation tool with a new screencast API (v1.59+)
that can stream JPEG frames in real-time.

**Pros:**
- Can stream browser content as video frames
- Cross-browser support (Chromium, Firefox, WebKit)
- Existing proof-of-concept projects for live browser viewing

**Cons:**
- **Not designed for interactive embedding** — it's a testing/automation tool
- Pixel streaming adds latency (not suitable for real-time interaction)
- No native UI integration — would need custom video player
- Input handling would need to be implemented via CDP (Chrome DevTools Protocol)
- Launches its own browser process — not "in-process"

**Verdict:** Interesting for AI agent visualization or remote browsing, but
not practical for an interactive desktop browser widget.

### D. Servo

[Project](https://servo.org) |
[Embedding update](https://servo.org/blog/2024/01/19/embedding-update/)

**What it is:** A web browser engine written in Rust, originally by Mozilla,
now under Linux Foundation Europe.

**Pros:**
- Lightweight (no bundled Chromium)
- Parallel layout engine (unique among web engines)
- Rust-based (memory safety)
- Offscreen rendering support

**Cons:**
- **Not production-ready** — "still in an experimental phase"
- 79% WPT pass rate (missing many web features)
- No stable embedding API yet
- Proof-of-concept Tauri integration exists but "definitely not
  production-ready"
- Cannot compete with established engines for real-world website compatibility

**Verdict:** Monitor for the future. Not ready for production use today.

### E. wry (Tauri's webview wrapper)

[Project](https://github.com/tauri-apps/wry)

**What it is:** Cross-platform Rust library that wraps system-native webviews
(WebView2 on Windows, WKWebView on macOS, WebKitGTK on Linux).

**Pros:**
- Lightweight (uses system webview, no bundled Chromium)
- Can be used standalone (not dependent on Tauri)
- Supports child webviews for embedding
- JavaScript bindings available via [webviewjs](https://github.com/webviewjs/webview)

**Cons:**
- **Cannot be embedded in Electron** — it's an alternative to Electron, not
  a component for it
- Different webview engines per platform (inconsistent rendering)
- Would require replacing Electron entirely

**Verdict:** Excellent for new projects, but not a component for an existing
Electron app.

### F. No practical non-Electron browser embedding found

Research across GitHub found **zero projects** that successfully embed a
non-Electron browser engine inside an Electron app. This makes sense:

1. Electron already bundles Chromium — adding another engine duplicates resources
2. Process complexity of running multiple browser engines is architecturally
   difficult
3. No benefit since Electron's Chromium is already full-featured
4. If you want a different engine, use a different framework (Tauri, CEF, etc.)

---

## Summary comparison

| Approach | Viable in Electron? | Production-ready? | Migration effort | Future-proof? |
|----------|---------------------|-------------------|------------------|---------------|
| **WebContentsView** | Yes (Electron 30+) | Yes | Large | Yes (official path) |
| **CEF** | No (conflicts) | Yes | N/A | Yes |
| **Playwright streaming** | Technically, but impractical | Yes | Very large | No (wrong tool) |
| **Servo** | No (no embedding API) | No | N/A | Unknown |
| **wry** | No (Electron alternative) | Yes | N/A | Yes |

---

## Sources

### Electron documentation
- [webview-tag.md](https://github.com/electron/electron/blob/main/docs/api/webview-tag.md) — Official webview tag docs with deprecation warning
- [web-contents-view.md](https://github.com/electron/electron/blob/main/docs/api/web-contents-view.md) — WebContentsView API docs
- [browser-view.md](https://github.com/electron/electron/blob/main/docs/api/browser-view.md) — Deprecated BrowserView docs
- [web-embeds.md](https://github.com/electron/electron/blob/main/docs/tutorial/web-embeds.md) — Web embedding options comparison
- [Electron 30 blog post](https://electronjs.org/blog/electron-30-0) — WebContentsView introduction, BrowserView deprecation
- [Migration guide](https://github.com/electron/website/blob/main/blog/migrate-to-webcontentsview.md) — BrowserView → WebContentsView migration

### Electron issues
- [Issue #18187](https://github.com/electron/electron/issues/18187) — "Is it safe to use webview tag in Electron?" — security assessment and bug list
- [Issue #34356](https://github.com/electron/electron/issues/34356) — No plans to remove webviewTag, but instability acknowledged

### Security
- [eslint-plugin-SDL-2: no-electron-enable-webview-tag](https://nick2bad4u.github.io/eslint-plugin-SDL-2/docs/rules/no-electron-enable-webview-tag) — ESLint rule flagging `webviewTag: true`

### Alternative engines
- [CEF project](https://github.com/chromiumembedded/cef) — Chromium Embedded Framework
- [CEF branches](https://chromiumembedded.github.io/cef/branches_and_building.html) — Release branches
- [Playwright screencast API](https://playwright.dev/docs/api/class-screencast) — Frame streaming
- [browser-live-view-example](https://github.com/matyascimbulka/browser-live-view-example) — Playwright live view PoC
- [PhantomStream](https://github.com/fullselfbrowsing/PhantomStream) — DOM-native browser mirroring
- [Servo](https://servo.org) — Rust web engine
- [Servo 2024 review](https://servo.org/blog/2025/01/31/servo-in-2024/) — Status update
- [Servo embedding update](https://servo.org/blog/2024/01/19/embedding-update/) — Tauri integration PoC
- [wry](https://github.com/tauri-apps/wry) — Tauri's webview wrapper
- [webviewjs](https://github.com/webviewjs/webview) — JavaScript bindings for wry

### WaveTerm codebase
- `frontend/app/view/webview/webview.tsx` — Main webview component (1135 lines)
- `frontend/app/block/blockregistry.ts` — Block type registration
- `frontend/app/view/tsunami/tsunami.tsx` — WaveApp webview extension
- `frontend/app/view/helpview/helpview.tsx` — Help docs webview extension
- `emain/preload-webview.ts` — Preload script injected into webviews
- `emain/emain-web.ts` — Backend web content operations
- `emain/emain-tabview.ts` — Tab view with `webviewTag: true`
- `emain/emain-builder.ts` — Window builder with `webviewTag: true`
- `.github/patches/002-bookmark-typeahead-fix.patch` — Webview patch
- `.github/patches/003-focus-fix.patch` — Focus fix patch
