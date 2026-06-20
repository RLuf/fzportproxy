# Changelog - fzportproxy

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-06-20
### Fixed
- **Critical: Fixed startup crash** (`bad event type or keysym "StateChanged"`). The `<StateChanged>` event does not exist in Tkinter/Tcl — replaced with the standard `<Unmap>` event for system tray minimization detection.
- **Fixed missing `import re`** in `gui.py` that could cause crashes when validating IP addresses or hostnames.

### Changed
- **Migrated compiler from PyInstaller to Nuitka**. Nuitka compiles Python to native C code, producing real machine-code binaries instead of self-extracting archives. This drastically reduces Windows Defender and antivirus false positive detections.
- **Centralized version management** into a new `version.py` module. All files (`gui.py`, `installer.py`, `build.py`) now reference `APP_VERSION` from a single source.
- **Versioned binary filenames**: Compiled executables are now named `fzportproxy_v1.1.0.exe` and `setup_fzportproxy_v1.1.0.exe` instead of generic names.
- **Updated `build.py`**: Complete rewrite to use Nuitka with auto-detection of MinGW64 or MSVC compiler backend.
- **Updated `requirements.txt`**: Replaced `pyinstaller` with `nuitka` and `ordered-set`.
- **Updated GitHub Actions** (`release.yml`): CI now uses Nuitka with MSVC via `ilammy/msvc-dev-cmd@v1` action and uploads versioned binaries.

### Added
- **`version.py`**: New centralized module containing `APP_VERSION`, `APP_NAME`, `APP_AUTHOR`, and `APP_WEBSITE`.
- **`sign.py`**: New code signing script that auto-generates a self-signed certificate (`CN=FZPortProxy, O=Webstorage`) via PowerShell and signs executables using `signtool.exe`. Includes timestamping via DigiCert for long-term validity.
- **Installer versioning**: The setup wizard now displays the current version in the title and banner.

### Removed
- Removed `fzportproxy.spec` and `setup_fzportproxy.spec` (PyInstaller spec files, no longer needed).
- Removed `pyinstaller` dependency.

## [1.0.0] - 2026-06-20
### Added
- **System Tray Integration**: Added full system tray minimization support (via `pystray`). The application now hides to the system tray on close or minimization (with a configuration toggle in the settings tab).
- **Custom Setup Installer**: Added a CustomTkinter-based installer (`installer.py`) that packages the standalone executable, prompts the user for the installation folder, and creates shortcuts including an option to start automatically with Windows (via user Startup directory).
- **Branding & Help Tab**: Added Roger Luft (VeilWalker) / Webstorage branding and a "Help & About" button in the header opening a descriptive modal with quick usage topics, author contacts, and a visually highlighted **Donate** button (with Copy Pix Key option).
- **No Console Flashing**: Added `creationflags=subprocess.CREATE_NO_WINDOW` to all commands executed in Windows via the `subprocess` module, completely stopping cmd/powershell windows from flashing.
- **Double-compile Release Chain**: Modified `build.py` to chain compile the main application followed by the installer bundling the app binary.

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
