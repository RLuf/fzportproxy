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

To compile to a standalone `.exe`:
```bash
python build.py
```
This generates a single executable under the `dist` folder.
