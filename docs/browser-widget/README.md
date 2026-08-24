# Browser Widget — Documentation Index

**Branch:** `feature/browser-widget`
**Status:** Research & design phase (not yet implemented)

## Documents

| Document | Status | Description |
|----------|--------|-------------|
| [research-current-state.md](./research-current-state.md) | Complete | Analysis of current `<webview>` wiring, why it's a maintenance issue, survey of 7 alternative approaches (WebContentsView, CEF, Playwright, Servo, wry, in-process embedding, remote browser streaming) with 8 streaming project profiles |
| [adr-local-containerized-browser.md](./adr-local-containerized-browser.md) | Complete | Architecture Decision Record: local Docker/Podman container with Neko streaming via WebRTC. New `"remotebrowser"` block type |
| [neko-api-surface.md](./neko-api-surface.md) | Partial | Neko client API: WebSocket signaling, WebRTC setup, input events, URL navigation, session management. **Open: needs validation against Neko source** |
| [component-design.md](./component-design.md) | Open | React component structure, atoms, view component tree, IPC channels |
| [ipc-contract.md](./ipc-contract.md) | Open | Electron IPC channel spec between renderer and main process |
| [risk-assessment.md](./risk-assessment.md) | Partial | Risk/mitigation table for known risks |
| [prototype-plan.md](./prototype-plan.md) | Open | Spike plan to validate Neko integration before full implementation |
| [open-questions.md](./open-questions.md) | Open | Tracked open questions with status lifecycle |

## Summary

The browser widget project aims to create a new WaveTerm block type
(`"remotebrowser"`) that streams a browser running inside a local
Docker/Podman container via Neko's WebRTC stack. This avoids Electron's
deprecated `<webview>` tag, provides container-level security isolation,
and enables engine independence (Chromium, Firefox, or future engines).

The existing `"web"` block is **not replaced** — both blocks coexist.
Users choose based on their needs (lightweight in-process vs. secure
containerized).

## Branch

```
dev.patch
  └── feature/browser-widget
       ├── a6fa0a13 docs: browser widget research — current state & challenge
       ├── 805eed9e docs: add remote browser streaming research
       └── 823f703a docs: ADR — local containerized browser streaming with Neko
```
