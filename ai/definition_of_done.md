# Definition of Done

All applicable checks must pass. A failed required check means the task is not
complete.

## Required Checks

Run checks in this order where they apply:

| Scope | Check | Command |
| --- | --- | --- |
| Every change | Diff whitespace and conflict markers | `git diff --check` |
| Python | Syntax/import compilation | `poetry --directory backend run python -m compileall -q backend/src/niimstudio` |
| Python metadata | Poetry validity | `poetry --directory backend check` |
| Python tests | Unit, integration, and minimum 80% coverage | `poetry --directory backend run pytest -c backend/pyproject.toml` |
| Python lint | Ruff static checks | `poetry --directory backend run ruff check backend/src/niimstudio backend/tests` |
| Python format | Ruff formatting | `poetry --directory backend run ruff format --check backend/src/niimstudio backend/tests` |
| Frontend | Type check, lint, tests, production build | Run the scripts defined in `frontend/package.json` |
| API/frontend integration | Contract and browser integration tests | Run the repository-defined suites |
| Documentation | Paths, commands, and cross-references | Verify against the current tree |

Do not invent commands for tooling the repository has not configured. If a
required suite or configuration does not exist yet, report that gap explicitly.

## Review Checklist

- The change solves the root cause with the smallest coherent scope.
- Dependency direction follows `ai/project_context.md`.
- Public behavior and contracts are typed and tested.
- Async work has timeout, cancellation, error propagation, and cleanup.
- Persistence and imported data are versioned, validated, bounded, and non-executable.
- UI changes include loading, empty, failure, offline/disconnected, and accessible interaction states as applicable.
- Logs and responses contain no secrets, raw tokens, unsafe paths, or unnecessary hardware identifiers.
- No generated files, caches, logs, local labels, or unrelated user changes are included.
- A live printer is not the only evidence for protocol or print correctness.
- A senior engineer could review and reproduce the result without hidden setup.

## Failure Handling

- Fix a failing check and rerun it.
- Never skip a failure, weaken a check, or delete a failing test without explicit approval.
- Distinguish failures caused by the change from pre-existing environment or repository failures and report both accurately.
- If a check cannot run, state the exact reason and what remains unverified.
