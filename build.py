# Copyright (c) 2026 Roger Luft (VeilWalker)
# Licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0).
# See LICENSE file in the project root for full license text.
# https://creativecommons.org/licenses/by/4.0/

"""
FZPortProxy Build Script — Nuitka Compiler
Compiles both the main application and the installer into standalone executables.
Uses Nuitka for native C compilation (avoids AV false positives from PyInstaller).
Requires: MinGW64 (gcc) or MSVC (cl.exe) installed on the system.
"""

import os
import sys
import subprocess
import shutil
import re as _re

# Ensure we can import our version module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from version import APP_VERSION, APP_NAME


def sanitize_path_for_nuitka():
    """
    Remove external Python installations from PATH so Nuitka uses the
    venv's Python for onefile compression. Python 3.14's zstd module
    has a known allocation error that breaks onefile builds.
    """
    venv_scripts = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".venv", "Scripts")
    path_dirs = os.environ.get("PATH", "").split(";")
    # Keep only dirs that don't contain other python executables
    # (except our venv and system dirs like System32)
    cleaned = [venv_scripts]  # Our venv first
    for d in path_dirs:
        d_lower = d.lower()
        # Skip directories that contain standalone Python installs
        if any(pattern in d_lower for pattern in [
            "python3.", "python\\3.", "cpython",
            "\\.local\\bin", "\\uv\\python",
            "appdata\\roaming\\uv", "appdata\\local\\programs\\python"
        ]):
            print(f"  PATH filtered: {d}")
            continue
        cleaned.append(d)
    os.environ["PATH"] = ";".join(cleaned)


def find_mingw():
    """Try to locate MinGW64 gcc on common paths."""
    common_paths = [
        r"C:\mingw64\bin",
        r"C:\msys64\mingw64\bin",
        r"C:\tools\mingw64\bin",
    ]
    for p in common_paths:
        gcc = os.path.join(p, "gcc.exe")
        if os.path.exists(gcc):
            return p
    # Check PATH
    try:
        result = subprocess.run(["where", "gcc"], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            return os.path.dirname(result.stdout.strip().splitlines()[0])
    except Exception:
        pass
    return None


def check_compiler():
    """Verify a C compiler is available for Nuitka."""
    # Check MSVC (cl.exe)
    try:
        result = subprocess.run(["where", "cl"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Found MSVC compiler: {result.stdout.strip().splitlines()[0]}")
            return "msvc"
    except Exception:
        pass

    # Check MinGW64
    mingw_path = find_mingw()
    if mingw_path:
        print(f"Found MinGW64 compiler at: {mingw_path}")
        # Ensure it's on PATH for Nuitka
        os.environ["PATH"] = mingw_path + ";" + os.environ.get("PATH", "")
        return "mingw64"

    print("ERROR: No C compiler found!")
    print("Nuitka requires either:")
    print("  - MSVC (Visual Studio Build Tools with C++ workload)")
    print("  - MinGW64 (gcc for Windows)")
    print("Install one and try again.")
    sys.exit(1)


def get_package_path(package_name):
    """Get the installation path of a Python package."""
    try:
        mod = __import__(package_name)
        return os.path.dirname(mod.__file__)
    except ImportError:
        print(f"WARNING: Package '{package_name}' not found in the environment.")
        return None


def build_executable(script, output_name, extra_args=None):
    """Build a single executable using Nuitka."""
    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--onefile",
        "--enable-plugin=tk-inter",
        "--windows-console-mode=disable",
        # NOTE: UAC elevation is handled at runtime in main.py via wm.run_as_admin_relaunch()
        # --windows-uac-admin removed: it embeds a requireAdministrator manifest which causes
        # Windows to lock the intermediate exe, blocking the onefile linker from overwriting it.
        "--include-package=customtkinter",
        "--include-package=PIL",
        "--include-package=pystray",
        "--include-module=version",
        f"--output-filename={output_name}",
        f"--output-dir=dist",
        "--remove-output",  # Clean intermediate build folder
        "--assume-yes-for-downloads",  # Auto-accept any dependency downloads
        "--lto=no",  # Disable LTO to avoid out-of-memory on linker
    ]

    # Add icon via rcedit (post-build, avoids PermissionError with UAC exes)
    # icon is added after compilation via post_build_icon()

    # Add customtkinter data files (themes/assets)
    ctk_path = get_package_path("customtkinter")
    if ctk_path:
        cmd.append(f"--include-data-dir={ctk_path}=customtkinter")

    if extra_args:
        cmd.extend(extra_args)

    cmd.append(script)

    return cmd


def post_build_icon(exe_path):
    """Add icon to exe using rcedit (avoids Nuitka UAC+icon PermissionError)."""
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.ico")
    rcedit_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rcedit.exe")
    if not os.path.exists(rcedit_path):
        print("  [WARN] rcedit.exe not found, skipping icon injection.")
        return
    if not os.path.exists(icon_path):
        print("  [WARN] icon.ico not found, skipping icon injection.")
        return
    try:
        result = subprocess.run(
            [rcedit_path, exe_path, "--set-icon", icon_path],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"  [OK] Icon added to {os.path.basename(exe_path)}")
        else:
            print(f"  [WARN] rcedit failed: {result.stderr.strip()}")
    except Exception as e:
        print(f"  [WARN] Icon injection error: {e}")


def run_build(cmd, step_name):
    """Execute a build command and handle errors."""
    print(f"\n{'='*50}")
    print(f"  {step_name}")
    print(f"{'='*50}")
    print(f"Command: {' '.join(cmd)}\n")

    try:
        subprocess.run(cmd, check=True)
        print(f"\n[OK] {step_name} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n[FAIL] {step_name} FAILED: {e}")
        return False


def build():
    """Main build process."""
    print(f"""
==============================================
  {APP_NAME} Build System v{APP_VERSION}
  Compiler: Nuitka (Native C compilation)
=============================================="""
)

    # 1. Sanitize PATH to prevent Nuitka from using Python 3.14
    print("Sanitizing PATH for Nuitka compatibility...")
    sanitize_path_for_nuitka()

    # 2. Check compiler availability
    compiler = check_compiler()
    print(f"Using compiler backend: {compiler}\n")

    # 2. Create dist directory
    os.makedirs("dist", exist_ok=True)

    # 3. Build Main Application
    main_name = f"fzportproxy_v{APP_VERSION}.exe"
    cmd_main = build_executable("main.py", main_name)
    if not run_build(cmd_main, f"STEP 1: Building Main Application ({main_name})"):
        sys.exit(1)

    # Verify main exe exists
    main_exe_path = os.path.join("dist", main_name)
    if not os.path.exists(main_exe_path):
        print(f"ERROR: {main_exe_path} was not created.")
        sys.exit(1)

    post_build_icon(main_exe_path)

    # 4. Build Installer (embedding the main exe)
    installer_name = f"setup_fzportproxy_v{APP_VERSION}.exe"
    extra_installer_args = [
        f"--include-data-files={main_exe_path}=fzportproxy.exe",
    ]
    cmd_installer = build_executable("installer.py", installer_name, extra_installer_args)
    if not run_build(cmd_installer, f"STEP 2: Building Installer ({installer_name})"):
        sys.exit(1)
    post_build_icon(os.path.join("dist", installer_name))

    # 5. Summary
    print(f"""
==============================================
  Build Completed Successfully!
----------------------------------------------
  1. Main App:  dist/{main_name}
  2. Installer: dist/{installer_name}
----------------------------------------------
  Next: Run 'python sign.py' to sign them
=============================================="""
)


if __name__ == "__main__":
    build()
