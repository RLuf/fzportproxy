# Changelog - fzportproxy

All notable changes to this project will be documented in this file.

## [0.1.1] - 2026-06-20
### Added
- Configured GitHub Actions release workflow (`.github/workflows/release.yml`) to automatically compile the standalone Windows `.exe` executable via PyInstaller and upload it as a release asset when pushing a version tag (e.g. `v*`).
- Configured run artifact uploading in GitHub Actions to retrieve the built executable from manual workflow runs.
- Updated documentation with step-by-step instructions for publishing releases.

### Fixed
- Fixed startup crash due to unsupported `segment_button_width_medium` argument during `CTkTabview` initialization in `gui.py`.
- Replaced console-blocking `input()` with a graphical `tkinter.messagebox` in `main.py` when handling startup errors in windowed/non-console mode.

## [0.1.0] - 2026-06-20
### Added
- Project initialization.
- Added `AGENTS.md` workspace rules.
- Created core module `wsl_manager.py` with support for listing WSL distros, fetching WSL IPv4, running netsh portproxy, managing Windows Firewall rules, and updating the Windows hosts file.
- Created `gui.py` containing a modern CustomTkinter desktop dashboard, dynamic WSL-linked rules, hostname-to-WSL mappings, and an automated background synchronization loop.
- Created `main.py` entry point with auto-UAC elevation checking.
- Created `build.py` compilation script for generating a single-file executable requiring UAC privileges.
- Documented project in `README.md` and added dependency list in `requirements.txt`.
