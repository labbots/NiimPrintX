# NiimStudio

NiimStudio currently provides a standalone Python console application for
printing raster images with Niimbot Bluetooth label printers. The previous
Tkinter application is archived on the `legacy/tkinter-app` branch while a new
React interface is developed independently.

## Features

- BLE printer discovery and connection through Bleak
- Image printing with density, quantity, rotation, and pixel offsets
- Printer serial number, software version, and hardware version queries
- Supported CLI model selectors: B1, B18, B21, D11, D11_H, and D110
- Linux, macOS, and Windows console packaging

The complete implementation checklist is in `ai/project_features.md`.

## Requirements

- Python 3.12 or 3.13
- Poetry 1.8 or newer
- A supported Bluetooth adapter and operating-system BLE permissions

The console application does not require Tkinter, Cairo, or ImageMagick.

## Installation

```shell
git clone https://github.com/csobik/NiimStudio.git
cd NiimStudio/backend
poetry install
```

## Usage

Run the module directly:

```shell
poetry run python -m niimstudio.cli --help
```

Poetry also installs `niimstudio` and the compatibility command `niimprintx`:

```shell
poetry run niimstudio --help
```

### Print an image

```shell
poetry run niimstudio print \
  --model d110 \
  --density 3 \
  --quantity 1 \
  --rotate 90 \
  --image path/to/image.png
```

Use `--ho` and `--vo` for horizontal and vertical offsets in pixels.

### Read printer information

```shell
poetry run niimstudio info --model d110
```

## Development

The automated suite does not access real Bluetooth hardware. It uses fake
devices and transports to test CLI behavior, cleanup, packet validation, raster
encoding, and printer command sequencing.

```shell
poetry check
poetry run python -m compileall -q src/niimstudio
poetry run ruff check src/niimstudio tests
poetry run ruff format --check src/niimstudio tests
poetry run pytest
poetry run pyinstaller spec_files/cli_app/NiimStudio.spec --noconfirm --clean
./dist/niimstudio --help
```

## Legacy Application

The historical Tkinter editor, its assets, and GUI packaging remain available
on the non-merge branch `legacy/tkinter-app` for reference and implementation
research. New work does not depend on that branch.

## License

GNU GPLv3. See `LICENSE`.
