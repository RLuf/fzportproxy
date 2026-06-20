import tkinter as tk
import customtkinter as ctk
import wsl_manager as wm
import threading
import time
import json
import os
from tkinter import messagebox

# Set theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

class FZPortProxyApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("FZPortProxy - WSL Port Forwarding & Hostname Manager")
        self.geometry("900x650")
        self.resizable(True, True)

        # Load Configuration
        self.load_config()

        # Admin status warning
        self.is_admin_mode = wm.is_admin()
        
        # WSL state
        self.wsl_distros = []
        self.wsl_ips = {} # distro_name -> ip

        # GUI elements setup
        self.setup_layout()
        
        # Initial refresh
        self.refresh_all_data()

        # Start auto-sync thread if enabled
        self.sync_thread_running = True
        self.sync_thread = threading.Thread(target=self.bg_sync_loop, daemon=True)
        self.sync_thread.start()

    def load_config(self):
        default_config = {
            "auto_sync": True,
            "sync_interval": 10,
            "auto_firewall": True,
            "dynamic_rules": [], # [{"listen_port": 8080, "distro": "Ubuntu-24.04", "connect_port": 80, "listen_addr": "0.0.0.0"}]
            "dynamic_hosts": {}  # {"app.wsl": "Ubuntu-24.04"}
        }
        if os.path.exists(CONFIG_PATH):
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                # Ensure all default keys exist
                for k, v in default_config.items():
                    if k not in self.config:
                        self.config[k] = v
            except Exception as e:
                print(f"Error loading config.json, resetting: {e}")
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()

    def save_config(self):
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving config.json: {e}")

    def setup_layout(self):
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # 1. Header Frame
        self.header_frame = ctk.CTkFrame(self, height=60, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        self.header_frame.grid_columnconfigure(1, weight=1)

        title_label = ctk.CTkLabel(
            self.header_frame, 
            text="FZPortProxy", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # Admin Badge
        admin_text = "Running as Administrator" if self.is_admin_mode else "Requires Admin Privileges!"
        admin_color = "#2ecc71" if self.is_admin_mode else "#e74c3c"
        admin_badge = ctk.CTkLabel(
            self.header_frame,
            text=admin_text,
            text_color=admin_color,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        admin_badge.grid(row=0, column=1, padx=20, pady=10, sticky="e")

        # 2. Main Tabview
        self.tabview = ctk.CTkTabview(self, segment_button_width_medium=True)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=15, pady=10)

        self.tab_rules = self.tabview.add("Port Forwards")
        self.tab_wsl = self.tabview.add("WSL Distros")
        self.tab_hosts = self.tabview.add("Hosts Configuration")
        self.tab_settings = self.tabview.add("Settings")

        self.setup_tab_rules()
        self.setup_tab_wsl()
        self.setup_tab_hosts()
        self.setup_tab_settings()

    # --- PORT FORWARDS TAB ---
    def setup_tab_rules(self):
        self.tab_rules.grid_columnconfigure(0, weight=3)
        self.tab_rules.grid_columnconfigure(1, weight=1)
        self.tab_rules.grid_rowconfigure(0, weight=1)

        # Left: List of active rules
        list_frame = ctk.CTkFrame(self.tab_rules)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)
        list_frame.grid_rowconfigure(1, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        list_header = ctk.CTkLabel(list_frame, text="Active Windows Portproxy Rules", font=ctk.CTkFont(size=14, weight="bold"))
        list_header.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.rules_scroll = ctk.CTkScrollableFrame(list_frame)
        self.rules_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # Right: Add Forward Form
        form_frame = ctk.CTkFrame(self.tab_rules)
        form_frame.grid(row=0, column=1, sticky="nsew", pady=5)
        form_frame.grid_columnconfigure(0, weight=1)

        form_header = ctk.CTkLabel(form_frame, text="Add Port Forward", font=ctk.CTkFont(size=14, weight="bold"))
        form_header.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Type Selection (Dynamic WSL or Static IP)
        ctk.CTkLabel(form_frame, text="Type:").grid(row=1, column=0, padx=10, pady=(5, 0), sticky="w")
        self.rule_type = ctk.CTkComboBox(form_frame, values=["WSL Distro (Dynamic)", "Static IP"], command=self.on_rule_type_change)
        self.rule_type.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        # Listen Port
        ctk.CTkLabel(form_frame, text="Listen Port (Windows):").grid(row=3, column=0, padx=10, pady=(5, 0), sticky="w")
        self.entry_listen_port = ctk.CTkEntry(form_frame, placeholder_text="e.g. 8080")
        self.entry_listen_port.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

        # Destination WSL Dropdown / IP entry
        self.lbl_dest = ctk.CTkLabel(form_frame, text="Target WSL Distro:")
        self.lbl_dest.grid(row=5, column=0, padx=10, pady=(5, 0), sticky="w")
        
        self.combo_distro = ctk.CTkComboBox(form_frame, values=[])
        self.combo_distro.grid(row=6, column=0, padx=10, pady=5, sticky="ew")

        self.entry_static_ip = ctk.CTkEntry(form_frame, placeholder_text="e.g. 192.168.1.50")
        # Kept hidden initially until type is changed

        # Target Port
        ctk.CTkLabel(form_frame, text="Connect Port (WSL/Target):").grid(row=7, column=0, padx=10, pady=(5, 0), sticky="w")
        self.entry_connect_port = ctk.CTkEntry(form_frame, placeholder_text="e.g. 80")
        self.entry_connect_port.grid(row=8, column=0, padx=10, pady=5, sticky="ew")

        # Listen IP (Optional/Advanced, default 0.0.0.0)
        ctk.CTkLabel(form_frame, text="Listen IP (Optional):").grid(row=9, column=0, padx=10, pady=(5, 0), sticky="w")
        self.entry_listen_addr = ctk.CTkEntry(form_frame, placeholder_text="0.0.0.0")
        self.entry_listen_addr.grid(row=10, column=0, padx=10, pady=5, sticky="ew")
        self.entry_listen_addr.insert(0, "0.0.0.0")

        # Buttons
        self.btn_add_rule = ctk.CTkButton(form_frame, text="Add Forward Rule", command=self.add_rule_action, fg_color="#3498db", hover_color="#2980b9")
        self.btn_add_rule.grid(row=11, column=0, padx=10, pady=15, sticky="ew")

        self.btn_refresh_rules = ctk.CTkButton(form_frame, text="Refresh Rules", command=self.refresh_all_data, fg_color="#95a5a6", hover_color="#7f8c8d")
        self.btn_refresh_rules.grid(row=12, column=0, padx=10, pady=5, sticky="ew")

    def on_rule_type_change(self, value):
        if value == "Static IP":
            self.lbl_dest.configure(text="Target IP Address:")
            self.combo_distro.grid_forget()
            self.entry_static_ip.grid(row=6, column=0, padx=10, pady=5, sticky="ew")
        else:
            self.lbl_dest.configure(text="Target WSL Distro:")
            self.entry_static_ip.grid_forget()
            self.combo_distro.grid(row=6, column=0, padx=10, pady=5, sticky="ew")

    # --- WSL DISTROS TAB ---
    def setup_tab_wsl(self):
        self.tab_wsl.grid_columnconfigure(0, weight=1)
        self.tab_wsl.grid_rowconfigure(1, weight=1)

        wsl_header_frame = ctk.CTkFrame(self.tab_wsl, fg_color="transparent")
        wsl_header_frame.grid(row=0, column=0, sticky="ew", pady=(5, 10))
        wsl_header_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            wsl_header_frame, 
            text="Installed Windows Subsystem for Linux (WSL) Instances", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, sticky="w")
        
        ctk.CTkButton(
            wsl_header_frame, 
            text="Scan WSL Distros", 
            width=120, 
            command=self.refresh_wsl_list
        ).grid(row=0, column=1, sticky="e")

        self.wsl_scroll = ctk.CTkScrollableFrame(self.tab_wsl)
        self.wsl_scroll.grid(row=1, column=0, sticky="nsew", pady=5)

    # --- HOSTS CONFIGURATION TAB ---
    def setup_tab_hosts(self):
        self.tab_hosts.grid_columnconfigure(0, weight=2)
        self.tab_hosts.grid_columnconfigure(1, weight=1)
        self.tab_hosts.grid_rowconfigure(0, weight=1)

        # Left: List of custom hostnames
        hosts_list_frame = ctk.CTkFrame(self.tab_hosts)
        hosts_list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)
        hosts_list_frame.grid_rowconfigure(1, weight=1)
        hosts_list_frame.grid_columnconfigure(0, weight=1)

        hosts_header = ctk.CTkLabel(hosts_list_frame, text="Active FZPortProxy Mappings in hosts file", font=ctk.CTkFont(size=14, weight="bold"))
        hosts_header.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.hosts_scroll = ctk.CTkScrollableFrame(hosts_list_frame)
        self.hosts_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # Right: Add Hostname Form
        hosts_form_frame = ctk.CTkFrame(self.tab_hosts)
        hosts_form_frame.grid(row=0, column=1, sticky="nsew", pady=5)
        hosts_form_frame.grid_columnconfigure(0, weight=1)

        hosts_form_header = ctk.CTkLabel(hosts_form_frame, text="Add Hostname Mapping", font=ctk.CTkFont(size=14, weight="bold"))
        hosts_form_header.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(hosts_form_frame, text="Hostname:").grid(row=1, column=0, padx=10, pady=(5, 0), sticky="w")
        self.entry_hostname = ctk.CTkEntry(hosts_form_frame, placeholder_text="e.g. app.wsl")
        self.entry_hostname.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(hosts_form_frame, text="Target WSL Distro:").grid(row=3, column=0, padx=10, pady=(5, 0), sticky="w")
        self.combo_hosts_distro = ctk.CTkComboBox(hosts_form_frame, values=[])
        self.combo_hosts_distro.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

        self.btn_add_host = ctk.CTkButton(hosts_form_frame, text="Add Hostname Mappings", command=self.add_hosts_action, fg_color="#3498db", hover_color="#2980b9")
        self.btn_add_host.grid(row=5, column=0, padx=10, pady=20, sticky="ew")

    # --- SETTINGS TAB ---
    def setup_tab_settings(self):
        self.tab_settings.grid_columnconfigure(0, weight=1)
        self.tab_settings.grid_rowconfigure(1, weight=1)

        settings_frame = ctk.CTkFrame(self.tab_settings)
        settings_frame.grid(row=0, column=0, sticky="nsew", pady=5)
        settings_frame.grid_columnconfigure(0, weight=1)

        settings_header = ctk.CTkLabel(settings_frame, text="Application Settings", font=ctk.CTkFont(size=16, weight="bold"))
        settings_header.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        # 1. Auto-sync switch
        self.switch_auto_sync = ctk.CTkSwitch(
            settings_frame, 
            text="Enable background Auto-Sync (resolves dynamic WSL IPs automatically)", 
            command=self.toggle_auto_sync
        )
        self.switch_auto_sync.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        if self.config.get("auto_sync", True):
            self.switch_auto_sync.select()

        # 2. Sync interval
        interval_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        interval_frame.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        ctk.CTkLabel(interval_frame, text="Sync Interval (seconds):").grid(row=0, column=0, sticky="w")
        self.entry_sync_interval = ctk.CTkEntry(interval_frame, width=80)
        self.entry_sync_interval.grid(row=0, column=1, padx=10, sticky="w")
        self.entry_sync_interval.insert(0, str(self.config.get("sync_interval", 10)))
        
        btn_save_interval = ctk.CTkButton(interval_frame, text="Save Interval", width=100, command=self.save_interval_action)
        btn_save_interval.grid(row=0, column=2, padx=5, sticky="w")

        # 3. Auto-firewall switch
        self.switch_auto_firewall = ctk.CTkSwitch(
            settings_frame, 
            text="Open Windows Firewall port automatically when adding forward rules", 
            command=self.toggle_auto_firewall
        )
        self.switch_auto_firewall.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        if self.config.get("auto_firewall", True):
            self.switch_auto_firewall.select()

        # 4. Status message log
        self.txt_status_logs = ctk.CTkTextbox(settings_frame, height=180)
        self.txt_status_logs.grid(row=4, column=0, padx=20, pady=20, sticky="ew")
        self.txt_status_logs.insert("0.0", "FZPortProxy initialized.\n")
        self.txt_status_logs.configure(state="disabled")

    def log_message(self, message):
        self.txt_status_logs.configure(state="normal")
        self.txt_status_logs.insert("end", f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.txt_status_logs.see("end")
        self.txt_status_logs.configure(state="disabled")

    # --- ACTIONS & DATA REFRESH ---
    def refresh_all_data(self):
        # Refresh WSL in thread to prevent freezing
        threading.Thread(target=self.async_refresh_data, daemon=True).start()

    def async_refresh_data(self):
        self.log_message("Scanning system for changes...")
        # 1. Distros
        self.wsl_distros = wm.list_wsl_distros()
        
        # 2. Get IPs
        distro_names = []
        for d in self.wsl_distros:
            name = d["name"]
            distro_names.append(name)
            ip = wm.get_wsl_ip(name)
            if ip:
                self.wsl_ips[name] = ip
            else:
                self.wsl_ips.pop(name, None)
                
        # Update combo box values in main thread
        self.after(0, lambda: self.update_comboboxes(distro_names))
        
        # 3. Active netsh rules
        active_rules = wm.list_portproxy_rules()
        
        # 4. Active hosts rules
        hosts_rules = wm.get_hosts_mappings()
        
        # 5. Populate UI
        self.after(0, lambda: self.populate_rules_ui(active_rules))
        self.after(0, lambda: self.populate_wsl_ui())
        self.after(0, lambda: self.populate_hosts_ui(hosts_rules))

    def update_comboboxes(self, distro_names):
        self.combo_distro.configure(values=distro_names)
        if distro_names:
            self.combo_distro.set(distro_names[0])
            
        self.combo_hosts_distro.configure(values=distro_names)
        if distro_names:
            self.combo_hosts_distro.set(distro_names[0])

    def refresh_wsl_list(self):
        threading.Thread(target=self.async_refresh_wsl_only, daemon=True).start()

    def async_refresh_wsl_only(self):
        self.log_message("Scanning WSL instances...")
        self.wsl_distros = wm.list_wsl_distros()
        distro_names = []
        for d in self.wsl_distros:
            name = d["name"]
            distro_names.append(name)
            ip = wm.get_wsl_ip(name)
            if ip:
                self.wsl_ips[name] = ip
            else:
                self.wsl_ips.pop(name, None)
        self.after(0, lambda: self.update_comboboxes(distro_names))
        self.after(0, self.populate_wsl_ui)

    # --- UI POPULATION FUNCTIONS ---
    def populate_rules_ui(self, active_rules):
        # Clear frame
        for widget in self.rules_scroll.winfo_children():
            widget.destroy()

        # Add headers
        ctk.CTkLabel(self.rules_scroll, text="Listen Port", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.rules_scroll, text="Target IP", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.rules_scroll, text="Target Port", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.rules_scroll, text="Type", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.rules_scroll, text="Actions", font=ctk.CTkFont(weight="bold")).grid(row=0, column=4, padx=5, pady=5, sticky="w")

        # Map active rules to our dynamic config rules to match them
        row_idx = 1
        for rule in active_rules:
            listen_addr = rule["listen_addr"]
            listen_port = rule["listen_port"]
            connect_addr = rule["connect_addr"]
            connect_port = rule["connect_port"]

            # Check if this maps to a dynamic rule
            is_dynamic = False
            linked_distro = ""
            for dr in self.config.get("dynamic_rules", []):
                if dr["listen_port"] == listen_port and dr["connect_port"] == connect_port:
                    # Verify if connect_addr matches the distro IP
                    distro_ip = self.wsl_ips.get(dr["distro"])
                    if distro_ip == connect_addr:
                        is_dynamic = True
                        linked_distro = dr["distro"]
                        break

            type_text = f"WSL ({linked_distro})" if is_dynamic else "Static Portproxy"
            type_color = "#3498db" if is_dynamic else "#e67e22"

            ctk.CTkLabel(self.rules_scroll, text=f"{listen_addr}:{listen_port}").grid(row=row_idx, column=0, padx=5, pady=3, sticky="w")
            ctk.CTkLabel(self.rules_scroll, text=connect_addr).grid(row=row_idx, column=1, padx=5, pady=3, sticky="w")
            ctk.CTkLabel(self.rules_scroll, text=str(connect_port)).grid(row=row_idx, column=2, padx=5, pady=3, sticky="w")
            
            lbl_type = ctk.CTkLabel(self.rules_scroll, text=type_text, text_color=type_color, font=ctk.CTkFont(size=11, weight="bold"))
            lbl_type.grid(row=row_idx, column=3, padx=5, pady=3, sticky="w")

            btn_del = ctk.CTkButton(
                self.rules_scroll, 
                text="Delete", 
                width=60, 
                height=22, 
                fg_color="#e74c3c", 
                hover_color="#c0392b",
                command=lambda la=listen_addr, lp=listen_port: self.delete_rule_action(la, lp)
            )
            btn_del.grid(row=row_idx, column=4, padx=5, pady=3, sticky="w")
            row_idx += 1

        if not active_rules:
            ctk.CTkLabel(self.rules_scroll, text="No active port forwarding rules.", text_color="gray").grid(row=1, column=0, columnspan=5, pady=20)

    def populate_wsl_ui(self):
        # Clear frame
        for widget in self.wsl_scroll.winfo_children():
            widget.destroy()

        # Add headers
        ctk.CTkLabel(self.wsl_scroll, text="Name", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.wsl_scroll, text="State", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.wsl_scroll, text="Version", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.wsl_scroll, text="Resolved IP Address", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=10, pady=5, sticky="w")

        row_idx = 1
        for d in self.wsl_distros:
            name = d["name"]
            state = d["state"]
            version = d["version"]
            
            # Show default indicator
            default_marker = " [Default]" if d["is_default"] else ""
            display_name = f"{name}{default_marker}"
            
            # State color
            state_color = "#2ecc71" if state == "Running" else "#95a5a6"

            # Get IP
            ip = self.wsl_ips.get(name, "Not Running / No IP")
            ip_color = "white" if ip != "Not Running / No IP" else "gray"

            ctk.CTkLabel(self.wsl_scroll, text=display_name).grid(row=row_idx, column=0, padx=10, pady=5, sticky="w")
            
            lbl_state = ctk.CTkLabel(self.wsl_scroll, text=state, text_color=state_color, font=ctk.CTkFont(weight="bold"))
            lbl_state.grid(row=row_idx, column=1, padx=10, pady=5, sticky="w")
            
            ctk.CTkLabel(self.wsl_scroll, text=f"WSL {version}").grid(row=row_idx, column=2, padx=10, pady=5, sticky="w")
            
            lbl_ip = ctk.CTkLabel(self.wsl_scroll, text=ip, text_color=ip_color)
            lbl_ip.grid(row=row_idx, column=3, padx=10, pady=5, sticky="w")
            row_idx += 1

        if not self.wsl_distros:
            ctk.CTkLabel(self.wsl_scroll, text="No WSL distros detected on this system.", text_color="gray").grid(row=1, column=0, columnspan=4, pady=20)

    def populate_hosts_ui(self, hosts_rules):
        # Clear frame
        for widget in self.hosts_scroll.winfo_children():
            widget.destroy()

        # Add headers
        ctk.CTkLabel(self.hosts_scroll, text="Hostname", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.hosts_scroll, text="Current IP", font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.hosts_scroll, text="Dynamic Mapping To", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.hosts_scroll, text="Actions", font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=10, pady=5, sticky="w")

        row_idx = 1
        for host, ip in hosts_rules.items():
            # Check if this maps to a dynamic host
            linked_distro = self.config.get("dynamic_hosts", {}).get(host, "Static Mapping")
            distro_color = "#3498db" if linked_distro != "Static Mapping" else "#95a5a6"

            ctk.CTkLabel(self.hosts_scroll, text=host).grid(row=row_idx, column=0, padx=10, pady=3, sticky="w")
            ctk.CTkLabel(self.hosts_scroll, text=ip).grid(row=row_idx, column=1, padx=10, pady=3, sticky="w")
            
            lbl_distro = ctk.CTkLabel(self.hosts_scroll, text=linked_distro, text_color=distro_color, font=ctk.CTkFont(size=11, weight="bold"))
            lbl_distro.grid(row=row_idx, column=2, padx=10, pady=3, sticky="w")

            btn_del = ctk.CTkButton(
                self.hosts_scroll, 
                text="Delete", 
                width=60, 
                height=22, 
                fg_color="#e74c3c", 
                hover_color="#c0392b",
                command=lambda h=host: self.delete_host_action(h)
            )
            btn_del.grid(row=row_idx, column=3, padx=10, pady=3, sticky="w")
            row_idx += 1

        if not hosts_rules:
            ctk.CTkLabel(self.hosts_scroll, text="No FZPortProxy mappings in Windows hosts file.", text_color="gray").grid(row=1, column=0, columnspan=4, pady=20)

    # --- BUTTON CLICK HANDLERS ---
    def add_rule_action(self):
        if not self.is_admin_mode:
            messagebox.showerror("Permission Error", "Administrative privileges are required to modify netsh portproxy settings!")
            return

        rule_type = self.rule_type.get()
        listen_port_str = self.entry_listen_port.get().strip()
        connect_port_str = self.entry_connect_port.get().strip()
        listen_addr = self.entry_listen_addr.get().strip()

        if not listen_port_str.isdigit() or not connect_port_str.isdigit():
            messagebox.showerror("Validation Error", "Ports must be positive integers!")
            return

        listen_port = int(listen_port_str)
        connect_port = int(connect_port_str)

        if not listen_addr:
            listen_addr = "0.0.0.0"

        # Determine target IP
        target_ip = ""
        distro_name = ""

        if rule_type == "WSL Distro (Dynamic)":
            distro_name = self.combo_distro.get()
            if not distro_name:
                messagebox.showerror("Validation Error", "No WSL Distro selected!")
                return
            
            # Force starting the distro if it's stopped, to get its IP
            self.log_message(f"Resolving IP for WSL Distro '{distro_name}'...")
            target_ip = wm.get_wsl_ip(distro_name)
            
            if not target_ip:
                # If IP could not be resolved, the distro might be stopped. Run a quick command to boot it.
                try:
                    subprocess.run(["wsl.exe", "-d", distro_name, "-e", "true"], capture_output=True)
                    target_ip = wm.get_wsl_ip(distro_name)
                except:
                    pass
                    
            if not target_ip:
                messagebox.showerror("Error", f"Failed to get IP address for WSL Distro '{distro_name}'. Make sure the distro is running.")
                return
        else:
            target_ip = self.entry_static_ip.get().strip()
            # Basic validation
            if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", target_ip):
                messagebox.showerror("Validation Error", "Please enter a valid target IPv4 address!")
                return

        # Try to apply the rule
        self.log_message(f"Adding rule: Listen {listen_addr}:{listen_port} -> Connect {target_ip}:{connect_port}...")
        success = wm.add_portproxy_rule(listen_addr, listen_port, target_ip, connect_port)
        
        if success:
            # Firewall rule configuration
            if self.config.get("auto_firewall", True):
                self.log_message(f"Adding Windows Defender Firewall rule for port {listen_port}...")
                wm.manage_firewall_rule(listen_port, "add")
                
            # If dynamic WSL rule, save to config to track
            if distro_name:
                # Check for existing rule for this listen port to avoid duplicates in config
                self.config["dynamic_rules"] = [r for r in self.config["dynamic_rules"] if r["listen_port"] != listen_port]
                self.config["dynamic_rules"].append({
                    "listen_addr": listen_addr,
                    "listen_port": listen_port,
                    "distro": distro_name,
                    "connect_port": connect_port
                })
                self.save_config()
                self.log_message(f"Saved dynamic rule link for {distro_name} to config.json.")
            else:
                # If they added a static rule over a previous dynamic rule, remove the dynamic config entry
                self.config["dynamic_rules"] = [r for r in self.config["dynamic_rules"] if r["listen_port"] != listen_port]
                self.save_config()

            # Refresh
            self.refresh_all_data()
            self.entry_listen_port.delete(0, "end")
            self.entry_connect_port.delete(0, "end")
            messagebox.showinfo("Success", "Port forwarding rule added successfully!")
        else:
            messagebox.showerror("Error", "Failed to add port proxy rule via netsh.")

    def delete_rule_action(self, listen_addr, listen_port):
        if not self.is_admin_mode:
            messagebox.showerror("Permission Error", "Administrative privileges are required to modify netsh settings!")
            return

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete forwarding rule for port {listen_port}?"):
            self.log_message(f"Deleting rule for Listen {listen_addr}:{listen_port}...")
            success = wm.delete_portproxy_rule(listen_addr, listen_port)
            
            if success:
                # Remove firewall rule
                self.log_message(f"Deleting Windows Defender Firewall rule for port {listen_port}...")
                wm.manage_firewall_rule(listen_port, "delete")
                
                # Update config
                self.config["dynamic_rules"] = [r for r in self.config["dynamic_rules"] if r["listen_port"] != listen_port]
                self.save_config()
                
                self.refresh_all_data()
                messagebox.showinfo("Success", f"Port proxy rule for port {listen_port} deleted.")
            else:
                messagebox.showerror("Error", "Failed to delete port proxy rule.")

    def add_hosts_action(self):
        if not self.is_admin_mode:
            messagebox.showerror("Permission Error", "Administrative privileges are required to edit the hosts file!")
            return

        hostname = self.entry_hostname.get().strip().lower()
        distro_name = self.combo_hosts_distro.get()

        if not hostname:
            messagebox.showerror("Validation Error", "Hostname cannot be empty!")
            return

        if not distro_name:
            messagebox.showerror("Validation Error", "No WSL distro selected!")
            return

        # Clean host name (keep simple domains)
        if not re.match(r"^[a-z0-9.-]+$", hostname):
            messagebox.showerror("Validation Error", "Invalid hostname! Use only letters, numbers, dots, and dashes.")
            return

        # Resolve IP
        self.log_message(f"Resolving IP for {distro_name} to map to hostname '{hostname}'...")
        ip = wm.get_wsl_ip(distro_name)
        if not ip:
            messagebox.showerror("Error", f"Failed to get IP address for WSL distro '{distro_name}'. Distro must be running.")
            return

        # Get existing mappings from file
        current_mappings = wm.get_hosts_mappings()
        current_mappings[hostname] = ip

        # Apply update
        success = wm.update_hosts_mappings(current_mappings)
        if success:
            # Save association to config so auto-sync updates it later
            self.config["dynamic_hosts"][hostname] = distro_name
            self.save_config()
            self.log_message(f"Mapped {hostname} -> {distro_name} ({ip}) in hosts file and config.")
            
            self.refresh_all_data()
            self.entry_hostname.delete(0, "end")
            messagebox.showinfo("Success", f"Hostname '{hostname}' mapped to {distro_name} ({ip}) successfully!")
        else:
            messagebox.showerror("Error", "Failed to write to Windows hosts file. Verify file permissions.")

    def delete_host_action(self, hostname):
        if not self.is_admin_mode:
            messagebox.showerror("Permission Error", "Administrative privileges are required to edit the hosts file!")
            return

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to remove hostname mapping for '{hostname}'?"):
            current_mappings = wm.get_hosts_mappings()
            current_mappings.pop(hostname, None)
            
            success = wm.update_hosts_mappings(current_mappings)
            if success:
                # Remove dynamic association
                self.config["dynamic_hosts"].pop(hostname, None)
                self.save_config()
                self.log_message(f"Removed mapping for {hostname} from hosts file and config.")
                
                self.refresh_all_data()
                messagebox.showinfo("Success", f"Hostname mapping for '{hostname}' removed.")
            else:
                messagebox.showerror("Error", "Failed to update hosts file.")

    # --- SETTINGS FORM ACTIONS ---
    def toggle_auto_sync(self):
        enabled = self.switch_auto_sync.get() != 0
        self.config["auto_sync"] = enabled
        self.save_config()
        self.log_message(f"Auto-Sync enabled: {enabled}")

    def toggle_auto_firewall(self):
        enabled = self.switch_auto_firewall.get() != 0
        self.config["auto_firewall"] = enabled
        self.save_config()
        self.log_message(f"Auto-Firewall enabled: {enabled}")

    def save_interval_action(self):
        val = self.entry_sync_interval.get().strip()
        if not val.isdigit() or int(val) < 2:
            messagebox.showerror("Validation Error", "Interval must be an integer (minimum 2 seconds)!")
            return
        
        self.config["sync_interval"] = int(val)
        self.save_config()
        self.log_message(f"Sync interval set to {val} seconds.")
        messagebox.showinfo("Success", f"Sync interval updated to {val} seconds.")

    # --- AUTO-SYNC BACKGROUND LOOP ---
    def bg_sync_loop(self):
        """Runs in background thread to periodically check WSL IPs and update netsh rules + hosts file."""
        while self.sync_thread_running:
            # Read config settings at start of loop
            sync_enabled = self.config.get("auto_sync", True)
            interval = self.config.get("sync_interval", 10)
            
            if sync_enabled and self.is_admin_mode:
                try:
                    # 1. Fetch current WSL distros and their active IPs
                    distros = wm.list_wsl_distros()
                    current_ips = {}
                    for d in distros:
                        name = d["name"]
                        if d["state"] == "Running":
                            ip = wm.get_wsl_ip(name)
                            if ip:
                                current_ips[name] = ip
                                self.wsl_ips[name] = ip

                    # 2. Check dynamic port forwarding rules
                    dynamic_rules = self.config.get("dynamic_rules", [])
                    active_rules = wm.list_portproxy_rules()
                    
                    changed = False
                    for dr in dynamic_rules:
                        listen_addr = dr.get("listen_addr", "0.0.0.0")
                        listen_port = dr["listen_port"]
                        distro_name = dr["distro"]
                        connect_port = dr["connect_port"]
                        
                        target_ip = current_ips.get(distro_name)
                        if not target_ip:
                            # Distro is stopped or has no IP, skip updating this rule for now
                            continue
                            
                        # Find matching active rule
                        matching_active = None
                        for ar in active_rules:
                            if ar["listen_port"] == listen_port:
                                matching_active = ar
                                break
                                
                        # Check if we need to add or update the rule
                        needs_update = False
                        if not matching_active:
                            # Rule is missing completely
                            self.log_message(f"Auto-Sync: Rule for listen port {listen_port} is missing. Adding...")
                            needs_update = True
                        elif matching_active["connect_addr"] != target_ip or matching_active["connect_port"] != connect_port:
                            # Rule connects to wrong IP (IP changed) or wrong port
                            self.log_message(f"Auto-Sync: WSL IP changed for {distro_name} ({matching_active['connect_addr']} -> {target_ip}). Updating rule for port {listen_port}...")
                            # Delete old rule
                            wm.delete_portproxy_rule(matching_active["listen_addr"], listen_port)
                            needs_update = True
                            
                        if needs_update:
                            # Add/Update rule
                            success = wm.add_portproxy_rule(listen_addr, listen_port, target_ip, connect_port)
                            if success:
                                changed = True
                                if self.config.get("auto_firewall", True):
                                    wm.manage_firewall_rule(listen_port, "add")
                                    
                    # 3. Check dynamic hostnames
                    dynamic_hosts = self.config.get("dynamic_hosts", {})
                    if dynamic_hosts:
                        current_hosts_mappings = wm.get_hosts_mappings()
                        hosts_changed = False
                        
                        for hostname, distro_name in dynamic_hosts.items():
                            target_ip = current_ips.get(distro_name)
                            if not target_ip:
                                continue
                                
                            existing_ip = current_hosts_mappings.get(hostname)
                            if existing_ip != target_ip:
                                self.log_message(f"Auto-Sync: Hostname IP changed for {hostname} -> {distro_name} ({existing_ip} -> {target_ip}). Updating hosts...")
                                current_hosts_mappings[hostname] = target_ip
                                hosts_changed = True
                                
                        if hosts_changed:
                            wm.update_hosts_mappings(current_hosts_mappings)
                            changed = True

                    # 4. If any change happened, refresh the UI
                    if changed:
                        self.log_message("Auto-Sync: System rules updated successfully.")
                        self.after(0, self.async_refresh_data)

                except Exception as e:
                    print(f"Error in bg_sync_loop: {e}")

            # Sleep
            time.sleep(interval)

    def destroy(self):
        # Stop background thread gracefully
        self.sync_thread_running = False
        super().destroy()

if __name__ == "__main__":
    app = FZPortProxyApp()
    app.mainloop()
