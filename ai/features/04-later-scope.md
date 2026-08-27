# Later CLI Scope

These requirements are CLI capabilities that are not prerequisites for the core
print workflow. Moving an item into an earlier delivery file is a
product-priority change and should include acceptance criteria for the affected
vertical slice.

## Print History and Diagnostics

1. [ ] The CLI contains print history with printer, settings, timestamp, progress, and result.
2. [ ] Print history contains safe reprint with current printer and label validation.
3. [ ] Failed jobs contain save-for-later and retry commands.
4. [ ] The application contains a diagnostics bundle with sanitized logs, environment details, and protocol summary.
5. [ ] CLI failures contain what happened, document safety, printer state, and the next safe action.

## Distribution

1. [ ] The repository contains CLI packages for Linux, macOS, and Windows.
2. [ ] The repository contains tag-triggered Linux, macOS, and Windows release workflows for the CLI.
3. [ ] Release verification contains automated package smoke tests on every supported platform.
4. [ ] Releases contain aligned CLI versions, signed artifacts, and document migration checks.

## Optional Integrations

1. [ ] The application contains multi-printer batch routing.
2. [ ] The application contains plugin providers for external data sources.
