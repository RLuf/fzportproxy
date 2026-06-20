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

    # PyInstaller arguments
    # --uac-admin ensures the resulting .exe requests admin privileges on start.
    # --noconsole / --windowed hides the command prompt window.
    # --add-data copies customtkinter's assets (fonts, themes) to the bundle.
    cmd = [
        pyinstaller_path,
        "--noconfirm",
        "--onefile",
        "--windowed",
        f"--add-data={ctk_dir};customtkinter",
        "--uac-admin",
        "--name=fzportproxy",
        "main.py"
    ]

    print("Building executable...")
    print("Command:", " ".join(cmd))
    
    try:
        subprocess.run(cmd, check=True)
        print("\nBuild Successful!")
        print("Your compiled executable can be found in the 'dist' directory: E:\\fzportproxy\\fzportproxy\\dist\\fzportproxy.exe")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    build()
