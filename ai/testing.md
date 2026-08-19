# Testing Guidelines

Tests protect behavior and architecture without requiring a live printer.

## General Rules

- Use Given-When-Then structure, either through clear blocks or concise comments where they improve readability.
- Test public behavior and contracts, not private implementation details.
- Keep each test focused on one behavior. Use parameterization only for distinct logical branches, boundaries, or error states.
- Use descriptive test names that state the condition and expected outcome.
- Compare complete value objects and collections when practical instead of asserting unrelated fields one by one.
- Use distinct values for fields that could be accidentally swapped.
- Keep expected input and output visible in tests for pure converters and codecs.
- Use shared factories for large recurring integration fixtures, not to hide the behavior under test.
- Never depend on test order, wall-clock timing, local Bluetooth state, or an existing user file.
- A regression test must fail for the original defect and pass for the fix.

## Python Unit Tests

- Use Pytest and plain assertions unless the repository config establishes another convention.
- Test domain values, geometry, capabilities, schema migrations, protocol codecs, rendering metadata, and state transitions as pure units.
- Replace application ports with small fakes that model behavior. Prefer fakes over deep mocks for stateful BLE, storage, clock, and job interactions.
- Mock only the direct boundary needed by the unit under test.
- Verify outcomes first; verify calls only when orchestration itself is the contract.
- Cover success, timeout, cancellation, disconnect, malformed response, fragmented response, cleanup, and duplicate-prevention branches where applicable.
- Use deterministic clocks, IDs, random sources, fonts, and image fixtures.

## Backend Integration Tests

- Exercise real internal layers together and fake only external boundaries such as BLE hardware and OS integration.
- Drive FastAPI through HTTP/WebSocket test clients rather than calling route functions directly.
- Verify status, typed body/event, ordering, and side effects.
- Reset storage, fake transports, subscriptions, and background tasks before each test.
- Test WebSocket snapshot/reconnect behavior, stale event rejection, and monotonic sequencing.
- Test safe document open/save, atomic-write failure, schema migration, and bounded invalid input.
- Compare preview and print raster bytes or stable fixtures for supported rendering scenarios.

## Frontend Tests

- Use the test runner and Testing Library setup defined by the frontend project.
- Query rendered UI by role, label, and visible text rather than implementation classes or component internals.
- Test user workflows with realistic pointer and keyboard interactions.
- Mock the typed network boundary, not internal hooks or child components, for feature tests.
- Verify loading, empty, stale, offline, failure, retry, cancellation, and success states.
- Include accessibility checks for critical screens and keyboard-only completion of the basic label workflow.
- Use end-to-end browser tests for printer setup, editing, review, and print progress with a fake backend; keep the suite small and high value.

## Hardware Tests

- Keep a documented manual or opt-in matrix for supported printer models and operating systems.
- Hardware tests supplement automated fake-transport tests and never run as the only CI evidence.
- Record printer model, firmware, label type, expected raster dimensions, and observed protocol result.
- Do not make normal test execution discover or connect to nearby printers.

## Test Review

Reject tests that pass without exercising the changed behavior, merely reproduce
implementation code, hide failures with broad exception handling, or use sleeps
instead of deterministic synchronization.
