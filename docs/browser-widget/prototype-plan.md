# Prototype Plan — RemoteBrowser Block

**Branch:** `feature/browser-widget`
**Date:** 2026-08-24
**Status:** Open (not yet started)

---

## Goal

Validate that Neko + WebRTC streaming works inside WaveTerm before
committing to full implementation. Answer the key technical questions
that can only be resolved by building and testing.

---

## Scope

A minimal spike — not production code. The prototype proves the
architecture, the prototype implementation is throwaway.

---

## Prototype steps

### Step 1: Run Neko container manually

**Status:** Open

```bash
# Pull and run Neko container
docker run -d --name neko-test \
    -p 8080:8080 \
    -p 52000-52100:52000-52100/udp \
    -e NEKO_SCREEN=1920x1080@30 \
    -e NEKO_ENCODER=vp8 \
    -e NEKO_PASSWORD=test \
    -e NEKO_PASSWORD_ADMIN=admin \
    m1k1o/neko:chromium

# Open in browser
open http://localhost:8080
```

**Validate:**
- [ ] Container starts and Neko is accessible at `localhost:8080`
- [ ] WebRTC video stream works in a regular browser
- [ ] Mouse and keyboard input work
- [ ] Audio works
- [ ] Clipboard sync works
- [ ] Performance is acceptable (framerate, latency)

### Step 2: Connect from WaveTerm's renderer

**Status:** Open

Write a minimal React component that:
1. Opens a WebSocket to `ws://localhost:8080/ws?password=test`
2. Negotiates WebRTC (SDP offer/answer + ICE)
3. Renders the video stream in a `<video>` element
4. Forwards mouse events via DataChannel

**Validate:**
- [ ] WebRTC connection establishes from Electron renderer
- [ ] Video renders in `<video>` element
- [ ] Mouse clicks reach the remote browser
- [ ] Keyboard input reaches the remote browser
- [ ] No Electron security restrictions block WebRTC or WebSocket

### Step 3: Container lifecycle from main process

**Status:** Open

Write a minimal `emain-container.ts` that:
1. Detects Docker or Podman
2. Starts a Neko container with port mappings
3. Waits for health check
4. Returns the connection URL
5. Stops and removes the container on cleanup

**Validate:**
- [ ] Container starts from Electron main process
- [ ] Port allocation works (no conflicts)
- [ ] Health check detects when Neko is ready
- [ ] Container stops and is removed cleanly
- [ ] Works with both Docker and Podman

### Step 4: URL navigation via keyboard forwarding

**Status:** Open

Test the "hacky" URL navigation approach:
1. Focus the remote browser (click on video)
2. Send Ctrl+L (focus URL bar in Chromium)
3. Type a URL character by character via keyboard events
4. Press Enter

**Validate:**
- [ ] Ctrl+L focuses the URL bar in the remote Chromium
- [ ] Typed characters appear in the URL bar
- [ ] Enter navigates to the URL
- [ ] Timing is reliable (no race conditions with focus)
- [ ] Works for URLs with special characters

### Step 5: CDP bridge investigation

**Status:** Open

Test whether CDP (Chrome DevTools Protocol) can be used alongside Neko:

```bash
# Run Neko container with Chromium remote debugging enabled
docker run -d --name neko-cdp \
    -p 8080:8080 \
    -p 9222:9222 \
    -p 52000-52100:52000-52100/udp \
    -e NEKO_PASSWORD=test \
    -e CHROMIUM_ARGS="--remote-debugging-port=9222 --remote-debugging-address=0.0.0.0" \
    m1k1o/neko:chromium
```

**Validate:**
- [ ] Can connect to CDP at `localhost:9222`
- [ ] Can navigate to a URL via CDP (`Page.navigate`)
- [ ] Can get current URL via CDP
- [ ] Can get loading state via CDP
- [ ] CDP doesn't interfere with Neko's WebRTC streaming
- [ ] CDP works alongside Neko's input handling

**If CDP works:** This becomes the preferred approach for URL navigation,
loading state, and back/forward support. Much better than keyboard forwarding.

### Step 6: Performance benchmarking

**Status:** Open

Measure:
- [ ] Latency: time from mouse click to visual response
- [ ] Framerate: FPS at different resolutions and bitrates
- [ ] CPU usage: container + WaveTerm during active browsing
- [ ] Memory usage: container + WaveTerm
- [ ] Bandwidth: even on localhost, measure the stream data rate
- [ ] Text clarity: screenshot comparison of text rendering at different
      bitrates and encoders (VP8 vs H.264 vs JPEG)

---

## Prototype success criteria

The prototype is successful if:

1. **WebRTC streaming works from WaveTerm renderer** — video renders,
   input works, no Electron blockers
2. **Container lifecycle works from main process** — start, health check,
   stop, cleanup all function correctly
3. **URL navigation works** — either via keyboard forwarding or CDP bridge
4. **Performance is acceptable** — latency < 50ms, framerate ≥ 30 FPS,
   text is readable
5. **Resource usage is reasonable** — < 1 GB RAM per container, < 15% CPU
   during active browsing

If any criterion fails, document the failure and reassess the architecture
before proceeding to full implementation.

---

## Time estimate

**Status:** Open — not estimated

The prototype should be completed before starting Phase 1 of the
implementation plan. It answers the highest-risk questions with minimal
code investment.

---

## Deliverables

After the prototype:
- [ ] Working spike code (throwaway, not merged)
- [ ] Performance measurements documented
- [ ] CDP bridge feasibility assessment
- [ ] Updated risk assessment with real-world findings
- [ ] Decision: proceed with architecture or pivot
- [ ] Updated open questions with answers from prototype
