_default:
    @just --list

run:
    #!/bin/bash
    source venv/bin/activate
    python -m NiimPrintX.ui
