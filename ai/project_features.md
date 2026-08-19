# FEATURES -- NiimStudio

> Product feature checklist for implementation work. Architecture and technology
> decisions are defined in `ai/project_context.md`.

**Legend:** `[x]` Implemented and retained | `[ ]` Missing, incomplete, or scheduled for replacement

Every item describes the application in its intended state. The checkbox alone
expresses whether that complete behavior exists in an implementation retained
by the target application.

## Application Interfaces

1. [ ] The application contains a graphical label editor for creating and printing labels.
2. [x] The application contains a command-line interface with `print` and `info` commands.
3. [x] The application contains local design and printing workflows that require no cloud account.
4. [ ] The graphical editor contains printer setup, label setup, editing, image export, preview, and print controls in one window.
5. [ ] The application contains a React and TypeScript browser interface backed by the local Python service.
6. [ ] The application contains a responsive workbench with element tools, artboard, inspector, layers, printer state, and print action.
7. [ ] The application contains a welcome screen with new label, recent documents, templates, last printer, and recovery actions.
8. [ ] The application contains a native shell that packages the local backend and browser interface as one desktop application.

## Command-Line Interface

1. [x] The CLI contains help output and configurable verbose logging.
2. [x] The CLI print command contains image path, printer model, density, copy count, rotation, and pixel offset options.
3. [x] The CLI print command contains raster image loading and model-dependent print-width validation.
4. [x] The CLI print command contains automatic printer discovery, connection, printing, and disconnection.
5. [x] The CLI info command contains printer serial number, software version, and hardware version queries.
6. [x] The CLI contains typed failures, actionable diagnostics, and non-zero exit codes for unsuccessful operations.
7. [ ] The CLI contains the same capability, validation, rendering, and print-job services as the browser interface.
8. [ ] The CLI contains explicit printer selection when more than one matching printer is available.

## Printer Models and Label Setup

1. [ ] The graphical editor contains target printer selection for D110, D11, D11_H, D101, and B18 models.
2. [x] The CLI contains target printer selection for B1, B18, B21, D11, D11_H, and D110 models.
3. [ ] The graphical editor contains configured physical label sizes and DPI values for each listed model.
4. [ ] The graphical editor contains a label-size selector that updates the artboard dimensions.
5. [ ] The artboard contains millimetre-to-pixel conversion based on the selected printer DPI.
6. [ ] The application contains one authoritative capability registry shared by UI, CLI, renderer, API, and printer services.
7. [ ] The capability registry contains complete model identity, DPI, printable dimensions, label sizes, density limits, orientation rules, and feature flags.
8. [ ] The label selector contains physical label cards with dimensions, orientation, compatibility, and realistic previews.
9. [ ] The label setup contains safe area, printable area, margins, bleed, pixel dimensions, and overflow visualization.
10. [ ] The label-size change workflow contains preserve, scale, resize, or start-over choices without silently losing the design.

## Printer Discovery and Connection

1. [x] The application contains BLE printer discovery through Bleak.
2. [ ] The application contains discovery that uses a case-insensitive model-name prefix only as a fallback and presents ambiguous matches for selection.
3. [ ] The graphical editor contains manual Connect and Disconnect actions.
4. [ ] The graphical editor contains a connected or disconnected status indicator.
5. [x] The printer client contains connect, disconnect, GATT write, and notification subscription operations.
6. [ ] The printer client contains periodic heartbeat polling while the graphical editor is connected and idle.
7. [ ] The printer setup contains a cancellable scan and a selectable list of all discovered printers.
8. [ ] The discovered printer list contains stable identity, friendly name, model confidence, signal strength, and last-seen time.
9. [ ] The connection workflow contains explicit idle, scanning, connecting, connected, reconnecting, disconnecting, and failed states.
10. [ ] The application contains remembered printer selection without silently printing to an unknown printer.
11. [ ] The application contains automatic reconnection with bounded retries and a user-visible recovery action.
12. [ ] The printer setup contains platform-specific Bluetooth permission and troubleshooting guidance.

## Printer Status and Protocol

1. [x] The printer protocol contains packet framing, payload length, XOR checksum generation, and checksum validation.
2. [x] The printer client contains printer information, RFID, heartbeat, label type, density, print start/end, page start/end, dimensions, quantity, raster row, and print status commands.
3. [x] The heartbeat parser contains lid, power, paper, and RFID-read values for supported response variants.
4. [x] The printer client contains discovery of a GATT characteristic with read, write-without-response, and notification properties.
5. [ ] The graphical interface contains battery, paper, lid, RFID, signal, and readiness status where the printer provides it.
6. [x] The command channel contains serialized requests, response-command validation, response correlation, and fragmented notification buffering.
7. [x] Every printer operation contains a hard deadline, cancellation path, and deterministic resource cleanup.
8. [ ] Printer failures contain typed causes instead of `None` or an unrelated later exception.
9. [ ] The application contains fake BLE transports for successful, fragmented, timeout, disconnect, invalid-response, lid-open, and paper-out scenarios.

## Label Artboard

1. [ ] The editor contains a white physical-label boundary on the artboard.
2. [ ] The editor contains a centered dashed print-area boundary inside the physical label.
3. [ ] The editor contains pointer selection, movement, resizing, and deletion for text elements.
4. [ ] The editor contains pointer selection, movement, independent width/height resizing, and deletion for image elements.
5. [ ] The editor contains one selection model shared by all element types.
6. [ ] The editor contains zoom, fit-to-label, pan, rulers, grid, and physical scale.
7. [ ] The editor contains snapping to label center, edges, margins, guides, and nearby elements.
8. [ ] The editor contains pointer and keyboard movement, resizing, rotation, duplication, and deletion.
9. [ ] The editor contains alignment, distribution, z-order, grouping, locking, and multi-selection.
10. [ ] The editor contains layers and an object list synchronized with artboard selection.
11. [ ] The editor contains undo and redo for every document-changing operation.
12. [ ] The editor contains copy and paste within a document and between documents.
13. [ ] The editor contains overflow and minimum-readable-size warnings before printing.
14. [ ] New elements appear inside the printable area at a useful centered position.

## Text Elements

1. [ ] The editor contains multiline text elements rendered on the label.
2. [ ] Text controls contain font family, font size, kerning, bold, italic, and underline settings.
3. [ ] Text controls contain a sample preview of the selected font properties.
4. [ ] The text tool contains font families discovered from the ImageMagick font registry.
5. [ ] Existing text elements contain content and style updates.
6. [ ] Text elements contain horizontal and vertical alignment within their bounds.
7. [ ] Text elements contain automatic fit, wrapping rules, and minimum-readable-size warnings.
8. [ ] Text elements contain reusable styles and recently used fonts.
9. [ ] Text rendering contains deterministic font resolution shared by preview and print output.

## Images, Icons, and Shapes

1. [ ] The editor contains PNG, JPEG, BMP, and GIF image import through a file picker.
2. [ ] Imported images contain RGBA conversion and proportional fitting to the physical-label boundary.
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

## Preview and Rasterization

1. [ ] The graphical editor contains composition of text and image elements into a label-sized raster.
2. [ ] The graphical editor contains PNG export of the composed label.
3. [ ] The graphical editor contains a popup label preview before printing.
4. [x] The printer encoder contains grayscale conversion, inversion, one-bit conversion, and row packet generation.
5. [ ] The application contains one deterministic renderer shared by browser preview, PNG export, CLI, and physical printing.
6. [ ] The final preview contains the exact monochrome raster sent to the selected printer.
7. [ ] The preview contains selected orientation, rotation, threshold or dithering, offsets, printable bounds, and pixel dimensions.
8. [ ] The preview contains stale-output detection when the document or effective print settings change.
9. [ ] The renderer contains fixture-tested pixel parity between preview and printer output.

## Print Settings and Jobs

1. [ ] The graphical print popup contains density, copy count, and horizontal/vertical millimetre offset controls.
2. [x] The CLI contains density, copy count, clockwise rotation, and horizontal/vertical pixel offset controls.
3. [ ] The application contains physical printing from both the graphical editor and CLI.
4. [x] The print sequence contains density, label type, print/page start, dimensions, quantity, raster rows, page completion, status polling, and print end commands.
5. [ ] The print flow contains a final review of printer, label, dimensions, orientation, monochrome output, copies, density, offsets, and warnings.
6. [ ] Print settings are read and validated when the user confirms printing rather than captured earlier by the interface.
7. [ ] Print jobs contain queued, discovering, connecting, preparing, sending, printing, completed, cancelled, and failed states.
8. [ ] Print jobs contain visible progress, cancellation, bounded timeout, safe retry, and sanitized diagnostics.
9. [x] The print completion state contains validated printer protocol confirmation.
10. [ ] Retry and reconnect behavior contains duplicate-print prevention and an explanation of the last confirmed physical state.
11. [ ] The application contains one print queue per printer.
12. [ ] The application contains a test label and printer calibration workflow.

## Documents and Recovery

1. [ ] The graphical editor contains Save and Open actions for legacy `.niim` documents.
2. [ ] Legacy documents contain the selected model, label size, text, images, positions, font properties, and embedded PNG data.
3. [ ] Documents contain a versioned and validated JSON schema with explicit units and stable element IDs.
4. [ ] Documents contain safe embedded assets or validated packaged asset references without executable serialization.
5. [ ] Document saving contains atomic replacement and corruption-safe error handling.
6. [ ] The application contains autosave and crash recovery for unsaved documents.
7. [ ] The application contains an unsaved-change indicator and confirmation before destructive navigation.
8. [ ] The application contains recent documents with missing-file handling.
9. [ ] The application contains safe one-way migration from legacy `.niim` files without exposing pickle loading through the normal application API.
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

1. [ ] The application contains first-run guidance for printer selection, label selection, and the first element.
2. [ ] Empty states contain examples and direct actions for creating or opening a label.
3. [ ] The interface contains the user terms Printer, Label, Elements, Copies, and Print darkness.
4. [ ] The interface contains complete keyboard navigation, visible focus, accessible names, and logical focus restoration.
5. [ ] The editor contains keyboard shortcuts and discoverable shortcut help.
6. [ ] Status and validation information contains text or icons in addition to color.
7. [ ] The interface contains readable contrast, reduced-motion support, and touch-sized controls.
8. [ ] The interface contains Czech and English localization.
9. [ ] The visual interface contains the paper-and-signal design language with paper surfaces, graphite chrome, cyan connection state, and orange print action.

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
