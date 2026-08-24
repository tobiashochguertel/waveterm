# ADR: Enhance Preview Block with Document Format Support

**Branch:** `feature/browser-widget`
**Date:** 2026-08-24
**Status:** Accepted

---

## Context

WaveTerm's existing `"preview"` block handles text files, markdown, CSV,
directories, images, PDFs (via browser iframe), and video/audio. It does
not support Word (.docx), Excel (.xlsx), PowerPoint (.pptx), or other
Office document formats. See
[research-current-state.md](./research-current-state.md) for the full
analysis.

## Decision

Enhance the existing `"preview"` block by adding new specialized views for
document formats. Do **not** create a new block type — reuse the existing
preview infrastructure (file detection, MIME type resolution, streaming,
directory navigation, bookmarks).

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Preview Block (existing, "preview")                        │
│                                                             │
│  PreviewModel.getSpecializedView(mimeType)                  │
│    │                                                        │
│    ├── streaming ────► StreamingPreview (existing)          │
│    │   ├── PDF ───────► PdfPreview (NEW, replaces iframe)   │
│    │   ├── image ─────► ImagePreview (existing + enhanced)  │
│    │   ├── video ─────► (existing)                          │
│    │   └── audio ─────► (existing)                          │
│    ├── markdown ─────► MarkdownPreview (existing, no change)│
│    ├── codeedit ─────► CodeEditPreview (existing, no change)│
│    ├── csv ──────────► CSVView (existing, no change)        │
│    ├── directory ────► DirectoryPreview (existing, no change)│
│    ├── docx ─────────► DocxPreview (NEW)                    │
│    ├── xlsx ─────────► XlsxPreview (NEW)                    │
│    └── pptx ─────────► PptxPreview (NEW)                    │
│                                                             │
│  SpecializedViewMap (extended)                              │
└─────────────────────────────────────────────────────────────┘
```

### Key decisions

#### 1. Enhance existing block, not new block type

**Rationale:**
- All infrastructure already exists: file detection, MIME type resolution,
  streaming endpoint, directory navigation, bookmarks, error handling
- Adding to `SpecializedViewMap` is a minimal change (one line per format)
- Users don't need to learn a new block type — they just open a file and
  the right renderer is selected automatically
- No changes to `blockregistry.ts` — `"preview"` already registered

#### 2. Replace PDF iframe with react-pdf

**Rationale:**
- Current PDF viewer uses browser's native viewer via `<iframe>` — no
  control over UI, no page navigation, no search, no thumbnails
- `react-pdf` (wraps PDF.js, MIT) gives full control: page navigation,
  zoom, search, text selection, thumbnail sidebar
- PDF.js is the industry standard (24M weekly downloads, Apache-2.0)
- Lazy-load the library so it only affects bundle size when a PDF is opened

#### 3. DOCX via docx-preview

**Rationale:**
- `docx-preview` (Apache-2.0) provides visual fidelity — renders DOCX
  with page breaks, fonts, styles, images
- `mammoth.js` (BSD-2-Clause) is an alternative for semantic content
  extraction but loses visual formatting
- Use `docx-preview` for preview, fall back to `mammoth` for very large
  documents where fidelity isn't critical

#### 4. XLSX via SheetJS + existing CSVView

**Rationale:**
- `SheetJS` (xlsx, Apache-2.0) parses XLSX into JSON data
- WaveTerm already has `CSVView` component using `@tanstack/react-table`
- Parse XLSX with SheetJS → feed data into CSVView → reuse all existing
  table features (sorting, resizing, keyboard navigation)
- No need for a heavy spreadsheet UI (Univer, Handsontable) for preview
- Formula support is not needed for preview (show values, not formulas)

#### 5. PPTX via @aiden0z/pptx-renderer

**Rationale:**
- `@aiden0z/pptx-renderer` (Apache-2.0) is the most mature PPTX renderer
- High-fidelity HTML/SVG rendering: 187+ shapes, 134+ SmartArt layouts
- 452+ visual regression test cases
- Active development, 220K weekly downloads

#### 6. Lazy-load all new libraries

**Rationale:**
- PDF.js (~2.5MB), docx-preview (~500KB), SheetJS (~1MB), pptx-renderer
  (~800KB) — total ~4.8MB if loaded upfront
- Use dynamic `import()` to load libraries only when the corresponding
  format is previewed
- No impact on initial bundle size or startup time

```typescript
// Example: lazy-load docx-preview
async function DocxPreview({ model }: SpecializedViewProps) {
    const { renderAsync } = await import("docx-preview");
    // ... render
}
```

#### 7. MIME type detection for Office formats

Add to `getSpecializedView()` in `preview-model.tsx`:

```typescript
// Office document types
const officeMimeTypes = {
    docx: "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    xlsx: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    pptx: "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    // Legacy formats
    doc: "application/msword",
    xls: "application/vnd.ms-excel",
    ppt: "application/vnd.ms-powerpoint",
    // OpenDocument
    odt: "application/vnd.oasis.opendocument.text",
    ods: "application/vnd.oasis.opendocument.spreadsheet",
    odp: "application/vnd.oasis.opendocument.presentation",
};
```

**Open:** Legacy formats (.doc, .xls, .ppt) and OpenDocument formats (.odt,
.ods, .odp) may not be supported by the chosen libraries. Need to verify
and potentially fall back to "not supported" message for these.

#### 8. File size limits

| Format | Proposed limit | Rationale |
|--------|---------------|-----------|
| PDF | 50 MB | PDF.js can handle large files with lazy page loading |
| DOCX | 20 MB | docx-preview renders to DOM, large files are slow |
| XLSX | 10 MB | SheetJS parses in memory, same as current CSV limit |
| PPTX | 20 MB | pptx-renderer renders slides, moderate size |

Current `MaxFileSize` (10MB) applies to non-streaming types. Streaming types
(PDF, video, audio, image) have no size limit. Need to adjust limits per
format.

### New specialized views

#### DocxPreview

**File:** `frontend/app/view/preview/preview-docx.tsx` (new)

```typescript
// Pseudocode
async function DocxPreview({ model }: SpecializedViewProps) {
    const { renderAsync } = await import("docx-preview");
    const containerRef = useRef<HTMLDivElement>(null);
    const fileData = useAtomValue(model.fileBinaryData); // new atom

    useEffect(() => {
        if (fileData && containerRef.current) {
            renderAsync(fileData, containerRef.current, null, {
                className: "docx",
                inWrapper: true,
                breakPages: true,
            });
        }
    }, [fileData]);

    return <div ref={containerRef} className="docx-preview-container" />;
}
```

**Open:** Need a `fileBinaryData` atom in PreviewModel for binary file
content (current `fileContent` is string-based for text files).

#### XlsxPreview

**File:** `frontend/app/view/preview/preview-xlsx.tsx` (new)

```typescript
// Pseudocode
async function XlsxPreview({ model }: SpecializedViewProps) {
    const XLSX = await import("xlsx");
    const fileData = useAtomValue(model.fileBinaryData);
    const [sheetNames, setSheetNames] = useState<string[]>([]);
    const [activeSheet, setActiveSheet] = useState<string>("");
    const [sheetData, setSheetData] = useState<any[][]>([]);

    useEffect(() => {
        if (fileData) {
            const workbook = XLSX.read(fileData, { type: "array" });
            setSheetNames(workbook.SheetNames);
            setActiveSheet(workbook.SheetNames[0]);
        }
    }, [fileData]);

    useEffect(() => {
        if (activeSheet && workbook) {
            const worksheet = workbook.Sheets[activeSheet];
            const data = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
            setSheetData(data);
        }
    }, [activeSheet]);

    return (
        <div>
            <SheetTabs names={sheetNames} active={activeSheet} onSelect={setActiveSheet} />
            <CSVView content={csvString} readonly={true} />
        </div>
    );
}
```

**Key:** Reuse existing `CSVView` component for the actual table rendering.
Only the parsing differs (SheetJS instead of papaparse).

#### PptxPreview

**File:** `frontend/app/view/preview/preview-pptx.tsx` (new)

```typescript
// Pseudocode
async function PptxPreview({ model }: SpecializedViewProps) {
    const { PptxViewer } = await import("@aiden0z/pptx-renderer");
    const containerRef = useRef<HTMLDivElement>(null);
    const fileData = useAtomValue(model.fileBinaryData);

    useEffect(() => {
        if (fileData && containerRef.current) {
            PptxViewer.open(fileData, containerRef.current, {
                listOptions: { windowed: true }
            });
        }
    }, [fileData]);

    return <div ref={containerRef} className="pptx-preview-container" />;
}
```

#### PdfPreview (replaces iframe in StreamingPreview)

**File:** `frontend/app/view/preview/preview-pdf.tsx` (new)

```typescript
// Pseudocode
async function PdfPreview({ model }: SpecializedViewProps) {
    const { Document, Page, pdfjs } = await import("react-pdf");
    pdfjs.GlobalWorkerOptions.workerSrc = /* configure */;
    const streamingUrl = useAtomValue(model.streamingUrl);
    const [numPages, setNumPages] = useState(0);
    const [pageNumber, setPageNumber] = useState(1);

    return (
        <div className="pdf-preview-container">
            <PdfToolbar
                pageNumber={pageNumber}
                numPages={numPages}
                onPageChange={setPageNumber}
            />
            <Document file={streamingUrl} onLoadSuccess={({ numPages }) => setNumPages(numPages)}>
                <Page pageNumber={pageNumber} />
            </Document>
        </div>
    );
}
```

### Changes to existing files

| File | Change |
|------|--------|
| `preview-model.tsx` | Add Office MIME types to `getSpecializedView()`, add `fileBinaryData` atom, adjust file size limits |
| `preview.tsx` | Add new entries to `SpecializedViewMap` |
| `preview-streaming.tsx` | Replace PDF iframe with `PdfPreview` component |
| `package.json` | Add: `react-pdf`, `pdfjs-dist`, `docx-preview`, `xlsx`, `@aiden0z/pptx-renderer` |

### No changes needed

- `blockregistry.ts` — `"preview"` already registered
- `preview-markdown.tsx` — markdown rendering is already excellent
- `csvview.tsx` — reused as-is for XLSX
- `preview-directory.tsx` — no changes
- `preview-edit.tsx` — no changes
- `previewenv.ts` — may need new RPC for binary file data (Open)

### Patch implications

This enhancement modifies files in `PATCHED_FILES`:
- `frontend/app/view/preview/preview-model.tsx` — already patched? Need to check
- `frontend/app/view/preview/preview.tsx` — already patched? Need to check

**Open:** Need to verify if these files are in `PATCHED_FILES` and whether
the changes will conflict with the sync workflow. If they do, this should
be developed as a patch file (like the SSH PRs) rather than direct commits
to `dev.patch`.

### Implementation plan

#### Phase 1: Infrastructure

- Add `fileBinaryData` atom to `PreviewModel` for binary file content
- Add binary file RPC to `previewenv.ts` (if needed)
- Add Office MIME type constants
- Update `getSpecializedView()` with new format branches
- Update file size limits per format

#### Phase 2: PDF enhancement

- Install `react-pdf` + `pdfjs-dist`
- Create `preview-pdf.tsx` with page navigation, zoom, search
- Replace iframe in `preview-streaming.tsx` with `PdfPreview`
- Configure PDF.js worker for Electron/Vite

#### Phase 3: DOCX support

- Install `docx-preview`
- Create `preview-docx.tsx`
- Add to `SpecializedViewMap`
- Test with various Word documents

#### Phase 4: XLSX support

- Install `xlsx` (SheetJS)
- Create `preview-xlsx.tsx` with sheet tabs + CSVView reuse
- Add to `SpecializedViewMap`
- Test with various Excel files

#### Phase 5: PPTX support

- Install `@aiden0z/pptx-renderer`
- Create `preview-pptx.tsx`
- Add to `SpecializedViewMap`
- Test with various PowerPoint files

#### Phase 6: Image enhancements (optional)

- Add HEIC support via `heic-to` (lazy-loaded)
- Add `image-orientation: from-image` CSS for EXIF rotation
- Add image metadata display (dimensions, format, file size)
- Consider gallery view for directories of images

### Security considerations

1. **docx-preview renders to DOM** — the HTML output should be sanitized.
   docx-preview renders to a container element. Consider wrapping in a
   sandboxed iframe or sanitizing the output.
2. **SheetJS parses in memory** — no DOM injection risk, but large files
   can cause memory pressure. File size limits mitigate this.
3. **pptx-renderer renders to HTML/SVG** — same sanitization concern as
   docx-preview.
4. **PDF.js renders to canvas** — no DOM injection risk. Safest option.
5. **All libraries are client-side** — no file content sent to external
   servers (unlike Google Docs Viewer or Office Online Viewer).

### Open questions

See [open-questions.md](./open-questions.md) for tracked questions.

## Sources

- [Research: current state](./research-current-state.md)
- [Library survey](./library-survey.md)
