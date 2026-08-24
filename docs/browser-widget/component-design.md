# Component Design — RemoteBrowser Block

**Branch:** `feature/browser-widget`
**Date:** 2026-08-24
**Status:** Open (preliminary structure, needs validation during implementation)

---

## Overview

The `"remotebrowser"` block consists of three layers:

1. **Renderer** — React component + ViewModel (user-facing UI)
2. **Main process** — Container Manager (Docker/Podman lifecycle)
3. **Container** — Neko server (browser + WebRTC streaming)

This document covers the renderer and main process component design.
The container side is documented in the
[ADR](./adr-local-containerized-browser.md).

---

## File structure

```
frontend/app/view/remotebrowser/
├── remotebrowser.tsx          # RemoteBrowserViewModel + WebView component
├── remotebrowser.scss         # Styles
├── webrtc-client.ts           # WebRTC connection + Neko signaling
├── input-forwarder.ts         # Mouse/keyboard/scroll → DataChannel events
└── remotebrowser.test.tsx     # Tests

emain/
├── emain-container.ts         # Container Manager (Docker/Podman lifecycle)
└── emain-container-ipc.ts     # IPC handlers for container operations
```

**Status:** Open — exact file structure may change during implementation.

---

## RemoteBrowserViewModel

**Status:** Open — preliminary design based on existing `WebViewModel` pattern

```typescript
export class RemoteBrowserViewModel implements ViewModel {
    viewType: string;                    // "remotebrowser"
    blockId: string;
    tabModel: TabModel;
    blockAtom: Atom<Block>;

    // URL state
    url: PrimitiveAtom<string>;          // Current URL in remote browser
    homepageUrl: Atom<string>;           // Default URL
    urlInputFocused: PrimitiveAtom<boolean>;

    // Connection state
    connectionState: PrimitiveAtom<"disconnected" | "connecting" | "connected" | "error">;
    containerId: PrimitiveAtom<string | null>;   // Docker container ID
    nekoUrl: PrimitiveAtom<string | null>;       // Neko WebSocket URL

    // Browser state
    isLoading: PrimitiveAtom<boolean>;
    canGoBack: PrimitiveAtom<boolean>;
    canGoForward: PrimitiveAtom<boolean>;
    mediaPlaying: PrimitiveAtom<boolean>;
    mediaMuted: PrimitiveAtom<boolean>;
    zoomFactor: PrimitiveAtom<number>;

    // Settings
    engine: Atom<"chromium" | "firefox" | "google-chrome" | "vivaldi" | "tor-browser">;
    resolution: Atom<string>;            // "1920x1080"
    framerate: Atom<number>;             // 30
    encoder: Atom<"vp8" | "h264">;
    audioEnabled: PrimitiveAtom<boolean>;

    // Refs
    videoRef: React.RefObject<HTMLVideoElement>;
    webrtcClient: WebRTCClient | null;

    // View metadata
    viewIcon: Atom<string | IconButtonDecl>;
    viewName: Atom<string>;
    viewText: Atom<HeaderElem[]>;
    endIconButtons?: Atom<IconButtonDecl[]>;
}
```

**Open questions:**
- How much of the `WebViewModel` interface can be reused vs. reimplemented?
- Should `RemoteBrowserViewModel` extend `WebViewModel` or implement
  `ViewModel` directly? (Direct implementation is cleaner — the internals
  are completely different)
- How to handle `canGoBack`/`canGoForward` — Neko may not expose browser
  navigation state. May need to track via URL change events.

---

## Component tree

**Status:** Open — preliminary structure

```
<RemoteBrowserBlock>                    # Block wrapper (from block system)
  └── <RemoteBrowserView>               # Main view component
      ├── <RemoteBrowserToolbar>        # URL bar + nav buttons
      │   ├── <BackButton>
      │   ├── <ForwardButton>
      │   ├── <ReloadButton>
      │   ├── <UrlInput>                # URL input field
      │   ├── <HomeButton>
      │   └── <SettingsMenu>            # Engine, resolution, encoder, etc.
      ├── <RemoteBrowserCanvas>         # Video stream container
      │   └── <video>                   # WebRTC MediaStream rendered here
      ├── <ConnectionOverlay>           # Loading/error states
      │   ├── <ConnectingSpinner>       # Shown while container starts
      │   └── <ErrorDisplay>            # Shown on connection failure
      ├── <RemoteBrowserSearch>         # Find-in-page (if implemented)
      └── <BookmarkTypeahead>           # Bookmark suggestions (reused from web block?)
```

**Open questions:**
- Should `<BookmarkTypeahead>` be extracted from `webview.tsx` into a shared
  component, or duplicated? (See [open-questions.md](./open-questions.md) Q7)
- Should the toolbar match the `"web"` block's toolbar exactly, or have a
  different style to distinguish the block type?

---

## WebRTC client

**Status:** Open — depends on Neko API surface research

```typescript
// webrtc-client.ts (preliminary)

export class WebRTCClient {
    private pc: RTCPeerConnection;
    private ws: WebSocket;              // Neko signaling WebSocket
    private dc: RTCDataChannel;         // Input events (mouse/keyboard)
    private videoTrack: MediaStreamTrack;
    private audioTrack: MediaStreamTrack;

    constructor(nekoUrl: string, password: string);

    // Connection lifecycle
    connect(): Promise<void>;           // WebSocket + WebRTC negotiation
    disconnect(): void;

    // Video/audio
    getMediaStream(): MediaStream;      // For <video> element
    setVolume(volume: number): void;
    toggleMute(): void;

    // Input (forwarded to remote browser via DataChannel)
    sendMouseEvent(event: MouseEvent): void;
    sendKeyboardEvent(event: KeyboardEvent): void;
    sendScrollEvent(event: WheelEvent): void;
    sendClipboard(text: string): void;

    // Navigation
    loadUrl(url: string): void;         // If Neko supports programmatic nav
    goBack(): void;
    goForward(): void;
    reload(): void;

    // Resolution
    setResolution(width: number, height: number): void;

    // Events
    onConnectionStateChange(cb: (state: string) => void): void;
    onUrlChange(cb: (url: string) => void): void;
    onLoadingStateChange(cb: (loading: boolean) => void): void;
}
```

**Open:** The exact Neko WebSocket protocol and DataChannel message format
need to be documented in [neko-api-surface.md](./neko-api-surface.md).

---

## Input forwarding

**Status:** Open — needs Neko DataChannel format

The input forwarder translates WaveTerm DOM events into Neko's DataChannel
messages:

```
WaveTerm DOM event          →  Neko DataChannel message
─────────────────────────────────────────────────────────
mousedown + coordinates     →  { type: "mouse_down", x, y, button }
mousemove + coordinates     →  { type: "mouse_move", x, y }
mouseup + coordinates       →  { type: "mouse_up", x, y, button }
wheel + deltaX/deltaY       →  { type: "wheel", x, y, deltaX, deltaY }
keydown + key code          →  { type: "key_down", key, code, modifiers }
keyup + key code            →  { type: "key_up", key, code, modifiers }
clipboard copy              →  { type: "clipboard", text }
```

**Open:** The exact message format (JSON, protobuf, binary) needs to be
verified from Neko's source code. Coordinate mapping (DOM pixels → remote
screen pixels) needs to account for video element scaling.

**Open:** How to handle focus? When the `<video>` element is focused,
keyboard events go to it. Need to capture and forward them. When focus
leaves, should the remote browser lose focus too?

---

## Atoms (state management)

**Status:** Open — follows existing Jotai patterns in WaveTerm

Key atoms the ViewModel exposes:

| Atom | Type | Description |
|------|------|-------------|
| `url` | `PrimitiveAtom<string>` | Current URL |
| `connectionState` | `PrimitiveAtom<ConnectionState>` | WebRTC connection status |
| `isLoading` | `PrimitiveAtom<boolean>` | Page loading state |
| `canGoBack` | `PrimitiveAtom<boolean>` | Browser can go back |
| `canGoForward` | `PrimitiveAtom<boolean>` | Browser can go forward |
| `containerId` | `PrimitiveAtom<string \| null>` | Docker container ID |
| `mediaMuted` | `PrimitiveAtom<boolean>` | Audio muted state |
| `zoomFactor` | `PrimitiveAtom<number>` | Video zoom level |

---

## Open items

The following need to be filled in during implementation:

- [ ] Exact Neko WebSocket message types and protocol
- [ ] DataChannel input event format (JSON vs binary)
- [ ] Coordinate mapping algorithm (DOM → remote screen)
- [ ] Keyboard event mapping (Electron key codes → browser key codes)
- [ ] Clipboard sync implementation details
- [ ] How Neko reports URL changes and loading state
- [ ] Whether Neko supports programmatic URL navigation or only user-driven
- [ ] Error handling for WebRTC negotiation failures
- [ ] Reconnection logic on temporary network issues
- [ ] Video element sizing and aspect ratio handling
- [ ] Fullscreen support for the remote browser
