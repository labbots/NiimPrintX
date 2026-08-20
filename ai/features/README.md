# Product Features

This directory is the canonical product requirement checklist for NiimStudio.
Architecture and technology decisions are defined in `ai/project_context.md` and
`ai/decisions/001-frontend-framework.md`.

**Legend:** `[x]` Implemented and retained | `[ ]` Missing, incomplete, or scheduled for replacement

Every requirement appears in exactly one feature file. Its section name and
item number form its stable reference, for example `Label Artboard 11`. Moving a
requirement must not change its wording, number, or status in the same change.
The checkbox indicates complete target behavior, not the presence of a partial
implementation or UI shell.

## Implementation Workflow

The feature files define product scope and acceptance. They are not implementation
plans and their file boundaries are not intended to be completed in one change.
Every development cycle follows this process:

1. Select one coherent vertical slice from the delivery order below.
2. Identify its primary requirement and any supporting requirements by stable
   reference, such as `Printer Models and Label Setup 6`.
3. Create `ai/plans/<feature-slug>.md` using `ai/plans/README.md`. The plan maps
   requirements to the current code, contracts, implementation steps, and checks.
4. Resolve product decisions and dependency approvals called out by the plan
   before implementation reaches the affected boundary.
5. Execute and verify the plan one independently testable step at a time, keeping
   its status and task checkboxes current.
6. On completion, reconcile the result with this checklist. Mark a product
   requirement `[x]` only when its complete wording is implemented and retained.

A completed plan may deliver only part of a broad requirement. In that case the
plan is complete while the canonical product checkbox remains `[ ]`. Plans are
execution records; the feature files remain the source of product truth.

## Delivery Order

The files separate work streams; their checklists are not a mandate to implement
every item in file order.

1. Establish the pre-UI contracts in
   `01-platform-contracts-and-printing.md`: document schema, capability snapshot,
   renderer boundary, typed API, fake adapters, and local security handshake.
2. Build `02-ui-foundation.md` against those contracts and deterministic fakes.
3. Deliver `03-editor-core.md` as small vertical slices, beginning with document
   operations, a physical artboard, text editing, and undo/redo.
4. Integrate authoritative preview and print jobs from
   `01-platform-contracts-and-printing.md` only after the editor can produce a
   valid document.
5. Pull from `04-later-scope.md` only after the core create-preview-print workflow
   is complete, unless product priorities explicitly change.

```text
platform contracts and fakes
          |
          +--> UI foundation --> editor core
                                      |
renderer and printer services --------+--> preview and print integration
                                                |
                                                +--> later scope
```

## Feature Files

- `01-platform-contracts-and-printing.md`: retained CLI/protocol behavior,
  backend contracts, rendering, persistence, printer lifecycle, and print jobs
- `02-ui-foundation.md`: browser shell, workbench, setup surfaces, application
  states, accessibility, and visual language
- `03-editor-core.md`: minimum useful artboard, text and image editing, layers,
  undo/redo, preview, and document safety
- `04-later-scope.md`: advanced editing, smart content, templates, recovery,
  history, packaging, localization, and optional integrations

## First UI Slice

The first reviewable UI slice is deliberately narrow:

1. Load a typed capability snapshot from a fake API boundary.
2. Show loading, failure, empty, and ready states in the workbench shell.
3. Select a printer model and compatible physical label without hard-coded
   capability data in components.
4. Create an empty versioned document and render its physical and printable
   boundaries as SVG.
5. Complete the flow with keyboard-only operation and focused frontend tests.

This slice does not require BLE, physical printing, a component library, a state
library, a canvas library, or a desktop shell.

The recommended first implementation plan is `capability-registry`. It should
cover `Printer Models and Label Setup 6-7` and the capability portion of
`Command-Line Interface 7`: introduce backend-owned typed capability data, move
the existing CLI width and density constants behind it, and verify current CLI
behavior without adding the HTTP API or frontend dependencies yet.

## Decisions Required Before Implementation

The following product data is not yet authoritative and must be resolved in the
relevant backend contract rather than guessed in the UI:

- supported model matrix: the UI currently names D101 while the CLI supports B1
  and B21 instead
- physical label sizes, compatibility, DPI, printable bounds, safe areas, and
  millimetre-to-pixel rounding
- whether `.niim` remains only a legacy import format or becomes the extension
  for the new safe JSON document
- whether ImageMagick is required, optional, or replaced by another font provider
- whether the native shell is a release requirement or later convenience

## Related Guidance

- `ai/development_guidelines.md`: task context and execution rules
- `ai/plans/README.md`: implementation-plan workflow and template
- `ai/project_context.md`: architecture, ownership, and cross-layer contracts
- `ai/react_frontend.md`: frontend implementation rules
- `ai/python_backend.md`: backend implementation rules
- `ai/testing.md`: test strategy
- `ai/definition_of_done.md`: required verification
