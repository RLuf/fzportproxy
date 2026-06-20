import os
import subprocess
import sys
import customtkinter

def build():
    # Find customtkinter directory
    ctk_dir = os.path.dirname(customtkinter.__file__)
    print(f"Detected CustomTkinter path: {ctk_dir}")

    # Path to PyInstaller in virtual env
    pyinstaller_path = os.path.join(".venv", "Scripts", "pyinstaller.exe")
    if not os.path.exists(pyinstaller_path):
        # fallback to system pyinstaller if not found in .venv
        pyinstaller_path = "pyinstaller"

    # ==========================================
    # 1. Build Main Application (fzportproxy.exe)
    # ==========================================
    cmd_main = [
        pyinstaller_path,
        "--noconfirm",
        "--onefile",
        "--windowed",
        f"--add-data={ctk_dir};customtkinter",
        "--uac-admin",
        "--name=fzportproxy",
        "main.py"
    ]

    print("\n-------------------------------------------")
    print("STEP 1: Building Standalone Main Executable")
    print("-------------------------------------------")
    print("Command:", " ".join(cmd_main))
    
    try:
        subprocess.run(cmd_main, check=True)
        print("Main executable compiled successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Failed to build main executable: {e}")
        sys.exit(1)

    # Verify main executable exists before building installer
    main_exe_path = os.path.join("dist", "fzportproxy.exe")
    if not os.path.exists(main_exe_path):
        print(f"Error: {main_exe_path} was not created by PyInstaller.")
        sys.exit(1)

    # ==========================================
    # 2. Build Installer Application (setup_fzportproxy.exe)
    # ==========================================
    # We bundle the compiled fzportproxy.exe inside the installer executable.
    cmd_installer = [
        pyinstaller_path,
        "--noconfirm",
        "--onefile",
        "--windowed",
        f"--add-data={main_exe_path};.", # Embed the standalone main exe in root
        f"--add-data={ctk_dir};customtkinter", # Embed customtkinter assets for installer UI
        "--uac-admin",
        "--name=setup_fzportproxy",
        "installer.py"
    ]

    print("\n-------------------------------------------")
    print("STEP 2: Building Setup Installer Executable")
    print("-------------------------------------------")
    print("Command:", " ".join(cmd_installer))

    try:
        subprocess.run(cmd_installer, check=True)
        print("\n===========================================")
        print("Build Process Completed Successfully!")
        print("-------------------------------------------")
        print(f"1. Standalone App: E:\\fzportproxy\\fzportproxy\\dist\\fzportproxy.exe")
        print(f"2. Setup Installer: E:\\fzportproxy\\fzportproxy\\dist\\setup_fzportproxy.exe")
        print("===========================================")
    except subprocess.CalledProcessError as e:
        print(f"Failed to build installer: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build()
