# Implementation Plans

Implementation plans turn a small slice of the canonical requirements in
`ai/features/` into executable engineering work. A plan is required before a
feature slice that changes multiple layers, introduces a contract, or needs
several independently verifiable steps.

Plans do not redefine product requirements. Reference requirements by section
and item number instead of copying a competing checklist.

## Plan Lifecycle

1. Create `ai/plans/<feature-slug>.md` with status `Draft`.
2. Inspect the current implementation and replace assumptions with concrete file
   paths, existing behavior, and identified gaps.
3. Resolve open product decisions and obtain required dependency or platform
   approvals before changing the plan status to `Ready`.
4. Change the status to `In progress` and complete each behavior in dependency
   order using the red-green-refactor cycle below.
5. Run every applicable check from `ai/definition_of_done.md` and record any
   unavailable check precisely.
6. Change the status to `Completed` only after implementation, tests,
   documentation, and checklist reconciliation are finished.

Allowed statuses are `Draft`, `Ready`, `In progress`, `Blocked`, and `Completed`.
Keep only one plan `In progress` unless its work streams are explicitly independent.

## Test-Driven Development

Every plan that changes production behavior must order work test-first. Repeat
this cycle for each independently observable behavior:

1. **Red:** Write or update the smallest test that expresses the next acceptance
   criterion. Run it and confirm that it fails for the intended missing behavior.
2. **Green:** Implement only enough production code to make that test pass. Run
   the focused test again.
3. **Refactor:** Improve names, structure, or duplication without changing
   behavior, keeping the focused and affected tests green.
4. Continue with the next behavior only after the current cycle is green.

Do not write production behavior before its failing test has been observed. For
cross-layer work, start with the narrowest useful contract or application test,
then add boundary and integration tests before implementing those boundaries.
When existing behavior lacks coverage and is only being refactored, first add a
characterization test and observe it pass; any changed behavior still requires a
new failing test.

Documentation-only changes do not require artificial tests. The plan must state
why no executable behavior changes and list the applicable documentation checks.

## Required Plan Content

Use this structure:

```markdown
# <Plan Title>

**Status:** Draft

## Feature References

- Primary: `<Section> <item>`
- Supporting: `<Section> <item>`

## Goal

State the user-visible or architectural outcome in one short paragraph.

## Acceptance Criteria

- Describe observable completion for this slice.
- Include failure, empty, loading, disconnected, or accessibility states when applicable.

## Out of Scope

- Name adjacent requirements deliberately excluded from this plan.

## Current State

Document relevant code paths, retained behavior, tests, and the root gap.

## Contracts and Decisions

Record types, ownership, API or persistence boundaries, migrations, and decisions
that must be settled. Link existing architecture documents instead of repeating them.

## Implementation Steps

- [ ] Red: add the test for the first acceptance criterion and confirm its expected failure.
- [ ] Green: implement the smallest change that makes the focused test pass.
- [ ] Refactor while keeping the focused and affected tests green.
- [ ] Repeat red-green-refactor for each remaining acceptance criterion.
- [ ] Add boundary or integration tests before implementing the corresponding boundary.

## Verification

- [ ] Exact applicable command from `ai/definition_of_done.md`.
- [ ] Feature-specific acceptance or integration check.

## Completion

- [ ] Documentation and cross-references reflect the implementation.
- [ ] Canonical feature statuses were reviewed and updated only where complete.
- [ ] No unrelated files or generated artifacts are included.
```

## Plan Sizing

A plan should normally produce one reviewable vertical slice. Split it when it
requires unrelated user outcomes, independently deployable migrations, or more
than one uncertain architecture decision. Do not split merely by backend and
frontend layer when neither part is useful or verifiable on its own.

Implementation steps must preserve test-first ordering. Do not group all tests
after production steps or create a final "add tests" phase.

Broad feature requirements can be delivered through several plans. Each plan
must state what remains before the broad requirement can be marked complete.
