# Copilot Instructions for NiimPrintX

## Project Overview
NiimPrintX is a Python library for interfacing with NiimBot label printers via Bluetooth. It provides both CLI and GUI interfaces for designing and printing labels.

## Requirements
- Python 3.12 or later
- ImageMagick library
- Poetry for dependency management

## Setup for Testing

### 1. Install System Dependencies

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y imagemagick libmagickwand-dev python3-tk xvfb libcairo2-dev pkg-config
```

**macOS:**
```bash
brew install libffi glib gobject-introspection cairo pkg-config imagemagick
export PKG_CONFIG_PATH="/usr/local/opt/libffi/lib/pkgconfig"
export LDFLAGS="-L/usr/local/opt/libffi/lib"
export CFLAGS="-I/usr/local/opt/libffi/include"
```

### 2. Install Python Dependencies

```bash
# Using pip (Linux/CI)
pip install -r requirements-ci.txt

# Using pip (macOS - includes pyobjc packages)
pip install -r requirements.txt

# Or using Poetry (recommended)
python -m venv venv
poetry install
```

**Note:** `requirements.txt` includes macOS-specific packages (pyobjc-*) which will fail on Linux. Use `requirements-ci.txt` for Linux/CI environments.

### 3. Running the Application

**GUI Application:**
```bash
python -m NiimPrintX.ui
```

**CLI Application:**
```bash
# Print command
python -m NiimPrintX.cli print -m d110 -d 3 -n 1 -r 90 -i path/to/image.png

# Info command
python -m NiimPrintX.cli info -m d110
```

## Testing Guidelines

### UI Testing (Headless Environment)

For GUI testing in CI/CD or headless environments:

```bash
# Start virtual display
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99

# Run the UI
python -m NiimPrintX.ui
```

### Linting

```bash
# Install flake8
pip install flake8

# Run linter (critical errors only)
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

# Run full lint (warnings as info)
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

### Security Scanning

Use CodeQL for security analysis:
```bash
# CodeQL analysis is configured in GitHub Actions
# Check .github/workflows/python-app.yml
```

## Supported Printer Models
- D11
- D110
- B21
- B1
- B18

## Key Modules

### UI Components
- `NiimPrintX/ui/main.py` - Main application window
- `NiimPrintX/ui/widget/TextTab.py` - Text input tab
- `NiimPrintX/ui/widget/TextOperation.py` - Text rendering operations
- `NiimPrintX/ui/widget/PrintOption.py` - Print settings

### CLI Components
- `NiimPrintX/cli/__main__.py` - CLI entry point

### Printer Interface
- `NiimPrintX/nimmy/printer.py` - Printer communication

## Testing Multi-line Text Feature

```python
import tkinter as tk
from NiimPrintX.ui.main import LabelPrinterApp

# Create app
app = LabelPrinterApp()
app.load_resources()

# Access text tab
text_tab = app.text_tab

# Test multi-line input
multi_line_text = "Line 1\nLine 2\nLine 3"
text_tab.content_entry.delete("1.0", tk.END)
text_tab.content_entry.insert("1.0", multi_line_text)

# Add to canvas
text_tab.add_button.invoke()

# Verify
assert len(app.app_config.text_items) > 0
```

## Common Issues

### Missing tkinter
```bash
sudo apt-get install python3-tk  # Linux
# tkinter is included with Python on macOS/Windows
```

### Missing ImageMagick
```bash
# Linux
sudo apt-get install imagemagick libmagickwand-dev

# macOS
brew install imagemagick
```

### Display not available (for testing)
```bash
# Use Xvfb for headless testing
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99
```

## CI/CD Integration

The project uses GitHub Actions with the following workflows:
- `python-app.yml` - Linting and testing
- `tag.yaml` - Release builds
- Build workflows for Linux, macOS, and Windows

See `.github/workflows/` for configuration details.
