# Copyright (c) 2026 Roger Luft (VeilWalker)
# Licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0).
# See LICENSE file in the project root for full license text.
# https://creativecommons.org/licenses/by/4.0/

import tkinter as tk
import customtkinter as ctk
import wsl_manager as wm
import threading
import time
import json
import os
import re
import subprocess
import pystray
from PIL import Image, ImageDraw
from tkinter import messagebox
from version import APP_VERSION, APP_NAME, APP_AUTHOR, APP_WEBSITE

# Set theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

# ─── Internationalization (i18n) ────────────────────────────────────────────
STRINGS = {
    "en": {
        # Header
        "app_title_suffix": "WSL Port Forwarding & Hostname Manager",
        "admin_running": "Running as Administrator",
        "admin_required": "Requires Admin Privileges!",
        "help_about_btn": "Help & About",

        # Tabs
        "tab_port_forwards": "Port Forwards",
        "tab_wsl_distros": "WSL Distros",
        "tab_hosts_config": "Hosts Configuration",
        "tab_settings": "Settings",

        # Port Forwards tab
        "active_rules_header": "Active Windows Portproxy Rules",
        "add_forward_header": "Add Port Forward",
        "col_listen_port": "Listen Port",
        "col_target_ip": "Target IP",
        "col_target_port": "Target Port",
        "col_type": "Type",
        "col_actions": "Actions",
        "lbl_type": "Type:",
        "type_wsl_dynamic": "WSL Distro (Dynamic)",
        "type_static_ip": "Static IP",
        "lbl_listen_port": "Listen Port (Windows):",
        "lbl_target_distro": "Target WSL Distro:",
        "lbl_target_ip_addr": "Target IP Address:",
        "lbl_connect_port": "Connect Port (WSL/Target):",
        "lbl_listen_ip": "Listen IP (Optional):",
        "btn_add_forward": "Add Forward Rule",
        "btn_refresh_rules": "Refresh Rules",
        "no_active_rules": "No active port forwarding rules.",
        "rules_persistence_info": "Rules remain active until changed. FZPortProxy can be closed and reopened at any time.",
        "type_wsl_fmt": "WSL ({distro})",
        "type_static_portproxy": "Static Portproxy",
        "btn_delete": "Delete",

        # WSL tab
        "wsl_header": "Installed Windows Subsystem for Linux (WSL) Instances",
        "btn_scan_wsl": "Scan WSL Distros",
        "col_name": "Name",
        "col_state": "State",
        "col_version": "Version",
        "col_resolved_ip": "Resolved IP Address",
        "no_wsl_detected": "No WSL distros detected on this system.",
        "wsl_not_running": "Not Running / No IP",

        # Hosts tab
        "hosts_header": "Active FZPortProxy Mappings in hosts file",
        "add_hostname_header": "Add Hostname Mapping",
        "lbl_hostname": "Hostname:",
        "lbl_target_wsl_distro": "Target WSL Distro:",
        "btn_add_hostname": "Add Hostname Mappings",
        "col_hostname": "Hostname",
        "col_current_ip": "Current IP",
        "col_dynamic_mapping": "Dynamic Mapping To",
        "static_mapping": "Static Mapping",
        "no_host_mappings": "No FZPortProxy mappings in Windows hosts file.",

        # Settings tab
        "settings_header": "Application Settings",
        "switch_auto_sync": "Enable background Auto-Sync (resolves dynamic WSL IPs automatically)",
        "lbl_sync_interval": "Sync Interval (seconds):",
        "btn_save_interval": "Save Interval",
        "switch_auto_firewall": "Open Windows Firewall port automatically when adding forward rules",
        "switch_minimize_tray": "Minimize to System Tray on close / minimize instead of exiting",
        "lbl_language": "Language / Idioma:",
        "lang_restart_msg": "Language changed. Please restart the application for the change to take effect.",
        "initialized_msg": "FZPortProxy initialized.",

        # Log / sync messages
        "log_scanning": "Scanning system for changes...",
        "log_scanning_wsl": "Scanning WSL instances...",
        "log_resolving_ip": "Resolving IP for WSL Distro '{distro}'...",
        "log_adding_rule": "Adding rule: Listen {listen_addr}:{listen_port} -> Connect {target_ip}:{connect_port}...",
        "log_adding_firewall": "Adding Windows Defender Firewall rule for port {port}...",
        "log_saved_dynamic": "Saved dynamic rule link for {distro} to config.json.",
        "log_deleting_rule": "Deleting rule for Listen {listen_addr}:{listen_port}...",
        "log_deleting_firewall": "Deleting Windows Defender Firewall rule for port {port}...",
        "log_mapping_host": "Mapped {hostname} -> {distro} ({ip}) in hosts file and config.",
        "log_removing_host": "Removed mapping for {hostname} from hosts file and config.",
        "log_tray_init": "System tray icon initialized.",
        "log_tray_fail": "Failed to start system tray: {error}",
        "log_minimized_tray": "Minimized to system tray.",
        "log_auto_sync_enabled": "Auto-Sync enabled: {enabled}",
        "log_auto_firewall_enabled": "Auto-Firewall enabled: {enabled}",
        "log_minimize_tray_enabled": "Minimize to Tray on Close enabled: {enabled}",
        "log_interval_set": "Sync interval set to {val} seconds.",
        "log_autosync_missing": "Auto-Sync: Rule for listen port {port} is missing. Adding...",
        "log_autosync_ip_changed": "Auto-Sync: WSL IP changed for {distro} ({old_ip} -> {new_ip}). Updating rule for port {port}...",
        "log_autosync_host_changed": "Auto-Sync: Hostname IP changed for {hostname} -> {distro} ({old_ip} -> {new_ip}). Updating hosts...",
        "log_autosync_updated": "Auto-Sync: System rules updated successfully.",
        "log_resolving_host_ip": "Resolving IP for {distro} to map to hostname '{hostname}'...",

        # Dialogs
        "err_permission": "Permission Error",
        "err_permission_netsh": "Administrative privileges are required to modify netsh portproxy settings!",
        "err_permission_hosts": "Administrative privileges are required to edit the hosts file!",
        "err_validation": "Validation Error",
        "err_ports_integer": "Ports must be positive integers!",
        "err_no_distro": "No WSL Distro selected!",
        "err_ip_resolve": "Failed to get IP address for WSL Distro '{distro}'. Make sure the distro is running.",
        "err_invalid_ip": "Please enter a valid target IPv4 address!",
        "err_add_rule_fail": "Failed to add port proxy rule via netsh.",
        "err_hostname_empty": "Hostname cannot be empty!",
        "err_no_distro_host": "No WSL distro selected!",
        "err_invalid_hostname": "Invalid hostname! Use only letters, numbers, dots, and dashes.",
        "err_ip_resolve_host": "Failed to get IP address for WSL distro '{distro}'. Distro must be running.",
        "err_hosts_write": "Failed to write to Windows hosts file. Verify file permissions.",
        "err_delete_rule_fail": "Failed to delete port proxy rule.",
        "err_update_hosts_fail": "Failed to update hosts file.",
        "err_interval_invalid": "Interval must be an integer (minimum 2 seconds)!",
        "success": "Success",
        "success_rule_added": "Port forwarding rule added successfully!",
        "success_rule_deleted": "Port proxy rule for port {port} deleted.",
        "success_host_added": "Hostname '{hostname}' mapped to {distro} ({ip}) successfully!",
        "success_host_deleted": "Hostname mapping for '{hostname}' removed.",
        "success_interval": "Sync interval updated to {val} seconds.",
        "confirm_delete": "Confirm Delete",
        "confirm_delete_rule": "Are you sure you want to delete forwarding rule for port {port}?",
        "confirm_delete_host": "Are you sure you want to remove hostname mapping for '{hostname}'?",

        # Help Modal
        "help_title": "Help & About - FZPortProxy",
        "help_tab_quick": "Quick Help",
        "help_tab_about": "About & Donate",
        "help_content": """{app_name} - WSL Port Forwarding & Hostname Manager
Version: {version}

Quick Start Guide:

1. Port Forwarding:
   - Go to the 'Port Forwards' tab to create rules.
   - You can add 'Static' rules (redirecting to a fixed IP) or 'WSL Dynamic' rules.
   - Dynamic rules automatically query the current IP address of your selected WSL distribution.

2. WSL Dynamic IP Syncing:
   - WSL 2 virtual machines get a new dynamic IP address every time they boot.
   - FZPortProxy solves this! It runs a background sync thread that polls WSL IPs.
   - If an IP change is detected, it automatically deletes the outdated netsh port proxy and recreates it with the new IP.
   - You can toggle this behavior and adjust the interval in the 'Settings' tab.

3. Windows Firewall Integration:
   - When adding a rule, FZPortProxy can automatically create a matching inbound rule in Windows Defender Firewall.
   - This allows external traffic to reach your port forwarding rule.
   - This option can be configured in the 'Settings' tab.

4. Hostname Configuration:
   - Want to access your WSL services using a friendly name like 'myproject.wsl' instead of '127.0.0.1'?
   - Go to the 'Hosts Configuration' tab, assign a hostname to a WSL distro, and click Add.
   - FZPortProxy will edit the Windows hosts file safely inside a dedicated block and automatically update the IP when WSL restarts.

5. Rule Persistence:
   - Rules remain active until changed. FZPortProxy can be closed and reopened at any time.
   - The port forwarding and hostname rules are managed at the Windows system level (netsh / hosts file), so they persist independently of this application.

Important: This application MUST be run as Administrator because 'netsh', Windows Firewall, and the 'hosts' file require elevated privileges to modify system configurations.
""",
        "about_author_label": "Author: {author}",
        "btn_webstorage": "Webstorage Site",
        "btn_author_page": "Author Page",
        "btn_github": "GitHub Profile",
        "lbl_contact": "Contact / Support Emails:",
        "donate_title": "Donate / Support the Project",
        "donate_desc": "If this utility saved you time and made your WSL development easier,\nconsider making a contribution! Any amount helps a lot.",
        "btn_copy_pix": "Copy Pix Key (Phone)",
        "pix_copied_title": "Pix Copied",
        "pix_copied_msg": "Pix key copied to clipboard:\n51992452539",

        # Tray
        "tray_show": "Show",
        "tray_exit": "Exit",
    },
    "pt": {
        # Header
        "app_title_suffix": "Encaminhamento de Portas WSL & Gerenciador de Hostnames",
        "admin_running": "Executando como Administrador",
        "admin_required": "Requer Privilégios de Administrador!",
        "help_about_btn": "Ajuda & Sobre",

        # Tabs
        "tab_port_forwards": "Encaminhamentos",
        "tab_wsl_distros": "Distros WSL",
        "tab_hosts_config": "Configuração de Hosts",
        "tab_settings": "Configurações",

        # Port Forwards tab
        "active_rules_header": "Regras Ativas de Portproxy do Windows",
        "add_forward_header": "Adicionar Encaminhamento",
        "col_listen_port": "Porta de Escuta",
        "col_target_ip": "IP de Destino",
        "col_target_port": "Porta de Destino",
        "col_type": "Tipo",
        "col_actions": "Ações",
        "lbl_type": "Tipo:",
        "type_wsl_dynamic": "Distro WSL (Dinâmico)",
        "type_static_ip": "IP Estático",
        "lbl_listen_port": "Porta de Escuta (Windows):",
        "lbl_target_distro": "Distro WSL de Destino:",
        "lbl_target_ip_addr": "Endereço IP de Destino:",
        "lbl_connect_port": "Porta de Conexão (WSL/Destino):",
        "lbl_listen_ip": "IP de Escuta (Opcional):",
        "btn_add_forward": "Adicionar Regra",
        "btn_refresh_rules": "Atualizar Regras",
        "no_active_rules": "Nenhuma regra de encaminhamento de porta ativa.",
        "rules_persistence_info": "As regras permanecem ativas até serem alteradas. O FZPortProxy pode ser fechado e aberto a qualquer momento.",
        "type_wsl_fmt": "WSL ({distro})",
        "type_static_portproxy": "Portproxy Estático",
        "btn_delete": "Excluir",

        # WSL tab
        "wsl_header": "Instâncias Instaladas do Windows Subsystem for Linux (WSL)",
        "btn_scan_wsl": "Escanear Distros WSL",
        "col_name": "Nome",
        "col_state": "Estado",
        "col_version": "Versão",
        "col_resolved_ip": "Endereço IP Resolvido",
        "no_wsl_detected": "Nenhuma distro WSL detectada neste sistema.",
        "wsl_not_running": "Não Executando / Sem IP",

        # Hosts tab
        "hosts_header": "Mapeamentos FZPortProxy Ativos no arquivo hosts",
        "add_hostname_header": "Adicionar Mapeamento de Hostname",
        "lbl_hostname": "Hostname:",
        "lbl_target_wsl_distro": "Distro WSL de Destino:",
        "btn_add_hostname": "Adicionar Mapeamento",
        "col_hostname": "Hostname",
        "col_current_ip": "IP Atual",
        "col_dynamic_mapping": "Mapeamento Dinâmico Para",
        "static_mapping": "Mapeamento Estático",
        "no_host_mappings": "Nenhum mapeamento FZPortProxy no arquivo hosts do Windows.",

        # Settings tab
        "settings_header": "Configurações do Aplicativo",
        "switch_auto_sync": "Ativar Auto-Sync em segundo plano (resolve IPs dinâmicos do WSL automaticamente)",
        "lbl_sync_interval": "Intervalo de Sincronização (segundos):",
        "btn_save_interval": "Salvar Intervalo",
        "switch_auto_firewall": "Abrir porta do Firewall do Windows automaticamente ao adicionar regras de encaminhamento",
        "switch_minimize_tray": "Minimizar para a Bandeja do Sistema ao fechar / minimizar em vez de sair",
        "lbl_language": "Language / Idioma:",
        "lang_restart_msg": "Idioma alterado. Por favor reinicie o aplicativo para que a alteração tenha efeito.",
        "initialized_msg": "FZPortProxy inicializado.",

        # Log / sync messages
        "log_scanning": "Escaneando sistema em busca de alterações...",
        "log_scanning_wsl": "Escaneando instâncias WSL...",
        "log_resolving_ip": "Resolvendo IP da Distro WSL '{distro}'...",
        "log_adding_rule": "Adicionando regra: Escuta {listen_addr}:{listen_port} -> Conexão {target_ip}:{connect_port}...",
        "log_adding_firewall": "Adicionando regra do Windows Defender Firewall para a porta {port}...",
        "log_saved_dynamic": "Link de regra dinâmica salvo para {distro} no config.json.",
        "log_deleting_rule": "Excluindo regra para Escuta {listen_addr}:{listen_port}...",
        "log_deleting_firewall": "Excluindo regra do Windows Defender Firewall para a porta {port}...",
        "log_mapping_host": "Mapeado {hostname} -> {distro} ({ip}) no arquivo hosts e config.",
        "log_removing_host": "Mapeamento removido para {hostname} do arquivo hosts e config.",
        "log_tray_init": "Ícone da bandeja do sistema inicializado.",
        "log_tray_fail": "Falha ao iniciar a bandeja do sistema: {error}",
        "log_minimized_tray": "Minimizado para a bandeja do sistema.",
        "log_auto_sync_enabled": "Auto-Sync ativado: {enabled}",
        "log_auto_firewall_enabled": "Auto-Firewall ativado: {enabled}",
        "log_minimize_tray_enabled": "Minimizar para Bandeja ao Fechar ativado: {enabled}",
        "log_interval_set": "Intervalo de sincronização definido para {val} segundos.",
        "log_autosync_missing": "Auto-Sync: Regra para porta de escuta {port} está ausente. Adicionando...",
        "log_autosync_ip_changed": "Auto-Sync: IP do WSL alterado para {distro} ({old_ip} -> {new_ip}). Atualizando regra para porta {port}...",
        "log_autosync_host_changed": "Auto-Sync: IP do hostname alterado para {hostname} -> {distro} ({old_ip} -> {new_ip}). Atualizando hosts...",
        "log_autosync_updated": "Auto-Sync: Regras do sistema atualizadas com sucesso.",
        "log_resolving_host_ip": "Resolvendo IP de {distro} para mapear ao hostname '{hostname}'...",

        # Dialogs
        "err_permission": "Erro de Permissão",
        "err_permission_netsh": "Privilégios administrativos são necessários para modificar as configurações do netsh portproxy!",
        "err_permission_hosts": "Privilégios administrativos são necessários para editar o arquivo hosts!",
        "err_validation": "Erro de Validação",
        "err_ports_integer": "As portas devem ser números inteiros positivos!",
        "err_no_distro": "Nenhuma Distro WSL selecionada!",
        "err_ip_resolve": "Falha ao obter o endereço IP da Distro WSL '{distro}'. Certifique-se de que a distro está em execução.",
        "err_invalid_ip": "Por favor, insira um endereço IPv4 de destino válido!",
        "err_add_rule_fail": "Falha ao adicionar regra de port proxy via netsh.",
        "err_hostname_empty": "O hostname não pode estar vazio!",
        "err_no_distro_host": "Nenhuma distro WSL selecionada!",
        "err_invalid_hostname": "Hostname inválido! Use apenas letras, números, pontos e hífens.",
        "err_ip_resolve_host": "Falha ao obter o endereço IP da distro WSL '{distro}'. A distro deve estar em execução.",
        "err_hosts_write": "Falha ao gravar no arquivo hosts do Windows. Verifique as permissões do arquivo.",
        "err_delete_rule_fail": "Falha ao excluir a regra de port proxy.",
        "err_update_hosts_fail": "Falha ao atualizar o arquivo hosts.",
        "err_interval_invalid": "O intervalo deve ser um número inteiro (mínimo de 2 segundos)!",
        "success": "Sucesso",
        "success_rule_added": "Regra de encaminhamento de porta adicionada com sucesso!",
        "success_rule_deleted": "Regra de port proxy para a porta {port} excluída.",
        "success_host_added": "Hostname '{hostname}' mapeado para {distro} ({ip}) com sucesso!",
        "success_host_deleted": "Mapeamento de hostname para '{hostname}' removido.",
        "success_interval": "Intervalo de sincronização atualizado para {val} segundos.",
        "confirm_delete": "Confirmar Exclusão",
        "confirm_delete_rule": "Tem certeza de que deseja excluir a regra de encaminhamento da porta {port}?",
        "confirm_delete_host": "Tem certeza de que deseja remover o mapeamento de hostname para '{hostname}'?",

        # Help Modal
        "help_title": "Ajuda & Sobre - FZPortProxy",
        "help_tab_quick": "Ajuda Rápida",
        "help_tab_about": "Sobre & Doação",
        "help_content": """{app_name} - Encaminhamento de Portas WSL & Gerenciador de Hostnames
Versão: {version}

Guia de Início Rápido:

1. Encaminhamento de Portas:
   - Vá para a aba 'Encaminhamentos' para criar regras.
   - Você pode adicionar regras 'Estáticas' (redirecionando para um IP fixo) ou regras 'WSL Dinâmico'.
   - Regras dinâmicas consultam automaticamente o endereço IP atual da sua distribuição WSL selecionada.

2. Sincronização Dinâmica de IP do WSL:
   - As máquinas virtuais WSL 2 recebem um novo endereço IP dinâmico toda vez que iniciam.
   - O FZPortProxy resolve isso! Ele executa uma thread de sincronização em segundo plano que consulta os IPs do WSL.
   - Se uma alteração de IP for detectada, ele exclui automaticamente o port proxy netsh desatualizado e o recria com o novo IP.
   - Você pode alternar esse comportamento e ajustar o intervalo na aba 'Configurações'.

3. Integração com o Firewall do Windows:
   - Ao adicionar uma regra, o FZPortProxy pode criar automaticamente uma regra de entrada correspondente no Firewall do Windows Defender.
   - Isso permite que o tráfego externo alcance sua regra de encaminhamento de porta.
   - Esta opção pode ser configurada na aba 'Configurações'.

4. Configuração de Hostnames:
   - Quer acessar seus serviços WSL usando um nome amigável como 'meuprojeto.wsl' em vez de '127.0.0.1'?
   - Vá para a aba 'Configuração de Hosts', atribua um hostname a uma distro WSL e clique em Adicionar.
   - O FZPortProxy editará o arquivo hosts do Windows com segurança dentro de um bloco dedicado e atualizará automaticamente o IP quando o WSL reiniciar.

5. Persistência das Regras:
   - As regras permanecem ativas até serem alteradas. O FZPortProxy pode ser fechado e aberto a qualquer momento.
   - As regras de encaminhamento de porta e hostname são gerenciadas no nível do sistema Windows (netsh / arquivo hosts), portanto persistem independentemente deste aplicativo.

Importante: Este aplicativo DEVE ser executado como Administrador porque 'netsh', Firewall do Windows e o arquivo 'hosts' requerem privilégios elevados para modificar configurações do sistema.
""",
        "about_author_label": "Autor: {author}",
        "btn_webstorage": "Site Webstorage",
        "btn_author_page": "Página do Autor",
        "btn_github": "Perfil GitHub",
        "lbl_contact": "Emails de Contato / Suporte:",
        "donate_title": "Donate / Apoie o Projeto",
        "donate_desc": "Se este utilitário te economizou tempo e facilitou seu desenvolvimento com WSL,\nconsidere fazer uma contribuição! Qualquer valor ajuda muito.",
        "btn_copy_pix": "Copiar Chave Pix (Celular)",
        "pix_copied_title": "Pix Copiado",
        "pix_copied_msg": "Chave Pix copiada para a área de transferência:\n51992452539",

        # Tray
        "tray_show": "Mostrar",
        "tray_exit": "Sair",
    },
}


class FZPortProxyApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Load Configuration
        self.load_config()

        # Load language strings
        self.lang = self.config.get("language", "en")
        if self.lang not in STRINGS:
            self.lang = "en"
        self.s = STRINGS[self.lang]

        self.title(f"{APP_NAME} v{APP_VERSION} - {self.s['app_title_suffix']}")
        self.geometry("900x650")
        self.resizable(True, True)

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

        # Tray and Window Close Setup
        self.tray_icon = None
        self.bind("<Unmap>", self.on_state_change)
        self.protocol("WM_DELETE_WINDOW", self.on_window_close)
        self.setup_tray_icon()

    def load_config(self):
        default_config = {
            "auto_sync": True,
            "sync_interval": 10,
            "auto_firewall": True,
            "minimize_to_tray_on_close": True,
            "language": "en",
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
        admin_text = self.s["admin_running"] if self.is_admin_mode else self.s["admin_required"]
        admin_color = "#2ecc71" if self.is_admin_mode else "#e74c3c"
        admin_badge = ctk.CTkLabel(
            self.header_frame,
            text=admin_text,
            text_color=admin_color,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        admin_badge.grid(row=0, column=1, padx=10, pady=10, sticky="e")

        # Help & About Button
        help_btn = ctk.CTkButton(
            self.header_frame,
            text=self.s["help_about_btn"],
            width=100,
            height=28,
            fg_color="#34495e",
            hover_color="#2c3e50",
            command=self.open_help_modal
        )
        help_btn.grid(row=0, column=2, padx=(10, 20), pady=10, sticky="e")

        # 2. Main Tabview
        self.tabview = ctk.CTkTabview(self)
        self.tabview.grid(row=1, column=0, sticky="nsew", padx=15, pady=10)

        self.tab_rules = self.tabview.add(self.s["tab_port_forwards"])
        self.tab_wsl = self.tabview.add(self.s["tab_wsl_distros"])
        self.tab_hosts = self.tabview.add(self.s["tab_hosts_config"])
        self.tab_settings = self.tabview.add(self.s["tab_settings"])

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

        list_header = ctk.CTkLabel(list_frame, text=self.s["active_rules_header"], font=ctk.CTkFont(size=14, weight="bold"))
        list_header.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.rules_scroll = ctk.CTkScrollableFrame(list_frame)
        self.rules_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 5))

        # Info label about rule persistence
        info_label = ctk.CTkLabel(
            list_frame,
            text=f"ℹ️  {self.s['rules_persistence_info']}",
            text_color="#7f8c8d",
            font=ctk.CTkFont(size=11),
            wraplength=500,
            justify="left"
        )
        info_label.grid(row=2, column=0, padx=10, pady=(2, 8), sticky="w")

        # Right: Add Forward Form
        form_frame = ctk.CTkFrame(self.tab_rules)
        form_frame.grid(row=0, column=1, sticky="nsew", pady=5)
        form_frame.grid_columnconfigure(0, weight=1)

        form_header = ctk.CTkLabel(form_frame, text=self.s["add_forward_header"], font=ctk.CTkFont(size=14, weight="bold"))
        form_header.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Type Selection (Dynamic WSL or Static IP)
        ctk.CTkLabel(form_frame, text=self.s["lbl_type"]).grid(row=1, column=0, padx=10, pady=(5, 0), sticky="w")
        self.rule_type = ctk.CTkComboBox(form_frame, values=[self.s["type_wsl_dynamic"], self.s["type_static_ip"]], command=self.on_rule_type_change)
        self.rule_type.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        # Listen Port
        ctk.CTkLabel(form_frame, text=self.s["lbl_listen_port"]).grid(row=3, column=0, padx=10, pady=(5, 0), sticky="w")
        self.entry_listen_port = ctk.CTkEntry(form_frame, placeholder_text="e.g. 8080")
        self.entry_listen_port.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

        # Destination WSL Dropdown / IP entry
        self.lbl_dest = ctk.CTkLabel(form_frame, text=self.s["lbl_target_distro"])
        self.lbl_dest.grid(row=5, column=0, padx=10, pady=(5, 0), sticky="w")
        
        self.combo_distro = ctk.CTkComboBox(form_frame, values=[])
        self.combo_distro.grid(row=6, column=0, padx=10, pady=5, sticky="ew")

        self.entry_static_ip = ctk.CTkEntry(form_frame, placeholder_text="e.g. 192.168.1.50")
        # Kept hidden initially until type is changed

        # Target Port
        ctk.CTkLabel(form_frame, text=self.s["lbl_connect_port"]).grid(row=7, column=0, padx=10, pady=(5, 0), sticky="w")
        self.entry_connect_port = ctk.CTkEntry(form_frame, placeholder_text="e.g. 80")
        self.entry_connect_port.grid(row=8, column=0, padx=10, pady=5, sticky="ew")

        # Listen IP (Optional/Advanced, default 0.0.0.0)
        ctk.CTkLabel(form_frame, text=self.s["lbl_listen_ip"]).grid(row=9, column=0, padx=10, pady=(5, 0), sticky="w")
        self.entry_listen_addr = ctk.CTkEntry(form_frame, placeholder_text="0.0.0.0")
        self.entry_listen_addr.grid(row=10, column=0, padx=10, pady=5, sticky="ew")
        self.entry_listen_addr.insert(0, "0.0.0.0")

        # Buttons
        self.btn_add_rule = ctk.CTkButton(form_frame, text=self.s["btn_add_forward"], command=self.add_rule_action, fg_color="#3498db", hover_color="#2980b9")
        self.btn_add_rule.grid(row=11, column=0, padx=10, pady=15, sticky="ew")

        self.btn_refresh_rules = ctk.CTkButton(form_frame, text=self.s["btn_refresh_rules"], command=self.refresh_all_data, fg_color="#95a5a6", hover_color="#7f8c8d")
        self.btn_refresh_rules.grid(row=12, column=0, padx=10, pady=5, sticky="ew")

    def on_rule_type_change(self, value):
        if value == self.s["type_static_ip"]:
            self.lbl_dest.configure(text=self.s["lbl_target_ip_addr"])
            self.combo_distro.grid_forget()
            self.entry_static_ip.grid(row=6, column=0, padx=10, pady=5, sticky="ew")
        else:
            self.lbl_dest.configure(text=self.s["lbl_target_distro"])
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
            text=self.s["wsl_header"], 
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, sticky="w")
        
        ctk.CTkButton(
            wsl_header_frame, 
            text=self.s["btn_scan_wsl"], 
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

        hosts_header = ctk.CTkLabel(hosts_list_frame, text=self.s["hosts_header"], font=ctk.CTkFont(size=14, weight="bold"))
        hosts_header.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.hosts_scroll = ctk.CTkScrollableFrame(hosts_list_frame)
        self.hosts_scroll.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # Right: Add Hostname Form
        hosts_form_frame = ctk.CTkFrame(self.tab_hosts)
        hosts_form_frame.grid(row=0, column=1, sticky="nsew", pady=5)
        hosts_form_frame.grid_columnconfigure(0, weight=1)

        hosts_form_header = ctk.CTkLabel(hosts_form_frame, text=self.s["add_hostname_header"], font=ctk.CTkFont(size=14, weight="bold"))
        hosts_form_header.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        ctk.CTkLabel(hosts_form_frame, text=self.s["lbl_hostname"]).grid(row=1, column=0, padx=10, pady=(5, 0), sticky="w")
        self.entry_hostname = ctk.CTkEntry(hosts_form_frame, placeholder_text="e.g. app.wsl")
        self.entry_hostname.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(hosts_form_frame, text=self.s["lbl_target_wsl_distro"]).grid(row=3, column=0, padx=10, pady=(5, 0), sticky="w")
        self.combo_hosts_distro = ctk.CTkComboBox(hosts_form_frame, values=[])
        self.combo_hosts_distro.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

        self.btn_add_host = ctk.CTkButton(hosts_form_frame, text=self.s["btn_add_hostname"], command=self.add_hosts_action, fg_color="#3498db", hover_color="#2980b9")
        self.btn_add_host.grid(row=5, column=0, padx=10, pady=20, sticky="ew")

    # --- SETTINGS TAB ---
    def setup_tab_settings(self):
        self.tab_settings.grid_columnconfigure(0, weight=1)
        self.tab_settings.grid_rowconfigure(1, weight=1)

        settings_frame = ctk.CTkFrame(self.tab_settings)
        settings_frame.grid(row=0, column=0, sticky="nsew", pady=5)
        settings_frame.grid_columnconfigure(0, weight=1)

        settings_header = ctk.CTkLabel(settings_frame, text=self.s["settings_header"], font=ctk.CTkFont(size=16, weight="bold"))
        settings_header.grid(row=0, column=0, padx=20, pady=15, sticky="w")

        # 1. Auto-sync switch
        self.switch_auto_sync = ctk.CTkSwitch(
            settings_frame, 
            text=self.s["switch_auto_sync"], 
            command=self.toggle_auto_sync
        )
        self.switch_auto_sync.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        if self.config.get("auto_sync", True):
            self.switch_auto_sync.select()

        # 2. Sync interval
        interval_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        interval_frame.grid(row=2, column=0, padx=20, pady=10, sticky="w")
        ctk.CTkLabel(interval_frame, text=self.s["lbl_sync_interval"]).grid(row=0, column=0, sticky="w")
        self.entry_sync_interval = ctk.CTkEntry(interval_frame, width=80)
        self.entry_sync_interval.grid(row=0, column=1, padx=10, sticky="w")
        self.entry_sync_interval.insert(0, str(self.config.get("sync_interval", 10)))
        
        btn_save_interval = ctk.CTkButton(interval_frame, text=self.s["btn_save_interval"], width=100, command=self.save_interval_action)
        btn_save_interval.grid(row=0, column=2, padx=5, sticky="w")

        # 3. Auto-firewall switch
        self.switch_auto_firewall = ctk.CTkSwitch(
            settings_frame, 
            text=self.s["switch_auto_firewall"], 
            command=self.toggle_auto_firewall
        )
        self.switch_auto_firewall.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        if self.config.get("auto_firewall", True):
            self.switch_auto_firewall.select()

        # 4. Minimize to tray switch
        self.switch_minimize_to_tray = ctk.CTkSwitch(
            settings_frame, 
            text=self.s["switch_minimize_tray"], 
            command=self.toggle_minimize_to_tray
        )
        self.switch_minimize_to_tray.grid(row=4, column=0, padx=20, pady=10, sticky="w")
        if self.config.get("minimize_to_tray_on_close", True):
            self.switch_minimize_to_tray.select()

        # 5. Language selector
        lang_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        lang_frame.grid(row=5, column=0, padx=20, pady=10, sticky="w")
        ctk.CTkLabel(lang_frame, text=self.s["lbl_language"]).grid(row=0, column=0, sticky="w")
        
        self.combo_language = ctk.CTkComboBox(
            lang_frame,
            values=["English", "Português"],
            width=150,
            command=self.on_language_change
        )
        self.combo_language.grid(row=0, column=1, padx=10, sticky="w")
        # Set current language in combo
        current_display = "Português" if self.lang == "pt" else "English"
        self.combo_language.set(current_display)

        # 6. Status message log
        self.txt_status_logs = ctk.CTkTextbox(settings_frame, height=150)
        self.txt_status_logs.grid(row=6, column=0, padx=20, pady=20, sticky="ew")
        self.txt_status_logs.insert("0.0", f"{self.s['initialized_msg']}\n")
        self.txt_status_logs.configure(state="disabled")

    def on_language_change(self, value):
        new_lang = "pt" if value == "Português" else "en"
        if new_lang != self.lang:
            self.config["language"] = new_lang
            self.save_config()
            # Use the NEW language's restart message
            restart_msg = STRINGS[new_lang]["lang_restart_msg"]
            messagebox.showinfo("FZPortProxy", restart_msg)

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
        self.log_message(self.s["log_scanning"])
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
        self.log_message(self.s["log_scanning_wsl"])
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
        ctk.CTkLabel(self.rules_scroll, text=self.s["col_listen_port"], font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.rules_scroll, text=self.s["col_target_ip"], font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.rules_scroll, text=self.s["col_target_port"], font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.rules_scroll, text=self.s["col_type"], font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=5, pady=5, sticky="w")
        ctk.CTkLabel(self.rules_scroll, text=self.s["col_actions"], font=ctk.CTkFont(weight="bold")).grid(row=0, column=4, padx=5, pady=5, sticky="w")

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

            type_text = self.s["type_wsl_fmt"].format(distro=linked_distro) if is_dynamic else self.s["type_static_portproxy"]
            type_color = "#3498db" if is_dynamic else "#e67e22"

            ctk.CTkLabel(self.rules_scroll, text=f"{listen_addr}:{listen_port}").grid(row=row_idx, column=0, padx=5, pady=3, sticky="w")
            ctk.CTkLabel(self.rules_scroll, text=connect_addr).grid(row=row_idx, column=1, padx=5, pady=3, sticky="w")
            ctk.CTkLabel(self.rules_scroll, text=str(connect_port)).grid(row=row_idx, column=2, padx=5, pady=3, sticky="w")
            
            lbl_type = ctk.CTkLabel(self.rules_scroll, text=type_text, text_color=type_color, font=ctk.CTkFont(size=11, weight="bold"))
            lbl_type.grid(row=row_idx, column=3, padx=5, pady=3, sticky="w")

            btn_del = ctk.CTkButton(
                self.rules_scroll, 
                text=self.s["btn_delete"], 
                width=60, 
                height=22, 
                fg_color="#e74c3c", 
                hover_color="#c0392b",
                command=lambda la=listen_addr, lp=listen_port: self.delete_rule_action(la, lp)
            )
            btn_del.grid(row=row_idx, column=4, padx=5, pady=3, sticky="w")
            row_idx += 1

        if not active_rules:
            ctk.CTkLabel(self.rules_scroll, text=self.s["no_active_rules"], text_color="gray").grid(row=1, column=0, columnspan=5, pady=20)

    def populate_wsl_ui(self):
        # Clear frame
        for widget in self.wsl_scroll.winfo_children():
            widget.destroy()

        # Add headers
        ctk.CTkLabel(self.wsl_scroll, text=self.s["col_name"], font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.wsl_scroll, text=self.s["col_state"], font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.wsl_scroll, text=self.s["col_version"], font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.wsl_scroll, text=self.s["col_resolved_ip"], font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=10, pady=5, sticky="w")

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
            ip = self.wsl_ips.get(name, self.s["wsl_not_running"])
            ip_color = "white" if ip != self.s["wsl_not_running"] else "gray"

            ctk.CTkLabel(self.wsl_scroll, text=display_name).grid(row=row_idx, column=0, padx=10, pady=5, sticky="w")
            
            lbl_state = ctk.CTkLabel(self.wsl_scroll, text=state, text_color=state_color, font=ctk.CTkFont(weight="bold"))
            lbl_state.grid(row=row_idx, column=1, padx=10, pady=5, sticky="w")
            
            ctk.CTkLabel(self.wsl_scroll, text=f"WSL {version}").grid(row=row_idx, column=2, padx=10, pady=5, sticky="w")
            
            lbl_ip = ctk.CTkLabel(self.wsl_scroll, text=ip, text_color=ip_color)
            lbl_ip.grid(row=row_idx, column=3, padx=10, pady=5, sticky="w")
            row_idx += 1

        if not self.wsl_distros:
            ctk.CTkLabel(self.wsl_scroll, text=self.s["no_wsl_detected"], text_color="gray").grid(row=1, column=0, columnspan=4, pady=20)

    def populate_hosts_ui(self, hosts_rules):
        # Clear frame
        for widget in self.hosts_scroll.winfo_children():
            widget.destroy()

        # Add headers
        ctk.CTkLabel(self.hosts_scroll, text=self.s["col_hostname"], font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.hosts_scroll, text=self.s["col_current_ip"], font=ctk.CTkFont(weight="bold")).grid(row=0, column=1, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.hosts_scroll, text=self.s["col_dynamic_mapping"], font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=10, pady=5, sticky="w")
        ctk.CTkLabel(self.hosts_scroll, text=self.s["col_actions"], font=ctk.CTkFont(weight="bold")).grid(row=0, column=3, padx=10, pady=5, sticky="w")

        row_idx = 1
        for host, ip in hosts_rules.items():
            # Check if this maps to a dynamic host
            linked_distro = self.config.get("dynamic_hosts", {}).get(host, self.s["static_mapping"])
            distro_color = "#3498db" if linked_distro != self.s["static_mapping"] else "#95a5a6"

            ctk.CTkLabel(self.hosts_scroll, text=host).grid(row=row_idx, column=0, padx=10, pady=3, sticky="w")
            ctk.CTkLabel(self.hosts_scroll, text=ip).grid(row=row_idx, column=1, padx=10, pady=3, sticky="w")
            
            lbl_distro = ctk.CTkLabel(self.hosts_scroll, text=linked_distro, text_color=distro_color, font=ctk.CTkFont(size=11, weight="bold"))
            lbl_distro.grid(row=row_idx, column=2, padx=10, pady=3, sticky="w")

            btn_del = ctk.CTkButton(
                self.hosts_scroll, 
                text=self.s["btn_delete"], 
                width=60, 
                height=22, 
                fg_color="#e74c3c", 
                hover_color="#c0392b",
                command=lambda h=host: self.delete_host_action(h)
            )
            btn_del.grid(row=row_idx, column=3, padx=10, pady=3, sticky="w")
            row_idx += 1

        if not hosts_rules:
            ctk.CTkLabel(self.hosts_scroll, text=self.s["no_host_mappings"], text_color="gray").grid(row=1, column=0, columnspan=4, pady=20)

    # --- BUTTON CLICK HANDLERS ---
    def add_rule_action(self):
        if not self.is_admin_mode:
            messagebox.showerror(self.s["err_permission"], self.s["err_permission_netsh"])
            return

        rule_type = self.rule_type.get()
        listen_port_str = self.entry_listen_port.get().strip()
        connect_port_str = self.entry_connect_port.get().strip()
        listen_addr = self.entry_listen_addr.get().strip()

        if not listen_port_str.isdigit() or not connect_port_str.isdigit():
            messagebox.showerror(self.s["err_validation"], self.s["err_ports_integer"])
            return

        listen_port = int(listen_port_str)
        connect_port = int(connect_port_str)

        if not listen_addr:
            listen_addr = "0.0.0.0"

        # Determine target IP
        target_ip = ""
        distro_name = ""

        if rule_type == self.s["type_wsl_dynamic"]:
            distro_name = self.combo_distro.get()
            if not distro_name:
                messagebox.showerror(self.s["err_validation"], self.s["err_no_distro"])
                return
            
            # Force starting the distro if it's stopped, to get its IP
            self.log_message(self.s["log_resolving_ip"].format(distro=distro_name))
            target_ip = wm.get_wsl_ip(distro_name)
            
            if not target_ip:
                # If IP could not be resolved, the distro might be stopped. Run a quick command to boot it.
                try:
                    subprocess.run(["wsl.exe", "-d", distro_name, "-e", "true"], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    target_ip = wm.get_wsl_ip(distro_name)
                except:
                    pass
                    
            if not target_ip:
                messagebox.showerror("Error", self.s["err_ip_resolve"].format(distro=distro_name))
                return
        else:
            target_ip = self.entry_static_ip.get().strip()
            # Basic validation
            if not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", target_ip):
                messagebox.showerror(self.s["err_validation"], self.s["err_invalid_ip"])
                return

        # Try to apply the rule
        self.log_message(self.s["log_adding_rule"].format(listen_addr=listen_addr, listen_port=listen_port, target_ip=target_ip, connect_port=connect_port))
        success = wm.add_portproxy_rule(listen_addr, listen_port, target_ip, connect_port)
        
        if success:
            # Firewall rule configuration
            if self.config.get("auto_firewall", True):
                self.log_message(self.s["log_adding_firewall"].format(port=listen_port))
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
                self.log_message(self.s["log_saved_dynamic"].format(distro=distro_name))
            else:
                # If they added a static rule over a previous dynamic rule, remove the dynamic config entry
                self.config["dynamic_rules"] = [r for r in self.config["dynamic_rules"] if r["listen_port"] != listen_port]
                self.save_config()

            # Refresh
            self.refresh_all_data()
            self.entry_listen_port.delete(0, "end")
            self.entry_connect_port.delete(0, "end")
            messagebox.showinfo(self.s["success"], self.s["success_rule_added"])
        else:
            messagebox.showerror("Error", self.s["err_add_rule_fail"])

    def delete_rule_action(self, listen_addr, listen_port):
        if not self.is_admin_mode:
            messagebox.showerror(self.s["err_permission"], self.s["err_permission_netsh"])
            return

        if messagebox.askyesno(self.s["confirm_delete"], self.s["confirm_delete_rule"].format(port=listen_port)):
            self.log_message(self.s["log_deleting_rule"].format(listen_addr=listen_addr, listen_port=listen_port))
            success = wm.delete_portproxy_rule(listen_addr, listen_port)
            
            if success:
                # Remove firewall rule
                self.log_message(self.s["log_deleting_firewall"].format(port=listen_port))
                wm.manage_firewall_rule(listen_port, "delete")
                
                # Update config
                self.config["dynamic_rules"] = [r for r in self.config["dynamic_rules"] if r["listen_port"] != listen_port]
                self.save_config()
                
                self.refresh_all_data()
                messagebox.showinfo(self.s["success"], self.s["success_rule_deleted"].format(port=listen_port))
            else:
                messagebox.showerror("Error", self.s["err_delete_rule_fail"])

    def add_hosts_action(self):
        if not self.is_admin_mode:
            messagebox.showerror(self.s["err_permission"], self.s["err_permission_hosts"])
            return

        hostname = self.entry_hostname.get().strip().lower()
        distro_name = self.combo_hosts_distro.get()

        if not hostname:
            messagebox.showerror(self.s["err_validation"], self.s["err_hostname_empty"])
            return

        if not distro_name:
            messagebox.showerror(self.s["err_validation"], self.s["err_no_distro_host"])
            return

        # Clean host name (keep simple domains)
        if not re.match(r"^[a-z0-9.-]+$", hostname):
            messagebox.showerror(self.s["err_validation"], self.s["err_invalid_hostname"])
            return

        # Resolve IP
        self.log_message(self.s["log_resolving_host_ip"].format(distro=distro_name, hostname=hostname))
        ip = wm.get_wsl_ip(distro_name)
        if not ip:
            messagebox.showerror("Error", self.s["err_ip_resolve_host"].format(distro=distro_name))
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
            self.log_message(self.s["log_mapping_host"].format(hostname=hostname, distro=distro_name, ip=ip))
            
            self.refresh_all_data()
            self.entry_hostname.delete(0, "end")
            messagebox.showinfo(self.s["success"], self.s["success_host_added"].format(hostname=hostname, distro=distro_name, ip=ip))
        else:
            messagebox.showerror("Error", self.s["err_hosts_write"])

    def delete_host_action(self, hostname):
        if not self.is_admin_mode:
            messagebox.showerror(self.s["err_permission"], self.s["err_permission_hosts"])
            return

        if messagebox.askyesno(self.s["confirm_delete"], self.s["confirm_delete_host"].format(hostname=hostname)):
            current_mappings = wm.get_hosts_mappings()
            current_mappings.pop(hostname, None)
            
            success = wm.update_hosts_mappings(current_mappings)
            if success:
                # Remove dynamic association
                self.config["dynamic_hosts"].pop(hostname, None)
                self.save_config()
                self.log_message(self.s["log_removing_host"].format(hostname=hostname))
                
                self.refresh_all_data()
                messagebox.showinfo(self.s["success"], self.s["success_host_deleted"].format(hostname=hostname))
            else:
                messagebox.showerror("Error", self.s["err_update_hosts_fail"])

    # --- SETTINGS FORM ACTIONS ---
    def toggle_auto_sync(self):
        enabled = self.switch_auto_sync.get() != 0
        self.config["auto_sync"] = enabled
        self.save_config()
        self.log_message(self.s["log_auto_sync_enabled"].format(enabled=enabled))

    def toggle_auto_firewall(self):
        enabled = self.switch_auto_firewall.get() != 0
        self.config["auto_firewall"] = enabled
        self.save_config()
        self.log_message(self.s["log_auto_firewall_enabled"].format(enabled=enabled))

    def toggle_minimize_to_tray(self):
        enabled = self.switch_minimize_to_tray.get() != 0
        self.config["minimize_to_tray_on_close"] = enabled
        self.save_config()
        self.log_message(self.s["log_minimize_tray_enabled"].format(enabled=enabled))

    # --- TRAY ICON & HELP MODAL IMPLEMENTATION ---
    def create_tray_icon_image(self):
        try:
            img = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            # Circular icon
            draw.ellipse([4, 4, 60, 60], fill=(30, 41, 59)) # Slate background
            draw.ellipse([8, 8, 56, 56], fill=(59, 130, 246)) # Blue circle
            
            # Connect two white nodes with a line and arrow head
            draw.ellipse([14, 24, 26, 36], fill=(255, 255, 255)) # Left node
            draw.ellipse([38, 24, 50, 36], fill=(255, 255, 255)) # Right node
            draw.line([26, 30, 38, 30], fill=(255, 255, 255), width=3) # Connector line
            draw.polygon([(34, 26), (38, 30), (34, 34)], fill=(255, 255, 255)) # Arrow head
            return img
        except Exception as e:
            print(f"Error creating tray image: {e}")
            return Image.new('RGB', (1, 1), color='blue')

    def setup_tray_icon(self):
        try:
            def on_click(icon, item):
                if str(item) == self.s["tray_show"]:
                    self.show_window_from_tray()
                elif str(item) == self.s["tray_exit"]:
                    self.quit_app_entirely()

            menu = pystray.Menu(
                pystray.MenuItem(self.s["tray_show"], on_click, default=True),
                pystray.MenuItem(self.s["tray_exit"], on_click)
            )
            
            img = self.create_tray_icon_image()
            self.tray_icon = pystray.Icon("fzportproxy", img, "FZPortProxy", menu)
            
            # Start tray in a background thread
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
            self.log_message(self.s["log_tray_init"])
        except Exception as e:
            print(f"Error starting system tray: {e}")
            self.log_message(self.s["log_tray_fail"].format(error=e))

    def on_state_change(self, event=None):
        # Only act when the main window itself is minimized (iconic)
        if event and event.widget == self and self.state() == "iconic":
            self.withdraw()
            self.log_message(self.s["log_minimized_tray"])

    def on_window_close(self):
        if self.config.get("minimize_to_tray_on_close", True):
            self.withdraw()
            self.log_message(self.s["log_minimized_tray"])
        else:
            self.quit_app_entirely()

    def show_window_from_tray(self):
        self.after(0, self.deiconify)
        self.after(50, self.focus_force)
        self.after(100, lambda: self.state("normal"))

    def quit_app_entirely(self):
        self.sync_thread_running = False
        try:
            if hasattr(self, "tray_icon") and self.tray_icon:
                self.tray_icon.stop()
        except:
            pass
        self.after(0, self.destroy)

    def open_help_modal(self):
        if hasattr(self, "help_win") and self.help_win.winfo_exists():
            self.help_win.focus()
            return
            
        self.help_win = ctk.CTkToplevel(self)
        self.help_win.title(self.s["help_title"])
        self.help_win.geometry("600x520")
        self.help_win.resizable(False, False)
        # Ensure it stays on top
        self.help_win.after(200, lambda: self.help_win.attributes("-topmost", True))
        
        # Setup tabs inside the modal
        tabview = ctk.CTkTabview(self.help_win)
        tabview.pack(fill="both", expand=True, padx=15, pady=15)
        
        tab_help = tabview.add(self.s["help_tab_quick"])
        tab_about = tabview.add(self.s["help_tab_about"])
        
        # 1. Quick Help Tab
        help_txt = ctk.CTkTextbox(tab_help, wrap="word")
        help_txt.pack(fill="both", expand=True, padx=10, pady=10)
        
        help_content = self.s["help_content"].format(app_name=APP_NAME, version=APP_VERSION)
        help_txt.insert("1.0", help_content)
        help_txt.configure(state="disabled")
        
        # 2. About & Donate Tab
        about_frame = ctk.CTkScrollableFrame(tab_about)
        about_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        ctk.CTkLabel(about_frame, text=f"{APP_NAME} v{APP_VERSION}", font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", pady=5)
        ctk.CTkLabel(about_frame, text=self.s["about_author_label"].format(author=APP_AUTHOR), font=ctk.CTkFont(weight="bold")).pack(anchor="w", pady=2)
        
        # Site / Links
        def open_url(url):
            import webbrowser
            webbrowser.open(url)
            
        link_frame = ctk.CTkFrame(about_frame, fg_color="transparent")
        link_frame.pack(fill="x", pady=10)
        
        ctk.CTkButton(link_frame, text=self.s["btn_webstorage"], width=120, command=lambda: open_url("https://www.webstorage.com.br")).grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkButton(link_frame, text=self.s["btn_author_page"], width=120, command=lambda: open_url("https://about.rogerluft.com.br")).grid(row=0, column=1, padx=5, pady=5)
        ctk.CTkButton(link_frame, text=self.s["btn_github"], width=120, command=lambda: open_url("https://github.com/RLuf/")).grid(row=0, column=2, padx=5, pady=5)
        
        # Emails
        email_frame = ctk.CTkFrame(about_frame)
        email_frame.pack(fill="x", pady=10, padx=5)
        ctk.CTkLabel(email_frame, text=self.s["lbl_contact"], font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        ctk.CTkLabel(email_frame, text="• roger@webstorage.com.br\n• eu@rogerluft.com.br").pack(anchor="w", padx=20, pady=5)
        
        # Donate Section
        donate_frame = ctk.CTkFrame(about_frame, border_color="#e74c3c", border_width=2, fg_color="#2c1e1e")
        donate_frame.pack(fill="x", pady=15, padx=5)
        
        ctk.CTkLabel(donate_frame, text=self.s["donate_title"], font=ctk.CTkFont(size=14, weight="bold"), text_color="#e74c3c").pack(anchor="w", padx=15, pady=5)
        ctk.CTkLabel(donate_frame, text=self.s["donate_desc"], justify="left").pack(anchor="w", padx=15, pady=5)
        
        pix_key = "51992452539"
        
        def copy_pix():
            self.clipboard_clear()
            self.clipboard_append(pix_key)
            self.update()
            messagebox.showinfo(self.s["pix_copied_title"], self.s["pix_copied_msg"])
            
        pix_btn = ctk.CTkButton(donate_frame, text=self.s["btn_copy_pix"], fg_color="#e74c3c", hover_color="#c0392b", command=copy_pix)
        pix_btn.pack(pady=10)

    def save_interval_action(self):
        val = self.entry_sync_interval.get().strip()
        if not val.isdigit() or int(val) < 2:
            messagebox.showerror(self.s["err_validation"], self.s["err_interval_invalid"])
            return
        
        self.config["sync_interval"] = int(val)
        self.save_config()
        self.log_message(self.s["log_interval_set"].format(val=val))
        messagebox.showinfo(self.s["success"], self.s["success_interval"].format(val=val))

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
                            self.log_message(self.s["log_autosync_missing"].format(port=listen_port))
                            needs_update = True
                        elif matching_active["connect_addr"] != target_ip or matching_active["connect_port"] != connect_port:
                            # Rule connects to wrong IP (IP changed) or wrong port
                            self.log_message(self.s["log_autosync_ip_changed"].format(distro=distro_name, old_ip=matching_active['connect_addr'], new_ip=target_ip, port=listen_port))
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
                                self.log_message(self.s["log_autosync_host_changed"].format(hostname=hostname, distro=distro_name, old_ip=existing_ip, new_ip=target_ip))
                                current_hosts_mappings[hostname] = target_ip
                                hosts_changed = True
                                
                        if hosts_changed:
                            wm.update_hosts_mappings(current_hosts_mappings)
                            changed = True

                    # 4. If any change happened, refresh the UI
                    if changed:
                        self.log_message(self.s["log_autosync_updated"])
                        self.after(0, self.async_refresh_data)

                except Exception as e:
                    print(f"Error in bg_sync_loop: {e}")

            # Sleep
            time.sleep(interval)

    def destroy(self):
        # Stop background thread gracefully
        self.sync_thread_running = False
        try:
            if hasattr(self, "tray_icon") and self.tray_icon:
                self.tray_icon.stop()
        except:
            pass
        super().destroy()

if __name__ == "__main__":
    app = FZPortProxyApp()
    app.mainloop()
