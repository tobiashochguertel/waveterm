# Neko API Surface

**Branch:** `feature/browser-widget`
**Date:** 2026-08-24
**Status:** Researched (from Neko source code) — needs validation during prototype

---

## Overview

Neko uses WebSocket for signaling and WebRTC for media transport. Input
events are sent over a WebRTC DataChannel. The client connects, negotiates
WebRTC, receives video/audio streams, and sends mouse/keyboard events back.

**Important limitation:** Neko has **no programmatic URL navigation API**.
Neko is a remote desktop gateway, not a browser controller. URLs must be
typed in the remote browser's URL bar by the user (or via keyboard event
forwarding).

---

## 1. WebSocket Signaling

### Connection

```
ws://<host>:<port>/ws?password=<password>
```

Password is sent as a query parameter. Two password levels:
- `NEKO_PASSWORD` — regular user
- `NEKO_PASSWORD_ADMIN` — admin (can change resolution, control locks)

### Message format

Messages are JSON with an `event` field and payload fields.

### Client → Server messages

| Event | Payload | Description |
|-------|---------|-------------|
| `signal/provide` | `{id, sdp, lite, ice}` | SDP offer from client |
| `signal/candidate` | `{data}` | ICE candidate from client (JSON string) |
| `control/keyboard` | `{layout, variant}` | Keyboard layout info |
| `client/heartbeat` | — | Keep-alive (interval from `system/init`) |

### Server → Client messages

| Event | Payload | Description |
|-------|---------|-------------|
| `identity/provide` | `{id}` | Session ID assignment |
| `signal/answer` | `{sdp}` | SDP answer from server |
| `signal/candidate` | `{data}` | ICE candidate from server (JSON string) |
| `screen/resolution` | `{width, height, rate}` | Screen configuration |
| `member/list` | `{members: []}` | Connected members list |
| `system/init` | `{locks, implicit_hosting, file_transfer, heartbeat_interval}` | System settings |
| `broadcast/status` | `{url, isActive}` | Broadcast streaming status |
| `system/disconnect` | — | Session termination |

### Connection flow

```
Client                          Server
  │                               │
  ├── WebSocket connect ─────────►│
  │   ws://host:port/ws?pw=...    │
  │                               │
  │◄── identity/provide ─────────┤  (session ID)
  │◄── screen/resolution ────────┤  (width, height, rate)
  │◄── system/init ──────────────┤  (settings, heartbeat interval)
  │◄── member/list ──────────────┤  (current members)
  │                               │
  ├── signal/provide ────────────►│  (SDP offer)
  │                               │
  │◄── signal/answer ────────────┤  (SDP answer)
  │                               │
  ├── signal/candidate ──────────►│  (ICE candidates)
  │◄── signal/candidate ──────────┤  (ICE candidates)
  │                               │
  │   WebRTC connection established│
  │   Video/audio streams flowing  │
  │   DataChannel open              │
  │                               │
  ├── client/heartbeat ──────────►│  (periodic)
  │                               │
```

---

## 2. WebRTC Connection

### Peer connection setup

```typescript
const pc = new RTCPeerConnection(iceConfig);

// Receive audio and video from server
pc.addTransceiver('audio', { direction: 'recvonly' });
pc.addTransceiver('video', { direction: 'recvonly' });

// Data channel is created by server, received by client
pc.ondatachannel = (event) => {
    const dc = event.channel;  // channel name: "data"
    dc.onmessage = onDataMessage;
    dc.onclose = onDisconnected;
};

// Receive media tracks
pc.ontrack = (event) => {
    if (event.track.kind === 'video') {
        videoTrack = event.track;
    } else if (event.track.kind === 'audio') {
        audioTrack = event.track;
    }
    // Attach to <video> element
    const stream = new MediaStream([videoTrack, audioTrack]);
    videoElement.srcObject = stream;
};
```

### SDP offer/answer

```typescript
// Client creates offer
const offer = await pc.createOffer();
await pc.setLocalDescription(offer);

// Send to server via WebSocket
ws.send(JSON.stringify({
    event: 'signal/provide',
    id: sessionId,
    sdp: offer.sdp,
    lite: false,
    ice: []
}));

// Receive answer from server
// (on WebSocket message 'signal/answer')
await pc.setRemoteDescription({ type: 'answer', sdp: answerSdp });
```

### ICE candidate exchange

```typescript
// Client sends ICE candidates
pc.onicecandidate = (event) => {
    if (event.candidate) {
        ws.send(JSON.stringify({
            event: 'signal/candidate',
            data: JSON.stringify(event.candidate)
        }));
    }
};

// Server sends ICE candidates
// (on WebSocket message 'signal/candidate')
const candidate = JSON.parse(data);
await pc.addIceCandidate(candidate);
```

### Media constraints

- **Audio:** `recvonly` (receive only — server sends audio)
- **Video:** `recvonly` (receive only — server sends video)
- **DataChannel:** Named `"data"`, created by server, received via `ondatachannel`

---

## 3. Input Event Format (DataChannel)

Input events are sent over the WebRTC DataChannel as JSON text messages.

### Mouse events

```javascript
// Mouse move — coordinates scaled to remote screen resolution
dc.send(JSON.stringify({
    event: 'mousemove',
    x: Math.round((remoteWidth / videoRect.width) * (clientX - videoRect.left)),
    y: Math.round((remoteHeight / videoRect.height) * (clientY - videoRect.top))
}));

// Mouse down/up — button is 1-based (1=left, 2=middle, 3=right)
dc.send(JSON.stringify({ event: 'mousedown', key: button + 1 }));
dc.send(JSON.stringify({ event: 'mouseup', key: button + 1 }));

// Wheel scroll
dc.send(JSON.stringify({ event: 'wheel', x: deltaX, y: deltaY }));
```

### Coordinate mapping

```
remoteX = (remoteWidth / videoElement.clientWidth) * (mouseX - videoElement.offsetLeft)
remoteY = (remoteHeight / videoElement.clientHeight) * (mouseY - videoElement.offsetTop)
```

The video element may be scaled (CSS) or letterboxed. Need to account for
`object-fit` and actual rendered video dimensions.

### Keyboard events

Keyboard events use **X11 key codes** (XK_* constants), not JavaScript key
codes. A key mapping table is required.

```javascript
// Key down/up — key is an X11 keycode
dc.send(JSON.stringify({ event: 'keydown', key: x11KeyCode }));
dc.send(JSON.stringify({ event: 'keyup', key: x11KeyCode }));
```

### X11 key code mapping (subset)

| Key | X11 Code | JavaScript `e.code` |
|-----|----------|---------------------|
| Control_L | 0xffe3 | ControlLeft |
| Control_R | 0xffe4 | ControlRight |
| Alt_L | 0xffe9 | AltLeft |
| Alt_R | 0xffea | AltRight |
| Meta_L | 0xffe7 | MetaLeft |
| Meta_R | 0xffe8 | MetaRight |
| Super_L | 0xffeb | OSLeft |
| Super_R | 0xffec | OSRight |
| Shift_L | 0xffe1 | ShiftLeft |
| Shift_R | 0xffe2 | ShiftRight |

**Open:** Full key mapping table needs to be built. Neko's client uses a
`KeyTable` object with X11 constants. We need a JS `KeyboardEvent.code` →
X11 keycode mapping. Reference: [noVNC's keysym.js](https://github.com/novnc/noVNC/blob/master/core/input/keysym.js)

### macOS key remapping

On macOS, Alt and Super (Meta) keys are swapped for server compatibility
(same behavior as noVNC, RealVNC, TigerVNC):

```javascript
if (platform === 'darwin') {
    // Alt → Meta, Meta → Alt
    if (key === 'AltLeft') key = 'MetaLeft';
    else if (key === 'AltRight') key = 'MetaRight';
    else if (key === 'MetaLeft') key = 'AltLeft';
    else if (key === 'MetaRight') key = 'AltRight';
}
```

---

## 4. URL Navigation

**There is no programmatic URL navigation API in Neko.**

Neko is a remote desktop gateway — it sends screen frames and input events.
It does not communicate with the browser inside the container.

### Workarounds

1. **Keyboard event forwarding** — focus the remote browser's URL bar
   (Ctrl+L or Cmd+L in Chromium), type the URL via keyboard events, press
   Enter. This is the most practical approach for WaveTerm.

2. **Browser startup page** — configure the browser to start with a
   specific URL via Neko environment variables or browser config.

3. **Custom Neko fork** — add a WebSocket event that uses `xdotool` or
   `chromium --remote-debugging-port` + CDP to load URLs. More complex,
   but provides true programmatic navigation.

4. **CDP bridge** — run Chromium with `--remote-debugging-port=9222` in
   the container, expose the port, and use CDP from WaveTerm to navigate.
   This bypasses Neko for URL control but uses Neko for display.

**Recommendation for WaveTerm:** Use approach 1 (keyboard forwarding) for
v1. The URL bar in WaveTerm sends Ctrl+L to the remote browser, types the
URL character by character, and presses Enter. This is hacky but works
without modifying Neko.

**Future:** Approach 4 (CDP bridge) for proper URL navigation, back/forward,
and loading state tracking.

---

## 5. Session Management

### Authentication

Password-based, sent as WebSocket query parameter:
```
ws://host:port/ws?password=<password>
```

### Session lifecycle

1. **Connect** — WebSocket connection with password
2. **Identity** — server assigns session ID (`identity/provide`)
3. **Screen config** — server sends resolution (`screen/resolution`)
4. **System init** — server sends settings (`system/init`)
5. **WebRTC negotiation** — SDP offer/answer + ICE exchange
6. **Connected** — video/audio flowing, DataChannel open
7. **Heartbeat** — client sends periodic `client/heartbeat`
8. **Disconnect** — WebSocket close or `system/disconnect` from server

### Control modes

- **Implicit control** — user gets control on mouse move/click (default)
- **Explicit control** — user must request control via UI button
- **Hosting** — admin is always host, can lock controls

### v3 features (not in legacy client)

- Session tokens as cookies for persistent login
- Session serialization to survive restarts
- Dynamic permissions with granular access control

**Open:** Which Neko version should we target? v3 server with legacy client,
or v3 client? Need to check Docker image versions.

---

## 6. Clipboard Sync

### Client → Remote

```javascript
async function syncClipboardToRemote() {
    if (document.hasFocus()) {
        const text = await navigator.clipboard.readText();
        if (lastClipboard !== text) {
            dc.send(JSON.stringify({ event: 'clipboard', text }));
            lastClipboard = text;
        }
    }
}
```

### Remote → Client

```javascript
// On DataChannel message with clipboard event
async function onClipboardFromRemote(text) {
    try {
        await navigator.clipboard.writeText(text);
    } catch (err) {
        console.error('Clipboard write failed', err);
    }
}
```

### Sync triggers

- On window focus (v3.1.5+)
- On mouse enter (legacy behavior)
- Manual sync via UI

### REST API (alternative)

```
POST /api/room/clipboard
{"text": "content", "html": "<b>content</b>"}
```

### Browser compatibility

- Firefox has clipboard read limitations
- Requires `document.hasFocus()` for read
- Requires HTTPS or localhost for Clipboard API

---

## 7. Resolution / Resize

### Server-side configuration

Environment variables:
```bash
NEKO_SCREEN=1920x1080@30    # width x height @ framerate
```

### Client-side change (admin only)

Admins can change resolution on-the-fly. Server sends `screen/resolution`
event with new dimensions.

v3.0.0+ supports `xrandr` for arbitrary resolutions (not just predefined).

### WebSocket event

```json
{
    "event": "screen/resolution",
    "width": 1920,
    "height": 1080,
    "rate": 30
}
```

**Open:** How does the client request a resolution change? Is it a
WebSocket message or a REST API call? Need to check Neko v3 source.

---

## 8. REST API (v3)

Neko v3 exposes a REST API alongside WebSocket:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/room/clipboard` | POST | Set clipboard content |
| `/api/health` | GET | Health check |
| `/api/members` | GET | List connected members |
| `/api/screen` | GET | Get current screen configuration |

**Open:** Full REST API documentation needed. Check Neko v3 server source
for available endpoints.

---

## Key source files in Neko

| File | Purpose |
|------|---------|
| `client/src/neko/base.ts` | WebSocket + WebRTC setup |
| `client/src/neko/index.ts` | Client entry point |
| `client/src/components/video.vue` | Input event handling (mouse/keyboard) |
| `client/src/plugins/neko.ts` | Vue plugin for Neko client |
| `server/internal/webrtc/webrtc.go` | Server WebRTC implementation |
| `server/internal/websocket/manager.go` | WebSocket message handling |
| `server/internal/http/legacy/handler.go` | Legacy HTTP handler |

---

## Implications for WaveTerm integration

1. **URL navigation is the biggest gap.** Neko doesn't control the browser.
   We need either keyboard event forwarding (hacky) or a CDP bridge (proper
   but more work). This is a key item for the prototype phase.

2. **X11 key code mapping** is required. We need a complete
   `KeyboardEvent.code → X11 keycode` table. noVNC's `keysym.js` is the
   best reference.

3. **Coordinate mapping** must account for video element scaling and
   letterboxing. The `<video>` element's `object-fit` and actual rendered
   size determine the mapping.

4. **Clipboard sync** works but has browser quirks (Firefox, focus
   requirements). WaveTerm runs in Electron (Chromium), so most quirks
   don't apply.

5. **No loading state or URL change events.** Neko doesn't report what
   the browser is doing. We won't know if a page is loading, what URL
   was navigated to, or if navigation failed. This means:
   - No loading spinner in WaveTerm's UI
   - No URL bar sync (URL bar shows what the user typed, not the actual
     current URL)
   - No error handling for failed navigation
   - **Mitigation:** CDP bridge would solve all of these

6. **Session management is simple.** Password auth, heartbeat, done.
   No complex token management needed for v1.

---

## Sources

- [Neko GitHub](https://github.com/m1k1o/neko) — source code
- [Neko issue #289](https://github.com/m1k1o/neko/issues/289) — URL
  navigation API request (not implemented)
- [noVNC keysym.js](https://github.com/novnc/noVNC/blob/master/core/input/keysym.js) —
  X11 key code reference table
