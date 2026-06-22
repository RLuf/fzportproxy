# Copyright (c) 2026 Roger Luft (VeilWalker)
# Licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0).
# See LICENSE file in the project root for full license text.
# https://creativecommons.org/licenses/by/4.0/

import subprocess
import re
import sys
import ctypes
import os

def is_admin():
    """Check if the current process is running with Administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def run_as_admin_relaunch():
    """Relaunch the script with Administrator privileges using UAC elevation."""
    if not is_admin():
        # Re-run the program with admin rights
        # sys.executable is the python interpreter
        # sys.argv is the arguments passed to the script
        params = " ".join([f'"{arg}"' for arg in sys.argv])
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, params, None, 1
            )
        except Exception as e:
            print(f"Failed to elevate process: {e}")
        sys.exit(0)

def list_wsl_distros():
    """
    Run 'wsl.exe -l -v' and parse the output.
    Returns a list of dicts: [{'name': 'Ubuntu', 'is_default': True, 'state': 'Running', 'version': 2}]
    """
    try:
        # Run wsl -l -v. WSL output is typically UTF-16 on Windows.
        result = subprocess.run(["wsl.exe", "--list", "--verbose"], capture_output=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        
        # Try decoding as UTF-16, then UTF-8, then fallback to cp1252
        stdout_bytes = result.stdout
        try:
            output = stdout_bytes.decode("utf-16")
        except UnicodeDecodeError:
            try:
                output = stdout_bytes.decode("utf-8")
            except UnicodeDecodeError:
                output = stdout_bytes.decode("cp1252", errors="ignore")
                
        lines = output.strip().split("\n")
        distros = []
        if len(lines) <= 1:
            return distros
            
        # First line is header, e.g. "  NAME      STATE      VERSION"
        # We can find column positions or just parse based on regex
        for line in lines[1:]:
            line_str = line.strip()
            if not line_str:
                continue
                
            # A line looks like: "*   Ubuntu-24.04    Running    2"
            is_default = line_str.startswith("*")
            clean_line = line_str.lstrip("*").strip()
            
            # Split by multiple spaces
            parts = re.split(r'\s{2,}', clean_line)
            if len(parts) >= 2:
                name = parts[0].strip()
                state = parts[1].strip()
                version = int(parts[2].strip()) if len(parts) > 2 and parts[2].strip().isdigit() else 2
                distros.append({
                    "name": name,
                    "is_default": is_default,
                    "state": state,
                    "version": version
                })
        return distros
    except Exception as e:
        print(f"Error listing WSL distros: {e}")
        return []

def get_wsl_ip(distro_name):
    """
    Get the IPv4 address of a specific WSL distro.
    Tries hostname -I first, falls back to ip addr.
    """
    try:
        # Try hostname -I
        result = subprocess.run(
            ["wsl.exe", "-d", distro_name, "-e", "hostname", "-I"],
            capture_output=True,
            text=True,
            errors="ignore",
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if result.returncode == 0 and result.stdout.strip():
            ips = result.stdout.strip().split()
            # Filter for valid IPv4 (simple check)
            for ip in ips:
                if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip) and not ip.startswith("172.17."):
                    return ip
            if ips:
                return ips[0]
                
        # Fallback to ip -4 -o addr show eth0
        result = subprocess.run(
            ["wsl.exe", "-d", distro_name, "-e", "ip", "-4", "-o", "addr", "show", "eth0"],
            capture_output=True,
            text=True,
            errors="ignore",
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if result.returncode == 0 and result.stdout.strip():
            # e.g. "2: eth0    inet 172.21.139.123/20 ..."
            match = re.search(r"inet\s+([0-9.]+)", result.stdout)
            if match:
                return match.group(1)
                
        # Universal fallback (any active interface IPv4 except docker/loopback)
        result = subprocess.run(
            ["wsl.exe", "-d", distro_name, "-e", "ip", "-4", "-o", "addr", "show"],
            capture_output=True,
            text=True,
            errors="ignore",
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if "lo" in line or "docker" in line:
                    continue
                match = re.search(r"inet\s+([0-9.]+)", line)
                if match:
                    return match.group(1)
                    
        return None
    except Exception as e:
        print(f"Error getting IP for {distro_name}: {e}")
        return None

def list_portproxy_rules():
    """
    List all active IPv4 netsh portproxy rules.
    Returns a list of dicts: [{'listen_addr': '0.0.0.0', 'listen_port': '80', 'connect_addr': '172.21.139.123', 'connect_port': '80'}]
    """
    try:
        # Use shell=True to avoid path/locale search issues with netsh
        result = subprocess.run(
            "netsh interface portproxy show all",
            capture_output=True,
            shell=True,
            check=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        # Try decoding as standard Windows console encoding (cp850 or cp1252 or utf-8)
        stdout_bytes = result.stdout
        for encoding in ["cp850", "cp1252", "utf-8"]:
            try:
                output = stdout_bytes.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            output = stdout_bytes.decode("utf-8", errors="ignore")

        rules = []
        lines = output.splitlines()
        
        # We search for the dashed line separating headers from content
        header_index = -1
        for idx, line in enumerate(lines):
            if "---" in line:
                header_index = idx
                break
                
        if header_index == -1:
            # Let's try parsing any line containing 4 tokens where 2nd and 4th are ports
            for line in lines:
                parts = line.split()
                if len(parts) == 4 and parts[1].isdigit() and parts[3].isdigit():
                    rules.append({
                        "listen_addr": parts[0],
                        "listen_port": int(parts[1]),
                        "connect_addr": parts[2],
                        "connect_port": int(parts[3])
                    })
            return rules
            
        # Parse lines after the dashed line header separator
        for line in lines[header_index + 1:]:
            parts = line.split()
            if len(parts) == 4:
                try:
                    rules.append({
                        "listen_addr": parts[0],
                        "listen_port": int(parts[1]),
                        "connect_addr": parts[2],
                        "connect_port": int(parts[3])
                    })
                except ValueError:
                    continue
        return rules
    except Exception as e:
        print(f"Error listing portproxy rules: {e}")
        return []

def add_portproxy_rule(listen_addr, listen_port, connect_addr, connect_port):
    """Add a netsh interface portproxy rule."""
    try:
        cmd = f"netsh interface portproxy add v4tov4 listenaddress={listen_addr} listenport={listen_port} connectaddress={connect_addr} connectport={connect_port}"
        subprocess.run(cmd, shell=True, check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return True
    except Exception as e:
        print(f"Error adding portproxy rule: {e}")
        return False

def delete_portproxy_rule(listen_addr, listen_port):
    """Delete a netsh interface portproxy rule."""
    try:
        cmd = f"netsh interface portproxy delete v4tov4 listenaddress={listen_addr} listenport={listen_port}"
        subprocess.run(cmd, shell=True, check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return True
    except Exception as e:
        print(f"Error deleting portproxy rule: {e}")
        return False

def manage_firewall_rule(port, action="add"):
    """Add or remove an inbound Windows Firewall rule for the port."""
    rule_name = f"FZPortProxy: {port}"
    try:
        if action == "add":
            # First ensure no duplicate exists
            subprocess.run(f'netsh advfirewall firewall delete rule name="{rule_name}"', shell=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
            # Add new rule
            cmd = f'netsh advfirewall firewall add rule name="{rule_name}" dir=in action=allow protocol=TCP localport={port}'
            subprocess.run(cmd, shell=True, check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            cmd = f'netsh advfirewall firewall delete rule name="{rule_name}"'
            subprocess.run(cmd, shell=True, check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
        return True
    except Exception as e:
        print(f"Error managing firewall rule: {e}")
        return False

def get_hosts_mappings():
    """
    Read current hostname mappings from the Windows hosts file under the FZPortProxy block.
    Returns a dict: {hostname: ip}
    """
    hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    mappings = {}
    if not os.path.exists(hosts_path):
        return mappings
        
    try:
        try:
            with open(hosts_path, "r", encoding="utf-8") as f:
                content = f.read()
        except:
            with open(hosts_path, "r", encoding="ansi") as f:
                content = f.read()
                
        start_tag = "# === FZPortProxy BEGIN ==="
        end_tag = "# === FZPortProxy END ==="
        
        if start_tag in content and end_tag in content:
            # Extract content between tags
            pattern = re.compile(rf"{re.escape(start_tag)}(.*?){re.escape(end_tag)}", re.DOTALL)
            match = pattern.search(content)
            if match:
                block = match.group(1)
                for line in block.splitlines():
                    line_str = line.strip()
                    if not line_str or line_str.startswith("#"):
                        continue
                    parts = line_str.split()
                    if len(parts) >= 2:
                        ip = parts[0]
                        hostname = parts[1]
                        mappings[hostname] = ip
    except Exception as e:
        print(f"Error reading hosts file: {e}")
    return mappings

def update_hosts_mappings(mappings):
    """
    Update Windows hosts file with the mappings.
    mappings: dict {hostname: ip}
    """
    hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    if not os.path.exists(hosts_path):
        # Create empty hosts file if not exists (unlikely on Windows)
        try:
            os.makedirs(os.path.dirname(hosts_path), exist_ok=True)
            with open(hosts_path, "w", encoding="utf-8") as f:
                f.write("# Windows hosts file\n")
        except Exception as e:
            print(f"Failed to create hosts path: {e}")
            return False

    try:
        # Read file
        try:
            with open(hosts_path, "r", encoding="utf-8") as f:
                content = f.read()
        except:
            with open(hosts_path, "r", encoding="ansi") as f:
                content = f.read()
                
        start_tag = "# === FZPortProxy BEGIN ==="
        end_tag = "# === FZPortProxy END ==="
        
        new_block_lines = [start_tag]
        for hostname, ip in sorted(mappings.items()):
            new_block_lines.append(f"{ip} {hostname}")
        new_block_lines.append(end_tag)
        new_block_content = "\n".join(new_block_lines)
        
        if start_tag in content and end_tag in content:
            # Replace existing block
            pattern = re.compile(rf"{re.escape(start_tag)}.*?{re.escape(end_tag)}", re.DOTALL)
            new_content = pattern.sub(new_block_content, content)
        else:
            # Append new block
            new_content = content.rstrip() + "\n\n" + new_block_content + "\n"
            
        with open(hosts_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        return True
    except Exception as e:
        print(f"Error updating hosts file: {e}")
        return False
