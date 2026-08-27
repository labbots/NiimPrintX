# Project Context -- NiimStudio

## Product Today

NiimStudio is a local command-line tool that prints a prepared image label on
one nearby Niimbot Bluetooth printer. It does not require a cloud account,
browser, server, or graphical editor.

Customers can select one of these printer models: B1, B18, B21, D11, D11_H, and
D110. They can print an image with density, copy count, rotation, and pixel
offsets, or read the printer's serial number and software and hardware versions.

The available customer-facing behavior is recorded in `ai/features/`.

## Current Implementation

- Python 3.12-3.13 application managed with Poetry.
- Click command-line interface in `backend/src/niimstudio/cli/`.
- Bluetooth discovery and printer protocol implementation in
  `backend/src/niimstudio/nimmy/` using Bleak.
- Immutable printer and label capability registry in
  `backend/src/niimstudio/domain/`.
- Pillow-based conversion of source images to the monochrome raster required by
  the printer.
- Hardware-independent pytest coverage for commands, Bluetooth handling,
  protocol behavior, raster encoding, and capabilities.

## Product Boundaries

- A command connects to one matching printer, performs its requested action,
  and disconnects.
- The supported models, density limits, print widths, physical label data, and
  orientation rules come from one registry.
- A successful print message is shown only after printer protocol confirmation.
- No local documents, editor, image export, print history, server, browser UI,
  or multi-printer workflow is currently provided.

## Reliability Expectations

- Bluetooth scans, connections, commands, printing, and disconnects have time
  limits and cleanup.
- Printer messages are framed, checksum-validated, serialized, and buffered for
  fragmented Bluetooth notifications.
- Command failures provide an actionable message and non-zero exit code.
- Automated tests do not require a real printer or connect to nearby devices.

The historical Tkinter application is reference material on the non-merge
`legacy/tkinter-app` branch and is not part of the current product.
