# Preview Widget — Research: Current State

**Branch:** `feature/browser-widget`
**Date:** 2026-08-24
**Status:** Complete

---

## Summary

WaveTerm has an existing `"preview"` block that handles text files, markdown,
CSV, directories, images, PDFs (via browser), and video/audio. It does **not**
support Word (.docx), Excel (.xlsx), PowerPoint (.pptx), or other Office
document formats. This document maps the current preview architecture and
identifies the gaps.

---

## Current architecture

### Block registration

`frontend/app/block/blockregistry.ts` (line 25):
```typescript
BlockRegistry.set("preview", PreviewModel);
```

### Specialized view selection

`frontend/app/view/preview/preview-model.tsx` — `getSpecializedView()`
(lines 508-560) determines which renderer to use based on MIME type:

```
File requested
    │
    ▼
getSpecializedView(mimeType)
    │
    ├── File not found? ──────────────────────► codeedit
    ├── MIME type is null? ───────────────────► error
    ├── isStreamingType(mimeType)? ───────────► streaming
    │   (PDF, video, audio, image)
    ├── File size > 10MB? ────────────────────► error
    ├── CSV > 1MB? ───────────────────────────► error
    ├── mimeType == "directory"? ─────────────► directory
    ├── mimeType == "text/csv"? ──────────────► csv (or codeedit if edit mode)
    ├── isMarkdownLike(mimeType)? ────────────► markdown (or codeedit if edit mode)
    ├── isTextFile(mimeType)? ────────────────► codeedit
    └── otherwise ────────────────────────────► error "Preview (mimeType)"
```

### Specialized view map

`frontend/app/view/preview/preview.tsx` (lines 26-32):
```typescript
const SpecializedViewMap = {
    streaming: StreamingPreview,    // PDF, video, audio, image
    markdown: MarkdownPreview,      // Markdown, MDX
    codeedit: CodeEditPreview,      // Text files (Monaco editor)
    csv: CSVViewPreview,            // CSV (papaparse + react-table)
    directory: DirectoryPreview,    // Directory listing
};
```

### File type detection

MIME type-based detection (no file extension mapping, no content sniffing).
MIME type comes from the backend `FileInfoCommand` RPC.

**`isStreamingType()`** (lines 66-76):
```typescript
function isStreamingType(mimeType: string): boolean {
    return mimeType.startsWith("application/pdf") ||
           mimeType.startsWith("video/") ||
           mimeType.startsWith("audio/") ||
           mimeType.startsWith("image/");
}
```

**`isTextFile()`** (lines 53-64):
- All `text/*` MIME types
- Specific `application/*` types: sql, php, pem, javascript, typescript,
  ruby, wasm, latex, sh, python, awk
- Application types containing: json, yaml, toml, xml

**`isMarkdownLike()`** (lines 78-83):
- `text/markdown`
- `text/mdx`

### File size limits

- Max file size: 10MB (`MaxFileSize`)
- Max CSV size: 1MB (`MaxCSVSize`)

---

## Current capabilities by format

### Markdown — works well

**File:** `frontend/app/view/preview/preview-markdown.tsx` (62 lines)

Uses `react-markdown` with a rich plugin stack:
- `remark-gfm` — GitHub Flavored Markdown
- `remark-github-blockquote-alert` — GitHub-style alerts
- `remark-flexible-toc` — Table of contents
- `rehype-highlight` — Syntax highlighting
- `rehype-raw` — Raw HTML support
- `rehype-sanitize` — HTML sanitization
- `rehype-slug` — Heading anchors
- `shiki` — TextMate grammar syntax highlighting
- `mermaid` — Diagram rendering

Features:
- Table of contents toggle
- Anchor navigation for bookmarks
- Font size overrides
- Relative path resolution for images and links
- Code blocks with copy and execute buttons

**Verdict:** No changes needed. Markdown rendering is already excellent.

### Images — works, could be enhanced

**File:** `frontend/app/view/preview/preview-streaming.tsx` (lines 32-47, 86-88)

Uses `react-zoom-pan-pinch` (v3.7.0) for zoom/pan. Images are streamed via
`/wave/stream-file` endpoint.

Features:
- Zoom in/out buttons
- Reset zoom button
- Pinch-to-zoom support
- Pan/zoom functionality
- Centered display

**Gaps:**
- No EXIF rotation handling (modern browsers auto-rotate via
  `image-orientation: from-image`, but this may not be set)
- No HEIC/HEIF support (Safari only natively; common on macOS/iOS)
- No AVIF explicit support (works in Chromium but not validated)
- No image metadata display (dimensions, file size, format)
- No thumbnail/preview for very large images
- No multi-image support (no gallery/album view for directories of images)

**Verdict:** Works for basic use. Could add HEIC conversion, metadata
display, and gallery view as enhancements.

### PDF — works, but minimal

**File:** `frontend/app/view/preview/preview-streaming.tsx` (lines 65-70)

```tsx
if (fileInfo.mimetype === "application/pdf") {
    return (
        <div className="...">
            <iframe src={streamingUrl} width="100%" height="100%" name="pdfview" />
        </div>
    );
}
```

Uses the browser's native PDF viewer via `<iframe>`. No custom rendering.

**Gaps:**
- Depends on browser's PDF viewer (Electron's Chromium has one, but UI is
  not customizable)
- No page navigation UI
- No thumbnail sidebar
- No text search within PDF
- No text selection/copy (depends on browser viewer)
- No zoom control (depends on browser viewer)
- No page bookmarks
- No PDF metadata display
- No loading progress indicator

**Verdict:** Functional but basic. Replacing with PDF.js or react-pdf would
give full control over the UI and features.

### CSV — works well

**File:** `frontend/app/view/preview/csvview.tsx` (217 lines)

Uses `papaparse` for parsing + `@tanstack/react-table` for rendering.

Features:
- Automatic header detection
- Sortable columns
- Column resizing
- Keyboard navigation
- Numeric string conversion
- Handles CSVs without headers
- Max 10MB data size

**Verdict:** No changes needed for CSV. Could be extended to handle Excel
files by parsing them with SheetJS and feeding the data into the same table
component.

### Video/audio — works

**File:** `frontend/app/view/preview/preview-streaming.tsx` (lines 72-84)

HTML5 `<video>` and `<audio>` elements with controls. Streamed via
`/wave/stream-file`.

**Verdict:** No changes needed.

### Directory — works well

**File:** `frontend/app/view/preview/preview-directory.tsx` (923 lines)

Full file directory listing with:
- Sortable columns (name, permissions, modified, size, type)
- Show/hide hidden files
- Search/filter
- Keyboard navigation
- Drag and drop
- Context menu (new file, rename, copy, delete, bookmark)
- File icons by MIME type
- Parent directory navigation

**Verdict:** No changes needed.

### Text/code editing — works well

**File:** `frontend/app/view/preview/preview-edit.tsx` (134 lines)

Monaco editor with:
- Syntax highlighting
- Read-only mode for non-writable files
- Save/revert buttons
- Keyboard shortcuts (Cmd+E, Cmd+S, Cmd+R)
- Font size override
- Word wrap toggle

**Verdict:** No changes needed.

---

## What's missing

### Word documents (.docx)

**MIME type:** `application/vnd.openxmlformats-officedocument.wordprocessingml.document`

Currently falls through to the error case: `"Preview (mimeType)"`.

No rendering library installed. No MIME type detection for Office formats.

### Excel spreadsheets (.xlsx)

**MIME type:** `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`

Currently falls through to the error case.

No rendering library installed. The existing CSV viewer could be reused if
the Excel data is parsed into the same format.

### PowerPoint (.pptx)

**MIME type:** `application/vnd.openxmlformats-officedocument.presentationml.presentation`

Currently falls through to the error case.

No rendering library installed.

### Other Office formats

- `.odt` (OpenDocument Text) — `application/vnd.oasis.opendocument.text`
- `.ods` (OpenDocument Spreadsheet) — `application/vnd.oasis.opendocument.spreadsheet`
- `.odp` (OpenDocument Presentation) — `application/vnd.oasis.opendocument.presentation`
- `.rtf` (Rich Text Format) — `application/rtf`
- `.doc` (legacy Word) — `application/msword`
- `.xls` (legacy Excel) — `application/vnd.ms-excel`
- `.ppt` (legacy PowerPoint) — `application/vnd.ms-powerpoint`

None of these are currently handled.

### HEIC images

Common on macOS/iOS. Not supported natively by Chromium (only Safari).
Would need a conversion library (`heic-to` or `libheif-js`).

---

## Key files

| File | Lines | Role |
|------|-------|------|
| `frontend/app/view/preview/preview-model.tsx` | 940 | PreviewModel — view selection logic, file info, MIME detection |
| `frontend/app/view/preview/preview.tsx` | 170 | PreviewView — SpecializedViewMap, main preview component |
| `frontend/app/view/preview/preview-streaming.tsx` | 92 | StreamingPreview — PDF, video, audio, image rendering |
| `frontend/app/view/preview/preview-markdown.tsx` | 62 | MarkdownPreview — markdown rendering |
| `frontend/app/view/preview/csvview.tsx` | 217 | CSVView — CSV table viewer |
| `frontend/app/view/preview/preview-directory.tsx` | 923 | DirectoryPreview — file directory listing |
| `frontend/app/view/preview/preview-edit.tsx` | 134 | CodeEditPreview — Monaco editor |
| `frontend/app/view/preview/preview-error-overlay.tsx` | 84 | ErrorOverlay — error display |
| `frontend/app/view/preview/previewenv.ts` | 35 | PreviewEnv — RPC interface definition |
| `frontend/app/block/blockregistry.ts` | 65 | Block registration |
| `frontend/app/element/markdown.tsx` | — | Shared Markdown component (used by preview + AI) |

### NPM packages already installed

| Package | Version | Purpose |
|---------|---------|---------|
| `react-markdown` | ^9.0.3 | Markdown rendering |
| `remark-gfm` | ^4.0.1 | GitHub Flavored Markdown |
| `remark-github-blockquote-alert` | ^1.3.1 | GitHub-style alerts |
| `remark-flexible-toc` | ^1.2.4 | Table of contents |
| `rehype-highlight` | ^7.0.2 | Syntax highlighting |
| `rehype-raw` | ^7.0.0 | Raw HTML support |
| `rehype-sanitize` | ^6.0.0 | HTML sanitization |
| `rehype-slug` | ^6.0.0 | Heading anchors |
| `shiki` | ^3.22.0 | TextMate grammar highlighting |
| `mermaid` | ^11.15.0 | Diagram rendering |
| `papaparse` | ^5.5.3 | CSV parsing |
| `@tanstack/react-table` | — | Table rendering (for CSV) |
| `react-zoom-pan-pinch` | ^3.7.0 | Image zoom/pan |
| `monaco-editor` | ^0.55.1 | Code editor |
| `pngjs` | ^7.0.0 | PNG processing |
| `fast-average-color` | ^9.5.0 | Color extraction |

### NPM packages NOT installed (needed for new formats)

| Package | Purpose |
|---------|---------|
| `pdfjs-dist` or `react-pdf` | PDF rendering (to replace iframe) |
| `docx-preview` or `mammoth` | Word document rendering |
| `xlsx` (SheetJS) | Excel parsing |
| `@aiden0z/pptx-renderer` | PowerPoint rendering |
| `heic-to` | HEIC image conversion |
