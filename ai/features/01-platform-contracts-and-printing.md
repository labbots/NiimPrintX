# Platform Contracts and Printing

This file owns retained CLI and protocol behavior plus the backend contracts the
UI consumes. Checked requirements describe the current baseline; unchecked
requirements include both pre-UI gates and later print integration.

## Implementation Sequence

1. Protect the retained CLI, BLE, protocol, and raster baseline.
2. Define capability, document, application-service, API, and fake-adapter contracts.
3. Extract deterministic rendering and font resolution shared by preview and print.
4. Expose typed printer lifecycle snapshots and sequenced events.
5. Integrate validated print settings, jobs, cancellation, and safe retry.
6. Move the CLI onto the same application services.

Do not block the UI shell on live BLE. The UI foundation and editor should use
the same typed contracts with deterministic fake responses.

## Application Interfaces

2. [x] The application contains a command-line interface with `print` and `info` commands.
3. [x] The application contains local design and printing workflows that require no cloud account.

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

2. [x] The CLI contains target printer selection for B1, B18, B21, D11, D11_H, and D110 models.
6. [ ] The application contains one authoritative capability registry shared by UI, CLI, renderer, API, and printer services.
7. [x] The capability registry contains complete model identity, DPI, printable dimensions, label sizes, density limits, orientation rules, and feature flags.

## Printer Discovery and Connection

1. [x] The application contains BLE printer discovery through Bleak.
2. [ ] The application contains discovery that uses a case-insensitive model-name prefix only as a fallback and presents ambiguous matches for selection.
5. [x] The printer client contains connect, disconnect, GATT write, and notification subscription operations.
6. [ ] The printer client contains periodic heartbeat polling while the graphical editor is connected and idle.
8. [ ] The discovered printer list contains stable identity, friendly name, model confidence, signal strength, and last-seen time.
10. [ ] The application contains remembered printer selection without silently printing to an unknown printer.
11. [ ] The application contains automatic reconnection with bounded retries and a user-visible recovery action.

## Printer Status and Protocol

1. [x] The printer protocol contains packet framing, payload length, XOR checksum generation, and checksum validation.
2. [x] The printer client contains printer information, RFID, heartbeat, label type, density, print start/end, page start/end, dimensions, quantity, raster row, and print status commands.
3. [x] The heartbeat parser contains lid, power, paper, and RFID-read values for supported response variants.
4. [x] The printer client contains discovery of a GATT characteristic with read, write-without-response, and notification properties.
6. [x] The command channel contains serialized requests, response-command validation, response correlation, and fragmented notification buffering.
7. [x] Every printer operation contains a hard deadline, cancellation path, and deterministic resource cleanup.
8. [ ] Printer failures contain typed causes instead of `None` or an unrelated later exception.
9. [ ] The application contains fake BLE transports for successful, fragmented, timeout, disconnect, invalid-response, lid-open, and paper-out scenarios.

## Text Elements

4. [ ] The text tool contains font families discovered from the ImageMagick font registry.
9. [ ] Text rendering contains deterministic font resolution shared by preview and print output.

## Preview and Rasterization

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

2. [ ] Legacy documents contain the selected model, label size, text, images, positions, font properties, and embedded PNG data.
3. [ ] Documents contain a versioned and validated JSON schema with explicit units and stable element IDs.
4. [ ] Documents contain safe embedded assets or validated packaged asset references without executable serialization.
5. [ ] Document saving contains atomic replacement and corruption-safe error handling.
9. [ ] The application contains safe one-way migration from legacy `.niim` files without exposing pickle loading through the normal application API.
