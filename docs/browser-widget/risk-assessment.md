# Risk Assessment — RemoteBrowser Block

**Branch:** `feature/browser-widget`
**Date:** 2026-08-24
**Status:** Partial (known risks documented, needs review)

---

## Risk matrix

| # | Risk | Likelihood | Impact | Mitigation | Status |
|---|------|-----------|--------|------------|--------|
| R1 | Docker/Podman not installed | High | High | Detect at runtime, show clear error message with install instructions, fall back to existing `"web"` block | Documented |
| R2 | Neko image pull fails (network issue) | Medium | Medium | Retry with backoff, show progress, allow cancel, cache image after first pull | Documented |
| R3 | Container fails to start | Low | High | Health check with timeout, detailed error logging, fallback to `"web"` block | Documented |
| R4 | WebRTC negotiation fails | Medium | High | Fallback to WebSocket transport (if using Selkies) or retry, check ICE connectivity, log SDP for debugging | Open |
| R5 | No programmatic URL navigation | Certain | Medium | Use keyboard event forwarding (Ctrl+L + type URL) for v1, CDP bridge for v2 | Documented |
| R6 | No loading state or URL change events | Certain | Medium | No loading spinner, URL bar shows user input only. CDP bridge would solve this | Documented |
| R7 | Text rendering quality (video encoding) | Medium | Low | Use high bitrate (2000+ kbps), VP8 at 1080p, allow quality settings | Documented |
| R8 | Input latency on localhost | Low | Low | WebRTC on localhost is ~10-20ms, acceptable for interactive use | Documented |
| R9 | Container resource leak (not stopped) | Medium | Medium | Track containers by block ID, cleanup on block close and app exit, `will-quit` handler, orphan detection on startup | Documented |
| R10 | Container OOM or crash | Low | High | Monitor container events, notify user, offer restart, fallback to `"web"` block | Documented |
| R11 | Port conflict (TCP/UDP ports in use) | Medium | Low | Find free ports dynamically, retry with different ports | Documented |
| R12 | macOS Docker Desktop not running | High | High | Check Docker daemon status, show "start Docker Desktop" message, support Podman as alternative | Documented |
| R13 | X11 key code mapping incomplete | Medium | Medium | Use noVNC's keysym.js as reference, test common keys, handle unmapped keys gracefully | Open |
| R14 | Coordinate mapping off (video scaling) | Medium | Medium | Account for `object-fit`, letterboxing, device pixel ratio. Test with different resolutions | Open |
| R15 | Clipboard sync fails | Low | Low | Graceful degradation (clipboard is optional), log error, continue without clipboard | Documented |
| R16 | Audio not working | Medium | Low | Graceful degradation, allow disabling audio, check WebRTC audio track status | Documented |
| R17 | Neko version incompatibility | Low | Medium | Pin Neko image version, test before upgrading, document compatible versions | Open |
| R18 | Container image too large (~1.2 GB) | Certain | Low | Pull on first use with progress, cache locally, consider smaller custom image in future | Documented |
| R19 | Multiple containers exhaust resources | Medium | Medium | Default to one container per block but warn if >3 running, suggest shared mode | Open |
| R20 | WaveTerm crash leaves orphaned containers | Medium | Medium | On startup, detect containers with WaveTerm label, offer to clean up | Open |

---

## Risk categories

### Infrastructure risks (R1, R3, R11, R12)

The block depends on external infrastructure (Docker/Podman) that WaveTerm
doesn't control. These risks are mitigated by:
- Clear error messages with actionable instructions
- Runtime detection before attempting to start containers
- Graceful fallback to the existing `"web"` block
- Health checks with timeouts

### API limitations (R5, R6)

Neko's lack of browser control APIs is the biggest functional gap. Two-phase
approach:
- **v1:** Keyboard event forwarding for URL navigation (works but hacky)
- **v2:** CDP bridge (run Chromium with `--remote-debugging-port`, connect
  from WaveTerm for proper URL control, loading state, navigation events)

### Resource risks (R9, R10, R18, R19)

Container resource management:
- Track all containers by block ID
- Cleanup on block close, app exit, and app crash recovery
- Resource monitoring (CPU, RAM)
- Suggest shared container mode if many blocks open

### Quality risks (R7, R8, R13, R14)

Video and input quality:
- High bitrate encoding for text clarity
- X11 key code mapping from noVNC reference
- Coordinate mapping with proper scaling math
- Test with real-world websites

---

## Open items

- [ ] Define fallback behavior: should the block automatically fall back to
  `"web"` if container fails, or show an error and let the user decide?
- [ ] Define container labeling scheme for orphan detection (e.g.
  `waveterm.block-id=<id>`)
- [ ] Define resource limits for containers (CPU, RAM)
- [ ] Test WebRTC on localhost across all supported platforms (macOS, Linux,
  Windows)
- [ ] Define Neko image version pinning strategy
- [ ] Create error message catalog (user-facing strings for each failure mode)
