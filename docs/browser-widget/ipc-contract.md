# IPC Contract — RemoteBrowser Block

**Branch:** `feature/browser-widget`
**Date:** 2026-08-24
**Status:** Open (preliminary design, needs validation during implementation)

---

## Overview

Electron IPC channels between the renderer process (React/RemoteBrowserViewModel)
and the main process (Container Manager). All channels use `ipcRenderer.invoke`
/ `ipcMain.handle` (request-response) or `ipcRenderer.send` /
`ipcMain.on` (fire-and-forget) patterns, consistent with existing WaveTerm IPC.

---

## Container lifecycle channels

### `remotebrowser:start-container`

**Direction:** Renderer → Main (request-response)
**Handler:** `emain-container-ipc.ts`

```typescript
// Request
ipcRenderer.invoke("remotebrowser:start-container", {
    engine: "chromium",          // "chromium" | "firefox" | "google-chrome" | ...
    resolution: "1920x1080",     // "WxH"
    framerate: 30,               // fps
    encoder: "vp8",              // "vp8" | "h264"
    audioEnabled: true,          // boolean
    password: "auto-generated",  // string (auto-gen if not provided)
    extraArgs: [],               // additional docker/podman run args
}) -> Promise<{
    containerId: string,         // Docker container ID
    nekoUrl: string,             // WebSocket URL (ws://localhost:<port>/ws)
    nekoPassword: string,        // Password for Neko auth
    tcpPort: number,             // Mapped TCP port
    udpPortRange: [number, number], // Mapped UDP port range
}>
```

**Main process:**
1. Detect container runtime (docker/podman)
2. Find free TCP port + UDP port range
3. Generate password if not provided
4. Pull image if not cached (return progress via `remotebrowser:pull-progress`)
5. Start container with port mappings
6. Health check (poll `http://localhost:<port>/health`)
7. Return connection info

### `remotebrowser:stop-container`

**Direction:** Renderer → Main (request-response)

```typescript
ipcRenderer.invoke("remotebrowser:stop-container", {
    containerId: string,
}) -> Promise<{ stopped: boolean }>
```

**Main process:** Stop and remove container. Clean up port mappings.

### `remotebrowser:container-status`

**Direction:** Renderer → Main (request-response)

```typescript
ipcRenderer.invoke("remotebrowser:container-status", {
    containerId: string,
}) -> Promise<{
    state: "running" | "stopped" | "exited" | "not-found",
    uptime: number,              // seconds
    cpuUsage: number,            // percentage
    memoryUsage: number,         // MB
}>
```

### `remotebrowser:restart-container`

**Direction:** Renderer → Main (request-response)

```typescript
ipcRenderer.invoke("remotebrowser:restart-container", {
    containerId: string,
}) -> Promise<{ restarted: boolean }>
```

---

## Runtime detection channels

### `remotebrowser:detect-runtime`

**Direction:** Renderer → Main (request-response)

```typescript
ipcRenderer.invoke("remotebrowser:detect-runtime") -> Promise<{
    runtime: "docker" | "podman" | null,
    version: string,
    canRunContainers: boolean,
    availableImages: string[],   // e.g. ["m1k1o/neko:chromium"]
}>
```

---

## Event channels (Main → Renderer)

### `remotebrowser:pull-progress`

**Direction:** Main → Renderer (event)

```typescript
ipcRenderer.on("remotebrowser:pull-progress", (event, data) => {
    // data: { layer: string, current: number, total: number, status: string }
})
```

Fired during `docker pull` / `podman pull` when image is not cached.

### `remotebrowser:container-event`

**Direction:** Main → Renderer (event)

```typescript
ipcRenderer.on("remotebrowser:container-event", (event, data) => {
    // data: { containerId: string, event: "started" | "stopped" | "died" | "error", message?: string }
})
```

Fired when container state changes (crash, OOM, unexpected exit).

---

## Channel registration

**Status:** Open — exact registration pattern to follow existing WaveTerm
IPC conventions in `emain-ipc.ts`

```typescript
// emain/emain-container-ipc.ts
import { ipcMain } from "electron";
import { ContainerManager } from "./emain-container";

export function registerContainerIpcHandlers() {
    ipcMain.handle("remotebrowser:start-container", handleStartContainer);
    ipcMain.handle("remotebrowser:stop-container", handleStopContainer);
    ipcMain.handle("remotebrowser:container-status", handleContainerStatus);
    ipcMain.handle("remotebrowser:restart-container", handleRestartContainer);
    ipcMain.handle("remotebrowser:detect-runtime", handleDetectRuntime);
}
```

---

## Open items

- [ ] Error handling: what happens if Docker/Podman is not installed?
- [ ] Error handling: what happens if image pull fails?
- [ ] Error handling: what happens if container fails to start?
- [ ] Error handling: what happens if health check times out?
- [ ] Port allocation strategy: random free ports or fixed range?
- [ ] Container cleanup on app exit: register a `will-quit` handler?
- [ ] Container cleanup on crash: what if WaveTerm crashes without stopping containers?
- [ ] Multiple blocks: how to track which container belongs to which block?
- [ ] IPC channel naming: follow existing WaveTerm naming convention?
- [ ] Should container status be polled or pushed via events?
- [ ] Resource limits: should containers have CPU/RAM limits configured?
