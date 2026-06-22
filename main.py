# Copyright (c) 2026 Roger Luft (VeilWalker)
# Licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0).
# See LICENSE file in the project root for full license text.
# https://creativecommons.org/licenses/by/4.0/

import sys
import wsl_manager as wm

def main():
    # Check for Admin Privileges (required for netsh, firewall, and hosts file access)
    if not wm.is_admin():
        print("Not running as Administrator. Requesting UAC elevation...")
        wm.run_as_admin_relaunch()
        sys.exit(0)

    # Start the GUI
    try:
        from gui import FZPortProxyApp
        app = FZPortProxyApp()
        app.mainloop()
    except Exception as e:
        print(f"Failed to start application: {e}")
        try:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Error", f"Failed to start application: {e}")
        except:
            pass

if __name__ == "__main__":
    main()
