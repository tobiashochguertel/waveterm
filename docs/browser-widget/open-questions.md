# Open Questions — Browser Widget

**Branch:** `feature/browser-widget`
**Date:** 2026-08-24

Tracked open questions for the remote browser widget. Questions are resolved
before implementation begins. Each has a status lifecycle:
`open` → `investigating` → `answered` → `implemented`.

---

## Q1: Container reuse vs separate per block

**Status:** open
**Recommendation:** Start with separate containers (simpler, safer), add
shared mode later

**Question:** Should multiple `"remotebrowser"` blocks share one container
(multiple tabs in one browser) or spawn separate containers?

**Options:**
- **Shared container** — lower resource use (~500MB shared vs ~500MB × N),
  but blocks are coupled (one crash affects all, one URL bar shared)
- **Separate containers** — higher resource use, but full isolation per block,
  independent lifecycle
- **Hybrid** — default separate, optional shared mode via config

**Context:** Neko supports multiple "members" in one session, but each member
sees the same browser. True tab isolation would need either multiple Neko
sessions in one container (not standard) or multiple containers.

**Decision needed by:** Phase 1 implementation

---

## Q2: Image pre-pull timing

**Status:** open
**Recommendation:** Pull on first use with a progress indicator

**Question:** When should the Neko container image (~1.2 GB) be pulled?

**Options:**
- **On WaveTerm install** — instant first use, but adds ~1.2 GB to install
  size (unacceptable for users who never use the block)
- **On first use** — smaller install, but first browser block is slow
  (~1-3 min download depending on connection)
- **Manual** — user runs `docker pull m1k1o/neko:chromium` themselves
  (poor UX, but no surprise download)
- **On first use + background pre-fetch** — start pull in background after
  WaveTerm starts (if container runtime detected), so it's likely ready
  by the time the user creates a browser block

**Decision needed by:** Phase 1 implementation

---

## Q3: GPU acceleration

**Status:** open
**Recommendation:** Document as optional, not required for v1

**Question:** Should we support GPU passthrough for hardware video encoding
(NVENC/VA-API) in the container?

**Context:**
- Improves encoding performance and reduces CPU usage
- Complex to configure (varies by GPU vendor, OS, and container runtime)
- Docker: `--gpus all` or `--device /dev/dri`
- Podman: `--device /dev/dri`
- macOS: no GPU passthrough to Linux containers (Docker Desktop limitation)
- Neko supports hardware encoding via GStreamer when GPU is available

**Decision needed by:** Phase 4 (polish) — not blocking v1

---

## Q4: Audio support

**Status:** open
**Recommendation:** Yes, include in v1 (Neko supports it natively)

**Question:** Should audio from the remote browser be played in WaveTerm?

**Context:**
- Neko supports audio via Opus codec over WebRTC
- Adds complexity: `<audio>` or WebAudio API, volume control, mute toggle
- Some users may not want audio (e.g. browsing in a quiet environment)
- Should be toggleable per block

**Decision needed by:** Phase 2 implementation

---

## Q5: Search (find in page)

**Status:** open
**Recommendation:** Use browser-side Ctrl+F, implement custom search later

**Question:** How to implement "find in page" search in the remote browser?

**Context:**
- The existing `"web"` block uses Electron's `findInPage()` API, which
  requires direct WebContents access — not available with remote streaming
- Options:
  - **Browser-side Ctrl+F** — forward Ctrl+F to the remote browser, let
    Chromium's native find bar handle it (simplest, but UI is inside the
    video stream, not WaveTerm's UI)
  - **CDP via Neko** — if Neko exposes CDP (Chrome DevTools Protocol),
    use `Page.searchInPage` or similar (need to verify Neko's CDP access)
  - **Custom overlay** — implement search in WaveTerm UI, send search
    queries to the remote browser via Neko's API, highlight results in
    the video stream (complex, results may not align with video frames)

**Decision needed by:** Phase 4 (polish) — can ship without custom search

---

## Q6: DevTools access

**Status:** open
**Recommendation:** Forward F12 to remote browser for v1

**Question:** How to access DevTools for the remote browser?

**Context:**
- The existing `"web"` block opens DevTools via `webview.openDevTools()`
- With remote streaming, DevTools would open inside the container's browser
- Options:
  - **Forward F12** — send F12 key to remote browser, DevTools opens inside
    the video stream (works but cramped in a streamed view)
  - **Remote DevTools** — expose container's CDP port, connect from
    WaveTerm's renderer or a separate DevTools window
  - **Neko's built-in DevTools** — check if Neko has a DevTools toggle

**Decision needed by:** Phase 3

---

## Q7: Bookmark integration

**Status:** open
**Recommendation:** Reuse existing bookmark system

**Question:** Should the `"remotebrowser"` block reuse WaveTerm's existing
bookmark system (from the `"web"` block)?

**Context:**
- The existing bookmark system stores bookmarks in `~/.config/waveterm/bookmarks.json`
- Patch `002-bookmark-typeahead-fix.patch` fixed the bookmark typeahead in `webview.tsx`
- The bookmark typeahead component (`BookmarkTypeahead`) is currently inside
  `webview.tsx` — may need extraction to a shared component
- Alternatively, duplicate the bookmark logic in the new block (simpler but
  divergent)

**Decision needed by:** Phase 3

---

## Q8: Container image selection UI

**Status:** open
**Recommendation:** Default to Chromium, allow selection in settings

**Question:** How should users select which browser engine to use in the
container?

**Context:**
- Neko provides multiple images: Chromium, Firefox, Google Chrome, Vivaldi,
  Tor Browser
- Default: `m1k1o/neko:chromium` (best compatibility, open source)
- Options:
  - **Per-block config** — each block specifies its engine
  - **Global setting** — one engine for all `"remotebrowser"` blocks
  - **Both** — global default, per-block override

**Decision needed by:** Phase 3

---

## Q9: Network configuration

**Status:** open
**Recommendation:** Default to bridge networking, document custom options

**Question:** Should the container support custom network configuration
(VPN, DNS, proxy)?

**Context:**
- Use cases:
  - Browse via VPN (mount VPN config into container)
  - Custom DNS (e.g. Pi-hole, internal DNS)
  - HTTP proxy (corporate proxy)
  - Network isolation (no internet access, only specific hosts)
- Docker/Podman support `--network`, `--dns`, `--add-host`, volume mounts
- Could expose these as block metadata options

**Decision needed by:** Phase 4 (polish) — not blocking v1

---

## Q10: Session persistence

**Status:** open
**Recommendation:** Not in v1, document as future feature

**Question:** Should the browser session persist across WaveTerm restarts?

**Context:**
- If WaveTerm crashes or restarts, the container could keep running and
  the user reconnects to the same browser session
- Requires: container survives WaveTerm exit, reconnection logic, session
  state tracking
- Neko sessions persist as long as the container runs
- Tradeoff: containers left running consume resources

**Decision needed by:** Post-v1
