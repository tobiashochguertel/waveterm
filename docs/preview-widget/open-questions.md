# Open Questions — Preview Widget

**Branch:** `feature/browser-widget`
**Date:** 2026-08-24

---

## Q1: Binary file data RPC

**Status:** open
**Recommendation:** Use `fetch()` with the streaming endpoint

**Question:** How to fetch binary file content (ArrayBuffer) for DOCX,
XLSX, PPTX rendering?

**Context:**
- Existing `FileReadCommand` RPC returns string content (for text files)
- DOCX/XLSX/PPTX are binary formats (ZIP archives containing XML)
- Options:
  - **Use `fetch()` with streaming endpoint** — `/wave/stream-file?path=...`
    already serves binary content. Use `fetch(url).then(r => r.arrayBuffer())`
  - **Add binary RPC** — new `FileReadBinaryCommand` that returns ArrayBuffer
  - **Use Blob** — `fetch(url).then(r => r.blob())` then `blob.arrayBuffer()`

**Decision needed by:** Phase 1 implementation

---

## Q2: PDF.js worker configuration

**Status:** open
**Recommendation:** Use Vite's `?url` import for the worker

**Question:** How to configure the PDF.js Web Worker in Electron + Vite?

**Context:**
- PDF.js requires a worker script (`pdf.worker.min.mjs`)
- In a Vite build, the worker needs to be served as a separate file
- Electron loads assets from `file://` protocol (not a web server)
- Options:
  - `new URL('pdfjs-dist/build/pdf.worker.min.mjs', import.meta.url).toString()`
  - Vite `?url` import: `import workerUrl from 'pdfjs-dist/build/pdf.worker.min.mjs?url'`
  - Inline worker (bundle worker into main bundle — defeats purpose)
  - Use `pdfjs-dist/legacy/build/pdf.worker.mjs` for compatibility

**Decision needed by:** Phase 2 implementation

---

## Q3: HTML sanitization for DOCX/PPTX

**Status:** open
**Recommendation:** Render in sandboxed iframe

**Question:** Should the HTML output from docx-preview and pptx-renderer
be sanitized?

**Context:**
- docx-preview renders DOCX to HTML DOM directly in the container element
- pptx-renderer renders to HTML/SVG
- Malicious DOCX/PPTX could contain scripts or dangerous HTML
- Options:
  - **Sandboxed iframe** — render in `<iframe sandbox="allow-same-origin">`
    (no scripts allowed)
  - **DOMPurify** — sanitize HTML before insertion
  - **Trust the libraries** — docx-preview and pptx-renderer should not
    execute scripts (but verify)

**Decision needed by:** Phase 3/5 implementation

---

## Q4: Legacy Office formats (.doc, .xls, .ppt)

**Status:** open
**Recommendation:** Not in v1, show "format not supported" message

**Question:** Should we support legacy Office formats (.doc, .xls, .ppt)?

**Context:**
- docx-preview only supports .docx (OOXML), not .doc (binary)
- SheetJS can parse .xls but with limitations
- No good JS library for .ppt rendering
- Legacy formats are increasingly rare
- Users can convert to modern formats

**Decision needed by:** Post-v1

---

## Q5: OpenDocument formats (.odt, .ods, .odp)

**Status:** open
**Recommendation:** Not in v1, investigate later

**Question:** Should we support OpenDocument formats?

**Context:**
- Used by LibreOffice, OpenOffice, Google Docs (export)
- docx-preview does not support .odt
- SheetJS may support .ods (need to verify)
- No good JS library for .odp rendering
- Lower priority than Microsoft formats

**Decision needed by:** Post-v1

---

## Q6: XLSX cell formatting

**Status:** open
**Recommendation:** Show raw values only for v1

**Question:** Should XLSX preview preserve cell formatting (colors,
borders, number formats)?

**Context:**
- SheetJS extracts data values but does not preserve cell formatting
- The existing CSVView component renders plain data tables
- Preserving formatting would require a full spreadsheet renderer
  (Univer, Handsontable) — heavy dependencies
- For preview purposes, showing data values is usually sufficient

**Decision needed by:** Phase 4 implementation

---

## Q7: XLSX formula support

**Status:** open
**Recommendation:** Show computed values, not formulas

**Question:** Should XLSX preview show formulas or computed values?

**Context:**
- SheetJS reads computed values by default (not formulas)
- Showing formulas would require `XLSX.utils.sheet_to_json(worksheet, { header: 1, raw: false })`
- For preview, computed values are what users expect to see

**Decision needed by:** Phase 4 implementation

---

## Q8: Patch file vs direct commit

**Status:** open
**Recommendation:** Check if modified files are in PATCHED_FILES

**Question:** Should the preview widget changes be a `.patch` file or
direct commits to `dev.patch`?

**Context:**
- The fork uses `.patch` files for changes to files that upstream modifies
- Need to check if `preview-model.tsx`, `preview.tsx`, `preview-streaming.tsx`
  are in `PATCHED_FILES`
- If they are: changes must be a `.patch` file (e.g. `009-preview-documents.patch`)
- If they are not: direct commits to `dev.patch` are fine
- New files (`preview-pdf.tsx`, `preview-docx.tsx`, etc.) don't need patches
  (they don't exist in upstream)

**Decision needed by:** Before implementation starts

---

## Q9: PDF search

**Status:** open
**Recommendation:** Include in v1 if react-pdf supports it easily

**Question:** Should the PDF viewer support text search?

**Context:**
- The current iframe-based viewer uses the browser's built-in search
- react-pdf/PDF.js has text layer support for search
- Adds complexity: search input, highlight results, next/previous match
- Very useful for large PDFs

**Decision needed by:** Phase 2 implementation

---

## Q10: Image gallery view

**Status:** open
**Recommendation:** Not in v1, document as future enhancement

**Question:** Should the preview block support an image gallery view
for directories containing multiple images?

**Context:**
- Currently, images are previewed one at a time
- A gallery view would show thumbnails of all images in a directory
- Would require thumbnail generation (can be done client-side with canvas)
- Useful for browsing photo directories, design assets, etc.

**Decision needed by:** Post-v1
