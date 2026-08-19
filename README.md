# NiimStudio

NiimStudio is a local-first label design and printing application for Niimbot
printers.

## Repository Structure

- `backend/`: Python domain, application, printer adapters, API, and CLI
- `frontend/`: React and TypeScript user interface (planned)
- `desktop/`: desktop application shell (planned)

The current implementation is the standalone Python console application in
`backend/`. See [`backend/README.md`](backend/README.md) for installation and
usage instructions.

The historical Tkinter application remains available on the non-merge
`legacy/tkinter-app` branch.

## License

GNU GPLv3. See [`LICENSE`](LICENSE).
