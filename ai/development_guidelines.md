# Development Guidelines

This file is the local entry point for AI-assisted development.

## Core Principles

- Prefer the smallest correct change.
- Fix root causes rather than adding workarounds.
- Touch only files required by the task.
- Do not add speculative abstractions, dependencies, or compatibility code.
- Preserve user changes and never remove failing tests to make checks pass.
- Prefer readability over cleverness and explicit contracts over conventions hidden in code.

## Context Mapping

Load all rows that apply to the task. The rows are additive.

| Scope | Required local files |
| --- | --- |
| Architecture or cross-layer design | `ai/project_context.md`, `ai/features/README.md`, applicable feature file |
| Python domain, application, adapters, CLI, BLE, rendering, or persistence | `ai/project_context.md`, `ai/python_backend.md` |
| HTTP or WebSocket API | `ai/project_context.md`, `ai/python_backend.md` |
| React UI, editor behavior, styling, or accessibility | `ai/project_context.md`, `ai/features/README.md`, applicable feature file, `ai/react_frontend.md`, `ai/decisions/001-frontend-framework.md` |
| Tests | `ai/testing.md` and the files for the tested layer |
| Product behavior or priorities | `ai/features/README.md`, applicable feature file |
| Completion and verification | `ai/definition_of_done.md` |

Use only these local files for project rules. If documentation conflicts with
working code, determine whether the code is a legacy boundary or the document
is stale before changing either.

## Execution

1. Inspect the relevant code and current worktree.
2. Identify the affected architecture layer and its contract.
3. For cross-layer work, define the contract first and proceed one observable
   behavior at a time through domain, application, adapters, interfaces, and composition.
4. Write the test for the next behavior and run it to confirm that it fails for
   the intended reason before changing production code.
5. Implement the smallest change that makes the new test pass, then refactor
   while keeping the applicable tests green.
6. Run the applicable checks from `ai/definition_of_done.md`.

A written plan is useful for several independently verifiable steps. It is not
required for a small coherent fix.

## Hard Rules

- Never introduce `pickle` for persistence, IPC, or user-provided data.
- Never expose raw BLE/GATT operations through the browser API.
- Never edit generated files or commit secrets, caches, local logs, and ad hoc label files.
- Never suppress a quality failure or remove a failing test to complete a task.
- Ask before adding production dependencies or changing CI, release, installer, or network-exposure behavior.
