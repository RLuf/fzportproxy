# Changelog - fzportproxy

All notable changes to this project will be documented in this file.

## [0.1.0] - 2026-06-20
### Added
- Project initialization.
- Added `AGENTS.md` workspace rules.
- Created core module `wsl_manager.py` with support for listing WSL distros, fetching WSL IPv4, running netsh portproxy, managing Windows Firewall rules, and updating the Windows hosts file.
- Created `gui.py` containing a modern CustomTkinter desktop dashboard, dynamic WSL-linked rules, hostname-to-WSL mappings, and an automated background synchronization loop.
- Created `main.py` entry point with auto-UAC elevation checking.
- Created `build.py` compilation script for generating a single-file executable requiring UAC privileges.
- Documented project in `README.md` and added dependency list in `requirements.txt`.
