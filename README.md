<h1 align="center">NiimPrintX</h1>
<p align="center">
<a href="https://github.com/labbots/NiimPrintX/releases"><img src="https://img.shields.io/github/release/labbots/NiimPrintX.svg?style=for-the-badge" alt="Latest Release"></a>
<a href="https://github.com/labbots/NiimPrintX/actions/workflows/tag.yaml"><img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/labbots/NiimPrintX/tag.yaml?style=for-the-badge"></a>
<a href="https://github.com/labbots/NiimPrintX/commits/main/"><img alt="GitHub commits since latest release" src="https://img.shields.io/github/commits-since/labbots/NiimPrintX/latest?style=for-the-badge"></a>
</p>


![NiimPrintX](docs/assets/NiimPrintX.gif)

NiimPrintX is a Python library designed to seamlessly interface with NiimBot label printers via Bluetooth.
It provides both a Command-Line Interface (CLI) and a Graphical User Interface (GUI) for users to design and print labels efficiently.

> **Hardware testing disclaimer:** The B21S protocol fixes and end-to-end print path in this branch were **tested only on a Niimbot B21S**. B1 support is included based on [PR #6](https://github.com/labbots/NiimPrintX/pull/6) (see Credits), but has **not** been hardware-verified here. Other models keep their previous code paths — please validate on your own printer before relying on them.

## Key Features
* **Cross-Platform Compatibility:** NiimPrintX works on Windows, macOS, and Linux, ensuring broad usability.
* **Bluetooth Connectivity:** Effortlessly connect to your NiimBot label printers via Bluetooth.
* **Model Support:** D11, D11_H, D110, D101, B18, B21, **B21S**, and **B1** (see testing disclaimer above).
* **Dual Interface Options:** CLI and GUI for automation or interactive label design.
* **Custom Label Design:** GUI supports text, emoji, built-in icons, custom images, and a live 1-bit thermal preview.
* **Advanced Print Settings:** Density, quantity, and image rotation.
* **Protocol variants:** Model-aware print dispatch (B1 7-byte PrintStart / 6-byte SetPageSize; B21S 6-byte SetPageSize + BLE MTU handling).

## What's new (this contribution)
* **B21S support:** 6-byte `SetPageSize` (blank labels with 4-byte size), BLE MTU negotiation, reliable GATT writes, Connect handshake, and model name matching that does not confuse `B1` with `B21`/`B21S`.
* **B1 support:** Merged protocol approach from [PR #6](https://github.com/labbots/NiimPrintX/pull/6) by [@LorisPolenz](https://github.com/LorisPolenz), including MultiMote's review fix so print quantity / page count is passed correctly.
* **GUI:** Image tab, emoji picker, live thermal preview, B1/B21/B21S label sizes, density max 1–5 for B-family, print-area-accurate export (no outline crop offset).
* **CLI:** `-m b21s` (and existing `-m b1`) with shared model metadata.

## Requirements
To run NiimPrintX, you need to have the following installed:

* Python 3.12 or later
* ImageMagick library
* Poetry for dependency management
* On Linux: Bluetooth (`bluez`), and for the GUI: `libcairo2-dev`, `pkg-config`, `python3-tk`


## Installation
To install NiimPrintX, follow these steps:

* Ensure that ImageMagick is installed and properly configured on your system. You can download it from [here](https://imagemagick.org/script/download.php).

Clone the repository:

```shell
git clone https://github.com/labbots/NiimPrintX.git
cd NiimPrintX
```
Install the necessary dependencies using Poetry:

```shell
python -m venv venv
poetry install
```

Linux (Debian/Ubuntu) extras for BLE + GUI:

```shell
sudo apt-get install -y imagemagick libcairo2-dev pkg-config python3-tk bluez
```

### Note:
MacOS specific setup for local development

```shell
brew install libffi
brew install glib gobject-introspection cairo pkg-config

export PKG_CONFIG_PATH="/usr/local/opt/libffi/lib/pkgconfig"
export LDFLAGS="-L/usr/local/opt/libffi/lib"
export CFLAGS="-I/usr/local/opt/libffi/include"
```


## Usage
NiimPrintX provides both CLI and GUI applications to use the printer.

### Command-Line Interface (CLI)
The CLI allows you to print images and get information about the printer models.

#### General CLI Usage
```shell
Usage: python -m NiimPrintX.cli [OPTIONS] COMMAND [ARGS]...

Options:
  -v, --verbose  Enable verbose logging
  -h, --help     Show this message and exit.

Commands:
  info
  print
```
#### Print Command
```shell
Usage: python -m NiimPrintX.cli print [OPTIONS]

Options:
  -m, --model [b1|b18|b21|b21s|d11|d11_h|d110|d101]
                                  Niimbot printer model  [default: d110]
  -d, --density INTEGER RANGE     Print density  [default: 3; 1<=x<=5]
  -n, --quantity INTEGER          Print quantity  [default: 1]
  -r, --rotate [0|90|180|270]     Image rotation (clockwise)  [default: 0]
  --vo INTEGER                    Vertical offset in pixels  [default: 0]
  --ho INTEGER                    Horizontal offset in pixels  [default: 0]
  -i, --image PATH                Image path  [required]
  -h, --help                      Show this message and exit.
```
**Example:**

```shell
# B21S (50×30 mm @ ~203 dpi → typically 384×240 px, no rotate)
python -m NiimPrintX.cli print -m b21s -d 5 -n 1 -i path/to/image.png

# B1 (protocol from PR #6 — not hardware-tested in this contribution)
python -m NiimPrintX.cli print -m b1 -d 3 -n 2 -i path/to/image.png

python -m NiimPrintX.cli print -m d110 -d 3 -n 1 -r 90 -i path/to/image.png
```

#### Info Command

```shell
Usage: python -m NiimPrintX.cli info [OPTIONS]

Options:
  -m, --model [b1|b18|b21|b21s|d11|d11_h|d110|d101]
                                  Niimbot printer model  [default: d110]
  -h, --help                      Show this message and exit.
```

**Example:**

```shell
python -m NiimPrintX.cli info -m b21s
```

### Graphical User Interface (GUI)
Design labels with text, emoji, icons, and images; preview a 1-bit thermal render; then print:

```shell
poetry run python -m NiimPrintX.ui
```

1. Select device (e.g. **B21S**) and label size  
2. Add content from the Text / Emoji, Icons, or Image tabs  
3. Use **Thermal preview** to check alignment  
4. Connect → Print  

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request with your improvements.

## Credits
* **B1 printer protocol:** Adapted from [PR #6 — Implement Support for B1 Printer](https://github.com/labbots/NiimPrintX/pull/6) by [@LorisPolenz](https://github.com/LorisPolenz), with review feedback from [@MultiMote](https://github.com/MultiMote) (page-count / quantity in PrintStart) and testing notes from [@hadess](https://github.com/hadess).
* **B21S blank-label / 6-byte SetPageSize insight:** Community findings in [AndBondStyle/niimprint#33](https://github.com/AndBondStyle/niimprint/issues/33) and related discussion in [#17](https://github.com/AndBondStyle/niimprint/issues/17).
* **Protocol reference:** [niimbluelib](https://github.com/MultiMote/niimbluelib) / [NiimBlue](https://github.com/MultiMote/niimblue) by [@MultiMote](https://github.com/MultiMote).
* Icons made by [Dave Gandy](https://www.flaticon.com/authors/dave-gandy) from [www.flaticon.com](https://www.flaticon.com/)
* Icons made by [Pixel perfect](https://www.flaticon.com/authors/pixel-perfect) from [www.flaticon.com](https://www.flaticon.com/)
* Icons made by [Freepik](https://www.freepik.com) from [www.flaticon.com](https://www.flaticon.com/)
* Icons made by [rddrt](https://www.flaticon.com/authors/rddrt) from [www.flaticon.com](https://www.flaticon.com/)
* Icons made by [Icongeek26](https://www.flaticon.com/authors/icongeek26) from [www.flaticon.com](https://www.flaticon.com/)
* Icons made by [SyafriStudio](https://www.flaticon.com/authors/syafristudio) from [www.flaticon.com](https://www.flaticon.com/)
* Icons made by [Wahyu Adam](https://www.flaticon.com/authors/wahyu-adam) from [www.flaticon.com](https://www.flaticon.com/)
* Icons made by [meaicon](https://www.flaticon.com/authors/meaicon) from [www.flaticon.com](https://www.flaticon.com/)
* Icons made by [IconKanan](https://www.flaticon.com/authors/iconkanan) from [www.flaticon.com](https://www.flaticon.com/)
* Icons made by [kornkun](https://www.flaticon.com/authors/kornkun) from [www.flaticon.com](https://www.flaticon.com/)
* Icons made by [Rifaldi Ridha Aisy](https://www.flaticon.com/authors/rifaldi-ridha-aisy) from [www.flaticon.com](https://www.flaticon.com/)
