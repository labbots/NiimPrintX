# UI Foundation

This file defines the browser shell, responsive workbench, setup surfaces,
application states, accessibility baseline, and visual language. Implement it
against typed API contracts and deterministic fakes from
`01-platform-contracts-and-printing.md`.

## Review Sequence

1. API client boundary and explicit loading, empty, failure, and ready states.
2. Responsive workbench shell and paper-and-signal design tokens.
3. Printer and physical-label setup using backend capability data.
4. Connection and printer-status presentation.
5. Keyboard, focus, touch, contrast, and error behavior.

The broad application-interface requirements are exit criteria. A rendered shell
alone does not complete them.

## Application Interfaces

1. [ ] The application contains a graphical label editor for creating and printing labels.
4. [ ] The graphical editor contains printer setup, label setup, editing, image export, preview, and print controls in one window.
5. [ ] The application contains a React and TypeScript browser interface backed by the local Python service.
6. [ ] The application contains a responsive workbench with element tools, artboard, inspector, layers, printer state, and print action.

## Printer Models and Label Setup

1. [ ] The graphical editor contains target printer selection for D110, D11, D11_H, D101, and B18 models.
3. [ ] The graphical editor contains configured physical label sizes and DPI values for each listed model.
4. [ ] The graphical editor contains a label-size selector that updates the artboard dimensions.
8. [ ] The label selector contains physical label cards with dimensions, orientation, compatibility, and realistic previews.

## Printer Discovery and Connection

3. [ ] The graphical editor contains manual Connect and Disconnect actions.
4. [ ] The graphical editor contains a connected or disconnected status indicator.
7. [ ] The printer setup contains a cancellable scan and a selectable list of all discovered printers.
9. [ ] The connection workflow contains explicit idle, scanning, connecting, connected, reconnecting, disconnecting, and failed states.
12. [ ] The printer setup contains platform-specific Bluetooth permission and troubleshooting guidance.

## Printer Status and Protocol

5. [ ] The graphical interface contains battery, paper, lid, RFID, signal, and readiness status where the printer provides it.

## Onboarding, Accessibility, and Language

1. [ ] The application contains first-run guidance for printer selection, label selection, and the first element.
2. [ ] Empty states contain examples and direct actions for creating or opening a label.
3. [ ] The interface contains the user terms Printer, Label, Elements, Copies, and Print darkness.
4. [ ] The interface contains complete keyboard navigation, visible focus, accessible names, and logical focus restoration.
6. [ ] Status and validation information contains text or icons in addition to color.
7. [ ] The interface contains readable contrast, reduced-motion support, and touch-sized controls.
9. [ ] The visual interface contains the paper-and-signal design language with paper surfaces, graphite chrome, cyan connection state, and orange print action.
