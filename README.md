# NiimStudio

NiimStudio is a local command-line tool for printing prepared image labels on
one nearby Niimbot printer. It works without a cloud account or network
service.

## Available Today

- Choose a supported printer model: B1, B18, B21, D11, D11_H, or D110.
- Print a raster image with the selected density, copy count, rotation, and
  pixel offsets.
- Automatically find one matching Bluetooth printer, connect, print, and
  disconnect.
- Read the connected printer's serial number and software and hardware versions.

The console application and its usage instructions are in
[`backend/`](backend/README.md). The historical Tkinter application remains on
the non-merge `legacy/tkinter-app` branch.

## License

GNU GPLv3. See [`LICENSE`](LICENSE).
