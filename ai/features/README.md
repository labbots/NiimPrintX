# Product Features

This directory is the canonical product requirement checklist for NiimStudio.
Architecture and technology decisions are defined in `ai/project_context.md`.

**Legend:** `[x]` Implemented and retained | `[ ]` Missing, incomplete, or scheduled for replacement

Every requirement appears in exactly one feature file. Its section name and
item number form its stable reference, for example `Print Settings and Jobs 7`. Moving a
requirement must not change its wording, number, or status in the same change.
The checkbox indicates complete target behavior, not the presence of a partial
implementation or command shell.

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

1. Protect the existing CLI, BLE, protocol, and raster behavior.
2. Establish typed capability, document, rendering, persistence, and print-job
   contracts in `01-platform-contracts-and-printing.md`.
3. Move the CLI onto the shared services while preserving its current commands.
4. Pull from `04-later-scope.md` only after the core CLI print workflow is
   complete, unless product priorities explicitly change.

```text
CLI, protocol, and raster baseline
             |
             +--> shared contracts and fake adapters
                            |
                            +--> CLI print workflow
                                        |
                                        +--> later scope
```

## Feature Files

- `01-platform-contracts-and-printing.md`: CLI/protocol behavior, backend
  contracts, rendering, persistence, printer lifecycle, and print jobs
- `04-later-scope.md`: later CLI capabilities, diagnostics, packaging, and
  optional integrations

## First CLI Slice

The first reviewable slice establishes a backend-owned capability registry. It
should cover `Printer Models and Label Setup 6-7` and `Command-Line Interface 7`:
move the existing CLI width and density constants behind typed capability data
and verify unchanged CLI behavior.

## Decisions Required Before Implementation

The following product data is not yet authoritative and must be resolved in the
relevant backend contract:

- physical label sizes, compatibility, DPI, printable bounds, safe areas, and
  millimetre-to-pixel rounding
- whether `.niim` remains only a legacy import format or becomes the extension
  for the new safe JSON document
- whether ImageMagick is required, optional, or replaced by another font provider

## Related Guidance

- `ai/development_guidelines.md`: task context and execution rules
- `ai/plans/README.md`: implementation-plan workflow and template
- `ai/project_context.md`: architecture, ownership, and cross-layer contracts
- `ai/python_backend.md`: backend implementation rules
- `ai/testing.md`: test strategy
- `ai/definition_of_done.md`: required verification
