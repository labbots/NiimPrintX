# Later Scope

These requirements remain part of the intended product but are not prerequisites
for the first complete create-preview-print workflow. Moving an item into an
earlier delivery file is a product-priority change and should include acceptance
criteria for the affected vertical slice.

## Application Interfaces

7. [ ] The application contains a welcome screen with new label, recent documents, templates, last printer, and recovery actions.
8. [ ] The application contains a native shell that packages the local backend and browser interface as one desktop application.

## Label Artboard

6. [ ] The editor contains zoom, fit-to-label, pan, rulers, grid, and physical scale.
7. [ ] The editor contains snapping to label center, edges, margins, guides, and nearby elements.
8. [ ] The editor contains pointer and keyboard movement, resizing, rotation, duplication, and deletion.
9. [ ] The editor contains alignment, distribution, z-order, grouping, locking, and multi-selection.
12. [ ] The editor contains copy and paste within a document and between documents.
13. [ ] The editor contains overflow and minimum-readable-size warnings before printing.

## Text Elements

7. [ ] Text elements contain automatic fit, wrapping rules, and minimum-readable-size warnings.
8. [ ] Text elements contain reusable styles and recently used fonts.

## Images, Icons, and Shapes

3. [ ] The editor contains a bundled category-based raster icon library.
4. [ ] The icon library contains computer, emoji, food, misc, organize, people, social, and unicorn categories.
5. [ ] The asset library contains search, tags, favorites, and recently used assets.
6. [ ] Image elements contain crop, fit, fill, proportional resize, rotation, flip, and reset controls.
7. [ ] Image elements contain invert, contrast, threshold, and dithering controls with monochrome previews.
8. [ ] The editor contains rectangle, ellipse, line, arrow, and other basic shape elements.
9. [ ] The editor contains drag-and-drop image import.
10. [ ] The asset library contains validated thumbnails that match final monochrome output.

## Smart Content

1. [ ] The editor contains QR code elements with content and printability validation.
2. [ ] The editor contains barcode elements with symbology-specific validation.
3. [ ] The editor contains date and time elements with configurable formatting.
4. [ ] The editor contains incrementing counter and serial-number elements.
5. [ ] The editor contains CSV and TSV data merge with row preview and batch validation.
6. [ ] The editor contains variable fields whose resolved values are visible before printing.

## Documents and Recovery

6. [ ] The application contains autosave and crash recovery for unsaved documents.
8. [ ] The application contains recent documents with missing-file handling.
10. [ ] The operating-system file association contains opening of the supplied document path.

## Templates

1. [ ] The application contains built-in templates for cable labels, addresses, bins, folders, QR labels, dates, and asset tags.
2. [ ] The application contains user templates with thumbnail, tags, label size, and printer compatibility.
3. [ ] The template library contains search, categories, favorites, and recently used templates.
4. [ ] The application contains explicit template import and export for offline sharing.

## Print History and Diagnostics

1. [ ] The application contains print history with document preview, printer, settings, timestamp, progress, and result.
2. [ ] Print history contains safe reprint with current printer and label validation.
3. [ ] Failed jobs contain save-for-later and retry actions.
4. [ ] The application contains a diagnostics bundle with sanitized logs, environment details, and protocol summary.
5. [ ] User-facing failures contain what happened, document safety, printer state, and the next safe action.

## Onboarding, Accessibility, and Language

8. [ ] The interface contains Czech and English localization.

## Distribution and Platform Integration

1. [ ] The repository contains separate application and CLI packages for Linux, macOS, and Windows.
2. [ ] The repository contains tag-triggered Linux, macOS, and Windows release workflows for the target application.
3. [ ] The macOS packaging contains DMG creation for the target application.
4. [ ] The Linux packaging contains desktop entry, AppStream metadata, and document MIME metadata for the target application.
5. [ ] Release verification contains automated package smoke tests on every supported platform.
6. [ ] The application contains one installer that starts the local backend and opens the browser or native shell.
7. [ ] Releases contain aligned application versions, signed artifacts, and document migration checks.

## Optional Integrations

1. [ ] The application contains trusted local-network mode that is authenticated and disabled by default.
2. [ ] The application contains multi-printer batch routing.
3. [ ] The application contains plugin providers for external data sources.
4. [ ] The application contains optional end-to-end encrypted cloud synchronization without raw BLE access.
5. [ ] The application contains an experimental direct Web Bluetooth mode without making it the only supported print path.
