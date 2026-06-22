# Copyright (c) 2026 Roger Luft (VeilWalker)
# Licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0).
# See LICENSE file in the project root for full license text.
# https://creativecommons.org/licenses/by/4.0/

"""
FZPortProxy Code Signing Script
Generates a self-signed certificate and signs the compiled executables.
Certificate: CN=FZPortProxy, O=Webstorage

NOTE: Self-signed certificates are for internal/development use.
For public distribution, replace with a certificate from a trusted CA.

Usage:
    python sign.py                  # Sign all executables in dist/
    python sign.py path/to/file.exe # Sign a specific file
"""

import os
import sys
import subprocess
import glob

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from version import APP_VERSION

# Certificate configuration
CERT_SUBJECT = "CN=FZPortProxy, O=Webstorage"
CERT_FRIENDLY_NAME = "FZPortProxy Code Signing"
CERT_STORE = r"Cert:\CurrentUser\My"
PFX_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".codesign")
PFX_PATH = os.path.join(PFX_DIR, "fzportproxy_sign.pfx")
PFX_PASSWORD_DEFAULT = "FZPortProxy2026!"  # Public fallback for CI/dev builds
PFX_PASSWORD_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sign-pass.cfg")


def load_pfx_password():
    """Load PFX password from environment variable, local file, or hardcoded default."""
    # 1. Environment variable (highest priority — for CI or secure setups)
    env_pass = os.environ.get("FZ_CODESIGN_PASSWORD")
    if env_pass:
        print("[PASSWORD] Using password from environment variable FZ_CODESIGN_PASSWORD")
        return env_pass

    # 2. Local file sign-pass.cfg (gitignored — for developer machines)
    if os.path.exists(PFX_PASSWORD_FILE):
        try:
            with open(PFX_PASSWORD_FILE, "r", encoding="utf-8") as f:
                file_pass = f.read().strip()
            if file_pass:
                print(f"[PASSWORD] Using password from local file: {PFX_PASSWORD_FILE}")
                return file_pass
        except Exception as e:
            print(f"[PASSWORD] Warning: Failed to read {PFX_PASSWORD_FILE}: {e}")

    # 3. Hardcoded default (public fallback)
    print("[PASSWORD] Using default hardcoded password (for development/CI use)")
    return PFX_PASSWORD_DEFAULT


PFX_PASSWORD = load_pfx_password()

# Timestamp server for the signature
TIMESTAMP_URL = "http://timestamp.digicert.com"


def find_signtool():
    """Locate signtool.exe from Windows SDK."""
    # Common Windows SDK paths
    sdk_base = r"C:\Program Files (x86)\Windows Kits\10\bin"
    if os.path.exists(sdk_base):
        # Find the latest version
        versions = sorted(
            [d for d in os.listdir(sdk_base) if d.startswith("10.")],
            reverse=True
        )
        for ver in versions:
            signtool = os.path.join(sdk_base, ver, "x64", "signtool.exe")
            if os.path.exists(signtool):
                return signtool

    # Try PATH
    try:
        result = subprocess.run(["where", "signtool"], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().splitlines()[0]
    except Exception:
        pass

    return None


def ensure_certificate():
    """
    Check if the FZPortProxy code signing certificate exists.
    If not, create a self-signed one and export to PFX.
    Returns True if certificate is ready.
    """
    os.makedirs(PFX_DIR, exist_ok=True)

    # Check if PFX already exists
    if os.path.exists(PFX_PATH):
        print(f"[OK] Certificate PFX found: {PFX_PATH}")
        return True

    print("Certificate not found. Creating self-signed certificate...")

    # PowerShell script to create certificate and export PFX
    ps_script = f"""
$ErrorActionPreference = 'Stop'

# Check if cert already exists in store
$existing = Get-ChildItem {CERT_STORE} | Where-Object {{ $_.Subject -eq '{CERT_SUBJECT}' -and $_.HasPrivateKey }}
if ($existing) {{
    $cert = $existing[0]
    Write-Host "Found existing certificate in store: $($cert.Thumbprint)"
}} else {{
    # Create new self-signed code signing certificate
    $cert = New-SelfSignedCertificate `
        -Type CodeSigningCert `
        -Subject '{CERT_SUBJECT}' `
        -FriendlyName '{CERT_FRIENDLY_NAME}' `
        -CertStoreLocation '{CERT_STORE}' `
        -KeyExportPolicy Exportable `
        -KeyLength 2048 `
        -HashAlgorithm SHA256 `
        -NotAfter (Get-Date).AddYears(5)
    Write-Host "Created new certificate: $($cert.Thumbprint)"
}}

# Export to PFX
$pwd = ConvertTo-SecureString -String '{PFX_PASSWORD}' -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath '{PFX_PATH}' -Password $pwd | Out-Null
Write-Host "Exported PFX to: {PFX_PATH}"

# Also add to Trusted Root (so local machine trusts it)
$rootStore = New-Object System.Security.Cryptography.X509Certificates.X509Store("Root", "CurrentUser")
$rootStore.Open("ReadWrite")
$rootStore.Add($cert)
$rootStore.Close()
Write-Host "Added certificate to Trusted Root store."
"""

    try:
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.returncode != 0:
            print(f"ERROR creating certificate: {result.stderr}")
            return False
        return os.path.exists(PFX_PATH)
    except Exception as e:
        print(f"ERROR: Failed to create certificate: {e}")
        return False


def sign_file(signtool_path, file_path):
    """Sign a single file with signtool."""
    print(f"\nSigning: {file_path}")

    cmd = [
        signtool_path, "sign",
        "/f", PFX_PATH,
        "/p", PFX_PASSWORD,
        "/fd", "SHA256",
        "/tr", TIMESTAMP_URL,
        "/td", "SHA256",
        "/d", f"FZPortProxy v{APP_VERSION}",
        file_path
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  [OK] Signed successfully!")
            return True
        else:
            print(f"  [FAIL] Signing failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"  [FAIL] Error: {e}")
        return False


def verify_signature(signtool_path, file_path):
    """Verify the digital signature of a file."""
    cmd = [signtool_path, "verify", "/pa", file_path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  [OK] Signature verified: {os.path.basename(file_path)}")
            return True
        else:
            print(f"  [WARN] Verification warning: {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"  [FAIL] Verification error: {e}")
        return False


def main():
    print(f"""
==============================================
  FZPortProxy Code Signing Tool
  Certificate: {CERT_SUBJECT}
=============================================="""
)

    # 1. Find signtool
    signtool = find_signtool()
    if not signtool:
        print("ERROR: signtool.exe not found!")
        print("Install the Windows SDK:")
        print("  https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/")
        sys.exit(1)
    print(f"[OK] signtool.exe found: {signtool}")

    # 2. Ensure certificate exists
    if not ensure_certificate():
        print("\nERROR: Failed to prepare code signing certificate.")
        sys.exit(1)

    # 3. Determine files to sign
    if len(sys.argv) > 1:
        # Sign specific files passed as arguments
        files_to_sign = sys.argv[1:]
    else:
        # Sign all .exe files in dist/
        dist_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")
        files_to_sign = glob.glob(os.path.join(dist_dir, "*.exe"))

    if not files_to_sign:
        print("\nNo executables found to sign.")
        print("Run 'python build.py' first, or pass file paths as arguments.")
        sys.exit(1)

    print(f"\nFiles to sign: {len(files_to_sign)}")

    # 4. Sign each file
    success_count = 0
    for filepath in files_to_sign:
        if not os.path.exists(filepath):
            print(f"\n[WARN] File not found: {filepath}")
            continue
        if sign_file(signtool, filepath):
            verify_signature(signtool, filepath)
            success_count += 1

    # 5. Summary
    print(f"""
==============================================
  Signing Complete
  Signed: {success_count}/{len(files_to_sign)} files
=============================================="""
)

    if success_count < len(files_to_sign):
        sys.exit(1)


if __name__ == "__main__":
    main()
