# Component Design — Preview Widget Enhancements

**Branch:** `feature/browser-widget`
**Date:** 2026-08-24
**Status:** Open (preliminary structure, needs validation during implementation)

---

## Overview

New specialized view components for the existing `"preview"` block. Each
is a self-contained React component that receives file data from
`PreviewModel` and renders it. All new libraries are lazy-loaded.

---

## File structure

```
frontend/app/view/preview/
├── preview-model.tsx          # Modified: add MIME types, fileBinaryData atom
├── preview.tsx                # Modified: add new SpecializedViewMap entries
├── preview-streaming.tsx      # Modified: replace PDF iframe with PdfPreview
├── preview-pdf.tsx            # NEW: PDF viewer (react-pdf)
├── preview-docx.tsx           # NEW: Word document viewer (docx-preview)
├── preview-xlsx.tsx           # NEW: Excel viewer (SheetJS + CSVView)
├── preview-pptx.tsx           # NEW: PowerPoint viewer (pptx-renderer)
├── preview-pdf.scss           # NEW: PDF viewer styles
├── preview-docx.scss          # NEW: DOCX viewer styles
├── preview-xlsx.scss          # NEW: XLSX viewer styles
└── preview-pptx.scss          # NEW: PPTX viewer styles
```

**Status:** Open — exact file structure may change during implementation.

---

## PreviewModel changes

### New atoms

```typescript
// Binary file data for non-text formats (DOCX, XLSX, PPTX)
fileBinaryData: Atom<Promise<ArrayBuffer | null>>;

// PDF-specific state
pdfPageNumber: PrimitiveAtom<number>;
pdfNumPages: PrimitiveAtom<number>;
pdfZoom: PrimitiveAtom<number>;
pdfSearchQuery: PrimitiveAtom<string>;

// XLSX-specific state
xlsxSheetNames: PrimitiveAtom<string[]>;
xlsxActiveSheet: PrimitiveAtom<string>;
```

### Updated getSpecializedView()

```typescript
async getSpecializedView(getFn: Getter): Promise<{ specializedView?: string }> {
    const mimeType = await getFn(this.fileMimeType);
    // ... existing checks ...

    // NEW: Office document types
    if (mimeType == "application/vnd.openxmlformats-officedocument.wordprocessingml.document") {
        return { specializedView: "docx" };
    }
    if (mimeType == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet") {
        return { specializedView: "xlsx" };
    }
    if (mimeType == "application/vnd.openxmlformats-officedocument.presentationml.presentation") {
        return { specializedView: "pptx" };
    }

    // NEW: PDF gets its own specialized view (not streaming)
    if (mimeType == "application/pdf") {
        return { specializedView: "pdf" };
    }

    // ... existing checks ...
}
```

### Updated SpecializedViewMap

```typescript
const SpecializedViewMap = {
    streaming: StreamingPreview,    // video, audio, image (PDF removed)
    pdf: PdfPreview,                // NEW
    markdown: MarkdownPreview,      // existing
    codeedit: CodeEditPreview,      // existing
    csv: CSVViewPreview,            // existing
    directory: DirectoryPreview,    // existing
    docx: DocxPreview,              // NEW
    xlsx: XlsxPreview,              // NEW
    pptx: PptxPreview,              // NEW
};
```

**Status:** Open — need to verify that `fileBinaryData` can be fetched via
existing RPC or if a new RPC endpoint is needed.

---

## Component: PdfPreview

**Status:** Open — preliminary design

```typescript
// preview-pdf.tsx

import { lazy, Suspense } from "react";
import type { SpecializedViewProps } from "./preview";

// Lazy-load react-pdf
const Document = lazy(() => import("react-pdf").then(m => ({ default: m.Document })));
const Page = lazy(() => import("react-pdf").then(m => ({ default: m.Page })));

function PdfToolbar({ pageNumber, numPages, zoom, onPageChange, onZoomChange }) {
    return (
        <div className="pdf-toolbar">
            <button onClick={() => onPageChange(pageNumber - 1)} disabled={pageNumber <= 1}>
                <i className="fa-sharp fa-chevron-left" />
            </button>
            <span>{pageNumber} / {numPages}</span>
            <button onClick={() => onPageChange(pageNumber + 1)} disabled={pageNumber >= numPages}>
                <i className="fa-sharp fa-chevron-right" />
            </button>
            <button onClick={() => onZoomChange(zoom + 0.25)}>
                <i className="fa-sharp fa-plus" />
            </button>
            <span>{Math.round(zoom * 100)}%</span>
            <button onClick={() => onZoomChange(zoom - 0.25)}>
                <i className="fa-sharp fa-minus" />
            </button>
        </div>
    );
}

function PdfPreview({ model }: SpecializedViewProps) {
    const streamingUrl = useAtomValue(model.streamingUrl);
    const [numPages, setNumPages] = useState(0);
    const [pageNumber, setPageNumber] = useAtom(model.pdfPageNumber);
    const [zoom, setZoom] = useAtom(model.pdfZoom);

    // Configure PDF.js worker (Open: how to configure for Electron/Vite?)
    useEffect(() => {
        import("react-pdf").then(({ pdfjs }) => {
            pdfjs.GlobalWorkerOptions.workerSrc = /* ... */;
        });
    }, []);

    return (
        <div className="pdf-preview">
            <PdfToolbar
                pageNumber={pageNumber}
                numPages={numPages}
                zoom={zoom}
                onPageChange={setPageNumber}
                onZoomChange={setZoom}
            />
            <div className="pdf-content">
                <Suspense fallback={<CenteredDiv>Loading PDF viewer...</CenteredDiv>}>
                    <Document file={streamingUrl} onLoadSuccess={({ numPages }) => setNumPages(numPages)}>
                        <Page pageNumber={pageNumber} scale={zoom} />
                    </Document>
                </Suspense>
            </div>
        </div>
    );
}
```

**Open items:**
- [ ] PDF.js worker configuration for Electron + Vite build system
- [ ] Text search within PDF
- [ ] Thumbnail sidebar
- [ ] Text selection and copy
- [ ] Continuous scroll vs single page view
- [ ] Print support
- [ ] Loading progress indicator

---

## Component: DocxPreview

**Status:** Open — preliminary design

```typescript
// preview-docx.tsx

function DocxPreview({ model }: SpecializedViewProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const fileData = useAtomValue(model.fileBinaryData);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!fileData || !containerRef.current) return;

        setLoading(true);
        setError(null);

        import("docx-preview").then(({ renderAsync }) => {
            renderAsync(fileData, containerRef.current, null, {
                className: "docx",
                inWrapper: true,
                breakPages: true,
                ignoreFonts: false,
                experimental: true,
            })
            .then(() => setLoading(false))
            .catch((err) => {
                setError(err.message);
                setLoading(false);
            });
        });
    }, [fileData]);

    if (error) return <CenteredDiv>Error rendering document: {error}</CenteredDiv>;
    if (loading) return <CenteredDiv>Loading document...</CenteredDiv>;

    return <div ref={containerRef} className="docx-preview-container" />;
}
```

**Open items:**
- [ ] HTML sanitization of docx-preview output
- [ ] Font handling (embedded fonts vs system fonts)
- [ ] Page navigation for multi-page documents
- [ ] Zoom support
- [ ] Large document performance (virtualized rendering?)
- [ ] mammoth.js fallback for large documents

---

## Component: XlsxPreview

**Status:** Open — preliminary design

```typescript
// preview-xlsx.tsx

function SheetTabs({ names, active, onSelect }) {
    return (
        <div className="xlsx-sheet-tabs">
            {names.map(name => (
                <button
                    key={name}
                    className={name === active ? "active" : ""}
                    onClick={() => onSelect(name)}
                >
                    {name}
                </button>
            ))}
        </div>
    );
}

function XlsxPreview({ model }: SpecializedViewProps) {
    const fileData = useAtomValue(model.fileBinaryData);
    const [workbook, setWorkbook] = useState<any>(null);
    const [sheetNames, setSheetNames] = useState<string[]>([]);
    const [activeSheet, setActiveSheet] = useState("");
    const [csvContent, setCsvContent] = useState("");

    // Parse workbook
    useEffect(() => {
        if (!fileData) return;
        import("xlsx").then((XLSX) => {
            const wb = XLSX.read(fileData, { type: "array" });
            setWorkbook(wb);
            setSheetNames(wb.SheetNames);
            setActiveSheet(wb.SheetNames[0]);
        });
    }, [fileData]);

    // Convert active sheet to CSV for CSVView
    useEffect(() => {
        if (!workbook || !activeSheet) return;
        import("xlsx").then((XLSX) => {
            const worksheet = workbook.Sheets[activeSheet];
            const csv = XLSX.utils.sheet_to_csv(worksheet);
            setCsvContent(csv);
        });
    }, [workbook, activeSheet]);

    return (
        <div className="xlsx-preview">
            <SheetTabs names={sheetNames} active={activeSheet} onSelect={setActiveSheet} />
            <CSVView content={csvContent} readonly={true} filename={activeSheet} />
        </div>
    );
}
```

**Open items:**
- [ ] Formula display (show values, not formulas — SheetJS does this by default)
- [ ] Cell formatting (colors, borders, number formats) — SheetJS doesn't preserve these
- [ ] Chart rendering — not supported by SheetJS
- [ ] Very large spreadsheets (10MB+ with many sheets)
- [ ] .xls (legacy) format support

---

## Component: PptxPreview

**Status:** Open — preliminary design

```typescript
// preview-pptx.tsx

function PptxPreview({ model }: SpecializedViewProps) {
    const containerRef = useRef<HTMLDivElement>(null);
    const fileData = useAtomValue(model.fileBinaryData);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (!fileData || !containerRef.current) return;

        setLoading(true);
        setError(null);

        import("@aiden0z/pptx-renderer").then(({ PptxViewer, RECOMMENDED_ZIP_LIMITS }) => {
            PptxViewer.open(fileData, containerRef.current, {
                zipLimits: RECOMMENDED_ZIP_LIMITS,
                listOptions: { windowed: true },
            })
            .then(() => setLoading(false))
            .catch((err) => {
                setError(err.message);
                setLoading(false);
            });
        });
    }, [fileData]);

    if (error) return <CenteredDiv>Error rendering presentation: {error}</CenteredDiv>;
    if (loading) return <CenteredDiv>Loading presentation...</CenteredDiv>;

    return <div ref={containerRef} className="pptx-preview-container" />;
}
```

**Open items:**
- [ ] Slide navigation UI (previous/next, slide selector)
- [ ] Fullscreen presentation mode
- [ ] Speaker notes display
- [ ] Animation support
- [ ] .ppt (legacy) format support
- [ ] HTML sanitization of rendered output

---

## Lazy loading strategy

All new libraries are loaded via dynamic `import()`:

```typescript
// In each component:
const { renderAsync } = await import("docx-preview");
const XLSX = await import("xlsx");
const { PptxViewer } = await import("@aiden0z/pptx-renderer");
const { Document, Page, pdfjs } = await import("react-pdf");
```

This ensures:
- No impact on initial bundle size
- Library code is only loaded when the corresponding format is previewed
- Vite automatically code-splits these imports into separate chunks

**Open:** Need to configure Vite to handle the PDF.js worker and WASM files
(for heic-to if added).

---

## Open items

- [ ] `fileBinaryData` atom: how to fetch binary file content via RPC?
  Existing `FileReadCommand` returns string — need binary variant or
  use the streaming endpoint with `fetch()`
- [ ] PDF.js worker path configuration for Electron + Vite
- [ ] HTML sanitization for docx-preview and pptx-renderer output
- [ ] Vite config for code-splitting and WASM loading
- [ ] File size limits per format (PDF: 50MB, DOCX: 20MB, XLSX: 10MB, PPTX: 20MB)
- [ ] Error handling for corrupt/malformed files
- [ ] Loading indicators for large files
- [ ] Patch file strategy: should these changes be a `.patch` file or
  direct commits to `dev.patch`?
