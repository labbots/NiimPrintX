# React Frontend Guidelines

Applies to the React/TypeScript browser UI. Product workflows and visual intent
are in `ai/project_features.md`; backend ownership and contracts are in
`ai/project_context.md`.

## Structure and Dependencies

- Organize code by product feature, with small shared UI and API modules only for genuinely shared behavior.
- Components depend on typed frontend services/hooks; they do not know endpoint construction, WebSocket framing, or backend implementation details.
- Use strict TypeScript. Avoid `any`, unchecked casts, non-null assertions, and duplicate handwritten backend schemas.
- Keep domain document IDs independent of React keys, DOM IDs, SVG IDs, and canvas object IDs.
- Do not add a component, state, styling, or editor library until a concrete feature demonstrates the need.
- Follow existing project conventions once the frontend scaffold defines them; do not introduce a second pattern.

## Component Design

- Prefer function components, composition, and platform semantics over wrapper-heavy abstractions.
- Keep rendering pure. Do not start network calls, timers, subscriptions, or state updates during render.
- Derive values during render when possible instead of mirroring them into state with an effect.
- Use effects only to synchronize with external systems and clean up every subscription, timer, and request.
- Prefer event-driven updates for user actions. Use transitions or deferred values for non-urgent expensive UI updates when they measurably improve responsiveness.
- Do not add `useMemo` or `useCallback` by default. Use them only for a demonstrated identity or performance requirement and follow the project's React Compiler setup.
- Preserve user edits across printer reconnects, preview failures, and panel/layout changes.

## State and Contracts

- Separate document/editor state, server resource state, and ephemeral UI state.
- Keep the backend capability snapshot authoritative for printer and label options.
- Apply WebSocket events only when their sequence is newer than the current snapshot/event.
- Reconnect by refreshing the snapshot before resuming events; never replay a print command automatically.
- Model loading, empty, stale, disconnected, success, failure, and cancellation explicitly.
- Display effective print settings from the validated backend response, not optimistic local assumptions.
- Keep units explicit in TypeScript types and variable names.

## API Boundary

- Use one API client boundary for base URL, local token, error decoding, cancellation, and retry policy.
- Never send raw BLE/GATT commands or accept arbitrary backend paths/URLs from UI state.
- Retry reads only when safe. Mutating and print requests require defined idempotency behavior before retry.
- Cancel obsolete preview and search requests. Ignore responses that no longer match the active document revision.
- Convert transport errors into typed frontend errors before they reach components.

## Editor and Rendering

- The logical document is the source of truth; SVG or Canvas is a projection.
- Every edit must be expressible as a document operation suitable for undo/redo.
- Use stable IDs and immutable updates for document elements.
- Keep selection, hover, guides, and viewport state out of the persisted document.
- The final monochrome preview comes from the backend renderer used by printing.
- Show overflow, printable bounds, orientation, dimensions, and stale-preview state before printing.
- Never silently resize, rotate, crop, or change print settings.

## Accessibility and Responsive UI

- Use semantic HTML first and ARIA only where native semantics are insufficient.
- Every action is keyboard reachable, has visible focus, and has an accessible name.
- Preserve a logical focus order and return focus after dialogs, drawers, and destructive actions.
- Do not communicate status through color alone. Respect reduced motion and readable contrast.
- Use touch-sized controls and support desktop plus narrow tablet layouts without hiding the primary workflow.
- Announce connection, validation, and print progress changes appropriately without flooding assistive technology.

## Styling

- Follow the "paper and signal" direction in `ai/project_features.md` rather than a generic dashboard aesthetic.
- Use design tokens or CSS custom properties for color, spacing, typography, focus, and surface values.
- Prefer classes and component styles over inline style objects, except for genuinely dynamic geometry.
- Keep custom styles purposeful; avoid decorative gradients, excessive cards, and animation without workflow value.
- Status components include text or an icon in addition to color.

## Error UX

- User-facing errors explain what happened, document safety, printer state, and the next safe action.
- Keep raw exceptions and protocol details out of primary messages; provide sanitized diagnostics separately.
- A failed external call must leave the editor usable whenever the document itself is still valid.
- Disable an action only when necessary and explain why near the control.
