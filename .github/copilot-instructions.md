# Copilot Instructions

Read `AGENTS.md` and the local documents it references before making changes.
Those files are authoritative.

The current repository contains a standalone Python console application and
printer core. It does not contain the historical Tkinter UI. Legacy GUI code is
available only on the non-merge branch `legacy/tkinter-app` for reference.

Use Poetry for setup and verification:

```bash
poetry --directory backend install
poetry --directory backend check
poetry --directory backend run python -m compileall -q backend/src/niimstudio
poetry --directory backend run ruff check backend/src/niimstudio backend/tests
poetry --directory backend run ruff format --check backend/src/niimstudio backend/tests
poetry --directory backend run pytest -c backend/pyproject.toml
```

Normal tests never discover or connect to real Bluetooth devices. Use fake
devices and transports for CLI, BLE, protocol, and raster behavior.
