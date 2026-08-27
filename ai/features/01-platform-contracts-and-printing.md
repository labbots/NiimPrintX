# Printing Capabilities

NiimStudio prints a prepared image label on one nearby supported printer. The
following behavior is available and covered by automated tests.

## Choose a Printer

- [x] Select B1, B18, B21, D11, D11_H, or D110 from the command line.
- [x] Use the selected model's approved print width and print-density limits.
- [x] Keep the supported printer details, label dimensions, orientation rules,
  and hardware capabilities in one shared registry.

## Connect and Print

- [x] Find one matching printer over Bluetooth, connect to it, print, and
  disconnect when finished.
- [x] Accept an image path, density, number of copies, clockwise rotation, and
  horizontal and vertical pixel offsets.
- [x] Check the prepared image against the selected printer before printing.
- [x] Convert the image to the printer's monochrome format and send its rows in
  the required order.
- [x] Confirm that the printer reports print completion before reporting success.

## Printer Information and Reliability

- [x] Show a connected printer's serial number and software and hardware versions.
- [x] Validate printer messages, including their framing and checksum.
- [x] Handle fragmented Bluetooth messages, one command at a time, operation
  time limits, and connection cleanup.
- [x] Return an actionable command-line error and a non-zero exit code when an
  operation fails.
