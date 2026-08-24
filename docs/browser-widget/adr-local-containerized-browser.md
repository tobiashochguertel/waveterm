# ADR: Local Containerized Browser Streaming with Neko

**Branch:** `feature/browser-widget`
**Date:** 2026-08-24
**Status:** Accepted
**Supersedes:** None (new feature, does not replace existing `"web"` block)

---

## Context

WaveTerm's current browser widget uses Electron's `<webview>` tag, which
Electron officially recommends against due to ongoing Chromium architectural
instability. See
[research-current-state.md](./research-current-state.md) for the full analysis.

After evaluating 7 alternative approaches (WebContentsView, CEF, Playwright
streaming, Servo, wry, no practical in-process embedding, and remote browser
streaming), we selected **local containerized browser streaming** as the
architecture for a new browser widget block.

## Decision

Create a new WaveTerm block type (`"remotebrowser"`) that streams a browser
running inside a local Docker/Podman container via Neko's WebRTC stack.

### Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  WaveTerm (Electron)                                         │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  React Renderer                                        │  │
│  │  RemoteBrowserViewModel (new block type)               │  │
│  │  ├── URL bar, nav, bookmarks, search                   │  │
│  │  ├── Connection manager (WebSocket → Neko signaling)   │  │
│  │  ├── <video> — renders WebRTC stream                   │  │
│  │  └── Input forwarder — mouse/keyboard → DataChannel    │  │
│  └─────────────────┬──────────────────────────────────────┘  │
│                    │ WebRTC (localhost)                       │
│  ┌─────────────────▼──────────────────────────────────────┐  │
│  │  Container Manager (main process)                      │  │
│  │  ├── Detect runtime: `docker` or `podman`              │  │
│  │  ├── Lifecycle: start / stop / restart container       │  │
│  │  ├── Port allocation (find free port for Neko)         │  │
│  │  ├── Health check (wait for Neko to be ready)          │  │
│  │  └── Cleanup on block close / app exit                 │  │
│  └─────────────────┬──────────────────────────────────────┘  │
│                    │ docker run / podman run                  │
└────────────────────┼─────────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────────┐
│  Container (m1k1o/neko:chromium or m1k1o/neko:firefox)       │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Xvfb (virtual framebuffer, 1920×1080)                 │  │
│  │  Chromium or Firefox                                    │  │
│  │  GStreamer (frame capture → VP8/H.264 encode)          │  │
│  │  Neko server (Go + pion/webrtc)                        │  │
│  │  ├── WebRTC signaling over HTTP                        │  │
│  │  ├── Video stream via SRTP                             │  │
│  │  ├── Input via DataChannel                             │  │
│  │  └── Clipboard sync                                    │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
│  Port mapping: container:8080 → host:<dynamic port>          │
│  Optional: GPU passthrough for hardware encoding             │
└──────────────────────────────────────────────────────────────┘
```

### Key decisions

#### 1. Container runtime: support both Docker and Podman

**Decision:** Auto-detect at runtime which container runtime is available.

**Rationale:**
- **Docker** — most widely used, best tooling, requires Docker Desktop on macOS
- **Podman** — rootless by default, daemonless, more secure, Docker-compatible CLI
- Users may have either or both installed
- Detection: check `which podman` first (preferred for rootless), then `which docker`
- CLI commands are compatible (`docker run` ↔ `podman run`)

**Implementation:**
```typescript
async function detectContainerRuntime(): Promise<"docker" | "podman" | null> {
    // Prefer podman (rootless, more secure)
    if (await commandExists("podman")) return "podman";
    if (await commandExists("docker")) return "docker";
    return null;
}
```

#### 2. Streaming server: Neko

**Decision:** Use [Neko](https://github.com/m1k1o/neko) as the streaming server
inside the container.

**Rationale:**
- **Docker-native** — designed to run in Docker, pre-built images available
  (`m1k1o/neko:chromium`, `m1k1o/neko:firefox`)
- **WebRTC** — low latency, adaptive bitrate, built-in congestion control
- **Battle-tested** — most popular open-source remote browser project,
  active community, MIT licensed
- **Multi-browser support** — both Chromium and Firefox images available
- **Multi-user** — supports co-browsing (multiple clients on same session)
- **Clipboard sync** — built-in clipboard sharing between client and remote browser
- **Audio** — PulseAudio + Opus codec for full audio support
- **Configurable** — resolution, framerate, encoder, password protection

**Neko configuration (environment variables):**
```bash
NEKO_SCREEN=1920x1080@30      # Virtual screen resolution + framerate
NEKO_ENCODER=vp8              # Video encoder (vp8, h264)
NEKO_VIDEO_BITRATE=2000       # Video bitrate (kbps)
NEKO_AUDIO_BITRATE=128        # Audio bitrate (kbps
NEKO_PASSWORD=...             # User password
NEKO_PASSWORD_ADMIN=...       # Admin password
NEKO_BIND=:8080               # Listen address
NEKO_EPR=52000-52100          # WebRTC UDP port range
```

#### 3. Lifecycle: auto-manage by default, external connection supported

**Decision:** WaveTerm manages the container lifecycle by default, but allows
connecting to an externally-managed container via configuration.

**Rationale:**
- **Auto-manage (default):** User creates a browser block, WaveTerm starts the
  container, connects, and stops the container when the block is closed.
  Zero manual setup — the user doesn't need to know about containers.
- **External (opt-in):** Power users or remote setups can run the container
  themselves (e.g. on a remote server, or with custom configuration) and point
  WaveTerm at it via a WebSocket URL.

**Auto-manage flow:**
```
1. User creates "remotebrowser" block
2. Container Manager detects runtime (docker/podman)
3. Find free port on host
4. Start container: `docker run -d -p <port>:8080 -e NEKO_... m1k1o/neko:chromium`
5. Wait for Neko health check (GET http://localhost:<port>/health)
6. Pass Neko URL to RemoteBrowserViewModel
7. ViewModel connects via WebRTC
8. ... user browses ...
9. User closes block → Container Manager stops container
```

**External connection flow:**
```
1. User configures block: { "mode": "external", "url": "ws://..." }
2. RemoteBrowserViewModel connects directly to the URL
3. Container Manager is not involved
```

**Configuration schema (block metadata):**
```json
{
    "view": "remotebrowser",
    "browser:mode": "auto",
    "browser:engine": "chromium",
    "browser:resolution": "1920x1080",
    "browser:framerate": 30,
    "browser:encoder": "vp8",
    "browser:external-url": null
}
```

When `browser:mode` is `"external"`, `browser:external-url` is used instead
of starting a container.

#### 4. New block type, not a modification of existing

**Decision:** Create a new `"remotebrowser"` block type rather than modifying
the existing `"web"` block.

**Rationale:**
- **No risk to existing functionality** — `"web"`, `"tsunami"`, and `"help"`
  blocks continue to work unchanged
- **Gradual migration** — users can try the new block without losing the old one
- **No patch conflicts** — doesn't touch `webview.tsx`, so no changes to
  `PATCHED_FILES` or the sync workflow
- **Clean separation** — different architecture, different code, different
  dependencies (WebRTC client vs. Electron webview API)

**Registration in `blockregistry.ts`:**
```typescript
import { RemoteBrowserViewModel } from "@/view/remotebrowser/remotebrowser";
BlockRegistry.set("remotebrowser", RemoteBrowserViewModel);
```

#### 5. WebRTC transport (not WebSocket)

**Decision:** Use WebRTC as the transport protocol.

**Rationale:**
- Neko is built on WebRTC (pion/webrtc in Go)
- Lower latency than WebSocket for video (UDP vs TCP)
- Adaptive bitrate — adjusts quality based on available bandwidth
- Built-in congestion control
- Even on localhost, WebRTC provides smooth 30-60 FPS streaming
- Audio support via Opus codec over WebRTC

**Tradeoff:** WebRTC requires UDP port range for the media stream. The
container manager must map both the TCP signaling port (8080) and a UDP port
range (e.g. 52000-52100) for the media stream.

**Port mapping:**
```bash
docker run -p <tcp_port>:8080 -p <udp_start>-<udp_end>:52000-52100/udp \
    -e NEKO_BIND=:8080 -e NEKO_EPR=52000-52100 \
    m1k1o/neko:chromium
```

### Implementation plan

#### Phase 1: Container Manager (Electron main process)

New file: `emain/emain-container.ts`

- `detectContainerRuntime()` — find docker or podman
- `startBrowserContainer(opts)` — pull image if needed, start container,
  return connection URL
- `stopBrowserContainer(containerId)` — stop and remove container
- `healthCheck(url)` — poll until Neko is ready
- `findFreePorts(count)` — allocate TCP + UDP port range
- Container tracking: map block ID → container ID for cleanup

#### Phase 2: RemoteBrowserViewModel (React renderer)

New files:
- `frontend/app/view/remotebrowser/remotebrowser.tsx` — ViewModel + component
- `frontend/app/view/remotebrowser/remotebrowser.scss` — styles
- `frontend/app/view/remotebrowser/webrtc-client.ts` — WebRTC connection logic

The ViewModel manages:
- URL state (what URL the remote browser should load)
- Connection state (connecting, connected, disconnected, error)
- Container lifecycle (request start/stop from main process via IPC)
- Input forwarding (mouse, keyboard, scroll, clipboard)
- Video rendering (`<video>` element with WebRTC MediaStream)
- Settings (engine, resolution, encoder, framerate)

#### Phase 3: Block registration + UI

- Register in `blockregistry.ts`
- Add block icon and name in `blockutil.ts`
- Add to block creation menu
- Add settings UI for container configuration

#### Phase 4: Polish

- Container image pre-pull on first use (with progress indicator)
- Container reuse — share one container across multiple browser blocks
- Clipboard sync between WaveTerm and remote browser
- Bookmark integration (reuse existing bookmark system)
- Keyboard shortcut handling (Ctrl+T for new tab in remote browser, etc.)
- Error handling (container failed to start, runtime not installed, etc.)
- Settings menu (zoom, reload, clear cookies, open DevTools in container)

### Container image

Use the official Neko images:

| Image | Browser | Size |
|-------|---------|------|
| `m1k1o/neko:chromium` | Chromium | ~1.2 GB |
| `m1k1o/neko:firefox` | Firefox | ~1.1 GB |
| `m1k1o/neko:google-chrome` | Google Chrome | ~1.3 GB |
| `m1k1o/neko:vivaldi` | Vivaldi | ~1.2 GB |
| `m1k1o/neko:tor-browser` | Tor Browser | ~1.2 GB |

Default: `m1k1o/neko:chromium` (best web compatibility, open source)

### Dependencies

**New npm dependencies:**
- WebRTC client — use native browser WebRTC API (no extra dependency needed)
  or [wrtc](https://www.npmjs.com/package/wrtc) if Node.js-side WebRTC is needed

**New system dependencies (user's machine):**
- Docker or Podman (auto-detected)
- ~1.2 GB disk space for container image (pulled on first use)

**No changes to existing dependencies.** The new block is self-contained.

### Security considerations

1. **Container isolation** — browser runs in a container, not in the Electron
   process. Malicious pages cannot access Electron's APIs or the host filesystem
   (unless volumes are explicitly mounted)
2. **No `webviewTag` needed** — the new block doesn't use Electron's `<webview>`
   tag at all, avoiding the security concerns documented in the research
3. **Network isolation** — container has its own network namespace by default.
   Can be configured with custom DNS, VPN, or network restrictions
4. **Password protection** — Neko supports password authentication for the
   WebRTC session (auto-generated per block by default)
5. **Port binding** — container ports are bound to localhost only by default,
   not exposed to the network
6. **Container cleanup** — containers are stopped and removed when blocks are
   closed, preventing resource leaks

### Limitations

1. **Requires Docker or Podman** — users without a container runtime cannot
   use this block (the existing `"web"` block remains available as fallback)
2. **~1.2 GB image download** — first use requires pulling the Neko image
   (subsequent uses use the cached image)
3. **Resource overhead** — running a container + Xvfb + browser + encoder
   uses more CPU/RAM than the in-process `<webview>` (estimated: ~500MB RAM,
   ~5-10% CPU for encoding)
4. **Text rendering** — video encoding may produce slightly softer text than
   native rendering (mitigated by using high bitrate and VP8 at 1080p)
5. **No direct DOM access** — unlike `<webview>`, the remote browser's DOM
   is not accessible from WaveTerm's renderer process (no `executeJavaScript`,
   no `findInPage`). Search would need to be implemented via Neko's API or
   browser-side keyboard shortcut (Ctrl+F)
6. **macOS Docker Desktop** — on macOS, Docker requires Docker Desktop
   (or colima/rancher as lightweight alternatives). Podman Desktop is also
   available

### Relationship to existing `"web"` block

| Aspect | `"web"` block (existing) | `"remotebrowser"` block (new) |
|--------|--------------------------|-------------------------------|
| Engine | Electron `<webview>` (Chromium) | Neko container (Chromium/Firefox) |
| Process | In-process (Electron renderer) | Separate container |
| Transport | Direct DOM rendering | WebRTC video stream |
| Isolation | Electron process | Container boundary |
| DOM access | Yes (`executeJavaScript`, `findInPage`) | No (remote) |
| Offline | Yes | Yes (local container) |
| Dependencies | Electron (already installed) | Docker/Podman + ~1.2 GB image |
| Latency | None (native) | ~10-20ms (localhost WebRTC) |
| Resource use | Low (~100MB per webview) | Higher (~500MB per container) |
| Security | Minimal (webview defaults) | Strong (container isolation) |
| Future | Uncertain (Electron may deprecate) | Stable (Neko is independent) |

The `"web"` block is **not removed**. Both blocks coexist. Users choose which
to use based on their needs:
- `"web"` — fast, lightweight, needs DOM access, accepts webview risks
- `"remotebrowser"` — secure, isolated, needs Docker/Podman, slightly higher latency

### Open questions

1. **Container reuse** — should multiple `"remotebrowser"` blocks share one
   container (multiple tabs in one browser) or spawn separate containers?
   - Shared: lower resource use, but blocks are coupled (one crash affects all)
   - Separate: higher resource use, but full isolation per block
   - **Recommendation:** Start with separate containers (simpler, safer),
     add shared mode later as an option

2. **Image pre-pull** — should WaveTerm pull the Neko image on install, on
   first use, or let the user pull it manually?
   - On install: adds ~1.2 GB to install size, but instant first use
   - On first use: smaller install, but first browser block is slow
   - Manual: user runs `docker pull m1k1o/neko:chromium` themselves
   - **Recommendation:** Pull on first use with a progress indicator

3. **GPU acceleration** — should we support GPU passthrough for hardware
   encoding (NVENC/VA-API)?
   - Improves performance and reduces CPU usage
   - Complex to configure (varies by GPU vendor and OS)
   - **Recommendation:** Document as optional, not required for v1

4. **Audio** — should audio from the remote browser be played in WaveTerm?
   - Neko supports audio via Opus over WebRTC
   - Adds complexity (audio element, volume control)
   - **Recommendation:** Yes, include in v1 (Neko supports it natively)

## Sources

- [Neko GitHub](https://github.com/m1k1o/neko) — Self-hosted virtual browser via WebRTC
- [Neko Docker images](https://hub.docker.com/u/m1k1o) — Pre-built container images
- [pion/webrtc](https://github.com/pion/webrtc) — Pure Go WebRTC implementation (Neko's transport)
- [Docker CLI reference](https://docs.docker.com/reference/cli/docker/) — Docker commands
- [Podman CLI](https://docs.podman.io/en/latest/Commands.html) — Podman commands (Docker-compatible)
- [Research document](./research-current-state.md) — Full analysis of current state and alternatives
