# Copyright (c) 2026 Roger Luft (VeilWalker)
# Licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0).
# See LICENSE file in the project root for full license text.
# https://creativecommons.org/licenses/by/4.0/

import os
import sys
import shutil
import subprocess
import ctypes
import tkinter as tk
import customtkinter as ctk
from tkinter import filedialog, messagebox
from version import APP_VERSION, APP_NAME

# Set theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def run_as_admin_relaunch():
    if not is_admin():
        params = " ".join([f'"{arg}"' for arg in sys.argv])
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, params, None, 1
            )
        except Exception as e:
            print(f"Failed to elevate installer: {e}")
        sys.exit(0)

class FZPortProxyInstaller(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"{APP_NAME} Setup v{APP_VERSION}")
        self.geometry("550x400")
        self.resizable(False, False)

        # Default Install Path
        default_dir = os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "FZPortProxy")
        self.install_dir = tk.StringVar(value=default_dir)
        self.start_with_windows = tk.BooleanVar(value=True)

        self.setup_ui()

    def setup_ui(self):
        # 1. Title Banner
        banner_frame = ctk.CTkFrame(self, height=80, corner_radius=0, fg_color="#1f2937")
        banner_frame.pack(fill="x", side="top")
        
        banner_lbl = ctk.CTkLabel(
            banner_frame, 
            text=f"{APP_NAME} Installation Setup v{APP_VERSION}", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#3b82f6"
        )
        banner_lbl.pack(pady=20, padx=20, anchor="w")

        # 2. Body Frame
        body_frame = ctk.CTkFrame(self, fg_color="transparent")
        body_frame.pack(fill="both", expand=True, padx=30, pady=20)

        intro_lbl = ctk.CTkLabel(
            body_frame,
            text=f"This wizard will install {APP_NAME} v{APP_VERSION} on your computer.\n{APP_NAME} will manage your Windows Portproxies and WSL Hostname configurations.",
            justify="left",
            anchor="w"
        )
        intro_lbl.pack(fill="x", pady=10)

        # Directory Selector
        dir_lbl = ctk.CTkLabel(body_frame, text="Select Installation Folder:", font=ctk.CTkFont(weight="bold"))
        dir_lbl.pack(anchor="w", pady=(10, 2))

        dir_selection_frame = ctk.CTkFrame(body_frame, fg_color="transparent")
        dir_selection_frame.pack(fill="x", pady=5)

        self.entry_dir = ctk.CTkEntry(dir_selection_frame, textvariable=self.install_dir, width=350)
        self.entry_dir.pack(side="left", fill="x", expand=True)

        btn_browse = ctk.CTkButton(dir_selection_frame, text="Browse...", width=80, command=self.browse_folder)
        btn_browse.pack(side="right", padx=(10, 0))

        # Checkbox
        self.chk_startup = ctk.CTkCheckBox(
            body_frame, 
            text="Start FZPortProxy automatically with Windows (Startup Shortcut)",
            variable=self.start_with_windows
        )
        self.chk_startup.pack(anchor="w", pady=15)

        # 3. Footer / Action Buttons
        footer_frame = ctk.CTkFrame(self, height=60, fg_color="transparent")
        footer_frame.pack(fill="x", side="bottom", padx=30, pady=10)

        self.btn_cancel = ctk.CTkButton(footer_frame, text="Cancel", fg_color="#374151", hover_color="#4b5563", command=self.destroy)
        self.btn_cancel.pack(side="left")

        self.btn_install = ctk.CTkButton(footer_frame, text="Install Now", fg_color="#2563eb", hover_color="#1d4ed8", command=self.start_installation)
        self.btn_install.pack(side="right")

    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.install_dir.get(), title="Select Installation Folder")
        if folder:
            # Append project folder name if chosen a parent dir
            if not folder.endswith("FZPortProxy"):
                folder = os.path.join(folder, "FZPortProxy")
            self.install_dir.set(os.path.normpath(folder))

    def create_startup_shortcut(self, exe_path):
        try:
            startup_folder = os.path.join(os.environ["USERPROFILE"], "AppData", "Roaming", "Microsoft", "Windows", "Start Menu", "Programs", "Startup")
            shortcut_path = os.path.join(startup_folder, "fzportproxy.lnk")
            
            # PowerShell command to create WScript.Shell shortcut silently
            powershell_cmd = f"$s = (New-Object -ComObject WScript.Shell).CreateShortcut('{shortcut_path}'); $s.TargetPath = '{exe_path}'; $s.WorkingDirectory = '{os.path.dirname(exe_path)}'; $s.Save()"
            subprocess.run(
                ["powershell", "-Command", powershell_cmd],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            return True
        except Exception as e:
            print(f"Error creating startup shortcut: {e}")
            return False

    def start_installation(self):
        dest_folder = self.install_dir.get().strip()
        if not dest_folder:
            messagebox.showerror("Error", "Please select a valid installation folder.")
            return

        # Determine source executable path
        # In PyInstaller, sys._MEIPASS holds the path to temporary resource files
        if hasattr(sys, "_MEIPASS"):
            src_exe = os.path.join(sys._MEIPASS, "fzportproxy.exe")
        else:
            # Fallback for local testing
            src_exe = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist", "fzportproxy.exe")
            if not os.path.exists(src_exe):
                src_exe = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fzportproxy.exe")

        if not os.path.exists(src_exe):
            messagebox.showerror("Error", "Source binary 'fzportproxy.exe' not found. Please compile it first.")
            return

        try:
            # Create destination folder
            os.makedirs(dest_folder, exist_ok=True)
            
            dest_exe = os.path.join(dest_folder, "fzportproxy.exe")
            
            # Copy executable
            shutil.copy2(src_exe, dest_exe)

            # Create startup shortcut if requested
            shortcut_created = False
            if self.start_with_windows.get():
                shortcut_created = self.create_startup_shortcut(dest_exe)

            # Show Success Dialog
            msg = f"FZPortProxy was successfully installed to:\n{dest_folder}\n\n"
            if self.start_with_windows.get():
                if shortcut_created:
                    msg += "Startup shortcut created successfully. The application will start with Windows."
                else:
                    msg += "Failed to create Startup shortcut, but the app was installed successfully."

            messagebox.showinfo("Success", msg)
            self.destroy()

        except PermissionError:
            messagebox.showerror("Access Denied", "Permission denied. Please ensure you are running the setup as Administrator.")
        except Exception as e:
            messagebox.showerror("Installation Failed", f"An error occurred during installation:\n{e}")

if __name__ == "__main__":
    if not is_admin():
        run_as_admin_relaunch()
    else:
        app = FZPortProxyInstaller()
        app.mainloop()
