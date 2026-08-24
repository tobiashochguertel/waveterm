# Library Survey — Document Rendering

**Branch:** `feature/browser-widget`
**Date:** 2026-08-24
**Status:** Complete (researched from npm, GitHub, and documentation)

---

## PDF rendering

### PDF.js (Mozilla)

| | |
|---|---|
| **npm** | [`pdfjs-dist`](https://www.npmjs.com/package/pdfjs-dist) (v6.2.108, 24M weekly) |
| **GitHub** | https://github.com/mozilla/pdf.js |
| **License** | Apache-2.0 |
| **Status** | Industry standard, actively maintained |

Renders PDF pages to `<canvas>`. Requires a Web Worker for performance.

```javascript
import { getDocument } from 'pdfjs-dist';
import * as pdfjsLib from 'pdfjs-dist';
pdfjsLib.GlobalWorkerOptions.workerSrc = 'pdfjs-dist/build/pdf.worker.mjs';

const pdf = await getDocument(url).promise;
const page = await pdf.getPage(1);
const viewport = page.getViewport({ scale: 1.5 });
const canvas = document.getElementById("canvas");
await page.render({ canvasContext: canvas.getContext("2d"), viewport }).promise;
```

### react-pdf

| | |
|---|---|
| **npm** | [`react-pdf`](https://www.npmjs.com/package/react-pdf) (v10.4.1) |
| **GitHub** | https://github.com/wojtekmaj/react-pdf |
| **License** | MIT |

React wrapper for PDF.js. Provides `<Document>` and `<Page>` components.

```jsx
import { Document, Page, pdfjs } from 'react-pdf';
pdfjs.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs', import.meta.url
).toString();

<Document file="/document.pdf">
  <Page pageNumber={1} />
</Document>
```

### MuPDF.js (WASM)

| | |
|---|---|
| **GitHub** | https://github.com/ArtifexSoftware/mupdf.js |
| **npm** | `mupdf-js` |
| **License** | AGPL-3.0 (commercial license available) |

WebAssembly-based, high-fidelity. Same engine as commercial viewers.
Full editing capabilities. TypeScript-first.

**Note:** AGPL license may be a concern for WaveTerm (Apache-2.0).

### @embedpdf/pdfium (WASM)

| | |
|---|---|
| **npm** | [`@embedpdf/pdfium`](https://www.npmjs.com/package/@embedpdf/pdfium) |
| **License** | MIT |

PDFium WebAssembly (Chrome's PDF engine). High-fidelity rendering, text
extraction, form filling.

**Recommendation:** `react-pdf` (MIT, React-native, wraps PDF.js which is
the industry standard and Apache-2.0).

---

## Word document (.docx) rendering

### docx-preview

| | |
|---|---|
| **npm** | [`docx-preview`](https://www.npmjs.com/package/docx-preview) (v0.4.0, 1.3M weekly) |
| **GitHub** | https://github.com/VolodymyrBaydalka/docxjs |
| **License** | Apache-2.0 |

Converts DOCX to HTML with visual fidelity. Parses the DOCX ZIP + XML,
renders to HTML with styles, page breaks, fonts.

```javascript
import { renderAsync } from 'docx-preview';
await renderAsync(docData, document.getElementById("container"), null, {
    className: "docx",
    inWrapper: true,
    breakPages: true,
    ignoreFonts: false,
});
```

**Pros:** Visual fidelity (looks like Word), page breaks, font handling
**Cons:** Renders to raw DOM (not React), large documents can be slow

### mammoth.js

| | |
|---|---|
| **npm** | [`mammoth`](https://www.npmjs.com/package/mammoth) (v1.12.1, 7.5M weekly) |
| **GitHub** | https://github.com/mwilliamson/mammoth.js |
| **License** | BSD-2-Clause |

Converts .docx to semantic HTML (content-focused, not visual fidelity).

```javascript
import mammoth from 'mammoth';
const result = await mammoth.convertToHtml({arrayBuffer});
const html = result.value;
```

**Pros:** Simple, fast, semantic output, very popular
**Cons:** No visual fidelity (no page layout, no fonts, no colors), loses
formatting

**Recommendation:** `docx-preview` for preview (visual fidelity matters),
`mammoth` as fallback for large documents or when fidelity isn't needed.

---

## Excel/spreadsheet (.xlsx) rendering

### SheetJS (xlsx)

| | |
|---|---|
| **npm** | [`xlsx`](https://www.npmjs.com/package/xlsx) (v0.20.3) |
| **GitHub** | https://github.com/SheetJS/sheetjs |
| **License** | Apache-2.0 |

Parses and writes spreadsheet data. Does NOT render — extracts data to JSON.

```javascript
import * as XLSX from 'xlsx';
const workbook = XLSX.read(data, {type: 'array'});
const worksheet = workbook.Sheets[workbook.SheetNames[0]];
const jsonData = XLSX.utils.sheet_to_json(worksheet);
```

**Use case:** Parse XLSX → feed data into WaveTerm's existing CSVView
component (which uses `@tanstack/react-table`).

### Univer

| | |
|---|---|
| **npm** | `@univerjs/sheets-ui`, `@univerjs/sheets` (v0.21.0) |
| **GitHub** | https://github.com/dream-num/univer |
| **License** | Apache-2.0 |

Full spreadsheet rendering with Canvas API. Formulas, charts, pivot tables.
Successor to Luckysheet (which is EOL).

**Pros:** Full spreadsheet UI with formulas and charts
**Cons:** Heavy dependency, complex integration, overkill for preview

### Handsontable

| | |
|---|---|
| **npm** | [`handsontable`](https://www.npmjs.com/package/handsontable) (v17.0.1) |
| **GitHub** | https://github.com/handsontable/handsontable |
| **License** | Commercial (free tier for non-commercial) |

Data grid with 400+ spreadsheet formulas, sorting, filtering, virtualization.

**Cons:** Commercial license for commercial use. WaveTerm is open source
(Apache-2.0), so this may not be suitable.

**Recommendation:** `SheetJS` for parsing + reuse existing `CSVView`
component for rendering. This is the lightest approach and reuses existing
code. For formula support, consider Univer in the future.

---

## PowerPoint (.pptx) rendering

### @aiden0z/pptx-renderer

| | |
|---|---|
| **npm** | [`@aiden0z/pptx-renderer`](https://www.npmjs.com/package/@aiden0z/pptx-renderer) (v1.2.4, 220K weekly) |
| **GitHub** | https://github.com/aiden0z/pptx-renderer |
| **License** | Apache-2.0 |

High-fidelity HTML/SVG rendering. 187+ shapes, 134+ SmartArt layouts, 452+
visual regression test cases. Charts, tables, gradients, pattern fills.

```typescript
import { PptxViewer } from '@aiden0z/pptx-renderer';
const viewer = await PptxViewer.open(arrayBuffer, container, {
    zipLimits: RECOMMENDED_ZIP_LIMITS,
    listOptions: { windowed: true }
});
```

### pptx-browser

| | |
|---|---|
| **npm** | `pptx-browser` (v4.1.5) |
| **License** | MIT |

Zero dependencies, Canvas rendering, SVG/PDF export, slide show.

**Recommendation:** `@aiden0z/pptx-renderer` — most mature, Apache-2.0,
high-fidelity, active development.

---

## Image enhancements

### HEIC/HEIF conversion

#### heic-to

| | |
|---|---|
| **npm** | [`heic-to`](https://www.npmjs.com/package/heic-to) (v1.5.2) |
| **GitHub** | https://github.com/stelli-hub/heic-to |
| **License** | MIT |

Converts HEIC to JPEG/PNG/Bitmap using libheif WASM.

```javascript
import { heicTo } from "heic-to";
const jpeg = await heicTo({ blob: file, type: "image/jpeg", quality: 0.5 });
```

### EXIF rotation

Modern browsers auto-rotate via CSS `image-orientation: from-image`.
No library needed if this CSS property is set on the `<img>` element.

For explicit control: `exifr` (lightweight EXIF parser).

### Existing (already installed)

- `react-zoom-pan-pinch` (v3.7.0) — zoom/pan for images
- `pngjs` (v7.0.0) — PNG processing
- `fast-average-color` (v9.5.0) — color extraction

---

## Universal document viewers

### shrimp-doc-viewer

| | |
|---|---|
| **GitHub** | https://github.com/cjo4m06/shrimp-doc-viewer |
| **Formats** | PDF, DOCX, XLSX, PPTX, CSV, Markdown, RTF, ODF, images |
| **Technology** | Rust → WASM core, PDFium-WASM for PDF |
| **License** | Open source |

Virtualized, zoomable, CJK support, Web Worker rendering.

```javascript
import { mount } from 'shrimp-doc-viewer';
const viewer = await mount(container, arrayBuffer);
```

### @file-viewer/web-full

| | |
|---|---|
| **npm** | [`@file-viewer/web-full`](https://www.npmjs.com/package/@file-viewer/web-full) (v2.2.9) |
| **Formats** | 208 file extensions (Office, PDF, CAD, archives, email) |
| **License** | Commercial (with free tier) |

### docMentis

| | |
|---|---|
| **npm** | `@docmentis/udoc-viewer` |
| **Formats** | PDF, DOCX, PPTX, XLSX, images |
| **License** | MIT (viewer), commercial for engine |

**Recommendation:** Individual libraries rather than a universal viewer.
Universal viewers are large (10-50MB with WASM), may have license issues,
and we only need 4 formats. Individual libraries give more control and
smaller bundle size (lazy-loaded per format).

---

## Iframe-based viewers (not recommended)

### Google Docs Viewer

```
https://docs.google.com/viewer?url={encodedUrl}&embedded=true
```

**Limitation:** Requires publicly accessible URL. WaveTerm previews local
files, so this doesn't work.

### Office Online Viewer

```
https://view.officeapps.live.com/op/view.aspx?src={encodedUrl}
```

**Limitation:** Same — requires public URL. Also sends file content to
Microsoft servers (privacy concern).

**Recommendation:** Do not use iframe-based viewers. All rendering should
be client-side for privacy and offline capability.

---

## Summary: recommended libraries

| Format | Library | License | npm package | Bundle size (est.) |
|--------|---------|---------|-------------|---------------------|
| **PDF** | react-pdf (wraps PDF.js) | MIT | `react-pdf` + `pdfjs-dist` | ~2.5 MB (lazy) |
| **DOCX** | docx-preview | Apache-2.0 | `docx-preview` | ~500 KB |
| **XLSX** | SheetJS (parse) + existing CSVView | Apache-2.0 | `xlsx` | ~1 MB |
| **PPTX** | @aiden0z/pptx-renderer | Apache-2.0 | `@aiden0z/pptx-renderer` | ~800 KB |
| **HEIC** | heic-to | MIT | `heic-to` | ~2 MB (WASM, lazy) |
| **Markdown** | (already installed) | — | — | — |
| **Images** | (already installed) | — | — | — |

All libraries should be **lazy-loaded** (dynamic import) so they only
affect bundle size when the corresponding format is previewed.

---

## Sources

- [PDF.js](https://github.com/mozilla/pdf.js) — Mozilla PDF renderer
- [react-pdf](https://github.com/wojtekmaj/react-pdf) — React wrapper for PDF.js
- [MuPDF.js](https://github.com/ArtifexSoftware/mupdf.js) — WASM PDF renderer
- [@embedpdf/pdfium](https://www.npmjs.com/package/@embedpdf/pdfium) — PDFium WASM
- [docx-preview](https://github.com/VolodymyrBaydalka/docxjs) — DOCX to HTML
- [mammoth.js](https://github.com/mwilliamson/mammoth.js) — DOCX to semantic HTML
- [SheetJS](https://github.com/SheetJS/sheetjs) — Spreadsheet parser
- [Univer](https://github.com/dream-num/univer) — Full spreadsheet UI
- [Handsontable](https://github.com/handsontable/handsontable) — Data grid
- [@aiden0z/pptx-renderer](https://github.com/aiden0z/pptx-renderer) — PPTX renderer
- [pptx-browser](https://www.npmjs.com/package/pptx-browser) — Canvas PPTX renderer
- [heic-to](https://github.com/stelli-hub/heic-to) — HEIC to JPEG converter
- [shrimp-doc-viewer](https://github.com/cjo4m06/shrimp-doc-viewer) — Universal viewer
- [@file-viewer/web-full](https://www.npmjs.com/package/@file-viewer/web-full) — Universal viewer
- [react-zoom-pan-pinch](https://www.npmjs.com/package/react-zoom-pan-pinch) — Image zoom (installed)
