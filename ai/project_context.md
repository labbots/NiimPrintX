# Project Context -- NiimStudio

## Project Values

- **Product:** Local-first label design and printing for Niimbot printers
- **Backend:** Python 3.12-3.13
- **Hardware:** Bluetooth Low Energy through Bleak
- **Package management:** Poetry for Python
- **Default deployment:** A local Python console application

The product requirements and delivery order are in `ai/features/README.md`.

## Current Baseline

The repository currently contains a standalone Python console application:

- `backend/src/niimstudio/nimmy/`: BLE transport, printer protocol, and raster encoding
- `backend/src/niimstudio/cli/`: Click CLI
- `backend/spec_files/cli_app/`: PyInstaller console packaging
- `backend/tests/`: hardware-independent CLI and printer-core verification

The historical Tkinter editor, assets, unsafe `.niim` persistence, and GUI
packaging are archived on the non-merge branch `legacy/tkinter-app`. The main
development line preserves the console interface and protocol knowledge without
depending on that legacy application.

## Target Architecture

Use Hexagonal Architecture with Onion dependency rules. Dependencies point
inward; technology-specific adapters never define domain behavior.

```text
CLI --calls--> application --> domain
                 | ports
                 v
             adapters --> BLE, files, images/fonts
```

### Backend layers

| Layer | Responsibility | May depend on |
| --- | --- | --- |
| `domain` | Documents, label geometry, printer capabilities, print options, job states, protocol values | Python standard library only |
| `application` | Use cases for discovery, connection, rendering, validation, persistence, and print jobs; port definitions | `domain` |
| `adapters` | Bleak, filesystem, image/font providers, clocks, and other external integrations | `application`, `domain` |
| `cli` | Inbound command-line adapter | `application`, `domain` |
| composition root | Creates adapters and wires them to application services | all backend layers |

Rules:

- Domain and application code must not import Bleak or Tkinter concerns.
- CLI commands validate command input, call one application use case, and map the result. They contain no BLE or rendering logic.
- Adapters implement ports owned by the application layer. Application services never instantiate concrete adapters.
- Cross-feature communication goes through application services or typed domain objects, not adapter internals.
- Keep protocol codecs and geometry deterministic and testable without hardware.
- Add architecture tests when the target package structure is introduced.

The package migration should converge incrementally toward:

```text
backend/
  src/
    niimstudio/
      domain/
      application/
      adapters/
      cli/
```

Do not move files merely to match this tree. Extract a boundary when a feature
needs it, keep each migration coherent, and keep the console application working
while shared application services are introduced.

## Technology Direction

### Python backend

- Async application services at hardware and job boundaries
- Bleak only in the BLE adapter
- Pillow/Cairo-based rendering behind application services or ports
- Versioned, validated JSON document storage with atomic writes
- Pytest with fake transports and deterministic fixtures

Use existing libraries until a concrete requirement justifies replacing them.
Adding a dependency requires checking that the same capability is not already
available in the standard library or current stack.

## Application Contracts

### Capabilities

Printer models, DPI, dimensions, darkness limits, orientation, and supported
features have one authoritative backend registry. The CLI, renderer, and printer
services derive their choices from it.

### Documents

New documents use a versioned JSON schema with explicit units, stable IDs, and
validated asset references. Never use `pickle` for files, CLI input, IPC, or
untrusted content. Legacy `.niim` support, if required, belongs in an isolated
one-way migration tool and must not expose pickle loading through the CLI.

### Rendering

CLI export and print use the same document, capabilities, options, and renderer.
The effective raster includes explicit pixel dimensions, orientation, monochrome
conversion, printable bounds, and overflow diagnostics.

### Printers and jobs

Hardware state is represented by typed snapshots and events, not booleans. A
print job progresses through explicit states such as `queued`, `discovering`,
`connecting`, `preparing`, `sending`, `printing`, `completed`, `cancelled`, and
`failed`.

Every hardware operation has a deadline and cleanup path. Events include a job
or printer ID, sequence number, and timestamp. A reconnect or retry must not
silently duplicate a physical print. Completion is reported only after protocol
confirmation.

## Error Handling

Use typed domain/application errors and map them at interface boundaries. User
errors state what happened, whether the document and printer are safe, and what
can be retried. Preserve technical diagnostics in logs or details; do not use a
raw traceback as the primary console message or convert failures to `None`.

## Testing Boundaries

- Domain tests cover capabilities, geometry, schema migration, raster metadata, protocol codecs, and job transitions.
- Application tests use fake BLE, storage, clock, and renderer ports.
- CLI tests verify command input, output, and exit-code contracts.
- Integration tests compare exported and print rasters and exercise timeout, disconnect, cancellation, and retry.
- Hardware tests supplement fake transports; real printers are never the only verification path.

## Migration Order

1. Protect protocol, capabilities, rendering, and job behavior with tests.
2. Extract pure domain types and application ports from the current implementation.
3. Introduce shared application services and fake adapters.
4. Move the CLI onto the shared services.
5. Package the preserved console application.

The legacy branch is reference material only and is never merged back into the
main development line.
