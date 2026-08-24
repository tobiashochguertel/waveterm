# Preview Widget — Documentation Index

**Branch:** `feature/browser-widget`
**Status:** Research & design phase (not yet implemented)

## Documents

| Document | Status | Description |
|----------|--------|-------------|
| [research-current-state.md](./research-current-state.md) | Complete | Analysis of existing preview block, what's supported, what's missing |
| [adr-enhance-preview-block.md](./adr-enhance-preview-block.md) | Complete | Architecture decision: enhance existing `"preview"` block with new specialized views |
| [library-survey.md](./library-survey.md) | Complete | Survey of JS/TS libraries for PDF, DOCX, XLSX, PPTX, image rendering |
| [component-design.md](./component-design.md) | Open | React component structure for new specialized views |
| [open-questions.md](./open-questions.md) | Open | Tracked open questions with status lifecycle |

## Summary

The preview widget project enhances WaveTerm's existing `"preview"` block
to support document formats not currently handled: Word (.docx), Excel
(.xlsx), PowerPoint (.pptx), and improved PDF rendering. Markdown and image
preview already work well.

The approach is to add new **specialized views** to the existing preview
block's `SpecializedViewMap`, rather than creating a new block type. This
reuses all existing infrastructure (file detection, MIME type resolution,
streaming, directory navigation, bookmarks).

## Relationship to browser widget

This is a separate widget idea from the
[browser widget](../browser-widget/README.md). Both are on the
`feature/browser-widget` branch but are independent projects.
