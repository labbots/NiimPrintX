# ADR 001: Frontend Framework

**Status:** Accepted, implementation gated

## Context

NiimStudio needs a local-first browser workbench over a localhost Python service,
with a possible later desktop shell. The UI includes an accessible SVG label
editor, immutable document operations, undo/redo, authoritative backend preview,
and sequenced printer and print-job state.

The repository currently has no frontend implementation or JavaScript dependency
investment. React, Vue, and Svelte can all satisfy the runtime architecture, so
the decision is based on maintenance and ecosystem risk rather than necessity.

## Decision

Use React function components, strict TypeScript, and Vite.

- Keep the document model and edit operations in framework-independent TypeScript.
- Use SVG as the initial editable geometry projection.
- Keep document/editor state, server resource state, and ephemeral UI state separate.
- Derive API types from the backend schema rather than copying DTOs by hand.
- Use backend rendering for authoritative monochrome preview and printing.
- Initially add no production component, editor, canvas, or state-management
  library beyond React and ReactDOM.
- Select and package any desktop shell through a separate decision.

React is selected because its mature editor, accessibility, testing, and
maintenance ecosystem lowers risk for a long-lived interaction-heavy editor.
Vue is a sound close alternative but offers no project-specific advantage that
justifies changing direction. Svelte is capable and concise, but its smaller
editor and accessibility ecosystem adds avoidable continuity risk. Bundle-size
differences are not material beside the packaged Python service and renderer.

## Consequences

- React-specific rendering and event concerns must not leak into the document model.
- SVG accessibility still requires semantic controls, an object list, keyboard
  editing, visible focus, and focus restoration; React does not provide these automatically.
- A future framework change remains possible while contracts and document
  operations stay independent of React.
- Canvas or WebGL is not introduced unless a representative performance test
  demonstrates that SVG is insufficient.

## Gates Before Scaffolding

1. Define a versioned JSON document schema with explicit units, stable IDs,
   asset rules, revision identity, and representative fixtures.
2. Specify document operations and transaction boundaries for undo/redo.
3. Move model dimensions, DPI, label sizes, density limits, orientation, and
   feature flags into one backend-owned capability registry.
4. Define the first typed API slice: capability snapshot, document validation,
   preview request/result, printer snapshot, and sequenced job events.
5. Choose one OpenAPI-to-TypeScript generation path and a contract-drift check.
6. Extract raster rendering behind an application boundary and prove preview and
   print parity with fixtures.
7. Define localhost binding, origin policy, local token delivery, WebSocket
   authentication, and reconnect sequencing.

The first UI foundation can be scaffolded once gates 1 through 5 have stable
draft contracts and deterministic fakes. Gates 6 and 7 must be complete before
real preview, printer, or print-job integration.

## Validation Spikes

Before committing to an editor library or changing framework, use plain React
and SVG to validate selection, drag, resize, keyboard movement, layers, and undo
with a representative 200-element document. The same basic edit workflow must
be completable with a keyboard and expose semantic controls without serious
automated accessibility violations.

## Reconsider When

- Maintainers have substantially stronger Vue or Svelte expertise and no React maintainer.
- A reusable editor or component implementation becomes available in another framework.
- Desktop-shell constraints demonstrably favor another framework.
- The SVG spike misses a defined responsiveness target and a suitable editor
  library strongly favors another framework.
- Measured dependency, binary-size, or baseline-hardware constraints show a
  material React disadvantage.
