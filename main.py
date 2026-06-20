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
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
