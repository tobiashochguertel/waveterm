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

### G. Remote browser streaming (WebSocket / WebRTC)

This approach decouples the browser from the Electron process entirely.
A browser runs on a server (or locally in a background process), its
framebuffer is captured and encoded as a video stream, and the stream is
sent to the client over WebSocket or WebRTC. The client renders the stream
in a `<canvas>` or `<video>` element and forwards mouse/keyboard input back.

This is the same pattern used by cloud gaming services (GeForce NOW, Google
Stadia), remote desktop tools (noVNC, Apache Guacamole), and browser
isolation platforms (Kasm, Hyperbeam).

#### Architecture

**Model A: Local streaming (browser runs on the same machine)**

```
┌─────────────────────────────────────────────────────────┐
│  WaveTerm (Electron)                                    │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │  React Renderer                                   │  │
│  │  BrowserWidget (new block type)                   │  │
│  │  ├── URL bar, nav, bookmarks, search              │  │
│  │  ├── <canvas> — renders incoming video frames     │  │
│  │  └── Input forwarder — mouse/keyboard → WebSocket │  │
│  └───────────┬───────────────────────────────────────┘  │
│              │ WebSocket (localhost)                     │
│  ┌───────────▼───────────────────────────────────────┐  │
│  │  Local streaming server (child process)           │  │
│  │  (Neko / vbrowser / Selkies / custom)             │  │
│  │  ├── Xvfb (virtual framebuffer)                   │  │
│  │  ├── Chromium / Firefox                           │  │
│  │  ├── Frame capture → H.264/VP8/JPEG encode        │  │
│  │  ├── Input injection → xdotool / XTEST            │  │
│  │  └── WebSocket server                             │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

- Latency: ~10-20ms (localhost loopback)
- Works offline (no network dependency)
- Still runs Chromium locally, but in an isolated process
- Simplest deployment: WaveTerm spawns the streaming server as a child process

**Model B: Remote streaming (browser runs on a server)**

```
┌─────────────────────────────────────────────────────────┐
│  WaveTerm (Electron, local machine)                     │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │  React Renderer                                   │  │
│  │  BrowserWidget (new block type)                   │  │
│  │  ├── URL bar, nav, bookmarks, search              │  │
│  │  ├── <canvas> or <video> — renders stream         │  │
│  │  └── Input forwarder — mouse/keyboard → WS/WebRTC │  │
│  └───────────┬───────────────────────────────────────┘  │
│              │ WebSocket or WebRTC (network)             │
└──────────────┼──────────────────────────────────────────┘
               │
               │ Network (LAN / VPN / Internet)
               │
┌──────────────▼──────────────────────────────────────────┐
│  Remote browser server                                  │
│                                                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Container or VM                                  │  │
│  │  ├── Xvfb (virtual framebuffer, e.g. 1920×1080)   │  │
│  │  ├── Browser (Chromium / Firefox / etc.)          │  │
│  │  ├── x11vnc or GStreamer (frame capture)          │  │
│  │  ├── Encoder (H.264 / VP8 / VP9 / JPEG)           │  │
│  │  ├── Input injection (xdotool / XTEST)            │  │
│  │  └── Streaming server (Neko / vbrowser / Selkies) │  │
│  └───────────────────────────────────────────────────┘  │
│                                                         │
│  Optional: Docker / Kubernetes orchestration            │
│  Optional: GPU acceleration (NVENC / VA-API)            │
│  Optional: Session persistence, multi-user sharing      │
└─────────────────────────────────────────────────────────┘
```

- Latency: ~20-100ms (depends on network)
- Requires network connectivity to the streaming server
- Browser runs in an isolated container/VM (security boundary)
- Can access networks not reachable from the local machine (VPN, restricted
  networks, corporate intranet)
- Multiple WaveTerm instances can share one browser session
- Server can run any browser engine (Chromium, Firefox, Servo in the future)

**Model C: Hybrid (configurable — local default, remote optional)**

```
┌─────────────────────────────────────────────────────────┐
│  WaveTerm (Electron)                                    │
│                                                         │
│  BrowserWidget config:                                  │
│  {                                                      │
│    "mode": "local" | "remote",                          │
│    "remote": {                                          │
│      "url": "wss://browser.example.com:8080",           │
│      "auth": "token or password"                        │
│    },                                                   │
│    "local": {                                           │
│      "engine": "chromium" | "firefox",                  │
│      "resolution": "1920x1080",                         │
│      "encoder": "h264" | "jpeg"                         │
│    }                                                    │
│  }                                                      │
│                                                         │
│  ┌─────────────┐       ┌─────────────────────────────┐  │
│  │ Local mode  │       │ Remote mode                 │  │
│  │             │       │                             │  │
│  │ Spawn child │       │ Connect to remote server    │  │
│  │ process     │       │ over WebSocket/WebRTC       │  │
│  │ (vbrowser/  │       │ (Neko/Kasm/Selkies)         │  │
│  │  Selkies)   │       │                             │  │
│  └──────┬──────┘       └──────────┬──────────────────┘  │
│         │                         │                      │
└─────────┼─────────────────────────┼──────────────────────┘
          │                         │
          ▼                         ▼
   Local browser              Remote browser
   (child process)            (container/VM)
```

- Default to local mode (works offline, minimal latency)
- User can configure remote server for specific use cases
- Same client-side code handles both (just different WebSocket endpoints)
- Most flexible approach

#### Transport protocols

**WebSocket**

- Simpler setup (single TCP connection, no STUN/TURN needed)
- Works through firewalls and proxies
- Lower CPU overhead (no ICE negotiation)
- Used by: Selkies (default), noVNC, Kasm
- Latency: slightly higher than WebRTC (TCP vs UDP), but fine for interactive
  use on localhost or LAN

**WebRTC**

- Lower latency (UDP transport, sub-frame encoding)
- Built-in congestion control and adaptive bitrate
- Requires STUN/TURN servers for NAT traversal (remote mode)
- Used by: Neko, vbrowser, Hyperbeam, vscreen
- Better for remote streaming over the internet

**Recommendation:** WebSocket for local mode (simplicity), WebRTC for remote
mode (latency). Selkies supports both, making it a good candidate for the
hybrid approach.

#### Encoding formats

| Format | Latency | Quality | CPU/GPU | Bandwidth | Use case |
|--------|---------|---------|---------|-----------|----------|
| **H.264** | Low | High | HW accel (NVENC/VA-API) or SW (x264) | 2-5 Mbps @ 1080p | Default, best balance |
| **VP8** | Low | Good | SW or HW | 3-8 Mbps @ 1080p | WebRTC default |
| **VP9** | Medium | Excellent | SW or HW | 1-3 Mbps @ 1080p | Better compression, higher CPU |
| **JPEG** | Very low | Medium (lossy) | Very low CPU | 5-20 Mbps @ 1080p | Fastest, lowest latency, high bandwidth |

For local streaming: JPEG or H.264 (low CPU, localhost has bandwidth)
For remote streaming: H.264 or VP8 (better compression for limited bandwidth)

#### Existing projects

| Project | Transport | Browser | Deployment | Embeddable | License |
|---------|-----------|---------|------------|------------|---------|
| **[Neko](https://github.com/m1k1o/neko)** | WebRTC | Chromium/Firefox in Docker | Docker container | iframe / Vue app | MIT |
| **[vbrowser](https://github.com/zulfikawr/vbrowser)** | WebRTC + GStreamer | Chrome/Chromium/Firefox | Single Go binary | Web client | MIT |
| **[Selkies](https://github.com/selkies-project/selkies)** | WebSocket (default) or WebRTC | Any X11 app | Python pip / Docker / k8s | HTML5 canvas (embeddable) | Apache 2.0 |
| **[noVNC](https://github.com/novnc/noVNC)** | WebSocket | Any VNC server | JS library + websockify | iframe / JS library | MPL 2.0 |
| **[Kasm Workspaces](https://kasm.com/)** | WebSocket | Chromium in container | Docker / k8s / enterprise | iframe via Developer API | Custom (free tier) |
| **[Hyperbeam](https://www.hyperbeam.com/)** | WebRTC | Cloud-hosted Chromium | SaaS (no self-hosting) | `<div>` via JS SDK | Commercial |
| **[vscreen](https://github.com/jameswebb68/vscreen)** | WebRTC | Headless Chromium + CDP | Node.js | `<video>` element | MIT |
| **[phantom-browse](https://github.com/Presidentsu/phantom-browse)** | VNC (noVNC) + Socket.IO | Chromium + Xvfb | Docker container | noVNC iframe | MIT |

#### Detailed project profiles

**Neko** — [GitHub](https://github.com/m1k1o/neko) | [Docs](https://github.com/m1k1o/neko/tree/master/docs)

Self-hosted virtual browser in Docker using WebRTC. The most popular
open-source remote browser project. Runs Chromium or Firefox inside a Docker
container with Xvfb, streams via WebRTC with VP8/H.264 encoding. Vue.js web
client. Supports multiple users watching the same session (co-browsing).
Battle-tested, active community.

- **Best for:** Remote streaming with multi-user support
- **Transport:** WebRTC (pion/webrtc in Go)
- **Encoding:** VP8/H.264 via GStreamer
- **Input:** Mouse, keyboard, clipboard via DataChannel
- **Docker image:** `m1k1o/neko` (Chromium), `m1k1o/neko:firefox` (Firefox)
- **Embedding:** Can be embedded via iframe or by integrating the Vue client

**vbrowser** — [GitHub](https://github.com/zulfikawr/vbrowser)

Single-binary Go application that streams Chrome, Chromium, or Firefox via
WebRTC and GStreamer. The simplest deployment option — one binary, no Docker
required. Ultra-low latency, 60 FPS streaming, hardware acceleration support.
SSH tunnel or Cloudflare for secure access.

- **Best for:** Local streaming (single binary, minimal setup)
- **Transport:** WebRTC (pion/webrtc)
- **Encoding:** VP8/H.264 via GStreamer, hardware acceleration
- **Input:** Mouse, keyboard via xdotool
- **Audio:** PulseAudio + Opus codec
- **Deployment:** Single binary, no container needed

**Selkies** — [GitHub](https://github.com/selkies-project/selkies) | [Docs](https://selkies-project.github.io/selkies/)

Open-source low-latency accelerated remote desktop streaming platform.
Started by Google engineers, now community-maintained. Streams over plain
WebSockets by default (no STUN/TURN needed), with WebRTC as opt-in. Uses
WebCodecs API on the client side for zero-copy rendering. Supports GPU
acceleration (NVENC, VA-API). Runs as a Python pip package — no Docker
required for local use.

- **Best for:** Hybrid approach (supports both WebSocket and WebRTC)
- **Transport:** WebSocket (default) or WebRTC (opt-in)
- **Encoding:** H.264 (hardware or software), JPEG, OpenH264
- **Client:** WebCodecs-based HTML5 (Chromium, Firefox, Safari)
- **Input:** Keyboard, mouse, gamepad, clipboard (two-way text and images)
- **Performance:** 60 FPS at Full HD, zero-copy rendering
- **Embedding:** "Any HTML5 web interface you wish to embed inside"
- **Deployment:** `pip install selkies` or Docker or Kubernetes

**noVNC** — [GitHub](https://github.com/novnc/noVNC) | [Embedding docs](https://novnc.com/noVNC/docs/EMBEDDING.html)

HTML5 VNC client library and application. The oldest and most widely deployed
solution. Connects to any VNC server via WebSocket (using websockify as a
proxy). Can be embedded via iframe or as a JavaScript library. Works with any
VNC server (x11vnc, TigerVNC, QEMU, etc.).

- **Best for:** Simple VNC-based streaming, maximum compatibility
- **Transport:** WebSocket (via websockify proxy)
- **Encoding:** VNC protocol ( Tight, H.264, Raw encodings)
- **Input:** Mouse, keyboard via VNC protocol
- **Embedding:** iframe (`vnc.html`) or JavaScript library (`RFB` class)
- **Limitation:** VNC protocol adds overhead vs. direct video encoding
- **Note:** iframe embedding requires HTTPS (mixed content blocking)

**Kasm Workspaces** — [Website](https://kasm.com/) | [Developer API](https://kasm.com/developer-api) | [Docs](https://docs.kasm.com)

Enterprise-grade container streaming platform. Streams containerized
browsers, desktops, and applications to any modern browser. Free tier
available, enterprise features for paid plans. Developer API allows
creating and controlling streaming sessions programmatically. Built-in
forward proxy with URL whitelisting/blacklisting.

- **Best for:** Enterprise/production remote browser isolation
- **Transport:** WebSocket (custom Guacamole-based connection proxy)
- **Browser:** Chromium in disposable containers
- **Features:** Session recording, multi-user, SAML SSO, GPU acceleration
- **Embedding:** iframe via Developer API (`embed_url` from REST API)
- **Deployment:** Docker, Kubernetes (Helm chart), or bare metal

**Hyperbeam** — [Website](https://www.hyperbeam.com/) | [SDK docs](https://docs.hyperbeam.com/) | [npm](https://www.npmjs.com/package/@hyperbeam/web)

Commercial cloud-hosted virtual browser API. No self-hosting — browsers run
on Hyperbeam's infrastructure. JavaScript SDK (`@hyperbeam/web`) creates a
virtual browser in a `<div>` element. Supports multiplayer (multiple users
on same session), programmatic navigation, tab management, permissions.

- **Best for:** Quick integration without infrastructure management
- **Transport:** WebRTC
- **Browser:** Cloud-hosted Chromium
- **Embedding:** `Hyperbeam(container, embedURL, options)` → `<div>`
- **Features:** Multiplayer cursors, programmatic tabs, volume control,
  frame callbacks (ImageBitmap / HTMLVideoElement), audio track callbacks
- **Cost:** Commercial (per-session pricing)
- **Limitation:** Data goes through Hyperbeam's servers (privacy concern)

**vscreen** — [GitHub](https://github.com/jameswebb68/vscreen)

Turns headless Chromium into a remotely viewable, controllable virtual screen.
Captures viewport via Chrome DevTools Protocol (CDP), encodes H.264/VP9 + Opus
audio, streams over WebRTC. Includes 47 MCP automation tools for AI agents.
Bidirectional input via DataChannel.

- **Best for:** AI agent browser automation with live visualization
- **Transport:** WebRTC
- **Capture:** CDP screencast (not Xvfb — uses headless Chromium directly)
- **Encoding:** H.264/VP9 video + Opus audio
- **Input:** Mouse + keyboard via DataChannel → CDP dispatch
- **Unique:** MCP tools for AI-driven page synthesis and automation

**phantom-browse** — [GitHub](https://github.com/Presidentsu/phantom-browse)

Security tool for isolating suspicious URL browsing in ephemeral Docker
containers. Uses Xvfb + Chromium + x11vnc + noVNC for live streaming. Full
network telemetry via CDP, VirusTotal integration, AI-powered threat analysis.

- **Best for:** Security analysis of suspicious URLs
- **Transport:** VNC (noVNC) + Socket.IO
- **Browser:** Chromium in disposable Docker container
- **Embedding:** noVNC iframe
- **Unique:** Network capture, threat detection, download scanning

#### Advantages over current `<webview>` approach

1. **No Electron `<webview>` dependency** — completely removes the deprecated
   tag and all its stability risks
2. **Engine independence** — server can run Chromium, Firefox, or any browser;
   not tied to Electron's bundled Chromium version
3. **Security isolation** — browser runs in a separate process/container/VM,
   not in the Electron process. Malicious pages can't access Electron's APIs
4. **Remote browsing** — browser can run on a server with different network
   access (VPN, restricted networks, corporate intranet, different geolocation)
5. **Simpler client** — just a video decoder + input forwarder, no WebContents
   API surface, no preload scripts, no IPC handlers
6. **Multi-user / co-browsing** — multiple WaveTerm instances can share one
   browser session (Neko, Hyperbeam support this natively)
7. **Session persistence** — browser session can survive WaveTerm restart
   (server keeps running, client reconnects)
8. **Scalability** — offload browser rendering to a more powerful server or
   GPU-equipped machine

#### Tradeoffs

1. **Requires a streaming server** — need to run Neko/vbrowser/Selkies
   somewhere (localhost, remote host, or container)
2. **Added latency** — network round-trip for every interaction
   - Local: ~10-20ms (barely noticeable)
   - Remote LAN: ~20-50ms (similar to remote desktop)
   - Remote Internet: ~50-150ms (depends on distance and connection)
3. **Bandwidth consumption** — video stream requires bandwidth
   - H.264 at 1080p: ~2-5 Mbps
   - JPEG at 1080p: ~5-20 Mbps
   - VP9 at 1080p: ~1-3 Mbps
4. **No offline use (remote mode)** — browser widget needs the streaming
   server running and reachable
5. **More moving parts** — Xvfb + browser + streaming server + WebSocket
   connection (vs. a single `<webview>` tag)
6. **Text rendering** — video encoding may produce slightly blurry text
   compared to native rendering (especially at lower bitrates)
7. **Input handling complexity** — need to map mouse/keyboard events to the
   remote browser, handle focus, clipboard sync, scrolling
8. **Audio** — need separate audio stream (Opus codec via WebRTC or
   WebSocket), adds complexity

#### Fit with WaveTerm's block system

A streaming-based browser widget would be a **new block type** (e.g.,
`"remotebrowser"` or `"streambrowser"`) rather than a modification of the
existing `"web"` block. This allows:

- Coexistence with the existing `<webview>`-based blocks (gradual migration)
- Different block icon and settings
- Configuration of streaming endpoint (local/remote, transport, encoder)
- No changes to `WebViewModel`, `TsunamiViewModel`, or `HelpViewModel`

The new block would register in `blockregistry.ts`:

```typescript
BlockRegistry.set("remotebrowser", RemoteBrowserViewModel);
```

And would need:
- `RemoteBrowserViewModel` — manages URL, connection state, settings
- `RemoteBrowserView` React component — renders `<canvas>`/`<video>`,
  forwards input
- WebSocket/WebRTC client — connects to streaming server
- Optional: local streaming server launcher (spawns child process for
  local mode)

---

## Summary comparison

| Approach | Viable in Electron? | Production-ready? | Migration effort | Future-proof? | Offline? |
|----------|---------------------|-------------------|------------------|---------------|----------|
| **WebContentsView** | Yes (Electron 30+) | Yes | Large | Yes (official path) | Yes |
| **CEF** | No (conflicts) | Yes | N/A | Yes | N/A |
| **Playwright streaming** | Technically, but impractical | Yes | Very large | No (wrong tool) | Yes |
| **Servo** | No (no embedding API) | No | N/A | Unknown | N/A |
| **wry** | No (Electron alternative) | Yes | N/A | Yes | N/A |
| **Remote browser streaming** | Yes (new block type) | Yes (multiple projects) | Medium (new block, no changes to existing) | Yes (engine-agnostic) | Local mode: yes, Remote: no |

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

### Remote browser streaming
- [Neko](https://github.com/m1k1o/neko) — Self-hosted virtual browser in Docker via WebRTC
- [vbrowser](https://github.com/zulfikawr/vbrowser) — Single-binary Go WebRTC browser streamer
- [Selkies](https://github.com/selkies-project/selkies) — WebSocket/WebRTC remote desktop streaming
- [Selkies docs](https://selkies-project.github.io/selkies/) — Documentation and quick start
- [Selkies web client](https://deepwiki.com/selkies-project/selkies/3.4-web-client) — Web client architecture
- [noVNC](https://github.com/novnc/noVNC) — HTML5 VNC client library
- [noVNC embedding docs](https://novnc.com/noVNC/docs/EMBEDDING.html) — How to embed noVNC
- [websockify](https://github.com/novnc/websockify) — WebSocket to TCP proxy for VNC
- [Kasm Workspaces](https://kasm.com/) — Container streaming platform
- [Kasm Developer API](https://kasm.com/developer-api) — Programmatic session creation
- [Kasm docs](https://docs.kasm.com/) — Documentation
- [Kasm Helm chart](https://github.com/kasmtech/kasm-helm) — Kubernetes deployment
- [Hyperbeam](https://www.hyperbeam.com/) — Cloud-hosted virtual browser API
- [Hyperbeam SDK docs](https://docs.hyperbeam.com/) — JavaScript SDK documentation
- [Hyperbeam getting started](https://docs.hyperbeam.com/home/getting-started) — Quick start guide
- [@hyperbeam/web npm](https://www.npmjs.com/package/@hyperbeam/web) — NPM package
- [vscreen](https://github.com/jameswebb68/vscreen) — Headless Chromium streaming with MCP tools
- [phantom-browse](https://github.com/Presidentsu/phantom-browse) — Sandboxed browser for security analysis

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
