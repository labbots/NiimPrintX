# Python Backend Guidelines

Applies to Python domain, application, adapters, FastAPI, CLI, BLE, rendering,
and persistence code. Architecture and dependency direction are defined only in
`ai/project_context.md`.

## Code Style

- Follow PEP 8 and the formatter, linter, and type-checker configured in the repository.
- Use 4 spaces, no wildcard imports, and one final newline.
- Use `snake_case` for modules, functions, and variables; `PascalCase` for classes; `UPPER_SNAKE_CASE` for constants.
- Prefer modules and functions with one responsibility. Extract helpers only when they clarify or reuse behavior.
- Keep public APIs small. Prefix implementation-only functions and attributes with `_`.
- Use explicit imports and avoid import-time I/O, hardware access, task creation, or mutable global state.
- Add docstrings to public APIs when their contract is not evident from the name and types. Comments explain decisions, not syntax.

## Types and Models

- Type all public functions, methods, dataclass fields, and port protocols.
- Use `dataclass(frozen=True, slots=True)` or another immutable value type for domain values where practical.
- Use enums or discriminated types for finite states. Do not replace state machines with several booleans.
- Represent absence with `None` only when absence is part of the contract; never use `None` as a swallowed error.
- Use explicit units in names and types, such as `width_mm`, `offset_px`, and `timeout_seconds`.
- Keep Pydantic request and response models at the API boundary. Domain and application code must not depend on Pydantic.
- Do not create separate create/update models when their fields and invariants are genuinely identical.
- Validate at the owning boundary: syntax and transport shape in API models, business invariants in domain/application code.

## Domain and Application

- Domain objects contain business state and invariants, not BLE, filesystem, HTTP, GUI, or framework behavior.
- Application services are the entry point for use cases and depend on ports, not concrete adapters.
- A use case returns typed domain/application results or raises a typed application error.
- Keep service-to-service calls limited. Prefer a focused use case over orchestration spread across peer services.
- Validate the complete operation before making an irreversible state change.
- Keep transformations pure when possible. Do not duplicate conversion logic across API, CLI, and UI paths.
- Keep capability lookup, geometry, protocol framing, raster metadata, and job transitions deterministic.

## Async and Hardware

- Async code must never call blocking I/O on the event loop. Isolate unavoidable blocking work in an appropriate executor or adapter.
- Every scan, connect, command, print, heartbeat, and disconnect operation has an explicit timeout and cleanup path.
- Own background tasks explicitly. Store them, propagate failures, cancel them during shutdown, and await cancellation.
- Serialize commands when the protocol allows only one in-flight request.
- Correlate and validate responses; do not assume one BLE notification equals one complete response.
- Handle fragmented input, stale notifications, disconnects, cancellation, and partial print confirmation.
- Translate Bleak and OS exceptions into typed adapter/application failures while preserving the original exception as the cause.
- A context manager or `try/finally` must release notifications, connections, files, and temporary resources.

## Adapters and Persistence

- Adapters implement application-owned ports and contain technology-specific mapping.
- Keep Bleak imports in the BLE adapter and filesystem serialization in the storage adapter.
- Use versioned, validated JSON with bounded resource sizes and atomic replace for documents.
- Never deserialize executable Python objects from user-controlled data.
- Separate parent and child storage responsibilities when they have distinct operations.
- Avoid N+1 I/O. Batch related reads when one operation needs a collection of resources.
- Keep transactions or atomic write boundaries in the adapter that owns persistence. Application code coordinates multiple ports only when the use case requires it.

## FastAPI and WebSocket

- Route handlers validate transport input, call an application use case, and map its result. They contain no BLE, storage, rendering, or business logic.
- Inject application services through the composition root. Do not construct concrete adapters in handlers.
- Use typed request, response, error, and event models. Keep one authoritative schema for Python and TypeScript clients.
- Map typed application errors centrally to stable status codes and error bodies.
- Do not expose tracebacks, filesystem paths, tokens, BLE characteristics, or raw packets in normal responses.
- Commands that can be retried or duplicated need explicit idempotency semantics.
- WebSocket events include resource ID, sequence number, event type, timestamp, and typed payload.
- A reconnecting client first obtains a current snapshot and then accepts only newer events.
- Enforce localhost binding, origin validation, and session-token rules from `ai/project_context.md`.

## CLI

- CLI commands are inbound adapters over the same application services as the API.
- Keep parsing and terminal formatting in the CLI; keep printer behavior in application services.
- Return actionable errors and non-zero exit codes. Technical details belong behind verbose output.
- Always disconnect and clean up on success, error, interruption, and cancellation.

## Errors and Logging

- Raise the most specific domain or application exception available.
- Do not catch `Exception` unless at a process boundary or to add context before re-raising.
- Preserve exception chaining with `raise ... from exception` when translating errors.
- Log once at the boundary that owns reporting. Avoid logging and re-logging the same failure in every layer.
- Never log secrets, local tokens, document contents, or unredacted hardware identifiers unnecessarily.
