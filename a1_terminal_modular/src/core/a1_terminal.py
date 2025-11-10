"""A1Terminal Main Class"""

import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog, colorchooser
import os
import yaml
import json
import copy
import threading
from datetime import datetime

from src.ui.color_wheel import ColorWheel
from src.ui.chat_bubble import ChatBubble
from src.ui.categorized_combobox import CategorizedComboBox
from src.ui.resizable_pane import ResizablePane
from src.ui.session_card import SessionCard
from src.ui.model_selector import ModelSelector
from src.ui.enhanced_chat_bubble import EnhancedChatBubble
from src.ui.ultimate_ui import setup_ultimate_ui
from src.ui.model_info_dropdown import ModelInfoDropdown
from src.core.ollama_manager import OllamaManager

class A1Terminal:
    """Main application class"""
    def __init__(self):
        self._session_just_loaded = False
        
        # Load YAML configuration file FIRST
        self.config_file = "a1_terminal_config.yaml"
        self.config = self.load_config()
        
        # Now create root with config values
        self.root = ctk.CTk()
        self.root.title("A1-Terminal - Ollama Chat Client")
        
        # Window size from config
        window_width = self.config.get('ui_window_width', 1400)
        window_height = self.config.get('ui_window_height', 900)
        self.root.geometry(f"{window_width}x{window_height}")
        
        # Make window resizable and set minimum size
        self.root.resizable(True, True)
        self.root.minsize(900, 500)
        self.root.maxsize(2560, 1440)
        
        self.ollama = OllamaManager()
        self.current_model = None
        self.chat_history = []
        
        # Stop functionality for generation and downloads
        self.generation_stopped = False
        self.download_stopped = False
        self.current_generation_thread = None
        self.current_download_thread = None
        
        # Progressive message display
        self.response_message_widget = None
        self.current_response_text = ""
        
        # Message history for arrow key navigation
        self.message_history = []
        self.history_index = -1
        
        # Chat bubbles for session management
        self.chat_bubbles = []
        
        # Initialize session management variables early
        self.sessions = {}
        self.current_session_id = None
        self.current_session_bias = ""
        self.bias_auto_save_timer = None
        
        # Initialize sessions directory early
        self.sessions_dir = os.path.join(os.getcwd(), "sessions")
        if not os.path.exists(self.sessions_dir):
            os.makedirs(self.sessions_dir)
        
        # Auto-save timer for session saving
        self.auto_save_timer = None
        
        # Setup UI
        self.setup_ui()
        self.check_ollama_status()
    
    def get_default_config(self):
        """Returns the default configuration"""
        return {
            # ========== BUBBLE COLORS ==========
            "user_bg_color": "#003300",      # You - Background
            "user_text_color": "#00FF00",    # You - Text (Matrix)
            "ai_bg_color": "#1E3A5F",        # AI - Background
            "ai_text_color": "white",        # AI - Text
            "system_bg_color": "#722F37",    # System - Background
            "system_text_color": "white",    # System - Text
            
            # ========== FONTS ==========
            "user_font": "Courier New",      # You - Matrix font
            "user_font_size": 11,            # You - Individual size
            "ai_font": "Consolas",           # AI - Code font
            "ai_font_size": 11,              # AI - Individual size
            "system_font": "Arial",          # System - Standard font
            "system_font_size": 10,          # System - Individual size
            
            # ========== UI LAYOUT ==========
            "ui_session_panel_width": 350,   # Width of session panel (px)
            "ui_window_width": 1400,         # Window width at startup (px)
            "ui_window_height": 900,         # Window height at startup (px)
            "ui_padding_main": 10,           # Main outer padding (px)
            "ui_padding_content": 5,         # Content padding (px)
            
            # ========== CHAT DISPLAY ==========
            "ui_chat_bubble_corner_radius": 10,    # Bubble corner radius
            "ui_chat_bubble_padding_x": 15,        # Bubble horizontal padding
            "ui_chat_bubble_padding_y": 10,        # Bubble vertical padding
            "ui_chat_spacing": 10,                 # Spacing between bubbles
            "ui_chat_max_width_ratio": 0.8,        # Max bubble width (80% of container)
            
            # ========== INPUT AREA ==========
            "ui_input_height": 40,           # Height of input field (px)
            "ui_input_font_size": 12,        # Font size in input
            "ui_button_width": 100,          # Width of buttons (px)
            "ui_button_height": 40,          # Height of buttons (px)
            
            # ========== SESSION LIST ==========
            "ui_session_item_height": 60,    # Height of session item (px)
            "ui_session_font_size": 11,      # Font size in session list
            "ui_session_spacing": 5,         # Spacing between sessions
            
            # ========== MODEL SELECTOR ==========
            "ui_model_dropdown_height": 32,  # Height of model dropdown (px)
            "ui_model_button_size": 35,      # Size of model buttons (px)
            "ui_model_font_size": 11,        # Font size in model selector
            "ui_model_title_size": 12,       # Font size model title
            "ui_model_label_size": 9,        # Font size model labels
            
            # ========== SESSION BUTTONS ==========
            "ui_session_button_width": 140,  # Width session buttons
            "ui_session_button_height": 25,  # Height session buttons
            "ui_session_button_font": 9,     # Font size session buttons
            
            # ========== BIAS TEXTBOX ==========
            "ui_bias_height": 60,            # Height BIAS input field
            "ui_bias_font_size": 9,          # Font size BIAS
            
            # ========== DEBUG BUTTONS ==========
            "ui_debug_button_height": 30,    # Height debug buttons
            "ui_debug_button_font": 9,       # Font size debug buttons
            
            # ========== TABS ==========
            "ui_tab_font_size": 13,          # Font size of tab names
            "ui_tab_height": 40,             # Height of tab bar (px)
            
            # ========== CONFIG TAB ==========
            "ui_config_label_width": 200,    # Width of labels in config
            "ui_config_slider_width": 300,   # Width of sliders
            "ui_config_entry_width": 200,    # Width of input fields
            
            # ========== COLORS & THEME ==========
            "ui_bg_color": "#1a1a1a",        # Main background
            "ui_fg_color": "#2b2b2b",        # Foreground/panels
            "ui_accent_color": "#2B8A3E",    # Accent color (buttons)
            "ui_hover_color": "#37A24B",     # Hover color
            "ui_text_color": "white",        # Standard text color
            "ui_border_color": "#3a3a3a",    # Border color
            
            # ========== SCROLLBAR ==========
            "ui_scrollbar_width": 12,        # Width of scrollbar (px)
            "ui_scrollbar_corner_radius": 6, # Scrollbar corner radius
            
            # ========== GENERAL OPTIONS ==========
            "show_system_messages": True,    # Show system messages in chat
            "auto_scroll_chat": True,        # Auto-scroll to new messages
            "show_timestamps": True,         # Show timestamps in chat
            "compact_mode": False,           # Compact display
        }
    
    def load_config(self):
        """Loads the configuration from the YAML file or creates default config"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as file:
                    config = yaml.safe_load(file)
                    if config:
                        # Fill missing values with default values
                        default_config = self.get_default_config()
                        for key, value in default_config.items():
                            if key not in config:
                                config[key] = value
                        print(f"✅ Configuration loaded from {self.config_file}")
                        return config
                    
            # Fallback to default configuration
            default_config = self.get_default_config()
            self.save_config(default_config)
            print(f"📝 Default configuration created in {self.config_file}")
            return default_config
            
        except Exception as e:
            print(f"❌ Error loading configuration: {e}")
            print("🔄 Using default configuration")
            return self.get_default_config()
    
    def save_config(self, config=None):
        """Saves the configuration to the YAML file"""
        try:
            config_to_save = config or self.config
            
            # Create YAML with comments
            yaml_content = """# A1-Terminal Configuration File
# This file is automatically created and updated
# All changes are saved when applying in the GUI

# ========================================
# CHAT BUBBLE COLORS
# ========================================
"""
            
            # Bubble colors section
            bubble_colors = {k: v for k, v in config_to_save.items() if 'color' in k and 'console' not in k}
            yaml_content += "# Colors for chat bubbles (Hex codes)\nbubble_colors:\n"
            
            for key, value in bubble_colors.items():
                comment = ""
                if "user" in key:
                    comment = "  # You"
                elif "ai" in key:
                    comment = "  # AI Model"
                elif "system" in key:
                    comment = "  # System Messages"
                yaml_content += f"  {key}: \"{value}\"{comment}\n"
            
            
            # Console configuration
            console_config = {k: v for k, v in config_to_save.items() if 'console' in k}
            yaml_content += "# Terminal/Console Output Styling\nconsole:\n"
            
            for key, value in console_config.items():
                yaml_content += f"  {key}: \"{value}\"\n"
                
            # Write YAML file
            with open(self.config_file, 'w', encoding='utf-8') as file:
                # Write manual YAML structure for better comments
                file.write(yaml_content)
                
                # Add flat structure for easy compatibility
                file.write("\n# Flat structure for compatibility (automatically generated)\n")
                yaml.dump(config_to_save, file, default_flow_style=False, allow_unicode=True)
            
            print(f"💾 Configuration saved in {self.config_file}")
            
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
    
    def reset_config_to_defaults(self):
        """Resets the configuration to default values and saves it"""
        self.config = self.get_default_config()
        self.save_config()
    
    
    def console_print(self, text, style="normal"):
        """Simple console output (without styling)"""
        print(text)
    
    

    # ============================================
    # SESSION MANAGEMENT SYSTEM
    # ============================================
    
    def setup_session_panel(self):
        """Creates the Session Management Panel"""
        
        # ============================================
        # MODEL MANAGEMENT AREA (TOP)
        # ============================================
        
        # Model Management Frame (at the top)
        model_frame = ctk.CTkFrame(self.session_panel)
        model_frame.pack(fill="x", padx=self.config.get("ui_padding_content", 5), 
                        pady=self.config.get("ui_padding_content", 5))
        
        model_title = ctk.CTkLabel(model_frame, text="🤖 Model Management", 
                                  font=("Arial", self.config.get("ui_model_title_size", 12), "bold"))
        model_title.pack(anchor="w", padx=self.config.get("ui_padding_main", 10), 
                        pady=(self.config.get("ui_padding_main", 10), self.config.get("ui_padding_content", 5)))
        
        # Ollama Status
        self.status_label = ctk.CTkLabel(model_frame, text="Ollama Status: Checking...",
                                        font=("Arial", self.config.get("ui_model_label_size", 9)))
        self.status_label.pack(anchor="w", padx=self.config.get("ui_padding_main", 10), pady=2)
        
        # Installed Models
        installed_frame = ctk.CTkFrame(model_frame)
        installed_frame.pack(fill="x", padx=self.config.get("ui_padding_main", 10), 
                            pady=self.config.get("ui_padding_content", 5))
        
        self.installed_label = ctk.CTkLabel(installed_frame, text="📦 Installed:",
                                          font=("Arial", self.config.get("ui_model_label_size", 9), "bold"))
        self.installed_label.pack(anchor="w", padx=self.config.get("ui_padding_content", 5), pady=2)
        
        # Model Dropdown und Info Panel in einer Zeile
        model_controls_frame = ctk.CTkFrame(installed_frame)
        model_controls_frame.pack(fill="x", padx=self.config.get("ui_padding_content", 5), pady=2)
        
        # Linke Seite: Dropdown
        left_frame = ctk.CTkFrame(model_controls_frame, fg_color="transparent")
        left_frame.pack(side="left", fill="x", expand=True, padx=(2, 5))
        
        # Verwende das neue ModelInfoDropdown
        self.model_dropdown = ModelInfoDropdown(
            left_frame,
            models_dict={},
            on_select=self.on_model_select_new
        )
        self.model_dropdown.pack(fill="x", pady=2)
        
        # Rechte Seite: Model Info Panel
        self.model_info_panel = ctk.CTkFrame(
            model_controls_frame,
            fg_color=("#e8e8e8", "#2b2b2b"),
            corner_radius=8,
            width=250
        )
        self.model_info_panel.pack(side="right", fill="both", padx=(0, 5), pady=2)
        self.model_info_panel.pack_propagate(False)
        
        # Info Panel Titel
        info_title = ctk.CTkLabel(
            self.model_info_panel,
            text="ℹ️ Model-Info",
            font=("Arial", 10, "bold"),
            anchor="w"
        )
        info_title.pack(anchor="w", padx=10, pady=(8, 5))
        
        # Info Text
        self.model_info_text = ctk.CTkTextbox(
            self.model_info_panel,
            font=("Arial", 9),
            wrap="word",
            activate_scrollbars=False
        )
        self.model_info_text.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.model_info_text.insert("1.0", "Select a model\nto view details.")
        self.model_info_text.configure(state="disabled")
        
        # Mausrad-Scrolling für model_dropdown aktivieren
        
        # Buttons unter dem Info Panel
        buttons_frame = ctk.CTkFrame(installed_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=self.config.get("ui_padding_content", 5), pady=(5, 2))
        
        # Delete Button 
        self.delete_btn = ctk.CTkButton(
            buttons_frame,
            text="🗑️ Delete",
            command=self.delete_selected_model,
            fg_color="red",
            hover_color="darkred",
            width=100,
            font=("Arial", 12, "bold")
        )
        self.delete_btn.pack(side="right", padx=5, pady=2)
        
        # Refresh Button  
        self.refresh_btn = ctk.CTkButton(
            buttons_frame,
            text="🔄 Refresh",
            command=self.refresh_models,
            width=130,
            font=("Arial", 12, "bold")
        )
        self.refresh_btn.pack(side="right", padx=5, pady=2)
        
        # Available Models for Download
        download_frame = ctk.CTkFrame(model_frame)
        download_frame.pack(fill="x", padx=self.config.get("ui_padding_main", 10), 
                           pady=self.config.get("ui_padding_content", 5))
        
        self.available_label = ctk.CTkLabel(download_frame, text="⬇️ Download:",
                                          font=("Arial", self.config.get("ui_model_label_size", 9), "bold"))
        self.available_label.pack(anchor="w", padx=self.config.get("ui_padding_content", 5), pady=2)
        
        # Download Controls
        download_controls_frame = ctk.CTkFrame(download_frame)
        download_controls_frame.pack(fill="x", padx=self.config.get("ui_padding_content", 5), pady=2)
        
        # New ModelInfoDropdown for available models to download
        self.available_dropdown = ModelInfoDropdown(
            download_controls_frame,
            models_dict={},
            on_select=None  # Kein Auto-Download bei Auswahl
        )
        self.available_dropdown.pack(side="left", fill="x", expand=True, padx=(2, 5), pady=2)
        
        # Download Button (direkt nach Dropdown)
        self.download_btn = ctk.CTkButton(
            download_controls_frame,
            text="⬇️ Download",
            command=self.download_selected_model,
            width=120,
            font=("Arial", 12, "bold")
        )
        self.download_btn.pack(side="left", padx=5, pady=2)
        
        # Manueller Download Button  
        self.manual_download_btn = ctk.CTkButton(
            download_controls_frame,
            text="💾 Manual",
            command=self.show_download_dialog,
            width=110,
            font=("Arial", 12, "bold")
        )
        self.manual_download_btn.pack(side="right", padx=5, pady=2)
        
        # Ollama Models-Folder open Button
        self.models_folder_btn = ctk.CTkButton(
            download_controls_frame,
            text="📂 Folder",
            command=self.open_ollama_models_folder,
            width=100,
            font=("Arial", 12, "bold"),
            fg_color="#2D5A87",
            hover_color="#3D6A97"
        )
        self.models_folder_btn.pack(side="right", padx=5, pady=2)
        
        # Progress Bar für Downloads (initial versteckt)
        self.progress_frame = ctk.CTkFrame(model_frame)
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="Download running...",
                                         font=("Arial", self.config.get("ui_model_label_size", 9)))
        self.progress_label.pack(pady=2)
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(fill="x", padx=self.config.get("ui_padding_main", 10), pady=2)
        
        # ============================================
        # SESSION MANAGEMENT AREA (DARUNTER)
        # ============================================
        
    # (Session Panel Header removed)
        
        # Session List
        sessions_frame = ctk.CTkFrame(self.session_panel)
        sessions_frame.pack(fill="both", expand=True, 
                           padx=self.config.get("ui_padding_content", 5), 
                           pady=self.config.get("ui_padding_content", 5))
        
        # Header-Frame für Session List mit Button nebeneinander
        session_header_frame = ctk.CTkFrame(sessions_frame)
        session_header_frame.pack(fill="x", padx=self.config.get("ui_padding_main", 10), 
                                 pady=(self.config.get("ui_padding_main", 10), self.config.get("ui_padding_content", 5)))
        
        list_label = ctk.CTkLabel(session_header_frame, text="🗂️ Session List:", 
                                 font=("Arial", self.config.get("ui_model_title_size", 12), "bold"))
        list_label.pack(side="left", anchor="w", padx=(0, self.config.get("ui_padding_main", 10)))
        
        # New Session Button - jetzt neben der Session List
        new_session_btn = ctk.CTkButton(
            session_header_frame, 
            text="➕ New Session",
            command=self.create_new_session,
            width=self.config.get("ui_session_button_width", 140),
            height=self.config.get("ui_session_button_height", 25),
            font=("Arial", self.config.get("ui_session_button_font", 9), "bold"),
            fg_color="#2B8A3E",
            hover_color="#37A24B"
        )
        new_session_btn.pack(side="right", padx=(self.config.get("ui_padding_main", 10), 0))
        
        # Scrollbare Session-List - mehr Platz durch Entfernung des "Current Session" Bereichs
        self.session_listbox = ctk.CTkScrollableFrame(sessions_frame, 
                                                      height=self.config.get("ui_session_item_height", 60) * 2.5)
        self.session_listbox.pack(fill="both", expand=True, 
                                 padx=self.config.get("ui_padding_main", 10), 
                                 pady=self.config.get("ui_padding_content", 5))
        
        # Session Actions unter der Session-List
        actions_frame = ctk.CTkFrame(sessions_frame)
        actions_frame.pack(fill="x", padx=self.config.get("ui_padding_main", 10), 
                          pady=self.config.get("ui_padding_content", 5))
        
        delete_session_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️ Session delete",
            command=self.delete_current_session,
            height=35,
            font=("Arial", 12, "bold"),
            fg_color="#C92A2A",
            hover_color="#E03131"
        )
        delete_session_btn.pack(side="left", fill="x", expand=True, padx=(0, 2))
        
        cleanup_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️ Alle delete",
            command=self.delete_all_sessions,
            height=35,
            font=("Arial", 12, "bold"),
            fg_color="#8B0000",
            hover_color="#A52A2A"
        )
        cleanup_btn.pack(side="left", fill="x", expand=True, padx=(2, 0))
        
        # Debug-Buttons unter der Session-List
        debug_frame = ctk.CTkFrame(sessions_frame)
        debug_frame.pack(fill="x", padx=self.config.get("ui_padding_main", 10), 
                        pady=(self.config.get("ui_padding_content", 5), self.config.get("ui_padding_content", 5)))
        
        debug_btn = ctk.CTkButton(
            debug_frame,
            text="🔍 Debug Sessions",
            command=self.show_session_debug,
            height=35,
            font=("Arial", 12, "bold"),
            fg_color="#4A4A4A",
            hover_color="#5A5A5A"
        )
        debug_btn.pack(side="left", fill="x", expand=True, padx=(0, 2))
        
        folder_btn = ctk.CTkButton(
            debug_frame,
            text="📁 Sessions-Folder",
            command=self.open_sessions_folder,
            height=35,
            font=("Arial", 12, "bold"),
            fg_color="#2D5A87",
            hover_color="#3D6A97"
        )
        folder_btn.pack(side="left", fill="x", expand=True, padx=(2, 0))
        
        # BIAS Input Frame
        bias_frame = ctk.CTkFrame(self.session_panel, border_width=2, border_color="#4A4A4A")
        bias_frame.pack(fill="x", 
                       padx=self.config.get("ui_padding_content", 5), 
                       pady=self.config.get("ui_padding_content", 5))

        bias_label = ctk.CTkLabel(bias_frame, text="🎯 Session BIAS:", 
                                 font=("Arial", self.config.get("ui_session_font_size", 11), "bold"))
        bias_label.pack(anchor="w", padx=self.config.get("ui_padding_main", 10), 
                       pady=(self.config.get("ui_padding_main", 10), 2))

        self.session_bias_entry = ctk.CTkTextbox(
            bias_frame,
            height=self.config.get("ui_bias_height", 60),
            font=("Arial", self.config.get("ui_bias_font_size", 9))
        )
        self.session_bias_entry.pack(fill="x", padx=self.config.get("ui_padding_main", 10), pady=2)

        # Auto-save for BIAS on text change
        self.bias_auto_save_timer = None
        self.session_bias_entry.bind("<KeyRelease>", self.on_bias_text_changed)
        self.session_bias_entry.bind("<Button-1>", self.on_bias_text_changed)

        # BIAS info label for current status
        self.bias_info_label = ctk.CTkLabel(
            bias_frame,
            text="� BIAS not set (Auto-Save active)",
            font=("Arial", self.config.get("ui_model_label_size", 9)),
            text_color="gray"
        )
        self.bias_info_label.pack(anchor="w", padx=self.config.get("ui_padding_main", 10), 
                                 pady=(2, self.config.get("ui_padding_main", 10)))

    def initialize_session_management(self):
        """Initializes the session management system"""
        # Session data structures (already initialized in __init__)
        # self.sessions = {}  # Alle Sessions: {session_id: session_data}
        # self.current_session_id = None
        # self.current_session_bias = ""
        
        # Sessions-Folder (bereits im __init__ created)
        # self.sessions_dir = os.path.join(os.getcwd(), "sessions")
        # if not os.path.exists(self.sessions_dir):
        #     os.makedirs(self.sessions_dir)
            
        # Chat bubbles for session management
        self.chat_bubbles = []
        
        # Load existing sessions
        self.load_all_sessions()
        
        # Show session status
        if not self.sessions:
            self.console_print("📋 No existing sessions found", "info")
            self.console_print("💡 Click on '➕ New Session' to begin", "info")
        else:
            # Load the latest session automatically
            latest_session = max(self.sessions.keys(), key=lambda x: self.sessions[x].get("created_at", ""))
            self.load_session(latest_session)
            self.console_print(f"📂 Latest session automatically loaded: {latest_session[:12]}...", "success")
        
        # Debug: Session analysis
        self.debug_session_analysis()
        
        # Keine automatische Session-Erstellung - Nutzer muss explizit create
        # UI refresh um "No Session" show state
        self.update_session_list()
        self.update_current_session_display()

    def create_new_session(self):
        """Erstellt eine neue Session"""
        # Session-ID generieren (mit Millisekunden für Eindeutigkeit)
        timestamp = datetime.now()
        session_id = timestamp.strftime("%Y%m%d_%H%M%S") + f"_{timestamp.microsecond // 1000:03d}"
        
        # Check ob Session-ID bereits existiert (Sicherheitscheck)
        counter = 1
        original_session_id = session_id
        while session_id in self.sessions:
            session_id = f"{original_session_id}_{counter}"
            counter += 1
            self.console_print(f"⚠️ Session-ID Konflikt, verwende: {session_id}", "warning")
        
        # Aktuelles Model verwenden oder None setzen
        current_model = getattr(self, 'current_model', None)
        
        # Session-Daten
        session_name = f"Session {timestamp.strftime('%d.%m %H-%M')}"
        session_data = {
            "session_id": session_id,
            "name": session_name,  # Standard-Name
            "created_at": timestamp.isoformat(),
            "last_modified": timestamp.isoformat(),
            "model": current_model,
            "bias": "",
            "messages": [],
            "total_messages": 0,
            "color": "#1f538d"  # Standard-Farbe: Blue
        }
        
        # Session save
        self.sessions[session_id] = session_data
        self.current_session_id = session_id
        
        # Chat leeren
        self.clear_chat_for_new_session()
        
        # BIAS für neue Session zurücksetzen
        self.current_session_bias = ""
        if hasattr(self, 'session_bias_entry'):
            self.session_bias_entry.delete("1.0", "end")
        # BIAS-Info-Label refresh
        self.update_bias_info_label()
        
        # UI refresh
        self.update_session_list()
        self.update_current_session_display()
        
        # Stelle sicher, dass Modelle loaded sind
        if hasattr(self, 'model_dropdown'):
            # Wenn das Dropdown leer ist, lade Modelle new
            if not self.model_dropdown.models_dict:
                self.console_print("🔄 Loading models for new session...", "info")
                self.refresh_models()
        
        # Session persistent save mit Feedback
        self.save_session_with_feedback()
        
        # Force update der UI nach kurzer Verzögerung
        self.root.after(100, self.update_session_list)

        self.console_print(f"✅ New Session created: {session_id}", "success")


    def debug_session_analysis(self):
        """Debug function for analyzing session problems"""
        if not self.sessions:
            return
            
        self.console_print(f"🔍 Session analysis: {len(self.sessions)} sessions found", "info")
        
        # Prüfe auf ähnliche Sessions (gleiche Erstellungszeiten)
        session_times = {}
        for session_id, session_data in self.sessions.items():
            created_at = session_data.get("created_at", "")
            if created_at:
                try:
                    date_obj = datetime.fromisoformat(created_at)
                    time_key = date_obj.strftime("%Y%m%d_%H%M%S")  # Nur Sekunden-Genauigkeit
                    
                    if time_key not in session_times:
                        session_times[time_key] = []
                    session_times[time_key].append(session_id)
                except:
                    pass
        
        # Warn about possible duplicates
        for time_key, session_ids in session_times.items():
            if len(session_ids) > 1:
                self.console_print(f"⚠️ Possible duplicates found at time {time_key}:", "warning")
                for sid in session_ids:
                    session_data = self.sessions[sid]
                    msg_count = session_data.get("total_messages", 0)
                    model = session_data.get("model", "No model")
                    self.console_print(f"   🆔 {sid[-12:]} | 💬 {msg_count} Msg | 🤖 {model}", "info")

    def show_session_debug(self):
        """Zeigt detaillierte Session-Debug-Informationen"""
        debug_text = "🔍 SESSION DEBUG INFORMATION\n" + "="*50 + "\n\n"
        
        if not self.sessions:
            debug_text += "❌ Keine Sessions vorhanden\n"
        else:
            debug_text += f"📊 Anzahl Sessions: {len(self.sessions)}\n"
            debug_text += f"🔄 Current Session: {self.current_session_id}\n\n"
            
            # Session-Details
            for i, (session_id, session_data) in enumerate(sorted(self.sessions.items(), 
                                                                 key=lambda x: x[1].get("created_at", ""), 
                                                                 reverse=True), 1):
                debug_text += f"SESSION #{i}:\n"
                debug_text += f"   🆔 ID: {session_id}\n"
                debug_text += f"   📅 Erstellt: {session_data.get('created_at', 'Unbekannt')}\n"
                debug_text += f"   ⏰ Geändert: {session_data.get('last_modified', 'Unbekannt')}\n"
                debug_text += f"   🤖 Model: {session_data.get('model', 'Nicht gesetzt')}\n"
                debug_text += f"   💬 Messages: {session_data.get('total_messages', 0)}\n"
                debug_text += f"   📝 BIAS: {'Ja' if session_data.get('bias', '') else 'Nein'}\n"
                
                # Check for session file (any name, but with matching ID)
                matching_files = [f for f in os.listdir(self.sessions_dir) if f.endswith(f"_session_{session_id}.json")]
                file_exists = len(matching_files) > 0
                debug_text += f"   💾 File: {'✅ Present' if file_exists else '❌ Missing'}\n"
                if file_exists:
                    try:
                        stat = os.stat(os.path.join(self.sessions_dir, matching_files[0]))
                        debug_text += f"   📏 File Size: {stat.st_size} Bytes\n"
                    except:
                        debug_text += f"   📏 File Size: Unreadable\n"
                
                debug_text += "\n"
        
        # Zeige Debug-Info in einem Dialog
        debug_dialog = ctk.CTkToplevel(self.root)
        debug_dialog.title("🔍 Session Debug Information")
        debug_dialog.geometry("600x500")
        debug_dialog.transient(self.root)
        debug_dialog.grab_set()
        
        # Text-Widget für Debug-Output
        debug_textbox = ctk.CTkTextbox(
            debug_dialog,
            font=("Consolas", 10),
            wrap="word"
        )
        debug_textbox.pack(fill="both", expand=True, padx=10, pady=10)
        debug_textbox.insert("1.0", debug_text)
        debug_textbox.configure(state="disabled")
        
        # Close-Button
        close_btn = ctk.CTkButton(
            debug_dialog,
            text="Close",
            command=debug_dialog.destroy,
            width=100
        )
        close_btn.pack(pady=10)

    def open_sessions_folder(self):
        """Öffnet das Sessions-Directory im Windows Explorer"""
        try:
            import subprocess
            import os
            
            # Verwende das gleiche Directory wie self.sessions_dir
            sessions_dir = self.sessions_dir
            
            if not os.path.exists(sessions_dir):
                # Erstelle das Directory falls es nicht existiert
                os.makedirs(sessions_dir, exist_ok=True)
                self.console_print(f"📁 Sessions directory created: {sessions_dir}", "success")
            
            # Open Explorer with sessions directory
            subprocess.Popen(f'explorer "{sessions_dir}"', shell=True)
            self.console_print(f"📂 Sessions folder opened: {sessions_dir}", "success")
            
        except Exception as e:
            self.console_print(f"❌ Error opening sessions folder: {e}", "error")

    def open_ollama_models_folder(self):
        """Öffnet das Ollama Models-Directory im Explorer/Finder"""
        try:
            import subprocess
            import os
            import sys
            from tkinter import messagebox
            
            # Bestimme den Ollama Models-Pfad basierend auf dem Betriebssystem
            if sys.platform == 'win32':
                ollama_dir = os.path.join(os.path.expanduser('~'), '.ollama', 'models')
            elif sys.platform == 'darwin':  # macOS
                ollama_dir = os.path.join(os.path.expanduser('~'), '.ollama', 'models')
            else:  # Linux
                ollama_dir = os.path.join(os.path.expanduser('~'), '.ollama', 'models')
            
            # Prüfe ob Directory existiert
            if not os.path.exists(ollama_dir):
                # Fallback: Versuche alternative Pfade
                alt_paths = [
                    os.path.join(os.getenv('APPDATA', ''), 'ollama', 'models'),
                    os.path.join(os.getenv('LOCALAPPDATA', ''), 'ollama', 'models'),
                    "C:\\Program Files\\Ollama\\models",
                ]
                
                for alt_path in alt_paths:
                    if os.path.exists(alt_path):
                        ollama_dir = alt_path
                        break
                else:
                    messagebox.showwarning(
                        "Folder nicht gefunden",
                        f"❌ Ollama Models-Folder nicht gefunden!\n\n"
                        f"Erwarteter Pfad:\n{ollama_dir}\n\n"
                        f"Mögliche Greende:\n"
                        f"• Ollama ist nicht installed\n"
                        f"• Noch keine Modelle heruntergeladen\n"
                        f"• Ollama verwendet einen benutzerdefinierten Pfad\n\n"
                        f"💡 Tipp: Load You zuerst ein Model herunter."
                    )
                    return
            
            # Öffne Explorer/Finder mit dem Models-Directory
            if sys.platform == 'win32':
                subprocess.Popen(f'explorer "{ollama_dir}"', shell=True)
            elif sys.platform == 'darwin':
                subprocess.Popen(['open', ollama_dir])
            else:
                subprocess.Popen(['xdg-open', ollama_dir])
            
            self.console_print(f"🤖 Ollama models folder opened: {ollama_dir}", "success")
            
        except Exception as e:
            self.console_print(f"❌ Error opening Ollama models folder: {e}", "error")

    def clear_chat_history(self):
        """Löscht die Chat-Historie für einen frischen Kontext mit dem Model"""
        result = messagebox.askyesno(
            "Chat-Historie delete",
            "⚠️ Chat-Historie delete?\n\n"
            f"Dies löscht den Kontext für das AI-Model.\n"
            f"Die Messages bleiben in der Session sichtbar,\n"
            f"aber das Model vergisst den bisherigen Verlauf.\n\n"
            f"Möchten You fortfahren?"
        )
        
        if result:
            old_count = len(self.chat_history)
            self.chat_history = []
            
            self.console_print(f"🗑️ Chat-Historie deleted: {old_count} Messages entfernt", "success")
            self.add_to_chat("System", "🗑️ Chat-Historie für AI-Model deleted - Frischer Kontext ab sofort")

    def load_session(self, session_id):
        """Lädt eine bestehende Session"""
        if session_id not in self.sessions:
            return False
        
        # If the session is already loaded, do nothing
        if self.current_session_id == session_id:
            self.console_print(f"ℹ️ Session already active: {session_id}", "info")
            return True
        
        # IMPORTANT: Set flag to prevent saving during load process
        self._session_just_loaded = True
        
        self.console_print(f"🔄 Switching to session: {session_id}", "info")
        
        # WICHTIG: Session-ID SOFORT wechseln BEVOR irgendwas anderes passiert!
        # Das verhindert, dass auto_save die alte Session mit neuen (leeren) Daten überschreibt
        old_session_id = self.current_session_id
        
        # Alte Session save BEVOR Chat geleert is being und BEVOR Session-ID gewechselt is being
        # Die Messages müssen noch in chat_bubbles sein für das Save
        # WICHTIG: Prüfe ob die alte Session noch existiert (könnte deleted worden sein)
        if old_session_id and old_session_id != session_id and old_session_id in self.sessions:
            # Save während chat_bubbles noch existieren und current_session_id noch die alte ist
            if self.save_current_session():
                self.console_print(f"💾 Alte Session saved: {old_session_id}", "success")
            else:
                self.console_print(f"⚠️ Warnung: Konnte alte Session nicht save", "warning")
        elif old_session_id and old_session_id != session_id and old_session_id not in self.sessions:
            # Alte Session wurde bereits deleted - keine Warnung nötig
            self.console_print(f"ℹ️ Alte Session {old_session_id} wurde bereits deleted", "info")
        
        # JETZT Session ID wechseln - KRITISCH: Muss VOR clear_chat passieren!
        self.current_session_id = session_id
        
        # Session-Daten aus der File load
        session_name = self.sessions[session_id].get("name", "")
        safe_name = "_".join(session_name.split()).replace("/", "_").replace("\\", "_")
        session_file = os.path.join(self.sessions_dir, f"{safe_name}_session_{session_id}.json")
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
                # Aktualisiere auch das in-memory Dictionary
                self.sessions[session_id] = session_data
        except Exception as e:
            self.console_print(f"⚠️ Error beim Load der Session-File: {e}", "warning")
            # Fallback auf in-memory Daten
            session_data = self.sessions[session_id]
        
        # JETZT ERST Chat-Anzeige leeren (NACH Session-ID Wechsel!)
        # Dadurch is being auto_save, falls es aufgerufen is being, die RICHTIGE (neue) Session save
        self.clear_chat_for_new_session()
        
        # Kleine Verzögerung für vollständiges Clearing
        self.root.update()
        
        # Chat-Historie für LLM zurücksetzen und new aufbauen
        self.chat_history = []
        
        # Model setzen wenn vorhanden
        if session_data.get("model"):
            self.current_model = session_data["model"]
            if hasattr(self, 'model_dropdown'):
                # Versuche das Model direkt zu setzen
                self.model_dropdown.set_selected(self.current_model)
                # Update model info panel
                self.root.after(100, lambda: self.update_model_info_panel(self.current_model))
                
                # Falls das Model noch nicht in models_dict ist (z.B. Modelle noch nicht loaded),
                # versuche es nach kurzer Verzögerung erneut
                def retry_set_model():
                    if self.current_model and hasattr(self, 'model_dropdown'):
                        # Prüfe ob Model jetzt in der List ist
                        if self.current_model in self.model_dropdown.models_dict:
                            self.model_dropdown.set_selected(self.current_model)
                            # Update model info panel after retry
                            self.update_model_info_panel(self.current_model)
                        else:
                            # Wenn nicht, aktualisiere die Modelle und versuche es nochmal
                            self.refresh_models()
                            self.root.after(500, lambda: self.model_dropdown.set_selected(self.current_model))
                            self.root.after(600, lambda: self.update_model_info_panel(self.current_model))
                
                # Retry nach 200ms
                self.root.after(200, retry_set_model)
        
        # BIAS setzen - WICHTIG: VOR dem Load der Messages
        self.current_session_bias = session_data.get("bias", "")
        if hasattr(self, 'session_bias_entry'):
            # Temporär Event-Handler deaktivieren um unnötige Saves zu vermeiden
            self.session_bias_entry.unbind("<KeyRelease>")
            self.session_bias_entry.unbind("<Button-1>")
            
            # BIAS-Text setzen
            self.session_bias_entry.delete("1.0", "end")
            if self.current_session_bias:
                self.session_bias_entry.insert("1.0", self.current_session_bias)
            
            # Event-Handler wieder aktivieren
            self.session_bias_entry.bind("<KeyRelease>", self.on_bias_text_changed)
            self.session_bias_entry.bind("<Button-1>", self.on_bias_text_changed)
        
        # BIAS-Info-Label refresh
        self.update_bias_info_label()
        
        # Messages load und Chat-Historie für LLM aufbauen
        message_count = 0
        for msg_data in session_data.get("messages", []):
            # Visuelle Message wiederherstellen
            self.restore_chat_message(msg_data)
            message_count += 1
            
            # Chat-Historie für LLM aufbauen (nur User und AI-Messages, keine System-Messages)
            sender = msg_data.get("sender", "")
            message = msg_data.get("message", "")
            
            if sender == "You":
                self.chat_history.append({"role": "user", "content": message})
            elif sender.startswith("🤖") and not sender.startswith("System"):
                # AI-Antwort hinzufügen
                self.chat_history.append({"role": "assistant", "content": message})
        
        # Layout nach dem Load aller Messages vollständig refresh
        if message_count > 0:
            # Mehrfaches Update für zuverlässiges Rendering
            self.chat_display_frame.update()
            self.chat_display_frame.update_idletasks()
            
            # Parent Canvas Update
            if hasattr(self.chat_display_frame, '_parent_canvas'):
                self.chat_display_frame._parent_canvas.update()
                self.chat_display_frame._parent_canvas.update_idletasks()
                
                # Scrollregion nur EINMAL refresh - keine unnötigen mehrfachen Updates
                self.root.after(300, lambda: self._update_scroll_region())
        else:
            # Auch für leere Sessions das Layout refresh
            if hasattr(self, 'chat_display_frame'):
                self.chat_display_frame.update()
                self.chat_display_frame.update_idletasks()
        
        # Debug info about restored chat history
        if self.chat_history:
            self.console_print(f"💬 Chat history restored: {len(self.chat_history)} messages for LLM context", "success")
        
        self.console_print(f"✅ Session loaded: {session_id} with {message_count} visible messages", "success")
        
        # UI refresh
        self.update_current_session_display()
        self.update_session_list()  # Session-List auch refresh
        
        # Zur letzten Message scrollen - nur EINMAL mit Verzögerung
        if message_count > 0:
            self.root.after(300, self.scroll_to_last_message)
        
        # WICHTIG: Flag zurücksetzen NACH allen Operationen die save könnten
        self._session_just_loaded = False
        
        return True
    
    def _update_scroll_region(self):
        """Hilfsmethode zum Refresh der Scroll-Region"""
        if hasattr(self, 'chat_display_frame') and hasattr(self.chat_display_frame, '_parent_canvas'):
            try:
                self.chat_display_frame._parent_canvas.configure(
                    scrollregion=self.chat_display_frame._parent_canvas.bbox("all")
                )
            except:
                pass

    def save_current_session(self):
        """Speichert die aktuelle Session"""
        if not self.current_session_id:
            return False
        
        # Check if session still exists (could have been deleted)
        if self.current_session_id not in self.sessions:
            self.console_print(f"⚠️ Session {self.current_session_id} no longer exists - save skipped", "warning")
            return False
            
        session_data = self.sessions[self.current_session_id]
        
        # Aktuelle Daten sammeln
        session_data["last_modified"] = datetime.now().isoformat()
        session_data["model"] = getattr(self, 'current_model', None)
        session_data["bias"] = self.current_session_bias
        session_data["total_messages"] = self.count_chat_messages()
        
        # Chat-Messages sammeln
        messages = []
        for bubble in self.chat_bubbles:
            msg_data = {
                "timestamp": bubble.timestamp,
                "sender": bubble.sender,
                "message": bubble.message
            }
            messages.append(msg_data)
        
        session_data["messages"] = messages
        
        # Session-File save: Name am Anfang, dann _session_<SessionID>.json
        session_name = self.sessions[self.current_session_id].get("name", "")
        safe_name = "_".join(session_name.split()).replace("/", "_").replace("\\", "_")
        session_file = os.path.join(self.sessions_dir, f"{safe_name}_session_{self.current_session_id}.json")

        # Lösche ggf. alte Dateien mit anderer Benennung für diese Session-ID
        for fname in os.listdir(self.sessions_dir):
            if fname.endswith(f"_session_{self.current_session_id}.json") and fname != f"{safe_name}_session_{self.current_session_id}.json":
                try:
                    os.remove(os.path.join(self.sessions_dir, fname))
                except Exception:
                    pass

        try:
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            self.console_print(f"❌ Error beim Save der Session: {e}", "error")
            return False

    def auto_save_session(self):
        """Automatisches Save mit Debounce-Logik"""
        # Lösche vorherigen Timer falls vorhanden
        if self.auto_save_timer:
            self.root.after_cancel(self.auto_save_timer)
        
        # Starte neuen Timer für verzögertes Save (200ms)
        self.auto_save_timer = self.root.after(200, self.perform_auto_save)
    
    def perform_auto_save(self):
        """Führt das tatsächliche automatische Save durch"""
        try:
            if self.save_current_session():
                # Nur in Debug-Modus show, um Konsole nicht zu überlasten
                # self.console_print(f"💾 Auto-Save: Session saved", "info")
                pass
        except Exception as e:
            self.console_print(f"❌ Auto-Save Error: {e}", "error")
        finally:
            self.auto_save_timer = None

    def save_session_with_feedback(self):
        """Manuelles Save mit Konsolen-Feedback"""
        if self.save_current_session():
            self.console_print(f"💾 Session manual saved: {self.current_session_id}", "success")
            return True
        return False

    def load_all_sessions(self):
        """Lädt alle Sessions aus dem Sessions-Folder"""
        try:
            session_files = [f for f in os.listdir(self.sessions_dir)
                             if f.endswith(".json")]
            
            for session_file in session_files:
                session_path = os.path.join(self.sessions_dir, session_file)
                try:
                    with open(session_path, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                        session_id = session_data.get("session_id")
                        if session_id:
                            # Füge Standard-Namen hinzu wenn nicht vorhanden (Migration bestehender Sessions)
                            if "name" not in session_data:
                                created_date = session_data.get("created_at", "")
                                if created_date:
                                    try:
                                        date_obj = datetime.fromisoformat(created_date)
                                        session_data["name"] = f"Session {date_obj.strftime('%d.%m %H-%M')}"
                                    except:
                                        session_data["name"] = f"Session {session_id[-8:]}"
                                else:
                                    session_data["name"] = f"Session {session_id[-8:]}"
                            # Füge Standard-Farbe hinzu wenn nicht vorhanden (Migration bestehender Sessions) 
                            if "color" not in session_data:
                                session_data["color"] = "#1f538d"  # Standard-Blue
                            self.sessions[session_id] = session_data
                except Exception as e:
                    self.console_print(f"❌ Error beim Load der Session {session_file}: {e}", "warning")
            
            self.update_session_list()
            self.console_print(f"📂 {len(self.sessions)} Sessions loaded", "info")
            
        except Exception as e:
            self.console_print(f"❌ Error beim Load der Sessions: {e}", "error")

    def calculate_session_word_count(self, session_data):
        """Berechnet die Gesamtanzahl der Wörter in einer Session"""
        total_words = 0
        messages = session_data.get("messages", [])
        
        for message in messages:
            content = message.get("message", "")
            if isinstance(content, str) and content.strip():
                # Einfache aber robuste Wort-Zählung
                # Teile bei Whitespace und filtere leere Strings
                words = [word for word in content.split() if word.strip()]
                total_words += len(words)
        
        # BIAS auch mitzählen falls vorhanden
        bias = session_data.get("bias", "")
        if bias and bias.strip():
            bias_words = [word for word in bias.split() if word.strip()]
            total_words += len(bias_words)
        
        return total_words

    def update_session_list(self):
        """Aktualisiert die Session-List in der UI"""
        if not hasattr(self, 'session_listbox'):
            return
            
        # Lösche alte Einträge
        for widget in self.session_listbox.winfo_children():
            widget.destroy()
        
        # Sortiere Sessions nach Erstellungsdatum (neueste zuerst)
        sorted_sessions = sorted(self.sessions.items(), 
                               key=lambda x: x[1].get("created_at", ""), 
                               reverse=True)
        
        for session_id, session_data in sorted_sessions:
            # Session-Info
            session_name = session_data.get("name", f"Session {session_id[-8:]}")
            created_date = session_data.get("created_at", "Unbekannt")
            if created_date != "Unbekannt":
                try:
                    date_obj = datetime.fromisoformat(created_date)
                    date_str = date_obj.strftime("%d.%m.%Y %H:%M")  # Ohne Sekunden für mehr Platz
                except:
                    date_str = created_date[:16] if len(created_date) > 16 else created_date
            else:
                date_str = created_date

            msg_count = session_data.get("total_messages", 0)
            model_name = session_data.get("model", "Kein Model")
            model_name = model_name[:12] if model_name else "Kein Model"

            # Token/Wort-Anzahl für diese Session berechnen
            word_count = self.calculate_session_word_count(session_data)
            word_display = f"{word_count}W" if word_count < 1000 else f"{word_count//1000:.1f}kW"

            # Aktive Session hervorheben: Keine gelbe Farbe, nur Session-Farbe verwenden
            is_active = session_id == self.current_session_id

            # Session-Container für Name und Buttons
            session_container = ctk.CTkFrame(self.session_listbox)
            session_container.pack(fill="x", pady=2)

            # Session-Button mit Namen - kompakter für schmale Fenster
            if len(session_name) > 20:
                session_name_display = session_name[:17] + "..."
            else:
                session_name_display = session_name

            button_text = f"📝 {session_name_display}\n📅 {date_str}\n💬 {msg_count} | 🤖 {model_name[:8]} | 📊 {word_display}"

            # Session-Farbe verwenden
            session_color = session_data.get("color", "#4A4A4A")
            btn_fg_color = session_color
            btn_hover_color = self.adjust_color_brightness(btn_fg_color, 1.2)

            session_btn = ctk.CTkButton(
                session_container,
                text=button_text,
                command=lambda sid=session_id: self.load_session(sid),
                height=75,  # Etwas höher für mehr Text
                font=("Arial", 9),
                anchor="w",
                fg_color=btn_fg_color,
                hover_color=btn_hover_color,
                text_color="#000000"  # Schrift schwarz
            )
            session_btn.pack(side="left", fill="both", expand=True, padx=(0, 5))
            
            # Quadratischer Zahnrad-Button für Session-Einstellungen (Umbenennen + Farbe)
            settings_btn = ctk.CTkButton(
                session_container,
                text="⚙️",
                command=lambda sid=session_id: self.show_session_settings(sid),
                width=75,
                height=75,
                font=("Arial", 18),
                fg_color="#4A4A4A",
                hover_color="#5A5A5A"
            )
            settings_btn.pack(side="right")
    
    def rename_session(self, session_id):
        """Zeigt einen Dialog zum Umbenennen einer Session"""
        if session_id not in self.sessions:
            return
            
        session_data = self.sessions[session_id]
        current_name = session_data.get("name", f"Session {session_id[-8:]}")
        
        # Dialog-Fenster create
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Rename session")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Dialog zentrieren
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"400x200+{x}+{y}")
        
        # Dialog content
        title_label = ctk.CTkLabel(dialog, text="Rename session", 
                                  font=("Arial", 16, "bold"))
        title_label.pack(pady=(20, 10))
        
        info_label = ctk.CTkLabel(dialog, text=f"Session ID: {session_id[-8:]}",
                                 font=("Arial", 10))
        info_label.pack(pady=5)
        
        # Name input
        name_label = ctk.CTkLabel(dialog, text="New name:", 
                                 font=("Arial", 12, "bold"))
        name_label.pack(pady=(10, 5))
        
        name_entry = ctk.CTkEntry(dialog, width=300, font=("Arial", 11))
        name_entry.pack(pady=5)
        name_entry.insert(0, current_name)
        name_entry.select_range(0, 'end')  # Text markieren
        name_entry.focus()  # Fokus setzen
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog)
        button_frame.pack(pady=20)
        
        def save_name():
            new_name = name_entry.get().strip()
            if new_name and new_name != current_name:
                # Name in Session-Daten refresh
                self.sessions[session_id]["name"] = new_name
                self.sessions[session_id]["last_modified"] = datetime.now().isoformat()
                # Find old file
                old_files = [f for f in os.listdir(self.sessions_dir) if f.endswith(f"_session_{session_id}.json")]
                old_path = os.path.join(self.sessions_dir, old_files[0]) if old_files else None
                # Save to new file with new name (name at beginning)
                safe_name = "_".join(new_name.split()).replace("/", "_").replace("\\", "_")
                new_path = os.path.join(self.sessions_dir, f"{safe_name}_session_{session_id}.json")
                try:
                    # Save updated session data to new file
                    with open(new_path, 'w', encoding='utf-8') as f:
                        json.dump(self.sessions[session_id], f, ensure_ascii=False, indent=2)
                    # Delete old file if it exists and is not the same as new file
                    if old_path and os.path.abspath(old_path) != os.path.abspath(new_path):
                        os.remove(old_path)
                except Exception as e:
                    self.console_print(f"❌ Error beim Umbenennen/Save der Session-File: {e}", "warning")
                # UI refresh
                self.update_session_list()
                self.update_current_session_display()
                self.console_print(f"✅ Session renamed: '{new_name}'", "success")
                dialog.destroy()
            elif not new_name:
                # Error message for empty name
                error_label = ctk.CTkLabel(dialog, text="⚠️ Name must not be empty!", 
                                         text_color="red", font=("Arial", 10, "bold"))
                error_label.pack(pady=5)
                dialog.after(2000, error_label.destroy)  # Remove after 2 seconds
            else:
                dialog.destroy()  # No change
        
        def cancel():
            dialog.destroy()
        
        # Enter-Taste für Save binden
        dialog.bind('<Return>', lambda e: save_name())
        dialog.bind('<Escape>', lambda e: cancel())
        
        save_btn = ctk.CTkButton(button_frame, text="💾 Save", 
                                command=save_name, fg_color="#2B8A3E", 
                                hover_color="#37A24B")
        save_btn.pack(side="left", padx=5)
        
        cancel_btn = ctk.CTkButton(button_frame, text="❌ Cancel", 
                                  command=cancel, fg_color="#C92A2A", 
                                  hover_color="#E03131")
        cancel_btn.pack(side="left", padx=5)
    
    def choose_session_color(self, session_id):
        """Zeigt einen Dialog zur Farbauswahl für eine Session"""
        if session_id not in self.sessions:
            return
            
        session_data = self.sessions[session_id]
        session_name = session_data.get("name", f"Session {session_id[-8:]}")
        current_color = session_data.get("color", "#4A4A4A")
        
        # Color-Picker Dialog
        color_dialog = ctk.CTkToplevel(self.root)
        color_dialog.title(f"Farbe select: {session_name}")
        color_dialog.geometry("700x600")  # Größer gemacht
        color_dialog.transient(self.root)
        color_dialog.grab_set()
        color_dialog.resizable(False, False)  # Feste Größe
        
        # Dialog zentrieren
        color_dialog.update_idletasks()
        x = (color_dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (color_dialog.winfo_screenheight() // 2) - (600 // 2)
        color_dialog.geometry(f"700x600+{x}+{y}")
        
        # Dialog content directly on dialog (without additional frames)
        title_label = ctk.CTkLabel(color_dialog, text=f"Color for '{session_name}' select", 
                                  font=("Arial", 16, "bold"))
        title_label.pack(pady=(20, 5))
        
        info_label = ctk.CTkLabel(color_dialog, text=f"Session ID: {session_id[-8:]}",
                                 font=("Arial", 10))
        info_label.pack(pady=(0, 15))
        
        # Current color variable
        selected_color = tk.StringVar(value=current_color)
        
        # Horizontal layout for color wheel and options
        content_frame = tk.Frame(color_dialog, bg='#212121')  # Standard Frame instead of CTkFrame
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Left side: Color wheel
        wheel_frame = tk.Frame(content_frame, bg='#212121')  # Standard Frame
        wheel_frame.pack(side="left", padx=(0, 20))
        
        wheel_label = ctk.CTkLabel(wheel_frame, text="🎨 Color Wheel", font=("Arial", 14, "bold"))
        wheel_label.pack(pady=(20, 10))
        
        # Color wheel widget
        color_wheel = ColorWheel(wheel_frame, size=220, initial_color=current_color)  # Larger
        color_wheel.pack(pady=10)
        
        # Right side: Preview and predefined colors
        options_frame = tk.Frame(content_frame, bg='#212121')  # Standard Frame
        options_frame.pack(side="right", fill="both", expand=True)
        
        # Color preview
        preview_label = ctk.CTkLabel(options_frame, text="Preview:", font=("Arial", 14, "bold"))
        preview_label.pack(pady=(20, 10))
        
        # Preview button (shows currently selected color)
        def update_preview():
            color = selected_color.get()
            preview_btn.configure(fg_color=color)
            hex_label.configure(text=f"Hex: {color}")
            
        preview_btn = ctk.CTkButton(
            options_frame,
            text=f"📝 {session_name}",
            fg_color=current_color,
            width=200,
            height=60,  # Higher for better visibility
            font=("Arial", 14, "bold"),
            state="disabled"  # Display only
        )
        preview_btn.pack(pady=(10, 10))
        
        # Hex value display
        hex_label = ctk.CTkLabel(options_frame, text=f"Hex: {current_color}", 
                                font=("Arial", 12))
        hex_label.pack(pady=(0, 20))
        
        # Callback for color wheel
        def on_wheel_color_change(color):
            selected_color.set(color)
            update_preview()
            
        color_wheel.set_color_callback(on_wheel_color_change)
        
        # Color selection - Predefined colors (larger and clearer)
        colors_label = ctk.CTkLabel(options_frame, text="Predefined colors:", font=("Arial", 13, "bold"))
        colors_label.pack(pady=(10, 15))
        
        # Popular colors for sessions
        predefined_colors = [
            ("#1f538d", "Blue"),
            ("#2B8A3E", "Green"),
            ("#C92A2A", "Red"), 
            ("#E67700", "Orange"),
            ("#6741D9", "Purple"),
            ("#C2185B", "Pink"),
            ("#00695C", "Turquoise"),
            ("#4A4A4A", "Gray")
        ]
        
        # Größeres Raster für Farbbuttons (2x4)
        color_grid = tk.Frame(options_frame, bg='#212121')
        color_grid.pack(pady=(0, 30))
        
        def select_color(color):
            selected_color.set(color)
            color_wheel.selected_color = color
            color_wheel.set_initial_position()
            update_preview()
        
        def make_color_button_command(color_value):
            """Erstellt eine sichere Command-Funktion für jeden Button"""
            def command():
                select_color(color_value)
            return command
            
        # 2x4 Raster für Farben - größere Buttons
        for i, (color, name) in enumerate(predefined_colors):
            row = i // 4
            col = i % 4
            
            color_btn = ctk.CTkButton(
                color_grid,
                text=name,  # Text show für bessere Übersicht
                command=make_color_button_command(color),
                fg_color=color,
                hover_color=color,
                width=80,  # Größere Buttons
                height=40,
                corner_radius=8,
                font=("Arial", 10, "bold"),
                text_color="white" if color in ["#4A4A4A", "#1A1A1A", "#7C2D12"] else "black"
            )
            color_btn.grid(row=row, column=col, padx=5, pady=5)
        
        # Buttons am Ende - größer und deutlich sichtbar
        button_frame = tk.Frame(color_dialog, bg='#212121')  # Standard Frame statt CTkFrame
        button_frame.pack(side="bottom", pady=30)  # Am unteren Rand mit viel Platz
        
        def save_color():
            new_color = selected_color.get()
            if new_color and new_color != current_color:
                # Farbe in Session-Daten refresh
                self.sessions[session_id]["color"] = new_color
                self.sessions[session_id]["last_modified"] = datetime.now().isoformat()
                # Session save
                self.save_session_with_feedback()
                # UI refresh
                self.update_session_list()
                # Wenn die aktuelle Session changed wurde, Anzeige sofort refresh
                if hasattr(self, 'current_session_id') and self.current_session_id == session_id:
                    self.update_current_session_display()
                self.console_print(f"🎨 Session-Farbe changed: {new_color}", "success")
            color_dialog.destroy()
        
        def cancel_color():
            color_dialog.destroy()
        
        # Enter/Escape Bindings
        color_dialog.bind('<Return>', lambda e: save_color())
        color_dialog.bind('<Escape>', lambda e: cancel_color())
        
        save_btn = ctk.CTkButton(button_frame, text="💾 Save", 
                                command=save_color, fg_color="#2B8A3E", 
                                hover_color="#37A24B",
                                width=120, height=45,  # Größer
                                font=("Arial", 14, "bold"))
        save_btn.pack(side="left", padx=20, pady=10)
        
        cancel_btn = ctk.CTkButton(button_frame, text="❌ Cancel", 
                                  command=cancel_color, fg_color="#C92A2A", 
                                  hover_color="#E03131",
                                  width=120, height=45,  # Größer
                                  font=("Arial", 14, "bold"))
        cancel_btn.pack(side="left", padx=20, pady=10)
        
        # Initiale Vorschau refresh
        update_preview()
    
    def show_session_settings(self, session_id):
        """Zeigt einen kombinierten Dialog für Session-Einstellungen (Name + Farbe)"""
        if session_id not in self.sessions:
            return
            
        session_data = self.sessions[session_id]
        current_name = session_data.get("name", f"Session {session_id[-8:]}")
        current_color = session_data.get("color", "#1f538d")
        
        # Dialog-Fenster create
        settings_dialog = ctk.CTkToplevel(self.root)
        settings_dialog.title("Session-Einstellungen")
        settings_dialog.geometry("750x700")
        settings_dialog.transient(self.root)
        settings_dialog.grab_set()
        settings_dialog.resizable(False, False)
        
        # Dialog zentrieren
        settings_dialog.update_idletasks()
        x = (settings_dialog.winfo_screenwidth() // 2) - (750 // 2)
        y = (settings_dialog.winfo_screenheight() // 2) - (700 // 2)
        settings_dialog.geometry(f"750x700+{x}+{y}")
        
        # Title
        title_label = ctk.CTkLabel(settings_dialog, text=f"⚙️ Settings: {current_name}", 
                                  font=("Arial", 18, "bold"))
        title_label.pack(pady=(20, 10))
        
        info_label = ctk.CTkLabel(settings_dialog, text=f"Session ID: {session_id[-8:]}",
                                 font=("Arial", 10))
        info_label.pack(pady=(0, 20))
        
        # === NAME SECTION ===
        name_section = ctk.CTkFrame(settings_dialog)
        name_section.pack(fill="x", padx=30, pady=(0, 20))
        
        name_title = ctk.CTkLabel(name_section, text="✏️ Session Name", 
                                 font=("Arial", 14, "bold"))
        name_title.pack(anchor="w", padx=15, pady=(15, 5))
        
        name_entry = ctk.CTkEntry(name_section, width=650, height=40, font=("Arial", 12))
        name_entry.pack(padx=15, pady=(0, 15))
        name_entry.insert(0, current_name)
        name_entry.select_range(0, 'end')
        name_entry.focus()
        
        # === COLOR SECTION ===
        color_section = ctk.CTkFrame(settings_dialog)
        color_section.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        color_title = ctk.CTkLabel(color_section, text="🎨 Session Color", 
                                  font=("Arial", 14, "bold"))
        color_title.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Selected color variable
        selected_color = tk.StringVar(value=current_color)
        
        # Content frame für Farbkreis und Optionen
        content_frame = tk.Frame(color_section, bg='#2B2B2B')
        content_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Linke Seite: Farbkreis
        wheel_frame = tk.Frame(content_frame, bg='#2B2B2B')
        wheel_frame.pack(side="left", padx=(10, 20))
        
        color_wheel = ColorWheel(wheel_frame, size=200, initial_color=current_color)
        color_wheel.pack(pady=10)
        
        # Rechte Seite: Vorschau und vordefinierte Farben
        options_frame = tk.Frame(content_frame, bg='#2B2B2B')
        options_frame.pack(side="right", fill="both", expand=True)
        
        # Vorschau
        preview_label = ctk.CTkLabel(options_frame, text="Preview:", font=("Arial", 12, "bold"))
        preview_label.pack(pady=(5, 5))
        
        preview_box = ctk.CTkFrame(options_frame, width=180, height=60, fg_color=current_color)
        preview_box.pack(pady=(0, 15))
        
        preview_text = ctk.CTkLabel(preview_box, text="Session", font=("Arial", 14, "bold"),
                                   text_color="#000000")
        preview_text.place(relx=0.5, rely=0.5, anchor="center")
        
        hex_display = ctk.CTkLabel(options_frame, text=current_color, font=("Arial", 10))
        hex_display.pack(pady=(0, 15))
        
        def update_preview(*args):
            color = selected_color.get()
            preview_box.configure(fg_color=color)
            hex_display.configure(text=color)
        
        def select_color(color):
            selected_color.set(color)
            update_preview()
        
        # Bind color wheel
        color_wheel.set_color_callback(lambda c: select_color(c))
        color_wheel.canvas.bind('<Button-1>', color_wheel.on_click)
        color_wheel.canvas.bind('<B1-Motion>', color_wheel.on_drag)
        color_wheel.set_initial_position()
        
        # Vordefinierte Farben
        colors_label = ctk.CTkLabel(options_frame, text="Quick selection:", font=("Arial", 11, "bold"))
        colors_label.pack(pady=(0, 5))
        
        color_grid = tk.Frame(options_frame, bg='#2B2B2B')
        color_grid.pack(pady=5)
        
        predefined_colors = [
            ("#1f538d", "Blue"), ("#2B8A3E", "Green"), ("#C92A2A", "Red"), ("#F59F00", "Orange"),
            ("#7C2D12", "Braun"), ("#5F3DC4", "Purple"), ("#0C8599", "Cyan"), ("#4A4A4A", "Gray")
        ]
        
        for i, (color, name) in enumerate(predefined_colors):
            row = i // 4
            col = i % 4
            
            btn = ctk.CTkButton(
                color_grid,
                text=name,
                command=lambda c=color: select_color(c),
                fg_color=color,
                hover_color=color,
                width=70,
                height=35,
                corner_radius=8,
                font=("Arial", 9, "bold"),
                text_color="white" if color in ["#4A4A4A", "#1A1A1A", "#7C2D12"] else "black"
            )
            btn.grid(row=row, column=col, padx=3, pady=3)
        
        # === BUTTONS ===
        button_frame = ctk.CTkFrame(settings_dialog)
        button_frame.pack(side="bottom", fill="x", padx=30, pady=20)
        
        def save_settings():
            new_name = name_entry.get().strip()
            new_color = selected_color.get()
            
            changed = False
            
            # Name change
            if new_name and new_name != current_name:
                self.sessions[session_id]["name"] = new_name
                changed = True
                
                # File umbenennen
                old_files = [f for f in os.listdir(self.sessions_dir) if f.endswith(f"_session_{session_id}.json")]
                old_path = os.path.join(self.sessions_dir, old_files[0]) if old_files else None
                safe_name = "_".join(new_name.split()).replace("/", "_").replace("\\", "_")
                new_path = os.path.join(self.sessions_dir, f"{safe_name}_session_{session_id}.json")
                
                try:
                    with open(new_path, 'w', encoding='utf-8') as f:
                        json.dump(self.sessions[session_id], f, ensure_ascii=False, indent=2)
                    if old_path and os.path.abspath(old_path) != os.path.abspath(new_path):
                        os.remove(old_path)
                except Exception as e:
                    self.console_print(f"❌ Error beim Save: {e}", "warning")
            
            # Farbe change
            if new_color and new_color != current_color:
                self.sessions[session_id]["color"] = new_color
                changed = True
            
            # Save und UI refresh
            if changed:
                self.sessions[session_id]["last_modified"] = datetime.now().isoformat()
                self.save_session_with_feedback()
                self.update_session_list()
                if hasattr(self, 'current_session_id') and self.current_session_id == session_id:
                    self.update_current_session_display()
                self.console_print("✅ Session-Einstellungen saved", "success")
            
            settings_dialog.destroy()
        
        def cancel():
            settings_dialog.destroy()
        
        # Keyboard shortcuts
        settings_dialog.bind('<Return>', lambda e: save_settings())
        settings_dialog.bind('<Escape>', lambda e: cancel())
        
        save_btn = ctk.CTkButton(button_frame, text="💾 Save", 
                                command=save_settings, 
                                fg_color="#2B8A3E", 
                                hover_color="#37A24B",
                                width=200, height=45,
                                font=("Arial", 14, "bold"))
        save_btn.pack(side="left", expand=True, padx=(0, 10))
        
        cancel_btn = ctk.CTkButton(button_frame, text="❌ Cancel", 
                                  command=cancel, 
                                  fg_color="#C92A2A", 
                                  hover_color="#E03131",
                                  width=200, height=45,
                                  font=("Arial", 14, "bold"))
        cancel_btn.pack(side="right", expand=True, padx=(10, 0))
        
        # Initiale Vorschau
        update_preview()
    
    def compress_chat_history(self, history, max_entries=None):
        """Komprimiert die Chat-History um Tokens zu sparen
        
        Args:
            history (list): Original Chat-History
            max_entries (int): Maximale Anzahl der letzten Messages (None = aus Config)
            
        Returns:
            list: Komprimierte Chat-History oder Original falls deaktiviert
        """
        # Prüfe ob Komprimierung aktiviert ist
        if not self.config.get("performance", {}).get("compress_chat_history", True):
            return history
        
        if not history:
            return []
        
        # Parameter aus Config oder Defaults
        if max_entries is None:
            max_entries = self.config.get("performance", {}).get("max_history_entries", 20)
        
        # Behalte nur die letzten max_entries Messages
        recent_history = history[-max_entries:] if len(history) > max_entries else history
        
        compressed = []
        for msg in recent_history:
            if msg.get("role") == "system":
                # System-Messages (BIAS) behalten - minimal kürzen
                content = msg.get("content", "").strip()
                compressed.append({"role": "system", "content": content})
                
            elif msg.get("role") == "user":
                # User-Messages: Whitespace normalisieren
                content = msg.get("content", "")
                content = " ".join(content.split())  # Normalisiere Whitespace
                compressed.append({"role": "user", "content": content})
                
            elif msg.get("role") == "assistant":
                # AI-Messages: Stärker komprimieren
                content = msg.get("content", "")
                # Entferne Emoji und überflüssige Formatierung
                content = content.replace("💭", "").replace("🤖", "").replace("✨", "")
                content = " ".join(content.split())  # Normalisiere Whitespace
                compressed.append({"role": "assistant", "content": content})
        
        return compressed
    
    def adjust_color_brightness(self, hex_color, factor):
        """Passt die Helligkeit einer Hex-Farbe an
        
        Args:
            hex_color (str): Hex-Farbcode (z.B. "#1f538d")  
            factor (float): Helligkeitsfaktor (>1 = heller, <1 = dunkler)
            
        Returns:
            str: Angepasster Hex-Farbcode
        """
        try:
            # Entferne # falls vorhanden
            hex_color = hex_color.lstrip('#')
            
            # Konvertiere zu RGB
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16) 
            b = int(hex_color[4:6], 16)
            
            # Anpassung der Helligkeit
            r = min(255, int(r * factor))
            g = min(255, int(g * factor))
            b = min(255, int(b * factor))
            
            # Zurück zu Hex
            return f"#{r:02x}{g:02x}{b:02x}"
            
        except (ValueError, IndexError):
            # Fallback bei ungültiger Farbe
            return "#5A5A5A"

    def silent_save_session(self):
        """Automatische Session-Speicherung ohne Konsolen-Output"""
        if self.current_session_id:
            try:
                with open("sessions.json", "w", encoding="utf-8") as f:
                    json.dump(self.sessions, f, indent=2, ensure_ascii=False)
            except Exception as e:
                # Stille Fehlerbehandlung - nur bei kritischen Fehlern show
                pass
    
    def update_current_session_display(self):
        """Aktualisiert die Umrandung des Chat-Verlaufs mit der Farbe der aktiven Session"""
        if not hasattr(self, 'chat_display_frame'):
            return
            
        if self.current_session_id and self.current_session_id in self.sessions:
            session_data = self.sessions[self.current_session_id]
            # Holen der Session-Farbe
            session_color = session_data.get("color", "#4A4A4A")
            
            # Umrandung des Chat-Verlaufs mit Session-Farbe refresh
            self.chat_display_frame.configure(border_color=session_color)
        else:
            # Keine aktive Session - Standard-Gray verwenden
            self.chat_display_frame.configure(border_color="#4A4A4A")

    def save_session_bias(self):
        """Speichert den Session-BIAS"""
        if not hasattr(self, 'session_bias_entry'):
            return
            
        bias_text = self.session_bias_entry.get("1.0", "end-1c")
        self.current_session_bias = bias_text
        
        if self.current_session_id and self.current_session_id in self.sessions:
            self.sessions[self.current_session_id]["bias"] = bias_text
            
        self.console_print("💾 Session-BIAS saved", "success")
        self.update_bias_info_label()
    
    def on_bias_text_changed(self, event=None):
        """Is being aufgerufen, wenn sich der BIAS-Text ändert (Auto-Save mit Verzögerung)"""
        # Vorherigen Timer stop
        if hasattr(self, 'bias_auto_save_timer') and self.bias_auto_save_timer:
            self.root.after_cancel(self.bias_auto_save_timer)
        
        # Neuen Timer für verzögerte Speicherung start (1 Sekunde nach letzter Input)
        self.bias_auto_save_timer = self.root.after(1000, self.auto_save_bias)
    
    def auto_save_bias(self):
        """Automatische BIAS-Speicherung"""
        if not hasattr(self, 'session_bias_entry'):
            return
        
        # WICHTIG: Nicht save während eine Session loaded is being
        if getattr(self, '_session_just_loaded', False):
            return
            
        bias_text = self.session_bias_entry.get("1.0", "end-1c").strip()
        old_bias = self.current_session_bias
        
        # Nur save wenn sich der Text changed hat
        if bias_text != old_bias:
            self.current_session_bias = bias_text
            
            if self.current_session_id and self.current_session_id in self.sessions:
                self.sessions[self.current_session_id]["bias"] = bias_text
                # Session automatic save
                self.silent_save_session()
                
            self.update_bias_info_label()
            
            if bias_text:
                self.console_print("💭 BIAS automatic aktualisiert", "info")
            else:
                self.console_print("💭 BIAS entfernt", "info")
    
    def update_bias_info_label(self):
        """Aktualisiert das BIAS-Info-Label"""
        if not hasattr(self, 'bias_info_label'):
            return
            
        bias_text = self.current_session_bias.strip()
        if bias_text:
            # Kurze Vorschau des BIAS (erste 50 Zeichen)
            preview = bias_text[:50]
            if len(bias_text) > 50:
                preview += "..."
            self.bias_info_label.configure(
                text=f"💭 BIAS active: {preview}",
                text_color="#4CAF50"  # Green für active
            )
        else:
            self.bias_info_label.configure(
                text="💭 BIAS not set",
                text_color="gray"
            )

    def delete_current_session(self):
        """Löscht die aktuelle Session"""
        if not self.current_session_id:
            return
        
        # Bestätigungsabfrage
        session_count = len(self.sessions)
        if session_count == 1:
            # Letzte Session - besondere Warnung
            result = messagebox.askyesno(
                "Letzte Session delete",
                "Dies ist die letzte Session.\n\n"
                "Möchten You diese wirklich delete?\n"
                "Nach dem Delete is being eine neue leere Session created."
            )
        else:
            # Normale Bestätigung
            result = messagebox.askyesno(
                "Session delete",
                f"Möchten You die aktuelle Session wirklich delete?\n\n"
                f"Session: {self.sessions[self.current_session_id].get('name', 'Unbenannt')}\n"
                f"({len(self.sessions[self.current_session_id].get('messages', []))} Messages)"
            )
        
        if not result:
            return
            
        deleted_session_id = self.current_session_id
        
        # Alle zugehörigen Session-Dateien delete (unabhängig vom Namen)
        try:
            deleted_files = 0
            for f in os.listdir(self.sessions_dir):
                if f.endswith(f"_session_{self.current_session_id}.json"):
                    file_path = os.path.join(self.sessions_dir, f)
                    try:
                        os.remove(file_path)
                        deleted_files += 1
                    except Exception as e:
                        self.console_print(f"❌ Error deleting session file {f}: {e}", "error")
            if deleted_files == 0:
                self.console_print(f"⚠️ No session file found for {self.current_session_id}.", "warning")
        except Exception as e:
            self.console_print(f"❌ Error deleting session files: {e}", "error")
        
        # Remove session from memory
        if self.current_session_id in self.sessions:
            del self.sessions[self.current_session_id]
        
        # Sessions persistent save
        try:
            with open("sessions.json", "w", encoding="utf-8") as f:
                json.dump(self.sessions, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.console_print(f"❌ Error beim Save der Session-List: {e}", "error")
        
        self.console_print(f"🗑️ Session deleted: {deleted_session_id}", "warning")
        
        # UI sofort refresh
        self.update_session_list()
        self.update_current_session_display()
        
        # Force update nach kurzer Verzögerung
        self.root.after(100, self.update_session_list)
        
        # Prüfe ob noch andere Sessions vorhanden sind
        if self.sessions:
            # Lade die neueste verfügbare Session
            latest_session = max(self.sessions.keys(), 
                               key=lambda x: self.sessions[x].get("created_at", ""))
            self.load_session(latest_session)
            self.console_print(f"🔄 Gewechselt zu Session: {latest_session}", "info")
        else:
            # Alle Sessions deleted - Chat leeren aber keine neue Session create
            self.current_session_id = None
            self.clear_chat_for_new_session()
            
            # UI für "keine Session" Zustand anpassen
            self.update_session_list()
            self.update_current_session_display()
            
            # BIAS-Feld leeren
            if hasattr(self, 'session_bias_entry'):
                self.session_bias_entry.delete("1.0", "end")
                
            # Model zurücksetzen
            self.current_model = None
            if hasattr(self, 'model_dropdown'):
                self.model_dropdown.update_models({})
                
            self.console_print("🔄 All sessions deleted - chat ready for new session", "info")

    def delete_all_sessions(self):
        """Deletes all sessions after confirmation"""
        if not self.sessions:
            messagebox.showinfo("No sessions", "There are no sessions to delete.")
            return
        
        session_count = len(self.sessions)
        
        # Bestätigungs-Dialog
        result = messagebox.askyesno(
            "Alle Sessions delete",
            f"Möchten You wirklich ALLE {session_count} Sessions delete?\n\n⚠️ WARNUNG: Dieser Vorgang kann nicht rückgängig gemacht werden!\nAlle Chat-Verläufe und Session-Daten gehen verloren."
        )
        
        if result:
            # Alle Session-Dateien delete
            deleted_count = 0
            failed_count = 0
            
            for session_id in list(self.sessions.keys()):
                found_file = False
                for f in os.listdir(self.sessions_dir):
                    if f.endswith(f"_session_{session_id}.json"):
                        found_file = True
                        file_path = os.path.join(self.sessions_dir, f)
                        try:
                            os.remove(file_path)
                            deleted_count += 1
                        except Exception as e:
                            failed_count += 1
                            self.console_print(f"❌ Error deleting {f}: {e}", "error")
                if not found_file:
                    self.console_print(f"⚠️ No session file found for {session_id}.", "warning")
            
            # Remove all sessions from memory
            self.sessions.clear()
            self.current_session_id = None
            
            # Sessions-File refresh (leere File)
            try:
                with open("sessions.json", "w", encoding="utf-8") as f:
                    json.dump({}, f, indent=2, ensure_ascii=False)
            except Exception as e:
                self.console_print(f"❌ Error beim Save der leeren Session-List: {e}", "error")
            
            # UI zurücksetzen
            self.clear_chat_for_new_session()
            self.update_session_list()
            self.update_current_session_display()
            
            # BIAS-Feld leeren
            if hasattr(self, 'session_bias_entry'):
                self.session_bias_entry.delete("1.0", "end")
            
            # Model zurücksetzen
            self.current_model = None
            if hasattr(self, 'model_dropdown'):
                self.model_dropdown.update_models({})
            
            # Ergebnis show
            if failed_count == 0:
                self.console_print(f"🧹 Alle {deleted_count} Sessions erfolgreich deleted", "success")
                messagebox.showinfo(
                    "Bereinigung abgeschlossen", 
                    f"✅ Alle {deleted_count} Sessions wurden erfolgreich deleted.\n\nKlicken You auf '➕ New Session' to begin."
                )
            else:
                self.console_print(f"🧹 {deleted_count} Sessions deleted, {failed_count} Error", "warning")
                messagebox.showwarning(
                    "Bereinigung mit Fehlern", 
                    f"⚠️ {deleted_count} Sessions deleted, aber {failed_count} Error aufgetreten.\nSiehe Konsole für Details."
                )

    def clear_chat_for_new_session(self):
        """Leert den Chat für eine neue Session"""
        # Lösche alle Chat-Bubbles gründlich
        if hasattr(self, 'chat_bubbles'):
            for bubble in self.chat_bubbles:
                try:
                    # Explizit pack_forget aufrufen vor destroy
                    bubble.pack_forget()
                    bubble.destroy()
                except Exception as e:
                    pass
            self.chat_bubbles.clear()
        
        # Chat-History leeren
        self.chat_history.clear()
        self.message_history.clear()
        self.history_index = -1
        
        # Layout MEHRFACH und gründlich refresh nach dem Delete
        if hasattr(self, 'chat_display_frame'):
            # Sofortiges Update
            self.chat_display_frame.update()
            self.chat_display_frame.update_idletasks()
            
            if hasattr(self.chat_display_frame, '_parent_canvas'):
                # Canvas Update
                self.chat_display_frame._parent_canvas.update()
                self.chat_display_frame._parent_canvas.update_idletasks()
                
                # Scrollregion zurücksetzen
                try:
                    self.chat_display_frame._parent_canvas.configure(
                        scrollregion=self.chat_display_frame._parent_canvas.bbox("all")
                    )
                except:
                    pass
                
                # Nach oben scrollen (für leere Chats)
                try:
                    self.chat_display_frame._parent_canvas.yview_moveto(0.0)
                except:
                    pass

    def restore_chat_message(self, msg_data):
        """Stellt eine Chat-Message aus Session-Daten wieder her"""
        timestamp = msg_data.get("timestamp", datetime.now().strftime("%H:%M:%S"))
        sender = msg_data.get("sender", "System")
        message = msg_data.get("message", "")
        
        # System-Messages ausblenden wenn Flag gesetzt ist (gleiche Logik wie in add_to_chat)
        if sender == "System" and not self.config.get("show_system_messages", True):
            return  # Keine UI-Bubble create für ausgeblendete System-Messages
        
        # Chat-Bubble create
        bubble = ChatBubble(
            self.chat_display_frame,
            sender=sender,
            message=message,
            timestamp=timestamp,
            app_config=self.config
        )
        
        self.chat_bubbles.append(bubble)
        
        # Sofortiges Layout-Update für jede Bubble
        bubble.update_idletasks()

    # ============================================
    # ENDE SESSION MANAGEMENT SYSTEM  
    # ============================================
    
    def setup_ui(self):
        """Erstellt die Benutzeroberfläche"""
        
        # Hauptframe mit pack (einfacher und stabiler)
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Horizontales Layout mit pack
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Session Management Panel (links) - Breite aus Config
        session_panel_width = self.config.get('ui_session_panel_width', 350)
        self.session_panel_container = ctk.CTkScrollableFrame(
            self.content_frame, 
            width=session_panel_width,
            label_text="Session Management"
        )
        self.session_panel_container.pack(side="left", fill="y", padx=(0, 5), pady=0)
        
        # Session Panel Inhalt
        self.session_panel = ctk.CTkFrame(self.session_panel_container)
        self.session_panel.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.setup_session_panel()
        
        # Tab-System (rechts) - nimmt restlichen Platz
        self.tab_view = ctk.CTkTabview(self.content_frame)
        self.tab_view.pack(side="right", fill="both", expand=True, padx=5, pady=0)
        
        # Chat-Tab hinzufügen
        self.chat_tab = self.tab_view.add("Chat")
        self.setup_chat_tab()
        
        # Config-Tab hinzufügen  
        self.config_tab = self.tab_view.add("Config")
        self.setup_config_tab()
        
        # Standard-Tab setzen
        self.tab_view.set("Chat")
        
        # Session Management initialisieren
        self.initialize_session_management()
        
        # Keyboard Shortcuts einrichten
        self.setup_keyboard_shortcuts()
    
    def setup_chat_tab(self):
        """Erstellt den Chat-Tab mit allen Elementen"""
        
        # Chat-Area (Model-Management jetzt im Session Panel)
        self.chat_frame = ctk.CTkFrame(self.chat_tab)
        self.chat_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Chat history with scrollable frame and colored border for active session
        self.chat_display_frame = ctk.CTkScrollableFrame(
            self.chat_frame,
            label_text="Chat History",
            border_width=3,
            border_color="#4A4A4A"  # Standard gray, updated on session change
        )
        self.chat_display_frame.pack(fill="both", expand=True, padx=10, pady=(10, 5))
        
        # List für Chat-Bubbles
        self.chat_bubbles = []
        
        # Input-Area
        self.input_frame = ctk.CTkFrame(self.chat_frame)
        self.input_frame.pack(fill="x", padx=self.config.get("ui_padding_main", 10), 
                             pady=(self.config.get("ui_padding_content", 5), self.config.get("ui_padding_main", 10)))
        
        self.message_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Message eingeben...",
            font=("Arial", self.config.get("ui_input_font_size", 12)),
            height=self.config.get("ui_input_height", 40)
        )
        self.message_entry.pack(side="left", fill="x", expand=True, 
                               padx=(0, self.config.get("ui_padding_main", 10)), 
                               pady=self.config.get("ui_padding_main", 10))
        self.message_entry.bind("<Return>", self.send_message)
        self.message_entry.bind("<Up>", self.navigate_history_up)
        self.message_entry.bind("<Down>", self.navigate_history_down)
        self.message_entry.bind("<Key>", self.on_key_press)
        
        self.send_btn = ctk.CTkButton(
            self.input_frame,
            text="Send",
            command=self.send_message,
            width=self.config.get("ui_button_width", 100),
            height=self.config.get("ui_button_height", 40),
            font=("Arial", self.config.get("ui_input_font_size", 12))
        )
        self.send_btn.pack(side="right", pady=self.config.get("ui_padding_main", 10))
        
        # Stop Button (initial deaktiviert)
        self.stop_btn = ctk.CTkButton(
            self.input_frame,
            text="Stop",
            command=self.stop_generation,
            fg_color="red",
            hover_color="darkred",
            width=self.config.get("ui_model_button_size", 60),
            height=self.config.get("ui_button_height", 40),
            font=("Arial", self.config.get("ui_input_font_size", 12)),
            state="disabled"
        )
        self.stop_btn.pack(side="right", padx=(0, self.config.get("ui_padding_main", 10)), 
                          pady=self.config.get("ui_padding_main", 10))
        
        # Keine automatische Session-Erstellung beim Start mehr
    
    def setup_config_tab(self):
        """Erstellt den Config-Tab mit Einstellungen"""
        
        # Container für Config-Tab mit fixierten Buttons
        config_container = ctk.CTkFrame(self.config_tab)
        config_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Haupt-Scrollable Frame für Config-Inhalte
        config_scroll = ctk.CTkScrollableFrame(config_container, label_text="Configuration")
        config_scroll.pack(fill="both", expand=True, padx=10, pady=(10, 10))
        
        # Fixierte Button-Leiste am unteren Rand
        button_frame = ctk.CTkFrame(config_container)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Container für zentrierte Buttons
        button_container = ctk.CTkFrame(button_frame)
        button_container.pack(expand=True)
        
        # Buttons nebeneinander zentriert
        restart_btn = ctk.CTkButton(button_container, text="🔄 Apply & Restart", 
                                   command=self.apply_and_restart, 
                                   width=200, height=40, font=("Arial", 13, "bold"),
                                   fg_color="#1f538d", hover_color="#2a6bb0")
        restart_btn.pack(side="left", padx=10, pady=15)
        
        reset_btn = ctk.CTkButton(button_container, text="↩️ Default", command=self.reset_config, 
                                 width=150, height=40, font=("Arial", 13, "bold"),
                                 fg_color="#722F37", hover_color="#8a3a45")
        reset_btn.pack(side="left", padx=10, pady=15)
        
        # Bubble-Farben Sektion
        bubble_frame = ctk.CTkFrame(config_scroll)
        bubble_frame.pack(fill="x", pady=(0, 20))
        
        bubble_title = ctk.CTkLabel(bubble_frame, text="🎨 Chat Bubble Colors", font=("Arial", 16, "bold"))
        bubble_title.pack(pady=(15, 10))
        
        # You (User) Farben - Komprimiert
        user_main_frame = ctk.CTkFrame(bubble_frame)
        user_main_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(user_main_frame, text="💬 You:", font=("Arial", 11, "bold"), width=50).pack(side="left", padx=5)
        
        user_colors_frame = ctk.CTkFrame(user_main_frame)
        user_colors_frame.pack(side="left", fill="x", expand=True, padx=5)
        
        self.user_bg_entry, self.user_bg_preview = self.setup_color_input_with_preview(
            user_colors_frame, "Hintergrund:", "user_bg_color", "#003300")
        self.user_text_entry, self.user_text_preview = self.setup_color_input_with_preview(
            user_colors_frame, "Text:", "user_text_color", "#00FF00")
        
        # AI-Model Farben - Komprimiert  
        ai_main_frame = ctk.CTkFrame(bubble_frame)
        ai_main_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(ai_main_frame, text="🤖 AI:", font=("Arial", 11, "bold"), width=50).pack(side="left", padx=5)
        
        ai_colors_frame = ctk.CTkFrame(ai_main_frame)
        ai_colors_frame.pack(side="left", fill="x", expand=True, padx=5)
        
        self.ai_bg_entry, self.ai_bg_preview = self.setup_color_input_with_preview(
            ai_colors_frame, "Hintergrund:", "ai_bg_color", "#1E3A5F")
        self.ai_text_entry, self.ai_text_preview = self.setup_color_input_with_preview(
            ai_colors_frame, "Text:", "ai_text_color", "white")
        
        # System Farben - Komprimiert
        system_main_frame = ctk.CTkFrame(bubble_frame)
        system_main_frame.pack(fill="x", padx=15, pady=(5, 10))
        ctk.CTkLabel(system_main_frame, text="ℹ️ System:", font=("Arial", 11, "bold"), width=50).pack(side="left", padx=5)
        
        system_colors_frame = ctk.CTkFrame(system_main_frame)
        system_colors_frame.pack(side="left", fill="x", expand=True, padx=5)
        
        self.system_bg_entry, self.system_bg_preview = self.setup_color_input_with_preview(
            system_colors_frame, "Hintergrund:", "system_bg_color", "#722F37")
        self.system_text_entry, self.system_text_preview = self.setup_color_input_with_preview(
            system_colors_frame, "Text:", "system_text_color", "white")
        
        # Schriftarten Sektion
        font_frame = ctk.CTkFrame(config_scroll)
        font_frame.pack(fill="x", pady=(0, 15))
        
        font_title = ctk.CTkLabel(font_frame, text="🔤 Fonts", font=("Arial", 16, "bold"))
        font_title.pack(pady=(10, 5))
        
        # Font-Dropdowns mit individuellen Größen
        font_dropdowns_frame = ctk.CTkFrame(font_frame)
        font_dropdowns_frame.pack(fill="x", padx=20, pady=10)
        
        # User Font mit Größen-Slider
        user_font_frame = ctk.CTkFrame(font_dropdowns_frame)
        user_font_frame.pack(fill="x", pady=3)
        
        # Label und Dropdown
        ctk.CTkLabel(user_font_frame, text="You:", width=100).pack(side="left", padx=5)
        self.user_font_combo = ctk.CTkComboBox(user_font_frame, 
            values=["Courier New", "Consolas", "Monaco", "Lucida Console"],
            width=130, command=self.update_user_font_preview)
        self.user_font_combo.pack(side="left", padx=5)
        self.user_font_combo.set(self.config["user_font"])
        
        # Mausrad-Scrolling für user_font_combo aktivieren
        
        # Größen-Slider
        ctk.CTkLabel(user_font_frame, text="Size:", width=40).pack(side="left", padx=(15, 2))
        self.user_font_size_slider = ctk.CTkSlider(user_font_frame, from_=8, to=24, number_of_steps=16, width=100)
        self.user_font_size_slider.pack(side="left", padx=3)
        self.user_font_size_slider.set(self.config["user_font_size"])
        self.user_font_size_label = ctk.CTkLabel(user_font_frame, text=f"{self.config['user_font_size']}px", width=30)
        self.user_font_size_label.pack(side="left", padx=3)
        self.user_font_size_slider.configure(command=self.update_user_font_preview)
        
        # Preview
        self.user_font_preview = ctk.CTkLabel(user_font_frame, text="💬 Hallo Welt! 123", 
                                             font=(self.config["user_font"], self.config["user_font_size"]),
                                             text_color="#00FF00", width=150)
        self.user_font_preview.pack(side="left", padx=10)
        
        # AI Font mit Größen-Slider
        ai_font_frame = ctk.CTkFrame(font_dropdowns_frame)
        ai_font_frame.pack(fill="x", pady=3)
        
        # Label und Dropdown
        ctk.CTkLabel(ai_font_frame, text="AI-Model:", width=100).pack(side="left", padx=5)
        self.ai_font_combo = ctk.CTkComboBox(ai_font_frame,
            values=["Consolas", "Courier New", "Arial", "Segoe UI"],
            width=130, command=self.update_ai_font_preview)
        self.ai_font_combo.pack(side="left", padx=5)
        self.ai_font_combo.set(self.config["ai_font"])
        
        # Mausrad-Scrolling für ai_font_combo aktivieren
        
        # Größen-Slider
        ctk.CTkLabel(ai_font_frame, text="Size:", width=40).pack(side="left", padx=(15, 2))
        self.ai_font_size_slider = ctk.CTkSlider(ai_font_frame, from_=8, to=24, number_of_steps=16, width=100)
        self.ai_font_size_slider.pack(side="left", padx=3)
        self.ai_font_size_slider.set(self.config["ai_font_size"])
        self.ai_font_size_label = ctk.CTkLabel(ai_font_frame, text=f"{self.config['ai_font_size']}px", width=30)
        self.ai_font_size_label.pack(side="left", padx=3)
        self.ai_font_size_slider.configure(command=self.update_ai_font_preview)
        
        # Preview
        self.ai_font_preview = ctk.CTkLabel(ai_font_frame, text="🤖 AI Response Text", 
                                           font=(self.config["ai_font"], self.config["ai_font_size"]),
                                           text_color="#FFFFFF", width=150)
        self.ai_font_preview.pack(side="left", padx=10)
        
        # System Font mit Größen-Slider
        system_font_frame = ctk.CTkFrame(font_dropdowns_frame)
        system_font_frame.pack(fill="x", pady=3)
        
        # Label und Dropdown
        ctk.CTkLabel(system_font_frame, text="System:", width=100).pack(side="left", padx=5)
        self.system_font_combo = ctk.CTkComboBox(system_font_frame,
            values=["Arial", "Segoe UI", "Helvetica", "Tahoma"],
            width=130, command=self.update_system_font_preview)
        self.system_font_combo.pack(side="left", padx=5)
        self.system_font_combo.set(self.config["system_font"])
        
        # Mausrad-Scrolling für system_font_combo aktivieren
        
        # Größen-Slider
        ctk.CTkLabel(system_font_frame, text="Size:", width=40).pack(side="left", padx=(15, 2))
        self.system_font_size_slider = ctk.CTkSlider(system_font_frame, from_=8, to=24, number_of_steps=16, width=100)
        self.system_font_size_slider.pack(side="left", padx=3)
        self.system_font_size_slider.set(self.config["system_font_size"])
        self.system_font_size_label = ctk.CTkLabel(system_font_frame, text=f"{self.config['system_font_size']}px", width=30)
        self.system_font_size_label.pack(side="left", padx=3)
        self.system_font_size_slider.configure(command=self.update_system_font_preview)
        
        # Preview
        self.system_font_preview = ctk.CTkLabel(system_font_frame, text="ℹ️ System-Message", 
                                               font=(self.config["system_font"], self.config["system_font_size"]),
                                               text_color="#FFFFFF", width=150)
        self.system_font_preview.pack(side="left", padx=10)
        
        
        # ========== UI-EINSTELLUNGEN SEKTION ==========
        ui_settings_frame = ctk.CTkFrame(config_scroll)
        ui_settings_frame.pack(fill="x", pady=(10, 15))
        
        ui_settings_title = ctk.CTkLabel(ui_settings_frame, text="🎛️ Layout & Sizes", font=("Arial", 16, "bold"))
        ui_settings_title.pack(pady=(15, 10))
        
        # Session Panel Width
        self.create_config_slider(ui_settings_frame, "Session Panel Width:", "ui_session_panel_width", 
                                 200, 600, self.config.get('ui_session_panel_width', 350), "px")
        
        # Window Start Size
        self.create_config_slider(ui_settings_frame, "Window Width (Start):", "ui_window_width", 
                                 1000, 2560, self.config.get('ui_window_width', 1400), "px")
        self.create_config_slider(ui_settings_frame, "Window Height (Start):", "ui_window_height", 
                                 600, 1440, self.config.get('ui_window_height', 900), "px")
        
        # Input & Buttons
        ui_input_title = ctk.CTkLabel(ui_settings_frame, text="⌨️ Input & Buttons", font=("Arial", 14, "bold"))
        ui_input_title.pack(pady=(15, 5))
        
        self.create_config_slider(ui_settings_frame, "Input Field Height:", "ui_input_height", 
                                 30, 60, self.config.get('ui_input_height', 40), "px")
        self.create_config_slider(ui_settings_frame, "Input Font Size:", "ui_input_font_size", 
                                 9, 18, self.config.get('ui_input_font_size', 12), "px")
        self.create_config_slider(ui_settings_frame, "Button Width:", "ui_button_width", 
                                 60, 150, self.config.get('ui_button_width', 100), "px")
        self.create_config_slider(ui_settings_frame, "Button Height:", "ui_button_height", 
                                 25, 60, self.config.get('ui_button_height', 40), "px")
        
        # Erweiterte Optionen
        ui_options_title = ctk.CTkLabel(ui_settings_frame, text="⚡ Advanced Options", font=("Arial", 14, "bold"))
        ui_options_title.pack(pady=(15, 5))
        
        options_frame = ctk.CTkFrame(ui_settings_frame)
        options_frame.pack(fill="x", padx=15, pady=(5, 10))
        
        # System-Messages Toggle (verschoben hierher)
        self.show_system_messages_var = ctk.BooleanVar(value=self.config.get("show_system_messages", True))
        system_msg_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="📢 System-Messages im Chat show",
            variable=self.show_system_messages_var,
            font=("Arial", 11)
        )
        system_msg_checkbox.pack(anchor="w", padx=10, pady=5)
        
        self.auto_scroll_var = ctk.BooleanVar(value=self.config.get("auto_scroll_chat", True))
        auto_scroll_cb = ctk.CTkCheckBox(options_frame, text="📜 Auto-Scroll to New Messages", 
                                        variable=self.auto_scroll_var, font=("Arial", 11))
        auto_scroll_cb.pack(anchor="w", padx=10, pady=5)
    
    def create_config_slider(self, parent, label_text, config_key, min_val, max_val, current_val, unit=""):
        """Erstellt einen Slider mit Label und Wert-Anzeige für Config-Einstellungen"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=15, pady=5)
        
        # Label
        label = ctk.CTkLabel(frame, text=label_text, width=200, anchor="w")
        label.pack(side="left", padx=5)
        
        # Value Display
        value_label = ctk.CTkLabel(frame, text=f"{int(current_val)}{unit}", width=60)
        value_label.pack(side="right", padx=5)
        
        # Slider
        slider = ctk.CTkSlider(frame, from_=min_val, to=max_val, width=300,
                              number_of_steps=(max_val - min_val))
        slider.set(current_val)
        slider.pack(side="right", padx=10)
        
        # Update function
        def update_value(val):
            value_label.configure(text=f"{int(float(val))}{unit}")
        
        slider.configure(command=update_value)
        
        # Store reference
        if not hasattr(self, 'config_sliders'):
            self.config_sliders = {}
        self.config_sliders[config_key] = slider
    
    def open_color_picker(self, entry_widget):
        """Öffnet einen RGB-Farbwähler und setzt den gewählten Farbwert in das Entry-Feld"""
        try:
            # Aktuelle Farbe aus dem Entry-Feld als Startwert verwenden
            current_color = entry_widget.get()
            if current_color and current_color.startswith('#'):
                initial_color = current_color
            else:
                initial_color = "#00FF00"  # Standard green
            
            # Open color picker
            color = colorchooser.askcolor(
                color=initial_color,
                title="🎨 Select Color",
                parent=self.root
            )
            
            # Wenn eine Farbe gewählt wurde, aktualisiere das Entry-Feld
            if color[1]:  # color[1] contains the hex value
                entry_widget.delete(0, 'end')
                entry_widget.insert(0, color[1].upper())
                
        except Exception as e:
            messagebox.showerror("Error", f"Error opening color picker: {e}")
    
    def create_color_preview(self, parent, color, size=20):
        """Erstellt ein kleines farbiges Quadrat als Farb-Preview"""
        preview = ctk.CTkLabel(parent, text="", width=size, height=size, 
                              fg_color=color, corner_radius=3)
        return preview
    
    def update_color_preview(self, preview_label, entry_widget):
        """Aktualisiert das Farb-Preview basierend auf dem Entry-Wert"""
        try:
            color = entry_widget.get()
            if color and color.startswith('#'):
                preview_label.configure(fg_color=color)
            else:
                preview_label.configure(fg_color="gray")
        except Exception:
            preview_label.configure(fg_color="gray")
    
    def setup_color_input_with_preview(self, parent, label_text, entry_var_name, default_color):
        """Erstellt ein kompaktes Farb-Eingabefeld mit Preview"""
        frame = ctk.CTkFrame(parent)
        frame.pack(side="left", padx=5, pady=2, fill="x", expand=True)
        
        # Label
        ctk.CTkLabel(frame, text=label_text, width=80).pack(side="left", padx=2)
        
        # Color Preview
        color_preview = self.create_color_preview(frame, default_color)
        color_preview.pack(side="left", padx=2)
        
        # Entry Field
        entry = ctk.CTkEntry(frame, placeholder_text=default_color, width=80)
        entry.pack(side="left", padx=2)
        entry.insert(0, self.config[entry_var_name])
        
        # Color Picker Button
        picker_btn = ctk.CTkButton(frame, text="🎨", width=25, height=25,
                                  command=lambda: self.open_color_picker_with_preview(entry, color_preview))
        picker_btn.pack(side="left", padx=2)
        
        # Bind update event
        entry.bind('<KeyRelease>', lambda e: self.update_color_preview(color_preview, entry))
        
        return entry, color_preview
    
    def open_color_picker_with_preview(self, entry_widget, preview_label):
        """Öffnet Color-Picker und aktualisiert Entry + Preview"""
        try:
            # Aktuelle Farbe als Startwert verwenden
            current_color = entry_widget.get()
            if current_color and current_color.startswith('#'):
                initial_color = current_color
            else:
                initial_color = "#00FF00"
            
            # Open color picker
            color = colorchooser.askcolor(
                color=initial_color,
                title="🎨 Select Color",
                parent=self.root
            )
            
            # If a color was selected, update entry and preview
            if color[1]:
                hex_color = color[1].upper()
                entry_widget.delete(0, 'end')
                entry_widget.insert(0, hex_color)
                preview_label.configure(fg_color=hex_color)
                
        except Exception as e:
            messagebox.showerror("Error", f"Error opening color picker: {e}")
    
    def update_user_font_preview(self, value=None):
        """Updates user font preview"""
        try:
            selected_font = self.user_font_combo.get()
            font_size = int(self.user_font_size_slider.get())
            self.user_font_size_label.configure(text=f"{font_size}px")
            self.user_font_preview.configure(font=(selected_font, font_size))
        except Exception:
            self.user_font_preview.configure(font=("Courier New", 11))
    
    def update_ai_font_preview(self, value=None):
        """Aktualisiert AI Font Preview"""
        try:
            selected_font = self.ai_font_combo.get()
            font_size = int(self.ai_font_size_slider.get())
            self.ai_font_size_label.configure(text=f"{font_size}px")
            self.ai_font_preview.configure(font=(selected_font, font_size))
        except Exception:
            self.ai_font_preview.configure(font=("Consolas", 11))
    
    def update_system_font_preview(self, value=None):
        """Aktualisiert System Font Preview"""
        try:
            selected_font = self.system_font_combo.get()
            font_size = int(self.system_font_size_slider.get())
            self.system_font_size_label.configure(text=f"{font_size}px")
            self.system_font_preview.configure(font=(selected_font, font_size))
        except Exception:
            self.system_font_preview.configure(font=("Arial", 10))
    
    def apply_config(self):
        """Wendet die neuen Konfigurationen an"""
        try:
            # Update Config-Dictionary - Farben
            self.config["user_bg_color"] = self.user_bg_entry.get() or "#003300"
            self.config["user_text_color"] = self.user_text_entry.get() or "#00FF00"
            self.config["ai_bg_color"] = self.ai_bg_entry.get() or "#1E3A5F"
            self.config["ai_text_color"] = self.ai_text_entry.get() or "white"
            self.config["system_bg_color"] = self.system_bg_entry.get() or "#722F37"
            self.config["system_text_color"] = self.system_text_entry.get() or "white"
            
            # Schriftarten und Größen
            self.config["user_font"] = self.user_font_combo.get()
            self.config["user_font_size"] = int(self.user_font_size_slider.get())
            self.config["ai_font"] = self.ai_font_combo.get()
            self.config["ai_font_size"] = int(self.ai_font_size_slider.get())
            self.config["system_font"] = self.system_font_combo.get()
            self.config["system_font_size"] = int(self.system_font_size_slider.get())
            
            # UI-Optionen
            self.config["show_system_messages"] = self.show_system_messages_var.get()
            self.config["auto_scroll_chat"] = self.auto_scroll_var.get()
            
            # UI-Slider-Werte übernehmen
            if hasattr(self, 'config_sliders'):
                for config_key, slider in self.config_sliders.items():
                    self.config[config_key] = int(slider.get())
            
            # Speichere Configuration in YAML-File
            self.save_config()
            
            # Aktualisiere alle bestehenden Chat-Bubbles mit neuer Configuration
            self.update_all_chat_bubbles()
            
            # Show success message
            self.add_to_chat("System", "✅ Configuration successfully applied and saved! Changes will be fully applied at next start.")
            
            # Info bei UI-Layout-Änderungen
            if hasattr(self, 'config_sliders'):
                self.add_to_chat("System", "ℹ️ Layout changes (panel sizes, button sizes etc.) will become active after next restart.")
            
        except Exception as e:
            self.add_to_chat("System", f"❌ Error beim Anwenden der Configuration: {e}")
    
    def apply_and_restart(self):
        """Wendet Configuration an und startet die Anwendung new"""
        try:
            # Speichere Configuration
            self.apply_config()
            
            # Kurze Pause damit Nutzer die Bestätigung sieht
            self.root.after(800, self.restart_application)
            
        except Exception as e:
            self.add_to_chat("System", f"❌ Error beim Neustart: {e}")
    
    def restart_application(self):
        """Startet die Anwendung new mit dem restart.py Script"""
        try:
            import sys
            import subprocess
            import os
            
            self.add_to_chat("System", "🔄 Anwendung is being new started...")
            self.root.update()
            
            # Speichere aktuelle Session
            if hasattr(self, 'current_session_id') and self.current_session_id:
                if hasattr(self, 'save_session_with_feedback'):
                    self.save_session_with_feedback()
            
            # Pfad zum restart.py Script
            restart_script = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "restart.py")
            
            # Starte restart.py im Hintergrund
            if os.path.exists(restart_script):
                subprocess.Popen([sys.executable, restart_script], 
                               creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
            else:
                # Fallback: Direkter Neustart ohne Script
                main_script = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "main.py")
                subprocess.Popen([sys.executable, main_script])
            
            # Schließe aktuelle Instanz nach kurzer Verzögerung
            self.root.after(300, self.root.destroy)
            
        except Exception as e:
            self.add_to_chat("System", f"❌ Error beim Neustart der Anwendung: {e}")
    
    def update_all_chat_bubbles(self):
        """Aktualisiert das Styling aller bestehenden Chat-Bubbles"""
        try:
            updated_count = 0
            for bubble in self.chat_bubbles:
                bubble.update_style(self.config)
                updated_count += 1
            
            if updated_count > 0:
                self.console_print(f"🎨 {updated_count} Chat-Bubbles mit neuer Configuration aktualisiert", "info")
                
                # Scrolle den Chat-Area nach unten, um Updates sichtbar zu machen
                if self.config.get("auto_scroll_chat", True):
                    self.chat_display_frame._parent_canvas.after(100, 
                        lambda: self.chat_display_frame._parent_canvas.yview_moveto(1.0))
                    
        except Exception as e:
            self.console_print(f"❌ Error beim Refresh der Chat-Bubbles: {e}", "error")
    
    
    def reset_config(self):
        """Setzt die Configuration auf Default values back"""
        # Verwende die neue reset_config_to_defaults() Methode
        self.reset_config_to_defaults()
        
        # Update UI Elements - Farben
        self.user_bg_entry.delete(0, 'end')
        self.user_bg_entry.insert(0, self.config["user_bg_color"])
        self.user_text_entry.delete(0, 'end')
        self.user_text_entry.insert(0, self.config["user_text_color"])
        
        self.ai_bg_entry.delete(0, 'end')
        self.ai_bg_entry.insert(0, self.config["ai_bg_color"])
        self.ai_text_entry.delete(0, 'end')
        self.ai_text_entry.insert(0, self.config["ai_text_color"])
        
        self.system_bg_entry.delete(0, 'end')
        self.system_bg_entry.insert(0, self.config["system_bg_color"])
        self.system_text_entry.delete(0, 'end')
        self.system_text_entry.insert(0, self.config["system_text_color"])
        
        # Update UI Elements - Individuelle Schriftarten und Größen
        self.user_font_combo.set(self.config["user_font"])
        self.user_font_size_slider.set(self.config["user_font_size"])
        self.ai_font_combo.set(self.config["ai_font"])
        self.ai_font_size_slider.set(self.config["ai_font_size"])
        self.system_font_combo.set(self.config["system_font"])
        self.system_font_size_slider.set(self.config["system_font_size"])
        
        # Update Previews
        self.update_user_font_preview()
        self.update_ai_font_preview()
        self.update_system_font_preview()
        
    # Konsole (entfernt)
        
        # UI-Optionen
        self.show_system_messages_var.set(self.config.get("show_system_messages", True))
        
        self.add_to_chat("System", "🔄 Configuration reset to default values and saved!")
    
    def check_ollama_status(self):
        """Prüft Ollama-Status und lädt Modelle"""
        def check():
            if self.ollama.is_ollama_running():
                self.status_label.configure(text="Ollama Status: ✅ Connected")
                self.refresh_models()
                self.load_available_models()
            else:
                self.status_label.configure(text="Ollama Status: ❌ Not Connected")
                self.add_to_chat("System", "Ollama ist nicht erreichbar. Stellen You sicher, dass Ollama running.")
        
        threading.Thread(target=check, daemon=True).start()
    
    def load_available_models(self):
        """Lädt alle verfügbaren Ollama-Modelle"""
        def load():
            self.add_to_chat("System", "🔄 Lade aktuelle Model-List von Ollama...")
            all_models = self.ollama.get_all_ollama_models()
            
            if all_models:
                # Konvertiere zu Model-Info-Dict mit Größen-Informationen
                models_dict = {}
                for model_name in all_models:
                    # Extrahiere Größen-Info aus dem Namen (z.B. llama3:8b)
                    size_info = ""
                    if ":" in model_name:
                        param_size = model_name.split(":")[-1]
                        if "b" in param_size.lower():
                            size_info = param_size.upper()
                    
                    models_dict[model_name] = {
                        "size": f"~{size_info.replace('B', ' Mrd Parameter')}" if size_info else "Available",
                        "type": "LLM",
                        "parameters": size_info
                    }
                
                self.root.after(0, lambda: self.available_dropdown.update_models(models_dict))
                model_count = len(models_dict)
                self.root.after(0, lambda: self.add_to_chat("System", 
                    f"✅ {model_count} Modelle zum Download available"))
            else:
                self.root.after(0, lambda: self.available_dropdown.update_models({}))
                self.root.after(0, lambda: self.add_to_chat("System", "❌ Keine Modelle available"))
        
        threading.Thread(target=load, daemon=True).start()
    
    def refresh_models(self):
        """Aktualisiert die Model-Listen"""
        def update():
            # Installed Models refresh
            models = self.ollama.get_available_models()
            if models:
                # Erstelle Model-Info-Dict für installierte Modelle
                models_dict = {}
                for model in models:
                    # Versuche Größe und Info zu bekommen
                    models_dict[model] = {
                        "size": "Installed",
                        "type": "LLM",
                        "parameters": ""
                    }
                
                self.root.after(0, lambda: self.model_dropdown.update_models(models_dict))
                if not self.current_model or self.current_model not in models:
                    self.root.after(0, lambda: self.model_dropdown.set_selected(models[0]))
                    self.current_model = models[0]
                    # Update model info panel for initial model
                    self.root.after(100, lambda: self.update_model_info_panel(models[0]))
                else:
                    # Update model info panel for current model
                    self.root.after(100, lambda: self.update_model_info_panel(self.current_model))
            else:
                self.root.after(0, lambda: self.model_dropdown.update_models({}))
                self.current_model = None
            
            # Verfügbare Modelle refresh
            all_models = self.ollama.get_all_ollama_models()
            if all_models:
                # Konvertiere zu Model-Info-Dict
                download_models_dict = {}
                for model_name in all_models:
                    size_info = ""
                    if ":" in model_name:
                        param_size = model_name.split(":")[-1]
                        if "b" in param_size.lower():
                            size_info = param_size.upper()
                    
                    download_models_dict[model_name] = {
                        "size": f"~{size_info.replace('B', ' Mrd Parameter')}" if size_info else "Available",
                        "type": "LLM",
                        "parameters": size_info
                    }
                
                self.root.after(0, lambda: self.available_dropdown.update_models(download_models_dict))
        
        threading.Thread(target=update, daemon=True).start()
    
    def on_model_select_new(self, choice):
        """Behandelt Model-Auswahl (neue Methode für ModelInfoDropdown)"""
        self.on_model_select(choice)
        self.update_model_info_panel(choice)
    
    def update_model_info_panel(self, model_name):
        """Aktualisiert das Model-Info-Panel mit Details zum ausgewählten Model"""
        if not model_name:
            self.model_info_text.configure(state="normal")
            self.model_info_text.delete("1.0", "end")
            self.model_info_text.insert("1.0", "Select a model\nto view details.")
            self.model_info_text.configure(state="disabled")
            return
        
        # Model-Informationen zusammenstellen
        def fetch_info():
            try:
                info_text = f"📦 Model: {model_name}\n\n"
                api_success = False
                
                # Versuche Infos über Ollama API zu bekommen
                try:
                    import ollama
                    result = ollama.show(model_name)
                    
                    if result and isinstance(result, dict):
                        api_success = True
                        
                        # Parameter Count aus details
                        if 'details' in result:
                            details = result['details']
                            
                            if 'parameter_size' in details:
                                param_size = details['parameter_size']
                                info_text += f"🔢 Parameters: {param_size}\n"
                            
                            if 'quantization_level' in details:
                                quant = details['quantization_level']
                                info_text += f"⚙️ Quantization: {quant}\n"
                            
                            if 'family' in details:
                                family = details['family']
                                info_text += f"👪 Family: {family.title()}\n"
                            
                            if 'format' in details:
                                format_info = details['format']
                                info_text += f"📄 Format: {format_info.upper()}\n"
                            
                            if 'families' in details:
                                families = details['families']
                                if families:
                                    info_text += f"🏷️ Tags: {', '.join(families[:3])}\n"
                        
                        # Size info
                        if 'size' in result:
                            size_mb = result['size'] / (1024 * 1024)
                            if size_mb >= 1024:
                                size_gb = size_mb / 1024
                                info_text += f"💾 Size: {size_gb:.2f} GB\n"
                            else:
                                info_text += f"💾 Size: {size_mb:.0f} MB\n"
                        
                        info_text += "\n"
                        
                        # Template info
                        if 'template' in result and result['template']:
                            info_text += "📝 Template: ✅ Configured\n"
                        
                        # Modified date
                        if 'modified_at' in result:
                            modified = result['modified_at'].split('T')[0] if 'T' in result['modified_at'] else result['modified_at']
                            info_text += f"🗓️ Last Modified:\n   {modified}\n\n"
                        
                        # Empfohlen für (basierend auf Familie und Tags)
                        recommendations = []
                        model_lower = model_name.lower()
                        
                        if 'code' in model_lower or 'coder' in model_lower:
                            recommendations.append("💻 Code Generation")
                            recommendations.append("🔧 Programming")
                        elif 'llava' in model_lower or 'vision' in model_lower:
                            recommendations.append("👁️ Image Analysis")
                            recommendations.append("🖼️ Vision Tasks")
                        elif 'math' in model_lower or 'wizard' in model_lower:
                            recommendations.append("🧮 Mathematics")
                            recommendations.append("📐 Calculations")
                        elif 'sql' in model_lower:
                            recommendations.append("🗄️ SQL Queries")
                            recommendations.append("📊 Database")
                        elif 'med' in model_lower or 'bio' in model_lower:
                            recommendations.append("🏥 Medicine")
                            recommendations.append("🧬 Biology")
                        else:
                            # Standard Chat-Modelle
                            if 'b' in model_lower:
                                param_num = ''.join(filter(str.isdigit, model_lower.split('b')[0].split(':')[-1]))
                                if param_num:
                                    param_val = int(param_num)
                                    if param_val <= 3:
                                        recommendations.append("💬 Quick Responses")
                                        recommendations.append("📱 Mobile Devices")
                                    elif param_val <= 8:
                                        recommendations.append("💬 Chat & Dialogue")
                                        recommendations.append("✍️ Text Creation")
                                    else:
                                        recommendations.append("🎯 Complex Tasks")
                                        recommendations.append("📚 Analysis & Research")
                        
                        if recommendations:
                            info_text += "✨ Recommended for:\n"
                            for rec in recommendations[:3]:  # Max 3 Empfehlungen
                                info_text += f"   {rec}\n"
                    
                except Exception as e:
                    print(f"Ollama API Error: {e}")
                    api_success = False
                
                # Fallback wenn ollama.show nicht funktioniert
                if not api_success:
                    info_text += "ℹ️ Type: LLM\n"
                    
                    # Parse Parameter aus Modellname
                    if ':' in model_name:
                        param_info = model_name.split(':')[-1]
                        if 'b' in param_info.lower():
                            param_clean = param_info.upper().replace('B', ' Billion')
                            info_text += f"🔢 Parameters: ~{param_clean}\n"
                    
                    # Model-Familie aus Namen ableiten
                    model_base = model_name.split(':')[0].lower()
                    if 'llama' in model_base:
                        info_text += "👪 Family: Llama\n"
                    elif 'mistral' in model_base:
                        info_text += "👪 Family: Mistral\n"
                    elif 'gemma' in model_base:
                        info_text += "👪 Family: Gemma\n"
                    elif 'phi' in model_base:
                        info_text += "👪 Family: Phi\n"
                    elif 'codellama' in model_base or 'code' in model_base:
                        info_text += "👪 Family: CodeLlama\n"
                    
                    info_text += "\n"
                    
                    # Empfehlungen auch im Fallback
                    recommendations = []
                    if 'code' in model_base:
                        recommendations = ["💻 Code Generation", "🔧 Programming"]
                    elif 'llava' in model_base:
                        recommendations = ["👁️ Image Analysis", "🖼️ Vision Tasks"]
                    elif 'math' in model_base:
                        recommendations = ["🧮 Mathematics", "📐 Calculations"]
                    else:
                        recommendations = ["💬 Chat & Dialogue", "✍️ Text Creation"]
                    
                    if recommendations:
                        info_text += "✨ Recommended for:\n"
                        for rec in recommendations[:3]:
                            info_text += f"   {rec}\n"
                
                # Update UI in main thread
                self.root.after(0, lambda: self._update_info_text(info_text))
                
            except Exception as e:
                error_text = f"📦 Model: {model_name}\n\n❌ Error beim Load der Details:\n{str(e)}"
                self.root.after(0, lambda: self._update_info_text(error_text))
        
        # Lade Infos in separatem Thread
        threading.Thread(target=fetch_info, daemon=True).start()
    
    def _update_info_text(self, text):
        """Hilfsmethode zum Refresh des Info-Textfelds (muss im Main-Thread laufen)"""
        self.model_info_text.configure(state="normal")
        self.model_info_text.delete("1.0", "end")
        self.model_info_text.insert("1.0", text)
        self.model_info_text.configure(state="disabled")
    
    def on_model_select(self, choice):
        """Behandelt Model-Auswahl"""
        if choice and choice != "Keine Modelle available":
            self.current_model = choice
            
            # WICHTIG: Nicht save während eine Session loaded is being
            if getattr(self, '_session_just_loaded', False):
                # Session is being gerade loaded, nicht save
                return
            
            # Reset chat history only for new/empty sessions
            # Keep history for existing sessions with messages
            if not hasattr(self, 'chat_bubbles') or len(self.chat_bubbles) == 0:
                self.chat_history = []  # Only reset for empty sessions
                self.console_print(f"🔄 New session - chat history reset", "info")
            else:
                self.console_print(f"📚 Existing session - chat history kept ({len(self.chat_history)} messages)", "info")
            
            # Save model in current session
            if hasattr(self, 'current_session_id') and self.current_session_id:
                if self.current_session_id in self.sessions:
                    self.sessions[self.current_session_id]["model"] = choice
                    self.sessions[self.current_session_id]["last_modified"] = datetime.now().isoformat()
                    
                    # Session persistent save
                    self.save_session_with_feedback()
                    
                    # UI vollständig refresh
                    self.update_current_session_display()
                    self.update_session_list()
            
            self.add_to_chat("System", f"Model switched to: {choice}")
            self.console_print(f"🤖 Model switched: {choice}", "info")
    
    def show_download_dialog(self):
        """Zeigt Dialog zum Model-Download"""
        dialog = ctk.CTkInputDialog(
            text="Geben You den Modellnamen ein (z.B. llama2, mistral, codellama):",
            title="Model herunterladen"
        )
        model_name = dialog.get_input()
        
        if model_name:
            self.download_model(model_name)
    
    def download_selected_model(self):
        """Lädt das ausgewählte Model aus dem Dropdown herunter"""
        selected_model = self.available_dropdown.get_selected()
        
        if not selected_model:
            messagebox.showwarning("Warning", "Please select a model to download!")
            return
        
        # Check ob das Model bereits installed ist
        installed_models = self.ollama.get_available_models()
        if selected_model in installed_models:
            result = messagebox.askyesno(
                "Model bereits vorhanden", 
                f"'{selected_model}' ist bereits installed. Trotzdem erneut herunterladen?"
            )
            if not result:
                return
        
        self.download_model(selected_model)
    
    def download_model(self, model_name):
        """Lädt ein Model mit verbessertem UI-Feedback und Stop-Funktionalität herunter"""
        self.progress_frame.pack(fill="x", padx=10, pady=5)
        self.add_to_chat("System", f"🚀 Download of {model_name} started...")
        self.add_to_chat("System", f"💡 Open console output for details!")
        
        # Reset Download Stop Flag
        self.download_stopped = False
        
        # Stop-Button aktivieren für Downloads
        self.stop_btn.configure(state="normal", text="Stop Download")
        self.send_btn.configure(state="disabled")
        
        # Initialisiere Progress Bar
        self.progress_bar.set(0)
        self.progress_label.configure(text="Starte Download...")
        
        def download():
            import time
            download_start = time.time()
            last_update = time.time()
            
            def progress_callback(status):
                nonlocal last_update
                current_time = time.time()
                
                # Stop-Check in Progress-Callback
                if self.download_stopped:
                    return
                
                # UI-Updates nur alle 0.2 Sekunden um Flooding zu vermeiden
                if current_time - last_update >= 0.2:
                    if 'total' in status and 'completed' in status:
                        progress = status['completed'] / status['total']
                        self.root.after(0, lambda p=progress: self.progress_bar.set(p))
                        
                        # Detaillierte Fortschrittsinformationen
                        completed_mb = status['completed'] / (1024 * 1024)
                        total_mb = status['total'] / (1024 * 1024)
                        percent = progress * 100
                        
                        # Geschwindigkeitsschätzung
                        elapsed = current_time - download_start
                        if elapsed > 0:
                            speed_mb = completed_mb / elapsed
                            eta_seconds = (total_mb - completed_mb) / speed_mb if speed_mb > 0 else 0
                            eta_text = f" | ETA: {eta_seconds/60:.1f}min" if eta_seconds > 0 else ""
                        else:
                            speed_mb = 0
                            eta_text = ""
                        
                        status_text = f"{percent:.1f}% ({completed_mb:.1f}/{total_mb:.1f}MB) | {speed_mb:.1f}MB/s{eta_text}"
                        self.root.after(0, lambda s=status_text: self.progress_label.configure(text=status_text))
                    else:
                        status_text = status.get('status', 'Downloading...')
                        self.root.after(0, lambda s=status_text: self.progress_label.configure(text=f"Status: {status_text}"))
                    
                    last_update = current_time
            
            # Übergebe die Referenz zu diesem Messenger für Stop-Checks
            success = self.ollama.download_model(model_name, progress_callback, parent_messenger=self)
            
            def finish():
                total_time = time.time() - download_start
                self.progress_frame.pack_forget()
                
                if self.download_stopped:
                    self.add_to_chat("System", f"🛑 Download von {model_name} stopped nach {total_time/60:.1f} Minuten")
                elif success:
                    self.add_to_chat("System", f"✅ {model_name} erfolgreich heruntergeladen! ({total_time/60:.1f} Minuten)")
                    self.refresh_models()
                else:
                    self.add_to_chat("System", f"❌ Error beim Download von {model_name} nach {total_time/60:.1f} Minuten")
                
                # UI zurücksetzen
                self.reset_download_ui()
            
            self.root.after(0, finish)
        
        # Download-Thread start und save
        self.current_download_thread = threading.Thread(target=download, daemon=True)
        self.current_download_thread.start()
    
    def delete_selected_model(self):
        """Löscht das ausgewählte Model"""
        if not self.current_model:
            messagebox.showwarning("Warning", "No model selected!")
            return
        
        result = messagebox.askyesno(
            "Model delete", 
            f"Möchten You '{self.current_model}' wirklich delete?"
        )
        
        if result:
            def delete():
                success = self.ollama.delete_model(self.current_model)
                def finish():
                    if success:
                        self.add_to_chat("System", f"✅ {self.current_model} wurde deleted")
                        self.current_model = None
                        self.refresh_models()
                    else:
                        self.add_to_chat("System", f"❌ Error beim Delete von {self.current_model}")
                
                self.root.after(0, finish)
            
            threading.Thread(target=delete, daemon=True).start()
    
    def send_message(self, event=None):
        """Sendet eine Message mit Stop-Funktionalität und Anti-Redundanz"""
        import time
        
        message = self.message_entry.get().strip()
        if not message:
            return
        
        if not self.current_model:
            messagebox.showwarning("Warning", "No model selected!")
            return
        
        # Reset Stop-Flag
        self.generation_stopped = False
        
        # Message zur Historie hinzufügen (nur wenn nicht leer)
        if message and message not in self.message_history:
            self.message_history.append(message)
        # Reset Historie-Index
        self.history_index = -1
        

        # Prüfe, ob die Session vorher leer war (keine Messages)
        session_empty = False
        if self.current_session_id and self.current_session_id in self.sessions:
            session_data = self.sessions[self.current_session_id]
            if not session_data.get("messages"):
                session_empty = True

        # Message show
        self.add_to_chat("You", message)
        self.message_entry.delete(0, 'end')

        # Wenn Session vorher leer war: Session-List, Anzeige und Chat-Konsole sofort refresh
        if session_empty:
            self.update_session_list()
            self.update_current_session_display()
            # Scrolle ans Ende der Chat-Konsole (falls vorhanden)
            if self.config.get("auto_scroll_chat", True):
                if hasattr(self, 'chat_display_frame') and hasattr(self.chat_display_frame, '_parent_canvas'):
                    self.chat_display_frame._parent_canvas.yview_moveto(1.0)
        
        # UI während Generation anpassen
        self.stop_btn.configure(state="normal")
        self.send_btn.configure(state="disabled", text="⏳ Generiert...")
        
        # Eingabefeld visuell anpassen (leicht transparent)
        if hasattr(self, 'message_entry'):
            self.message_entry.configure(state="disabled")
        
        # Antwort abrufen
        def get_response():
            try:
                # Denkprozess-Indikator hinzufügen
                self.root.after(0, self.add_thinking_indicator)
                
                # Session-BIAS berücksichtigen
                session_bias = ""
                if hasattr(self, 'current_session_bias') and self.current_session_bias:
                    session_bias = self.current_session_bias.strip()
                    print(f"🎯 BIAS active: {session_bias[:50]}...")
                    self.root.after(0, lambda: self.console_print(f"🎯 BIAS sent: {session_bias[:30]}...", "info"))
                else:
                    print("🎯 No BIAS set")
                
                # Nur bei Session-Load: volle History, sonst nur BIAS und aktuelle User-Input
                if getattr(self, '_session_just_loaded', False):
                    print("[INFO] Complete session history is being sent to the model (session was just loaded).")
                    modified_history = self.chat_history.copy()
                    if session_bias:
                        modified_history.insert(0, {"role": "system", "content": session_bias})
                    self._session_just_loaded = False
                else:
                    # Nur BIAS (falls gesetzt) und aktuelle User-Input
                    modified_history = []
                    if session_bias:
                        modified_history.append({"role": "system", "content": session_bias})
                # Letzte Model-Input für Debug-Zwecke save
                try:
                    history_copy = copy.deepcopy(modified_history)
                except Exception:
                    history_copy = modified_history.copy()

                response_stream = self.ollama.chat_with_model(
                    self.current_model, 
                    message, 
                    modified_history
                )
                
                if response_stream:
                    full_response = ""
                    
                    # Sammle alle Tokens
                    for chunk in response_stream:
                        # Stop-Check
                        if self.generation_stopped:
                            self.root.after(0, lambda: self.add_to_chat("System", "🛑 Generation stopped"))
                            break
                            
                        if 'message' in chunk:
                            content = chunk['message'].get('content', '')
                            if content:
                                full_response += content
                    
                    # Am Ende: Entferne "Denkt..." und zeige vollständige Antwort
                    if full_response and not self.generation_stopped:
                        def show_final_response():
                            self.remove_last_message()
                            formatted_content = self.format_ai_response(full_response)
                            self.add_to_chat(f"🤖 {self.current_model}", formatted_content)
                            
                            # WICHTIG: Session SOFORT save nach AI-Antwort
                            # Nicht waiting auf auto_save_timer (200ms), sondern direkt save
                            if self.current_session_id and self.current_session_id in self.sessions:
                                if self.save_current_session():
                                    self.console_print(f"💾 Session saved", "success")
                        
                        self.root.after(0, show_final_response)
                        
                        # Chat-Historie refresh (ohne BIAS für permanente Historie)
                        self.chat_history.append({"role": "user", "content": message})
                        self.chat_history.append({"role": "assistant", "content": full_response})
                    else:
                        print(f"⚠️ Empty response: {len(full_response)} characters")
                else:
                    print("❌ No response stream received")
                    
            except Exception as e:
                if not self.generation_stopped:
                    self.root.after(0, lambda: self.add_to_chat("System", f"❌ Error: {str(e)}"))
            finally:
                # UI zurücksetzen
                self.root.after(0, self.reset_generation_ui)
        
        # Thread start und save
        self.current_generation_thread = threading.Thread(target=get_response, daemon=True)
        self.current_generation_thread.start()
    
    def send_message_programmatic(self, message):
        """Sendet eine Message programmatisch (z.B. aus Textbox statt Entry)"""
        if not message or not message.strip():
            return
        
        message = message.strip()
        
        if not self.current_model:
            messagebox.showwarning("Warning", "No model selected!")
            return
        
        # Reset Stop-Flag
        self.generation_stopped = False
        
        # Message zur Historie hinzufügen
        if message and message not in self.message_history:
            self.message_history.append(message)
        self.history_index = -1
        
        # Prüfe, ob Session leer war
        session_empty = False
        if self.current_session_id and self.current_session_id in self.sessions:
            session_data = self.sessions[self.current_session_id]
            if not session_data.get("messages"):
                session_empty = True
        
        # Message show
        self.add_to_chat("You", message)
        
        # Session-List refresh wenn vorher leer
        if session_empty:
            self.update_session_list()
            self.update_current_session_display()
            if self.config.get("auto_scroll_chat", True):
                if hasattr(self, 'chat_display_frame') and hasattr(self.chat_display_frame, '_parent_canvas'):
                    self.chat_display_frame._parent_canvas.yview_moveto(1.0)
        
        # UI während Generation anpassen
        if hasattr(self, 'stop_btn'):
            self.stop_btn.configure(state="normal")
        if hasattr(self, 'send_btn'):
            self.send_btn.configure(state="disabled", text="⏳ Generiert...")
        if hasattr(self, 'message_entry'):
            self.message_entry.configure(state="disabled")
        
        # Antwort abrufen
        def get_response():
            try:
                self.root.after(0, self.add_thinking_indicator)
                
                # Session-BIAS berücksichtigen
                session_bias = ""
                if hasattr(self, 'current_session_bias') and self.current_session_bias:
                    session_bias = self.current_session_bias.strip()
                
                # Chat-Historie mit BIAS vorbereiten
                modified_history = self.chat_history.copy()
                if session_bias:
                    modified_history = [
                        {"role": "system", "content": session_bias}
                    ] + modified_history
                
                # Message zur Chat-History hinzufügen
                self.chat_history.append({"role": "user", "content": message})
                modified_history.append({"role": "user", "content": message})
                
                # Ollama API aufrufen mit Streaming
                response_text = ""
                self.current_response_text = ""
                self.response_message_widget = None
                
                for chunk in self.ollama.chat_stream(self.current_model, modified_history):
                    if self.generation_stopped:
                        break
                    response_text += chunk
                    self.root.after(0, lambda c=chunk: self.update_progressive_response(c))
                
                # Finale Antwort zur History hinzufügen
                if not self.generation_stopped and response_text:
                    self.chat_history.append({"role": "assistant", "content": response_text})
                    self.root.after(0, self.save_current_session)
                    
            except Exception as e:
                if not self.generation_stopped:
                    self.root.after(0, lambda: self.add_to_chat("System", f"❌ Error: {str(e)}"))
            finally:
                self.root.after(0, self.reset_generation_ui)
        
        # Thread start
        self.current_generation_thread = threading.Thread(target=get_response, daemon=True)
        self.current_generation_thread.start()
    
    def download_model_by_name(self, model_name):
        """Lädt ein Model nach Namen herunter"""
        if not model_name or not model_name.strip():
            messagebox.showwarning("Warning", "Please enter a model name!")
            return
        
        model_name = model_name.strip()
        
        # Prüfe ob Model bereits existiert
        existing_models = self.ollama.list_models()
        if model_name in existing_models:
            messagebox.showinfo("Info", f"Model '{model_name}' ist bereits installed!")
            return
        
        # Reset Download-Stop-Flag
        self.download_stopped = False
        
        def download():
            try:
                self.console_print(f"📥 Download started: {model_name}", "info")
                
                # Download mit Progress
                for progress in self.ollama.download_model_stream(model_name):
                    if self.download_stopped:
                        self.console_print(f"⏹️ Download canceled: {model_name}", "warning")
                        break
                    
                    # Progress show
                    if "status" in progress:
                        status = progress["status"]
                        if "total" in progress and "completed" in progress:
                            total = float(progress["total"]) if progress["total"] else 1
                            completed = float(progress["completed"]) if progress["completed"] else 0
                            percent = (completed / total) * 100
                            self.console_print(f"📥 {status}: {percent:.1f}%", "info")
                        else:
                            self.console_print(f"📥 {status}", "info")
                
                if not self.download_stopped:
                    self.console_print(f"✅ Download abgeschlossen: {model_name}", "success")
                    # Model-List refresh
                    self.root.after(0, self.refresh_models)
                    
            except Exception as e:
                self.console_print(f"❌ Download-Error: {str(e)}", "error")
        
        # Thread start
        self.current_download_thread = threading.Thread(target=download, daemon=True)
        self.current_download_thread.start()
    
    def export_session_markdown(self):
        """Exportiert die aktuelle Session als Markdown-File"""
        if not self.current_session_id:
            messagebox.showwarning("Warning", "No active session to export!")
            return
        
        # Session-Daten holen
        session = self.sessions.get(self.current_session_id)
        if not session:
            return
        
        # Dateiname vorschlagen
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"session_{self.current_session_id}_{timestamp}.md"
        
        # File-Dialog
        filepath = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown", "*.md"), ("Alle Dateien", "*.*")],
            initialfile=default_name
        )
        
        if not filepath:
            return
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # Header
                f.write(f"# Chat Session: {self.current_session_id}\n\n")
                f.write(f"**Model:** {session.get('model', 'Unknown')}\n\n")
                f.write(f"**Created:** {session.get('created_at', 'Unknown')}\n\n")
                
                # BIAS wenn vorhanden
                if session.get('bias'):
                    f.write(f"**BIAS/Context:**\n```\n{session['bias']}\n```\n\n")
                
                f.write("---\n\n")
                
                # Messages
                for msg in session.get('messages', []):
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')
                    
                    if role == 'user':
                        f.write(f"## 👤 You\n\n{content}\n\n")
                    elif role == 'assistant':
                        f.write(f"## 🤖 AI ({session.get('model', 'Unknown')})\n\n{content}\n\n")
                    elif role == 'system':
                        f.write(f"## ⚙️ System\n\n{content}\n\n")
                    
                    f.write("---\n\n")
            
            messagebox.showinfo("Success", f"Session exported to:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Export failed:\n{str(e)}")
    
    def export_session_json(self):
        """Exportiert die aktuelle Session als JSON-File"""
        if not self.current_session_id:
            messagebox.showwarning("Warning", "No active session to export!")
            return
        
        # Session-Daten holen
        session = self.sessions.get(self.current_session_id)
        if not session:
            return
        
        # Dateiname vorschlagen
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"session_{self.current_session_id}_{timestamp}.json"
        
        # File-Dialog
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON", "*.json"), ("Alle Dateien", "*.*")],
            initialfile=default_name
        )
        
        if not filepath:
            return
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Success", f"Session exported to:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Export failed:\n{str(e)}")
    
    def navigate_history_up(self, event=None):
        """Navigiert in der Messages-Historie nach oben (ältere Messages)"""
        if not self.message_history:
            return "break"  # Verhindert Standard-Verhalten
        
        # Wenn wir am Ende der Historie sind, gehe zum neuesten Eintrag
        if self.history_index <= 0:
            self.history_index = len(self.message_history) - 1
        else:
            self.history_index -= 1
        
        # Setze die Message ins Eingabefeld
        message = self.message_history[self.history_index]
        self.message_entry.delete(0, 'end')
        self.message_entry.insert(0, message)
        
        return "break"  # Verhindert Standard-Verhalten der Pfeiltaste
    
    def navigate_history_down(self, event=None):
        """Navigiert in der Messages-Historie nach unten (neuere Messages)"""
        if not self.message_history:
            return "break"
        
        # Wenn wir am Anfang der Historie sind oder keine Auswahl haben
        if self.history_index < 0 or self.history_index >= len(self.message_history) - 1:
            # Lösche das Eingabefeld (neueste "Message" ist leeres Feld)
            self.message_entry.delete(0, 'end')
            self.history_index = -1
        else:
            self.history_index += 1
            # Setze die Message ins Eingabefeld
            message = self.message_history[self.history_index]
            self.message_entry.delete(0, 'end')
            self.message_entry.insert(0, message)
        
        return "break"  # Verhindert Standard-Verhalten der Pfeiltaste
    
    def on_key_press(self, event=None):
        """Is being bei jeder Tasteneingabe aufgerufen - reset Historie-Index wenn getippt is being"""
        # Reset Historie-Index wenn der Benutzer tippt (außer bei Pfeiltasten)
        if event and event.keysym not in ['Up', 'Down']:
            self.history_index = -1
        return None  # Normale Tastatureingabe continue
    
    def stop_generation(self):
        """Stoppt die aktuelle Generation oder den Download sofort"""
        if self.current_generation_thread is not None:
            # Stop chat generation
            self.generation_stopped = True
            self.reset_generation_ui()
            print("\n🛑 Generation stopped by user")
        
        if self.current_download_thread is not None:
            # Stop download
            self.download_stopped = True
            self.reset_download_ui()
            print("\n🛑 Download stopped by user")
    
    def reset_generation_ui(self):
        """Setzt die UI nach Generation back"""
        self.stop_btn.configure(state="disabled", text="Stop")
        self.send_btn.configure(state="normal", text="Send")
        
        # Eingabefeld wieder aktivieren
        if hasattr(self, 'message_entry'):
            self.message_entry.configure(state="normal")
        
        self.current_generation_thread = None
    
    def reset_download_ui(self):
        """Setzt die UI nach Download back"""
        self.stop_btn.configure(state="disabled", text="Stop")
        self.send_btn.configure(state="normal", text="Send")
        
        # Eingabefeld wieder aktivieren
        if hasattr(self, 'message_entry'):
            self.message_entry.configure(state="normal")
        
        self.current_download_thread = None
    
    def format_ai_response(self, content):
        """Formatiert AI-Antworten für bessere Lesbarkeit"""
        if not content.strip():
            return content
        
        # Teile in Paragraphen
        paragraphs = content.split('\n\n')
        formatted_paragraphs = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # Erkenne Listen (nummeriert oder mit Bulletpoints)
            lines = paragraph.split('\n')
            if len(lines) > 1:
                # Prüfe ob es eine List ist
                is_numbered_list = any(line.strip() and line.strip()[0].isdigit() and '.' in line[:5] for line in lines)
                is_bullet_list = any(line.strip().startswith(('-', '*', '•')) for line in lines)
                
                if is_numbered_list or is_bullet_list:
                    # Formatiere als Code-Block für bessere Lesbarkeit
                    list_content = '\n'.join(f"    {line.strip()}" for line in lines if line.strip())
                    formatted_paragraphs.append(f"```\n{list_content}\n```")
                else:
                    # Normaler Paragraph
                    formatted_paragraphs.append(paragraph)
            else:
                # Einzelne Zeile
                formatted_paragraphs.append(paragraph)
        
        return '\n\n'.join(formatted_paragraphs)
    
    def count_chat_messages(self):
        """Zählt nur echte Chat-Messages (User + AI, keine System-Messages)"""
        return len([bubble for bubble in self.chat_bubbles if bubble.sender != "System"])
    
    def add_to_chat(self, sender, message):
        """Fügt eine Chat-Bubble zum Chat hinzu"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # System-Messages ausblenden wenn Flag gesetzt ist
        if sender == "System" and not self.config.get("show_system_messages", True):
            # System-Message is being trotzdem in der Session saved für spätere Verwendung
            if self.current_session_id and self.current_session_id in self.sessions:
                msg_data = {
                    "timestamp": timestamp,
                    "sender": sender,
                    "message": message
                }
                self.sessions[self.current_session_id]["messages"].append(msg_data)
                self.sessions[self.current_session_id]["last_modified"] = datetime.now().isoformat()
                self.auto_save_session()
            return None  # Keine UI-Bubble create
        
        # Erstelle automatic eine Session falls keine active ist
        if not self.current_session_id or self.current_session_id not in self.sessions:
            self.console_print("🔄 Keine aktive Session gefunden, erstelle neue Session", "info")
            self.create_new_session()
        
        # Prüfe nochmals ob Session existiert (Sicherheitscheck)
        if not self.current_session_id or self.current_session_id not in self.sessions:
            self.console_print("❌ Error: Konnte keine Session create!", "error")
            return
        
        # Prüfe ob die letzte Bubble eine System-Message ist und diese erweitert werden kann
        if (sender == "System" and 
            self.chat_bubbles and 
            self.chat_bubbles[-1].sender == "System"):
            
            # Erweitere die letzte System-Bubble
            last_bubble = self.chat_bubbles[-1]
            current_message = last_bubble.message_label.get("1.0", "end-1c")
            new_combined_message = current_message + "\n" + message
            
            # Aktualisiere die Bubble
            last_bubble.message_label.delete("1.0", "end")
            last_bubble.message_label.insert("1.0", new_combined_message)
            
            # Aktualisiere auch die Session-Daten
            if (self.current_session_id and 
                self.current_session_id in self.sessions and 
                self.sessions[self.current_session_id]["messages"]):
                
                last_msg = self.sessions[self.current_session_id]["messages"][-1]
                if last_msg["sender"] == "System":
                    last_msg["message"] = new_combined_message
                    last_msg["timestamp"] = timestamp  # Aktualisiere Timestamp
                    
            # Scrolle nach unten
            if self.config.get("auto_scroll_chat", True):
                self.chat_display_frame._parent_canvas.after(100, 
                    lambda: self.chat_display_frame._parent_canvas.yview_moveto(1.0))
            
            # Auto-Save für aktualisierte Message
            self.auto_save_session()
            
            return last_bubble
        
        # Erstelle neue Chat-Bubble mit aktueller Config (normale Logik)
        bubble = ChatBubble(
            self.chat_display_frame,
            sender=sender,
            message=message,
            timestamp=timestamp,
            app_config=self.config
        )
        
        # Füge Bubble zur List hinzu
        self.chat_bubbles.append(bubble)
        
        # Füge Message zur aktuellen Session hinzu
        if self.current_session_id and self.current_session_id in self.sessions:
            msg_data = {
                "timestamp": timestamp,
                "sender": sender,
                "message": message
            }
            self.sessions[self.current_session_id]["messages"].append(msg_data)
            self.sessions[self.current_session_id]["total_messages"] = self.count_chat_messages()
            self.sessions[self.current_session_id]["last_modified"] = datetime.now().isoformat()
            
            # ✅ Automatisches Save nach jeder Message
            self.auto_save_session()
        
        # Scrolle nach unten
        if self.config.get("auto_scroll_chat", True):
            self.chat_display_frame._parent_canvas.after(100, 
                lambda: self.chat_display_frame._parent_canvas.yview_moveto(1.0))
        
        return bubble
    
    def scroll_to_last_message(self):
        """Scrollt zur letzten Message in der Chat-Ansicht"""
        try:
            if self.config.get("auto_scroll_chat", True):
                if hasattr(self, 'chat_display_frame') and hasattr(self.chat_display_frame, '_parent_canvas'):
                    # Zuerst das Layout vollständig refresh
                    self.chat_display_frame.update_idletasks()
                    self.chat_display_frame._parent_canvas.update_idletasks()
                    
                    # Then scroll to last message
                    self.chat_display_frame._parent_canvas.yview_moveto(1.0)
                    
                    # After short delay scroll again for better reliability
                    self.root.after(50, lambda: self.force_scroll_to_bottom())
                    
                    self.console_print("📜 Scrolled to last message", "info")
        except Exception as e:
            self.console_print(f"❌ Error scrolling to last message: {e}", "error")
    
    def force_scroll_to_bottom(self):
        """Erzwingt das Scrollen zum Ende der Chat-Ansicht"""
        try:
            if self.config.get("auto_scroll_chat", True):
                if hasattr(self, 'chat_display_frame') and hasattr(self.chat_display_frame, '_parent_canvas'):
                    # Vollständige Layout-Aktualisierung
                    self.chat_display_frame.update()
                    self.chat_display_frame._parent_canvas.update()
                    
                    # Zum Ende scrollen
                    self.chat_display_frame._parent_canvas.yview_moveto(1.0)
                    
                    # Canvas-Größe new berechnen
                    self.chat_display_frame._parent_canvas.configure(scrollregion=self.chat_display_frame._parent_canvas.bbox("all"))
                    
                    # Nochmals zum Ende
                    self.chat_display_frame._parent_canvas.yview_moveto(1.0)
                
        except Exception as e:
            self.console_print(f"❌ Error beim erzwungenen Scrollen: {e}", "error")
    
    def add_thinking_indicator(self):
        """Zeigt dezenten Denkprozess-Indikator an"""
        thinking_message = "💭 Verarbeitet Ihre Anfrage..."
        bubble = self.add_to_chat(f"🤖 {self.current_model}", thinking_message)
        self.current_thinking_bubble = bubble
        return bubble
    
    def update_progressive_response(self, chunk):
        """Aktualisiert die progressive Antwort mit neuem Chunk"""
        if not hasattr(self, 'current_response_text'):
            self.current_response_text = ""
        
        self.current_response_text += chunk
        
        # Wenn noch kein Response-Widget existiert, erstelle eines
        if not hasattr(self, 'response_message_widget') or self.response_message_widget is None:
            # Entferne Thinking-Indikator wenn vorhanden
            if hasattr(self, 'current_thinking_bubble') and self.current_thinking_bubble:
                self.remove_last_message()
            
            # Erstelle neues Widget für die Antwort
            self.response_message_widget = self.add_to_chat(
                f"🤖 {self.current_model}", 
                self.current_response_text
            )
        else:
            # Aktualisiere bestehendes Widget
            try:
                # Finde das Text-Label im Widget und aktualisiere es
                for child in self.response_message_widget.winfo_children():
                    if isinstance(child, ctk.CTkLabel):
                        child.configure(text=self.current_response_text)
                        break
            except:
                pass
    
    def remove_last_message(self):
        """Entfernt die letzte Message (Thinking-Indikator)"""
        # Stoppe die ASCII-Animation
        self._thinking_animation_running = False
        if hasattr(self, 'current_thinking_bubble') and self.current_thinking_bubble:
            try:
                self.current_thinking_bubble.destroy()
                if self.current_thinking_bubble in self.chat_bubbles:
                    self.chat_bubbles.remove(self.current_thinking_bubble)
                
                # WICHTIG: Entferne auch aus der Session-Daten
                if self.current_session_id and self.current_session_id in self.sessions:
                    messages = self.sessions[self.current_session_id].get("messages", [])
                    # Entferne die letzte Message wenn sie der Thinking-Indikator ist
                    if messages and "Verarbeitet Ihre Anfrage" in messages[-1].get("message", ""):
                        messages.pop()
                        self.sessions[self.current_session_id]["last_modified"] = datetime.now().isoformat()
            except:
                pass
            self.current_thinking_bubble = None

    def export_session(self):
        """Exportiert die aktuelle Chat-Session"""
        if not self.chat_bubbles:
            messagebox.showinfo("Export", "No chat session available to export!")
            return
        
        # Hauptdialog für Formatauswahl
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Session Export - Format auswählen")
        dialog.geometry("900x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Zentriere das Dialog-Fenster
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (900 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f"900x600+{x}+{y}")
        
        # Hauptcontainer
        main_frame = ctk.CTkFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titel
        title_label = ctk.CTkLabel(main_frame, text="📄 Select Export Format", 
                                  font=("Arial", 20, "bold"))
        title_label.pack(pady=(10, 20))
        
        # Container für Format-Auswahl (Links/Rechts Layout)
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Linke Seite - Format-Buttons
        left_frame = ctk.CTkFrame(content_frame)
        left_frame.pack(side="left", fill="y", padx=(10, 5), pady=10)
        
        ctk.CTkLabel(left_frame, text="Available Formats:", 
                    font=("Arial", 14, "bold")).pack(pady=(10, 15))
        
        # Variable für Formatauswahl
        self.selected_format = None
        
        def show_markdown_preview():
            self.selected_format = "markdown"
            self.update_preview(preview_frame, "markdown")
            # Highlight aktiven Button
            markdown_btn.configure(fg_color="#1f538d", hover_color="#2966a3")
            json_btn.configure(fg_color="#4a4a4a", hover_color="#5a5a5a")
        
        def show_json_preview():
            self.selected_format = "json"
            self.update_preview(preview_frame, "json")
            # Highlight active button  
            json_btn.configure(fg_color="#1f538d", hover_color="#2966a3")
            markdown_btn.configure(fg_color="#4a4a4a", hover_color="#5a5a5a")
        
        # Format buttons
        markdown_btn = ctk.CTkButton(left_frame, 
                                   text="📄 Markdown (.md)\n\n🧑‍💼 Human-friendly\n📋 Formatted & readable\n📚 For documentation",
                                   command=show_markdown_preview,
                                   width=220, height=90,
                                   font=("Arial", 11),
                                   anchor="center")
        markdown_btn.pack(pady=10)
        
        json_btn = ctk.CTkButton(left_frame,
                               text="📊 JSON (.json)\n\n🤖 Machine-readable\n⚙️ Structured data\n🔗 For APIs & Tools", 
                               command=show_json_preview,
                               width=220, height=90,
                               font=("Arial", 11),
                               anchor="center")
        json_btn.pack(pady=10)
        
        # Rechte Seite - Vorschau
        right_frame = ctk.CTkFrame(content_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)
        
        ctk.CTkLabel(right_frame, text="Format Preview:", 
                    font=("Arial", 14, "bold")).pack(pady=(10, 10))
        
        # Vorschau-Frame
        preview_frame = ctk.CTkFrame(right_frame)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Standard: Markdown-Vorschau show
        show_markdown_preview()
        
        # Action-Buttons unten
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=(10, 10))
        
        def export_selected():
            if self.selected_format == "markdown":
                dialog.destroy()
                self.export_to_markdown()
            elif self.selected_format == "json":
                dialog.destroy()
                self.export_to_json()
        
        export_btn = ctk.CTkButton(button_frame, text="📤 Export", 
                                 command=export_selected, 
                                 width=120, height=35,
                                 font=("Arial", 12, "bold"))
        export_btn.pack(side="right", padx=(10, 20), pady=10)
        
        cancel_btn = ctk.CTkButton(button_frame, text="❌ Cancel", 
                                 command=dialog.destroy,
                                 width=100, height=35,
                                 fg_color="#666666", hover_color="#555555")
        cancel_btn.pack(side="right", padx=5, pady=10)

    def update_preview(self, preview_frame, format_type):
        """Aktualisiert die Vorschau basierend auf dem gewählten Format"""
        # Alle Widgets im Vorschau-Frame delete
        for widget in preview_frame.winfo_children():
            widget.destroy()
        
        if format_type == "markdown":
            self.show_markdown_preview(preview_frame)
        elif format_type == "json":
            self.show_json_preview(preview_frame)

    def show_markdown_preview(self, parent):
        """Zeigt eine Markdown-Vorschau"""
        # Header mit Info
        header_frame = ctk.CTkFrame(parent)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(header_frame, text="📄 Markdown Format", 
                    font=("Arial", 14, "bold")).pack(side="left", padx=10, pady=5)
        
        info_label = ctk.CTkLabel(header_frame, 
                                text="✅ Human-friendly  ✅ GitHub-compatible  ✅ Clear",
                                font=("Arial", 10),
                                text_color="#00AA00")
        info_label.pack(side="right", padx=10, pady=5)
        
        # Beispiel-Content
        markdown_example = """# A1-Terminal Chat Session

**Session-ID:** `20251107_143025`
**Exportiert am:** 07.11.2025 um 14:30:25
**Model:** llama3.1:8b  
**Anzahl Messages:** 4
**Session-Start:** 14:25:12
**Session-Ende:** 14:26:05

---

**[14:25:12]**

### 👤 Benutzer

Erkläre mir Machine Learning in einfachen Worten

**[14:25:15]**

### 🤖 llama3.1:8b

Machine Learning ist eine Methode der künstlichen 
Intelligenz, bei der Computer lernen, Muster in 
Daten zu erkennen und Vorhersagen zu treffen.

**Hauptkonzepte:**
- **Training:** Computer lernt aus Beispieldaten
- **Modelle:** Mathematische Algorithmen  
- **Vorhersagen:** System macht Prognosen

---

**[14:26:01]**

### 👤 Benutzer

Kannst du ein einfaches Beispiel geben?

---

*Session-ID: 20251107_143025*
*Generiert von A1-Terminal LLM Chat Client*"""

        # Scrollbarer Text
        text_frame = ctk.CTkScrollableFrame(parent)
        text_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Beispiel-Text in einem Textfeld
        text_widget = ctk.CTkTextbox(text_frame, height=350, font=("Consolas", 9))
        text_widget.pack(fill="both", expand=True)
        text_widget.insert("1.0", markdown_example)
        text_widget.configure(state="disabled")

    def show_json_preview(self, parent):
        """Zeigt eine JSON-Vorschau"""
        # Header mit Info
        header_frame = ctk.CTkFrame(parent)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        ctk.CTkLabel(header_frame, text="📊 JSON Format", 
                    font=("Arial", 14, "bold")).pack(side="left", padx=10, pady=5)
        
        info_label = ctk.CTkLabel(header_frame,
                                text="✅ Strukturiert  ✅ API-kompatibel  ✅ Maschinenlesbar",
                                font=("Arial", 10),
                                text_color="#00AA00")
        info_label.pack(side="right", padx=10, pady=5)
        
        # Beispiel-Content
        json_example = """{
  "session_info": {
    "session_id": "20251107_143025",
    "export_timestamp": "2025-11-07T14:30:25.123456",
    "session_start": "14:25:12",
    "session_end": "14:26:05",
    "model": "llama3.1:8b",
    "total_messages": 4
  },
  "messages": [
    {
      "timestamp": "14:25:12",
      "role": "user", 
      "sender": "Benutzer",
      "content": "Erkläre mir Machine Learning in einfachen Worten"
    },
    {
      "timestamp": "14:25:15",
      "role": "assistant",
      "sender": "llama3.1:8b", 
      "content": "Machine Learning ist eine Methode der künstlichen Intelligenz..."
    },
    {
      "timestamp": "14:26:01", 
      "role": "user",
      "sender": "Benutzer",
      "content": "Kannst du ein einfaches Beispiel geben?"
    },
    {
      "timestamp": "14:26:05",
      "role": "assistant", 
      "sender": "llama3.1:8b",
      "content": "Stellen You sich vor, You bringen einem Kind bei..."
    }
  ]
}"""

        # Scrollbarer Text
        text_frame = ctk.CTkScrollableFrame(parent)
        text_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Beispiel-Text in einem Textfeld
        text_widget = ctk.CTkTextbox(text_frame, height=350, font=("Consolas", 9))
        text_widget.pack(fill="both", expand=True)
        text_widget.insert("1.0", json_example)
        text_widget.configure(state="disabled")

    def export_to_markdown(self):
        """Exportiert die Chat-Session als Markdown-File"""
        try:
            # Session-ID mit Datum und Zeitstempel create
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Sessions-Folder create falls nicht vorhanden
            sessions_dir = os.path.join(os.getcwd(), "sessions")
            if not os.path.exists(sessions_dir):
                os.makedirs(sessions_dir)
            
            # Standard-Dateiname mit Session-ID
            default_filename = f"session_{session_id}.md"
            default_path = os.path.join(sessions_dir, default_filename)
            
            # File-Dialog mit Sessions-Folder als Standard
            file_path = filedialog.asksaveasfilename(
                defaultextension=".md",
                filetypes=[("Markdown files", "*.md"), ("All files", "*.*")],
                initialfile=default_filename,
                initialdir=sessions_dir,
                title="Chat-Session als Markdown exportieren"
            )
            
            if file_path:
                # Session-ID aus dem gewählten Dateipfad extrahieren
                filename = os.path.basename(file_path)
                if filename.startswith("session_") and filename.endswith(".md"):
                    session_id = filename[8:-3]  # Entferne "session_" und ".md"
                
                content = self._generate_markdown_content(session_id)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                messagebox.showinfo("Export successful", 
                                  f"Chat-Session wurde erfolgreich exportiert:\n{file_path}\n\nSession-ID: {session_id}")
        except Exception as e:
            messagebox.showerror("Export-Error", f"Error beim Exportieren: {str(e)}")

    def export_to_json(self):
        """Exportiert die Chat-Session als JSON-File"""
        try:
            # Session-ID mit Datum und Zeitstempel create
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Sessions-Folder create falls nicht vorhanden
            sessions_dir = os.path.join(os.getcwd(), "sessions")
            if not os.path.exists(sessions_dir):
                os.makedirs(sessions_dir)
            
            # Standard-Dateiname mit Session-ID
            default_filename = f"session_{session_id}.json"
            
            # File-Dialog mit Sessions-Folder als Standard
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                initialfile=default_filename,
                initialdir=sessions_dir,
                title="Chat-Session als JSON exportieren"
            )
            
            if file_path:
                # Session-ID aus dem gewählten Dateipfad extrahieren
                filename = os.path.basename(file_path)
                if filename.startswith("session_") and filename.endswith(".json"):
                    session_id = filename[8:-5]  # Entferne "session_" und ".json"
                
                # Sammle Chat-Daten
                chat_data = {
                    "session_info": {
                        "session_id": session_id,
                        "export_timestamp": datetime.now().isoformat(),
                        "session_start": self.chat_bubbles[0].timestamp if self.chat_bubbles else None,
                        "session_end": self.chat_bubbles[-1].timestamp if self.chat_bubbles else None,
                        "model": getattr(self, 'current_model', 'Unbekannt'),
                        "total_messages": self.count_chat_messages()
                    },
                    "messages": []
                }
                
                for bubble in self.chat_bubbles:
                    # Bereinige den Sender-Text (entferne Emojis)
                    sender = bubble.sender
                    if sender.startswith("👤"):
                        role = "user"
                        clean_sender = sender.replace("👤 ", "").strip()
                    elif sender.startswith("🤖"):
                        role = "assistant"  
                        clean_sender = sender.replace("🤖 ", "").strip()
                    else:
                        role = "system"
                        clean_sender = sender
                    
                    message_data = {
                        "timestamp": bubble.timestamp,
                        "role": role,
                        "sender": clean_sender,
                        "content": bubble.message
                    }
                    
                    chat_data["messages"].append(message_data)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(chat_data, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("Export successful", 
                                  f"Chat-Session wurde erfolgreich exportiert:\n{file_path}\n\nSession-ID: {session_id}")
        except Exception as e:
            messagebox.showerror("Export-Error", f"Error beim Exportieren: {str(e)}")

    def _generate_markdown_content(self, session_id=None):
        """Generiert Markdown-Content für den Export"""
        lines = []
        
        # Session-ID falls nicht übergeben
        if session_id is None:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Header mit Session-ID
        lines.append("# A1-Terminal Chat Session")
        lines.append("")
        lines.append(f"**Session-ID:** `{session_id}`")
        lines.append(f"**Exportiert am:** {datetime.now().strftime('%d.%m.%Y um %H:%M:%S')}")
        lines.append(f"**Model:** {getattr(self, 'current_model', 'Unbekannt')}")
        lines.append(f"**Anzahl Messages:** {self.count_chat_messages()}")
        
        # Session-Zeitraum
        if self.chat_bubbles:
            session_start = self.chat_bubbles[0].timestamp
            session_end = self.chat_bubbles[-1].timestamp
            lines.append(f"**Session-Start:** {session_start}")
            lines.append(f"**Session-Ende:** {session_end}")
        
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Chat-Messages
        for i, bubble in enumerate(self.chat_bubbles, 1):
            # Zeitstempel
            lines.append(f"**[{bubble.timestamp}]**")
            lines.append("")
            
            # Sender und Rolle ermitteln
            sender = bubble.sender
            if sender.startswith("👤"):
                lines.append(f"### 👤 Benutzer")
                lines.append("")
                lines.append(bubble.message)
            elif sender.startswith("🤖"):
                model_name = sender.replace("🤖 ", "").strip()
                lines.append(f"### 🤖 {model_name}")
                lines.append("")
                lines.append(bubble.message)
            else:
                lines.append(f"### ℹ️ {sender}")
                lines.append("")
                lines.append(bubble.message)
            
            lines.append("")
            
            # Trennlinie zwischen Messages (außer bei der letzten)
            if i < len(self.chat_bubbles):
                lines.append("---")
                lines.append("")
        
        # Footer
        lines.append("---")
        lines.append("")
        lines.append(f"*Session-ID: {session_id}*")
        lines.append("*Generiert von A1-Terminal LLM Chat Client*")
        
        return '\n'.join(lines)
    
    def setup_keyboard_shortcuts(self):
        """Sets up keyboard shortcuts"""
        # Ctrl+N - New Session
        self.root.bind("<Control-n>", lambda e: self.create_new_session())
        
        # Ctrl+L - Clear chat
        self.root.bind("<Control-l>", lambda e: self.clear_current_chat())
        
        # Ctrl+E - Export
        self.root.bind("<Control-e>", lambda e: self.export_session_markdown())
        
        # Ctrl+B - Focus BIAS
        self.root.bind("<Control-b>", lambda e: self.session_bias_entry.focus() if hasattr(self, 'session_bias_entry') else None)
        
        # Escape - Stop generation
        self.root.bind("<Escape>", lambda e: self.stop_generation())
        
        print("⌨️ Keyboard shortcuts activated:")
        print("  Ctrl+N: New Session")
        print("  Ctrl+L: Clear chat")
        print("  Ctrl+E: Export")
        print("  Ctrl+B: Focus BIAS")
        print("  Escape: Stop generation")
    
    def clear_current_chat(self):
        """Clears the current chat"""
        if not self.current_session_id:
            return
        
        response = messagebox.askyesno(
            "Clear chat",
            "Do you want to delete the entire chat history of this session?"
        )
        
        if response:
            # Clear chat history
            self.chat_history = []
            
            # Session refresh
            if self.current_session_id in self.sessions:
                self.sessions[self.current_session_id]["messages"] = []
                self.save_current_session()
            
            # Chat-Anzeige leeren
            for bubble in self.chat_bubbles:
                bubble.destroy()
            self.chat_bubbles.clear()
            
            # System-Message
            self.add_to_chat("System", "✨ Chat wurde geleert")
    
    def run(self):
        """Starts the application"""
        self.root.mainloop()
