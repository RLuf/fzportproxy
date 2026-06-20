# fzportproxy

`fzportproxy` is a modern, clean Windows desktop GUI tool written in Python to manage `netsh interface portproxy` redirections, resolve dynamic WSL IP addresses, update Windows `hosts` mappings, and configure Windows Defender Firewall.

## Features

- **Port Forwarding Management**: Add, remove, and list Windows port redirects.
- **Dynamic WSL Support**: Automatically query active WSL instances and resolve their IP addresses.
- **Auto-Sync**: Keep port proxies and hostnames updated in the background if WSL IPs change.
- **Windows Firewall Integration**: Open/close inbound firewall ports matching the port forwards.
- **Hosts File Mappings**: Map hostnames (like `ubuntu.wsl`) to your WSL IPs directly in the Windows `hosts` file.

## Requirements

- Windows 10/11
- Python 3.10+
- Administrative Privileges (to write to the hosts file, manage portproxy rules, and configure the firewall)

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

To compile the binaries:
```bash
python build.py
```
This generates two files in the `dist` folder:
1. `fzportproxy.exe` - The standalone UAC-elevated application.
2. `setup_fzportproxy.exe` - The graphical setup installer that bundles the main application, allows selecting the installation directory, and registers it to run automatically with Windows.

## Releases and CI/CD

This project uses GitHub Actions to automate compilation and release generation.

### Automated Releases (via Tags)

To create a new release and automatically build and upload both executables:

1. Draft a new tag locally (e.g. `v1.0.0`):
   ```bash
   git tag v1.0.0
   ```
2. Push the tag to GitHub:
   ```bash
   git push origin v1.0.0
   ```
This automatically triggers the **Build and Release** workflow on GitHub Actions. It will compile both `fzportproxy.exe` and `setup_fzportproxy.exe` on a Windows runner and publish them as release assets under a new GitHub Release matching the tag name.

### Manual Builds (via GitHub UI)

You can also trigger a manual build on any branch:
1. Navigate to the **Actions** tab in your GitHub repository.
2. Select the **Build and Release** workflow.
3. Click **Run workflow**, select the branch, and click the run button.
4. Once completed, you can download the compiled `fzportproxy-builds` zip archive containing both executables directly from the workflow run artifacts.
