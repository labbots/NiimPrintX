# Editor Core

This file defines the minimum useful editor. The logical document and edit
operations are the source of truth; SVG is their initial editable projection and
the backend renderer remains authoritative for final monochrome output.

## Review Sequence

1. Versioned logical document, immutable operations, selection, and undo/redo.
2. Physical label, printable bounds, safe areas, and label-size transitions.
3. Text creation, editing, movement, resize, and styling.
4. Basic image import, fitting, movement, and resize.
5. Layers synchronized with the artboard.
6. Backend composition, export, preview, and stale/error states.
7. Save/open surface, unsaved-change protection, and shortcut help.

Each slice must support pointer and keyboard use where the interaction applies.
Printer reconnects and preview failures must not discard editor state.

## Printer Models and Label Setup

5. [ ] The artboard contains millimetre-to-pixel conversion based on the selected printer DPI.
9. [ ] The label setup contains safe area, printable area, margins, bleed, pixel dimensions, and overflow visualization.
10. [ ] The label-size change workflow contains preserve, scale, resize, or start-over choices without silently losing the design.

## Label Artboard

1. [ ] The editor contains a white physical-label boundary on the artboard.
2. [ ] The editor contains a centered dashed print-area boundary inside the physical label.
3. [ ] The editor contains pointer selection, movement, resizing, and deletion for text elements.
4. [ ] The editor contains pointer selection, movement, independent width/height resizing, and deletion for image elements.
5. [ ] The editor contains one selection model shared by all element types.
10. [ ] The editor contains layers and an object list synchronized with artboard selection.
11. [ ] The editor contains undo and redo for every document-changing operation.
14. [ ] New elements appear inside the printable area at a useful centered position.

## Text Elements

1. [ ] The editor contains multiline text elements rendered on the label.
2. [ ] Text controls contain font family, font size, kerning, bold, italic, and underline settings.
3. [ ] Text controls contain a sample preview of the selected font properties.
5. [ ] Existing text elements contain content and style updates.
6. [ ] Text elements contain horizontal and vertical alignment within their bounds.

## Images, Icons, and Shapes

1. [ ] The editor contains PNG, JPEG, BMP, and GIF image import through a file picker.
2. [ ] Imported images contain RGBA conversion and proportional fitting to the physical-label boundary.

## Preview and Rasterization

1. [ ] The graphical editor contains composition of text and image elements into a label-sized raster.
2. [ ] The graphical editor contains PNG export of the composed label.
3. [ ] The graphical editor contains a popup label preview before printing.

## Documents and Recovery

1. [ ] The graphical editor contains Save and Open actions for legacy `.niim` documents.
7. [ ] The application contains an unsaved-change indicator and confirmation before destructive navigation.

## Onboarding, Accessibility, and Language

5. [ ] The editor contains keyboard shortcuts and discoverable shortcut help.
