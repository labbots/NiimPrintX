# Printer Capability Registry

**Status:** Completed

## Feature References

- Primary: `Printer Models and Label Setup 6`
- Primary: `Printer Models and Label Setup 7`
- Supporting: capability portion of `Command-Line Interface 7`

## Goal

Introduce one immutable, backend-owned printer capability registry that contains
approved model and physical-label facts and becomes the only source for the
retained CLI model choices, raster-width limits, density limits, and BLE model
identity. Preserve current CLI behavior while creating a standard-library-only
domain contract that later API, renderer, printer-service, and UI slices can
consume without copying capability data.

## Acceptance Criteria

- The backend domain exposes deterministic typed lookup and ordered enumeration
  of every approved printer model; unknown model IDs produce a specific domain
  error rather than `KeyError` or `None`.
- Every registered model has a stable ID, display identity, BLE discovery
  prefixes or aliases, DPI, maximum printable dimensions, compatible physical
  labels, density bounds and default, supported orientations, and an explicit
  set of feature flags. No required fact is represented by a guessed value or
  an unexplained `None`.
- Every physical-label record has a stable ID, explicit millimetre dimensions,
  printable bounds, and compatible orientation data. Its pixel bounds are
  deterministic for a selected printer and orientation using the approved
  millimetre-to-pixel rounding rule.
- Capability records, nested label records, orientation collections, feature
  collections, and the registry collection cannot be mutated by consumers.
- `niimstudio print` and `niimstudio info` derive their model choices from the
  registry while retaining the six currently checked CLI models, their ordering,
  case-insensitive input, and defaults. An approved additional model is appended
  without removing or reordering the retained selectors.
- CLI image-width validation and density clamping read the selected capability
  record and preserve the current effective-raster behavior for rotation and
  pixel offsets.
- BLE advertised-name matching reads model identity from the same registry and
  retains case-insensitive normalization, longest-prefix disambiguation, and the
  current no-match and ambiguous-match failures.
- Importing the capability domain does not import Click, Pillow, Bleak, Loguru,
  `niimstudio.cli`, or `niimstudio.nimmy`, and requires no new production
  dependency.
- Existing print, information-query, connection, cleanup, and protocol behavior
  remains unchanged and all verification is hardware-independent.

## Out of Scope

- Adding FastAPI, an HTTP capability snapshot, generated TypeScript contracts,
  React setup screens, or frontend dependencies.
- Moving rendering, BLE lifecycle, or print-job orchestration behind application
  services; those remaining parts of `Command-Line Interface 7` require later
  slices.
- Making `PrinterClient` model-aware or changing its generic protocol bounds,
  raster encoding, hard-coded label type, or print sequence.
- Adding physical-label selection to the CLI or changing density clamping into a
  validation error.
- Implementing multi-printer selection from `Command-Line Interface 8` or
  `Printer Discovery and Connection 2`.
- Treating values from `legacy/tkinter-app`, model-name suffixes, or available
  protocol commands as verified hardware capabilities without product approval
  and recorded evidence.

## Current State

- `backend/src/niimstudio/cli/command.py` owns `MODEL_MAX_WIDTH_PX`,
  `MODEL_MAX_DENSITY`, and `MODEL_CHOICES`. The six retained selectors are `b1`,
  `b18`, `b21`, `d11`, `d11_h`, and `d110`; width limits are split between 384
  and 240 pixels, and density ceilings between 5 and 3.
- The `print` and `info` Click options use those choices with defaults `d11` and
  `d110`. `prepare_image()` applies rotation and pixel offsets before checking
  the selected model's width. `print_command()` accepts density 1-5 and silently
  clamps it to the selected model's ceiling.
- `backend/src/niimstudio/nimmy/bluetooth.py` independently duplicates the six
  models in `KNOWN_MODEL_PREFIXES`. `_device_model()` normalizes advertised
  names and chooses the longest matching prefix to distinguish names such as
  D11, D110, and D11_H.
- The selected model is discarded after discovery. `PrinterClient` enforces only
  protocol-wide density, raster, quantity, and dimension bounds and has no
  capability input.
- `backend/tests/cli/test_command.py` characterizes D11 width rejection, D11
  density clamping, one clockwise rotation, offset validation, model forwarding,
  print cleanup, and B21/D110 information queries. It does not lock the complete
  model table or both width and density groups.
- `backend/tests/nimmy/test_bluetooth.py` protects case-insensitive and
  overlapping-prefix discovery behavior, but it cannot prevent the CLI and BLE
  model lists from drifting.
- No `niimstudio.domain` package or application capability service exists.
  `backend/pyproject.toml` measures coverage only for `niimstudio.cli` and
  `niimstudio.nimmy`, so a new domain package would otherwise be omitted from
  the coverage threshold.
- Current production code contains no authoritative DPI, physical-label,
  printable-bound, safe-area, per-model orientation, or feature-flag data.
  `ai/features/README.md` explicitly identifies those facts and the D101 versus
  B1/B21 model-matrix conflict as unresolved.

## Contracts and Decisions

### Ownership and Module Boundary

- Add `backend/src/niimstudio/domain/printer_capabilities.py` and expose only the
  small public capability API needed by consumers. Add
  `backend/src/niimstudio/domain/__init__.py` without re-exporting unrelated
  implementation details.
- Keep the domain module pure and based on immutable standard-library value
  types, preferably `dataclass(frozen=True, slots=True)`, `Enum`/`StrEnum`,
  tuples, and frozensets. It must not know about Click choices, BLE scanning,
  Pydantic, Pillow, or frontend presentation.
- Use an ordered immutable collection as the authoritative registry and a typed
  lookup function. Do not retain parallel model dictionaries in CLI or BLE
  modules.
- Keep input normalization at inbound/adaptor boundaries. Registry lookup uses a
  documented canonical model ID; Click remains responsible for
  case-insensitive user input and the BLE adapter remains responsible for
  advertised-name normalization.

### Proposed Domain Values

- `PrinterCapabilities`: canonical model ID, display name, discovery prefixes,
  horizontal and vertical DPI, maximum raster dimensions in pixels, compatible
  labels, density minimum/default/maximum, allowed orientations, and supported
  feature flags.
- `LabelCapabilities`: stable label ID, physical width and height in millimetres,
  printable rectangle with an explicit origin and dimensions, and allowed
  orientations. Represent millimetres exactly with standard-library `Decimal`
  values constructed from strings. Keep coordinate axes and whether dimensions
  describe media or the effective raster explicit in field names.
- `PrintableBounds`: left/top origin plus width/height in explicit physical units;
  keep it physical and independent of any one printer's DPI.
- A pure conversion function accepts the selected printer, label, and
  orientation and returns integer pixel bounds. Its contract defines axis
  swapping and whether the approved rounding rule applies to rectangle edges or
  dimensions, so labels shared by printers with different horizontal or
  vertical DPI cannot produce an ambiguous pixel result.
- `PrintOrientation` and `PrinterFeature`: finite enums whose meanings are
  consumer-independent. An empty feature set means that none of the defined
  features are supported, not that support is unknown.
- `UnknownPrinterModelError`: the specific failure for lookup outside the
  approved registry.

Names may be tightened during the first red-green-refactor cycle, but units,
immutability, ownership, and lookup semantics are contract requirements.

### Product-Data Gate

The plan cannot move to `Ready` until maintainers approve and record the
following matrix with a source or verification note for every value:

- The application-wide supported model set and stable IDs. B1, B18, B21, D11,
  D11_H, and D110 remain registered because they are retained requirements;
  decide whether D101 joins that set. All consumers may filter by compatibility
  or capabilities but must not maintain a competing model registry.
- User-facing model names and all BLE advertised-name prefixes/aliases.
- Horizontal and vertical DPI for every model; do not assume square DPI.
- Physical label sizes, stable label IDs, model compatibility, media axes,
  printable rectangles, margins or safe areas, and maximum printable length.
- The exact millimetre-to-pixel rounding rule, whether it rounds rectangle edges
  or dimensions, and the stage at which orientation swaps axes and DPI.
- Density minimum, default, and maximum for each model, including confirmation
  of the existing 3/5 ceilings and whether current silent CLI clamping remains
  the retained behavior.
- Orientation semantics and allowed orientations per model; `D11_H` must not be
  interpreted from its suffix alone.
- The closed feature-flag vocabulary and per-model values. Protocol support for
  RFID, heartbeat, battery, or label-type commands is not by itself evidence of
  model support.

Historical Tkinter data may be used to identify questions or hardware tests but
is not copied as authority. The six retained models require complete approved
data before this plan can proceed. Additional models without complete approved
data remain outside the registry; required fields do not receive placeholders
merely to make the contract instantiate.

### Approved Product Matrix

The project owner approved this initial matrix on 2026-08-20. Published product
specifications establish model DPI, media families, and the hardware feature
flags below. Existing checked CLI and BLE behavior establishes canonical IDs,
ordering, raster limits, density policy, and discovery prefixes. Printable
rectangles, orientation policy, and rounding are explicit NiimStudio product
decisions so the contract remains deterministic without requiring live hardware.

Register only these models, in this order:

| ID | Display name | Discovery prefixes | DPI X/Y | Max raster width | Density min/default/max | Orientations | Features | Labels |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `b1` | `NIIMBOT B1` | `b1` | 203/203 | 384 px | 1/3/5 | 0, 90, 180, 270 | NFC label identification | `b-50x30` |
| `b18` | `NIIMBOT B18` | `b18` | 203/203 | 384 px | 1/3/3 | 0, 180 | thermal transfer | `b18-14x30` |
| `b21` | `NIIMBOT B21` | `b21` | 203/203 | 384 px | 1/3/5 | 0, 90, 180, 270 | none | `b-50x30` |
| `d11` | `NIIMBOT D11` | `d11` | 203/203 | 240 px | 1/3/3 | 0, 180 | none | `d-12x40` |
| `d11_h` | `NIIMBOT D11_H` | `d11_h` | 300/300 | 240 px | 1/3/3 | 0, 180 | automatic label calibration | `d-12x40` |
| `d110` | `NIIMBOT D110` | `d110` | 203/203 | 240 px | 1/3/3 | 0, 180 | none | `d-12x40` |

`D101` is not registered in this slice because it is absent from retained CLI,
BLE, and protocol verification. Published alternate names such as N1 and D110_M
are not discovery aliases without an observed BLE advertisement.

Media width is the cross-feed X dimension and media length is the feed Y
dimension. Coordinates have a top-left origin. The initial physical-label
catalog is intentionally limited to representative rectangular stock with known
family compatibility:

| ID | Display name | Media width/length | Printable left/top/width/length | Models | Orientations |
| --- | --- | --- | --- | --- | --- |
| `b-50x30` | `50 x 30 mm` | 50/30 mm | 1/0/48/30 mm | B1, B21 | 0, 90, 180, 270 |
| `b18-14x30` | `14 x 30 mm` | 14/30 mm | 1/0/12/30 mm | B18 | 0, 180 |
| `d-12x40` | `12 x 40 mm` | 12/40 mm | 0/0/12/40 mm | D11, D11_H, D110 | 0, 180 |

For clockwise orientation, transform the physical printable rectangle before
applying DPI. Given media `W`/`H` and rectangle `x`/`y`/`w`/`h`, use:

| Orientation | Oriented media | Transformed rectangle |
| --- | --- | --- |
| 0 | `(W, H)` | `(x, y, w, h)` |
| 90 | `(H, W)` | `(H - (y + h), x, h, w)` |
| 180 | `(W, H)` | `(W - (x + w), H - (y + h), w, h)` |
| 270 | `(H, W)` | `(y, W - (x + w), h, w)` |

Convert each transformed left, top, right, and bottom edge independently with
exact decimal arithmetic and `ROUND_HALF_UP`:

```text
pixels = round_half_up(millimetres * dpi / 25.4)
```

Pixel width and height are the differences between rounded opposite edges. This
keeps adjacent physical rectangles on the same pixel boundary. Normal expected
bounds are B1/B21 `(8, 0, 384, 240)`, B18 `(8, 0, 96, 240)`, D11/D110
`(0, 0, 96, 320)`, and D11_H `(0, 0, 142, 472)`.

The closed initial feature vocabulary is NFC label identification, thermal
transfer, and automatic label calibration. Empty sets assert none of those
features, not unknown support. Protocol command availability is not feature
evidence.

Evidence:

- Retained IDs, order, raster widths, density policy, and prefixes:
  `backend/src/niimstudio/cli/command.py` and
  `backend/src/niimstudio/nimmy/bluetooth.py`.
- B1 203 DPI, 48 mm effective width, and NFC:
  <https://www.niimbot.com/us/solutionOverseas/retail> and
  <https://www.manualslib.com/manual/3958330/Niimbot-B1.html?page=10>.
- B18 203 DPI, 12 mm width, and thermal transfer:
  <https://www.manualslib.com/manual/2986811/Niimbot-B18.html?page=10>.
- B1/B21 and D-series label families and common sizes:
  <https://niimbot.com.sg/blogs/news/what-label-sizes-fit-the-niimbot-b21-and-b21-pro-complete-compatibility-guide>
  and
  <https://niimbot.com.sg/blogs/news/what-labels-fit-the-niimbot-d11-d110-and-d101-label-size-compatibility-guide>.
- D11_H 300 DPI, 12 x 40 mm stock, and automatic calibration:
  <https://niimbots.com/products/d11-h-label-maker-machine-with-tape-300dpi-upgraded-resolution>.
- D110 203 DPI and 15 mm media support:
  <https://www.manualshelf.com/manual/niimbot/d110/operating-instructions-english.html>.
- B18/N1 14 x 30 mm stock:
  <https://niimbots.com/collections/label-tape-for-b18>.

### Compatibility Decisions

- Preserve the checked CLI contract and ordering for B1, B18, B21, D11, D11_H,
  and D110. Any approved addition follows those retained selectors and must be
  reflected consistently in both CLI commands and BLE identity tests.
- Preserve lowercase canonical IDs passed to `_print()`, `_info()`, and
  `find_device()`, plus the existing uppercase model spelling in width errors.
- Preserve effective width as rotated image width plus horizontal pixel offset,
  protocol-height validation, density clamping, and the existing defaults. This
  slice changes data ownership, not those user-visible rules.
- The future API will map these domain values to boundary DTOs rather than expose
  Python objects directly. No Pydantic or JSON serialization contract is added
  in this plan.

## Implementation Steps

- [x] Resolve the Product-Data Gate, record the approved complete matrix and its
  evidence in this plan, and change status to `Ready`; do not begin production
  implementation with guessed or incomplete records.
- [x] Characterization: extend `backend/tests/cli/test_command.py` to lock the
  retained model choice order in `print --help` and `info --help`,
  case-insensitive canonical IDs, both 240/384-pixel width groups, both 3/5
  density groups, defaults, rotation-before-width validation, and pixel-offset
  behavior. Run the focused CLI tests and observe them pass before refactoring.
- [x] Characterization: extend `backend/tests/nimmy/test_bluetooth.py` so every
  existing model-ID prefix matches a representative advertised name and
  overlapping names still select the longest prefix. Run the focused BLE tests
  and observe them pass before removing the duplicate tuple; do not characterize
  newly approved aliases that current code does not support as existing behavior.
- [x] Characterization: extend `backend/tests/test_console_boundary.py` to lock
  that `print --help` and `info --help` expose model choices without loading
  Tkinter, frontend, or legacy modules. Run it and observe it pass before
  changing the CLI import graph.
- [x] Red: add `backend/tests/test_architecture.py` with an assertion that imports
  the real capability module and rejects dependencies on project outer layers or
  third-party frameworks. Confirm failure because the domain package does not
  exist; do not use a vacuous package or filename-only check.
- [x] Green/refactor: add `backend/src/niimstudio/domain/__init__.py` and the
  minimal `backend/src/niimstudio/domain/printer_capabilities.py` module, make the
  architecture boundary pass without a dependency, and keep the public surface
  empty until behavior tests require it.
- [x] Red: add focused tests in
  `backend/tests/domain/test_printer_capabilities.py` for exact immutable physical
  dimensions and printable rectangles, including rejection of non-positive
  dimensions and rectangles outside their media. Confirm failure because those
  value types do not exist.
- [x] Green/refactor: implement only the standard-library physical value types
  and invariants needed for those tests, using exact `Decimal` millimetres.
- [x] Red: add focused tests for model ID, display identity, asymmetric DPI,
  density minimum/default/maximum ordering, orientations, feature sets, and
  immutable discovery prefixes. Confirm failure for the missing model-capability
  value and invariants.
- [x] Green/refactor: implement the smallest immutable model-capability value and
  finite enums that pass those tests without introducing registry data yet.
- [x] Red: add focused label compatibility tests for allowed and rejected
  printer-label-orientation combinations. Confirm failure for missing
  compatibility behavior.
- [x] Green/refactor: implement only the pure compatibility behavior needed by
  those tests and keep all prior domain tests green.
- [x] Red: add selected printer-label-orientation conversion tests for asymmetric
  DPI, orientation axis swaps, printable-rectangle origin and opposite-edge
  boundaries, and approved rounding cases. Confirm failure for missing
  conversion behavior.
- [x] Green/refactor: implement the smallest pure conversion that passes those
  cases and keeps physical and pixel units explicit.
- [x] Red: add exact tests for the approved complete records, retained ordering,
  unique canonical model IDs and normalized discovery prefixes, and deep
  registry immutability. Confirm failure because registry data does not exist.
- [x] Green/refactor: add the approved records and ordered immutable collection,
  remove avoidable data duplication, and keep all domain and architecture tests
  green.
- [x] Red: add focused deterministic enumeration and unknown-model lookup tests.
  Confirm failure because the public lookup API does not exist.
- [x] Green/refactor: add the smallest typed enumeration and lookup API, including
  `UnknownPrinterModelError`, while preserving registry order and immutability.
- [x] Red, when the approved matrix adds a model beyond the retained six: not
  applicable because the approved matrix retains exactly the existing six; add
  failing `print --help`, `info --help`, and case-insensitive canonicalization
  tests for that model before changing CLI production imports.
- [x] Refactor: replace `MODEL_MAX_WIDTH_PX`, `MODEL_MAX_DENSITY`, and independently
  defined `MODEL_CHOICES` in `backend/src/niimstudio/cli/command.py` with ordered
  registry enumeration and selected-record lookup. Preserve Click defaults,
  input canonicalization, error text, density clamping, and `_print()`/`_info()`
  signatures. This is the green step for any new-model CLI tests; otherwise it is
  a refactor protected by characterization tests. Run CLI, domain, architecture,
  and console-boundary tests.
- [x] Red, when the approved matrix adds a model prefix or alias that current BLE
  matching does not support: not applicable because no alias was approved. An
  added identity would require its advertised-name test before adapter changes.
- [x] Green/refactor: update `backend/src/niimstudio/nimmy/bluetooth.py` to derive
  discovery identities from the registry, remove `KNOWN_MODEL_PREFIXES`, and
  preserve normalization, longest-prefix selection, scanner failures, and
  ambiguity behavior. This is the green step for newly approved identity tests;
  otherwise it is protected by the BLE characterization tests. Run BLE, domain,
  architecture, and CLI tests.
- [x] Refactor: review the resulting import direction and public capability API;
  keep protocol-wide limits in `nimmy.printer`, adapter normalization in
  `nimmy.bluetooth`, and Click parsing/formatting in `cli.command` rather than
  moving unrelated behavior into the registry.
- [x] Update `backend/pyproject.toml` coverage collection to include the new
  domain package, preferably by measuring `niimstudio` as a whole, and run the
  full suite to confirm the configured 80% threshold includes capability code.
- [x] Rerun `backend/tests/test_console_boundary.py` after the migration to prove
  the changed import graph retains the characterized console boundary.

## Verification

- [x] Focused domain cycle:
  `poetry --directory backend run pytest -c backend/pyproject.toml backend/tests/domain/test_printer_capabilities.py --no-cov`
- [x] Focused CLI cycle:
  `poetry --directory backend run pytest -c backend/pyproject.toml backend/tests/cli/test_command.py --no-cov`
- [x] Focused BLE cycle:
  `poetry --directory backend run pytest -c backend/pyproject.toml backend/tests/nimmy/test_bluetooth.py --no-cov`
- [x] Architecture and console boundaries:
  `poetry --directory backend run pytest -c backend/pyproject.toml backend/tests/test_architecture.py backend/tests/test_console_boundary.py --no-cov`
- [x] CLI acceptance smoke tests:
  `poetry --directory backend run niimstudio print --help`,
  `poetry --directory backend run niimstudio info --help`, and
  `poetry --directory backend run niimprintx print --help`
- [x] Diff whitespace and conflict markers: `git diff --check`
- [x] Syntax/import compilation:
  `poetry --directory backend run python -m compileall -q backend/src/niimstudio`
- [x] Poetry validity: `poetry --directory backend check`
- [x] Full tests and minimum 80% coverage:
  `poetry --directory backend run pytest -c backend/pyproject.toml`
- [x] Ruff static checks:
  `poetry --directory backend run ruff check backend/src/niimstudio backend/tests`
- [x] Ruff formatting:
  `poetry --directory backend run ruff format --check backend/src/niimstudio backend/tests`
- [x] Documentation check: verify all paths, feature references, approved model
  facts, and commands against the current tree.

## Completion

- [x] The approved capability matrix and evidence remain recorded with the plan,
  and no production value depends only on legacy or inferred data.
- [x] Documentation and cross-references reflect the implemented contract and
  retained CLI behavior.
- [x] Review `Printer Models and Label Setup 7` for completion only if every
  required field is approved and populated for every registered model.
- [x] Keep `Printer Models and Label Setup 6` unchecked until later API, UI,
  renderer, and printer-service slices consume this registry; this plan only
  establishes the authoritative backend source and migrates current consumers.
- [x] Keep `Command-Line Interface 7` unchecked until the CLI also shares the
  application validation, rendering, and print-job services; this plan completes
  only its capability portion.
- [x] No unrelated files, generated artifacts, local labels, or new production
  dependencies are included.
