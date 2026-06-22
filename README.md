# fzportproxy

`fzportproxy` is a modern, clean Windows desktop GUI tool written in Python to manage `netsh interface portproxy` redirections, resolve dynamic WSL IP addresses, update Windows `hosts` mappings, and configure Windows Defender Firewall.

## Features

- **Port Forwarding Management**: Add, remove, and list Windows port redirects.
- **Dynamic WSL Support**: Automatically query active WSL instances and resolve their IP addresses.
- **Auto-Sync**: Keep port proxies and hostnames updated in the background if WSL IPs change.
- **Windows Firewall Integration**: Open/close inbound firewall ports matching the port forwards.
- **Hosts File Mappings**: Map hostnames (like `ubuntu.wsl`) to your WSL IPs directly in the Windows `hosts` file.
- **System Tray Minimization**: Minimize to system tray instead of closing, with configurable behavior.

## Requirements

- Windows 10/11
- Python 3.10+
- Administrative Privileges (to write to the hosts file, manage portproxy rules, and configure the firewall)
- **For compilation**: MinGW64 (gcc) or MSVC (Visual Studio Build Tools with C++ workload)

## Development Setup

```bash
# Clone the repository
git clone https://github.com/RLuf/fzportproxy.git
cd fzportproxy

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

## Compilation

This project uses **Nuitka** to compile Python to native C code, producing real machine-code binaries that are far less likely to trigger antivirus false positives.

### Prerequisites

One of the following C compilers must be installed:
- **MinGW64**: Download from [MinGW-w64](https://www.mingw-w64.org/) and ensure `gcc.exe` is accessible (e.g., `C:\mingw64\bin\`)
- **MSVC**: Install [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) with the "Desktop development with C++" workload

### Build

```bash
python build.py
```

This generates two versioned files in the `dist` folder:
1. `fzportproxy_v{VERSION}.exe` — The standalone UAC-elevated application.
2. `setup_fzportproxy_v{VERSION}.exe` — The graphical setup installer that bundles the main application, allows selecting the installation directory, and registers it to run automatically with Windows.

### Code Signing (Optional)

After building, you can digitally sign the executables:

```bash
python sign.py
```

This will:
1. Generate a self-signed certificate (`CN=FZPortProxy, O=Webstorage`) if one doesn't exist
2. Sign all `.exe` files in the `dist/` directory using `signtool.exe`
3. Timestamp the signature via DigiCert for long-term validity

> **Note**: Self-signed certificates are for internal/development use. For public distribution, replace with a certificate from a trusted Certificate Authority (CA).

**Requirement**: The [Windows SDK](https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/) must be installed (provides `signtool.exe`).

## Releases and CI/CD

This project uses GitHub Actions to automate compilation and release generation.

### Automated Releases (via Tags)

To create a new release and automatically build and upload both executables:

1. Draft a new tag locally (e.g. `v1.1.0`):
   ```bash
   git tag v1.1.0
   ```
2. Push the tag to GitHub:
   ```bash
   git push origin v1.1.0
   ```
This automatically triggers the **Build and Release** workflow on GitHub Actions. It will compile both executables using Nuitka on a Windows runner with MSVC and publish them as release assets under a new GitHub Release matching the tag name.

### Manual Builds (via GitHub UI)

You can also trigger a manual build on any branch:
1. Navigate to the **Actions** tab in your GitHub repository.
2. Select the **Build and Release** workflow.
3. Click **Run workflow**, select the branch, and click the run button.
4. Once completed, you can download the compiled `fzportproxy-builds` zip archive containing both executables directly from the workflow run artifacts.

## Version Management

The application version is centralized in [`version.py`](version.py). To release a new version:
1. Update `APP_VERSION` in `version.py`
2. Update `CHANGELOG.md`
3. Commit, tag, and push

## Code Signing Password Management

The code signing password (`sign.py`) is resolved using a 3-tier chain:

1. **Environment variable** `FZ_CODESIGN_PASSWORD` — highest priority, ideal for CI/CD secrets
2. **Local file** `sign-pass.cfg` — a single-line plain text file in the project root (gitignored), ideal for developer machines
3. **Hardcoded default** — `FZPortProxy2026!`, the public fallback for development/CI builds

A message is printed indicating which source was used when running `python sign.py`.

## Language / Internationalization

FZPortProxy supports **English** and **Portuguese** interfaces. The language can be switched from the **Settings** tab via the "Language / Idioma" dropdown. A restart is required after changing the language.

The language preference is persisted in `config.json` under the `"language"` key (`"en"` or `"pt"`).

## Rule Persistence

Port forwarding rules and hostname mappings are managed at the Windows system level (`netsh interface portproxy` and the `hosts` file). This means **rules remain active until changed** — FZPortProxy can be closed and reopened at any time without losing your configuration.
