"""A1Terminal Hauptklasse"""

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
from src.core.ollama_manager import OllamaManager

class A1Terminal:
    """Hauptanwendungsklasse"""
    def __init__(self):
        self._session_just_loaded = False
        
        # YAML-Konfigurationsdatei ZUERST laden
        self.config_file = "ki_whisperer_config.yaml"
        self.config = self.load_config()
        
        # Jetzt root mit Config-Werten erstellen
        self.root = ctk.CTk()
        self.root.title("LLM Messenger - Ollama Chat Client")
        
        # Fenstergröße aus Config
        window_width = self.config.get('ui_window_width', 1400)
        window_height = self.config.get('ui_window_height', 900)
        self.root.geometry(f"{window_width}x{window_height}")
        
        # Fenster resizeable machen und Mindestgröße setzen
        self.root.resizable(True, True)
        self.root.minsize(900, 500)
        self.root.maxsize(2560, 1440)
        
        self.ollama = OllamaManager()
        self.current_model = None
        self.chat_history = []
        
        # Stop-Funktionalität für Generation und Downloads
        self.generation_stopped = False
        self.download_stopped = False
        self.current_generation_thread = None
        self.current_download_thread = None
        
        # Progressive Message-Anzeige
        self.response_message_widget = None
        self.current_response_text = ""
        
        # Nachrichten-Historie für Pfeiltasten-Navigation
        self.message_history = []
        self.history_index = -1
        
        # Chat-Bubbles für Session Management
        self.chat_bubbles = []
        
        # Session Management Variablen früh initialisieren
        self.sessions = {}
        self.current_session_id = None
        self.current_session_bias = ""
        self.bias_auto_save_timer = None
        
        # Sessions-Verzeichnis früh initialisieren
        self.sessions_dir = os.path.join(os.getcwd(), "sessions")
        if not os.path.exists(self.sessions_dir):
            os.makedirs(self.sessions_dir)
        
        # Auto-Save Timer für Session-Speicherung
        self.auto_save_timer = None
        
        # Setup UI
        self.setup_ui()
        self.check_ollama_status()
    
    def get_default_config(self):
        """Gibt die Standard-Konfiguration zurück"""
        return {
            # ========== BUBBLE-FARBEN ==========
            "user_bg_color": "#003300",      # Sie - Hintergrund
            "user_text_color": "#00FF00",    # Sie - Text (Matrix)
            "ai_bg_color": "#1E3A5F",        # AI - Hintergrund
            "ai_text_color": "white",        # AI - Text
            "system_bg_color": "#722F37",    # System - Hintergrund
            "system_text_color": "white",    # System - Text
            
            # ========== SCHRIFTARTEN ==========
            "user_font": "Courier New",      # Sie - Matrix-Font
            "user_font_size": 11,            # Sie - Individuelle Größe
            "ai_font": "Consolas",           # AI - Code-Font
            "ai_font_size": 11,              # AI - Individuelle Größe
            "system_font": "Arial",          # System - Standard-Font
            "system_font_size": 10,          # System - Individuelle Größe
            
            # ========== UI-LAYOUT ==========
            "ui_session_panel_width": 350,   # Breite des Session-Panels (px)
            "ui_window_width": 1400,         # Fensterbreite beim Start (px)
            "ui_window_height": 900,         # Fensterhöhe beim Start (px)
            "ui_padding_main": 10,           # Hauptabstand außen (px)
            "ui_padding_content": 5,         # Inhaltsabstand (px)
            
            # ========== CHAT-DISPLAY ==========
            "ui_chat_bubble_corner_radius": 10,    # Bubble-Ecken-Radius
            "ui_chat_bubble_padding_x": 15,        # Bubble horizontal padding
            "ui_chat_bubble_padding_y": 10,        # Bubble vertikal padding
            "ui_chat_spacing": 10,                 # Abstand zwischen Bubbles
            "ui_chat_max_width_ratio": 0.8,        # Max Bubble-Breite (80% des Containers)
            
            # ========== INPUT-BEREICH ==========
            "ui_input_height": 40,           # Höhe des Eingabefelds (px)
            "ui_input_font_size": 12,        # Schriftgröße im Input
            "ui_button_width": 100,          # Breite der Buttons (px)
            "ui_button_height": 40,          # Höhe der Buttons (px)
            
            # ========== SESSION-LISTE ==========
            "ui_session_item_height": 60,    # Höhe eines Session-Items (px)
            "ui_session_font_size": 11,      # Schriftgröße in Session-Liste
            "ui_session_spacing": 5,         # Abstand zwischen Sessions
            
            # ========== MODEL-SELECTOR ==========
            "ui_model_dropdown_height": 32,  # Höhe des Model-Dropdowns (px)
            "ui_model_button_size": 35,      # Größe der Model-Buttons (px)
            "ui_model_font_size": 11,        # Schriftgröße im Model-Selector
            "ui_model_title_size": 12,       # Schriftgröße Model-Titel
            "ui_model_label_size": 9,        # Schriftgröße Model-Labels
            
            # ========== SESSION-BUTTONS ==========
            "ui_session_button_width": 140,  # Breite Session-Buttons
            "ui_session_button_height": 25,  # Höhe Session-Buttons
            "ui_session_button_font": 9,     # Schriftgröße Session-Buttons
            
            # ========== BIAS-TEXTBOX ==========
            "ui_bias_height": 60,            # Höhe BIAS-Eingabefeld
            "ui_bias_font_size": 9,          # Schriftgröße BIAS
            
            # ========== DEBUG-BUTTONS ==========
            "ui_debug_button_height": 30,    # Höhe Debug-Buttons
            "ui_debug_button_font": 9,       # Schriftgröße Debug-Buttons
            
            # ========== TABS ==========
            "ui_tab_font_size": 13,          # Schriftgröße der Tab-Namen
            "ui_tab_height": 40,             # Höhe der Tab-Leiste (px)
            
            # ========== CONFIG-TAB ==========
            "ui_config_label_width": 200,    # Breite der Labels im Config
            "ui_config_slider_width": 300,   # Breite der Sliders
            "ui_config_entry_width": 200,    # Breite der Eingabefelder
            
            # ========== FARBEN & THEME ==========
            "ui_bg_color": "#1a1a1a",        # Haupthintergrund
            "ui_fg_color": "#2b2b2b",        # Vordergrund/Panels
            "ui_accent_color": "#2B8A3E",    # Akzentfarbe (Buttons)
            "ui_hover_color": "#37A24B",     # Hover-Farbe
            "ui_text_color": "white",        # Standard-Textfarbe
            "ui_border_color": "#3a3a3a",    # Border-Farbe
            
            # ========== SCROLLBAR ==========
            "ui_scrollbar_width": 12,        # Breite der Scrollbar (px)
            "ui_scrollbar_corner_radius": 6, # Scrollbar Ecken-Radius
            
            # ========== ALLGEMEINE OPTIONEN ==========
            "show_system_messages": True,    # System-Nachrichten im Chat anzeigen
            "auto_scroll_chat": True,        # Auto-Scroll zu neuen Nachrichten
            "show_timestamps": True,         # Timestamps in Chat anzeigen
            "compact_mode": False,           # Kompakte Darstellung
        }
    
    def load_config(self):
        """Lädt die Konfiguration aus der YAML-Datei oder erstellt Standard-Config"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as file:
                    config = yaml.safe_load(file)
                    if config:
                        # Fülle fehlende Werte mit Standardwerten auf
                        default_config = self.get_default_config()
                        for key, value in default_config.items():
                            if key not in config:
                                config[key] = value
                        print(f"✅ Konfiguration geladen aus {self.config_file}")
                        return config
                    
            # Fallback auf Standard-Konfiguration
            default_config = self.get_default_config()
            self.save_config(default_config)
            print(f"📝 Standard-Konfiguration erstellt in {self.config_file}")
            return default_config
            
        except Exception as e:
            print(f"❌ Fehler beim Laden der Konfiguration: {e}")
            print("🔄 Verwende Standard-Konfiguration")
            return self.get_default_config()
    
    def save_config(self, config=None):
        """Speichert die Konfiguration in die YAML-Datei"""
        try:
            config_to_save = config or self.config
            
            # Erstelle YAML mit Kommentaren
            yaml_content = """# Ki-Whisperer Konfigurationsdatei
# Diese Datei wird automatisch erstellt und aktualisiert
# Alle Änderungen werden beim Anwenden in der GUI gespeichert

# ========================================
# CHAT-BUBBLE FARBEN
# ========================================
"""
            
            # Bubble-Farben Sektion
            bubble_colors = {k: v for k, v in config_to_save.items() if 'color' in k and 'console' not in k}
            yaml_content += "# Farben für Chat-Bubbles (Hex-Codes)\nbubble_colors:\n"
            
            for key, value in bubble_colors.items():
                comment = ""
                if "user" in key:
                    comment = "  # Sie (Matrix-Style)"
                elif "ai" in key:
                    comment = "  # AI-Modell"
                elif "system" in key:
                    comment = "  # System-Nachrichten"
                yaml_content += f"  {key}: \"{value}\"{comment}\n"
            
            
            # Konsolen-Konfiguration
            console_config = {k: v for k, v in config_to_save.items() if 'console' in k}
            yaml_content += "# Terminal/Konsolen-Ausgabe Styling\nconsole:\n"
            
            for key, value in console_config.items():
                yaml_content += f"  {key}: \"{value}\"\n"
                
            # Schreibe YAML-Datei
            with open(self.config_file, 'w', encoding='utf-8') as file:
                # Schreibe manuelle YAML-Struktur für bessere Kommentare
                file.write(yaml_content)
                
                # Füge flache Struktur hinzu für einfache Kompatibilität
                file.write("\n# Flache Struktur für Kompatibilität (wird automatisch generiert)\n")
                yaml.dump(config_to_save, file, default_flow_style=False, allow_unicode=True)
            
            print(f"💾 Konfiguration gespeichert in {self.config_file}")
            
        except Exception as e:
            print(f"❌ Fehler beim Speichern der Konfiguration: {e}")
    
    def reset_config_to_defaults(self):
        """Setzt die Konfiguration auf Standardwerte zurück und speichert sie"""
        self.config = self.get_default_config()
        self.save_config()
    
    
    def console_print(self, text, style="normal"):
        """Einfache Konsolen-Ausgabe (ohne Styling)"""
        print(text)
    
    

    # ============================================
    # SESSION MANAGEMENT SYSTEM
    # ============================================
    
    def setup_session_panel(self):
        """Erstellt das Session Management Panel"""
        
        # ============================================
        # MODELL MANAGEMENT BEREICH (OBEN)
        # ============================================
        
        # Modell Management Frame (ganz oben)
        model_frame = ctk.CTkFrame(self.session_panel)
        model_frame.pack(fill="x", padx=self.config.get("ui_padding_content", 5), 
                        pady=self.config.get("ui_padding_content", 5))
        
        model_title = ctk.CTkLabel(model_frame, text="🤖 Modell Management", 
                                  font=("Arial", self.config.get("ui_model_title_size", 12), "bold"))
        model_title.pack(anchor="w", padx=self.config.get("ui_padding_main", 10), 
                        pady=(self.config.get("ui_padding_main", 10), self.config.get("ui_padding_content", 5)))
        
        # Ollama Status
        self.status_label = ctk.CTkLabel(model_frame, text="Ollama Status: Wird geprüft...",
                                        font=("Arial", self.config.get("ui_model_label_size", 9)))
        self.status_label.pack(anchor="w", padx=self.config.get("ui_padding_main", 10), pady=2)
        
        # Installierte Modelle
        installed_frame = ctk.CTkFrame(model_frame)
        installed_frame.pack(fill="x", padx=self.config.get("ui_padding_main", 10), 
                            pady=self.config.get("ui_padding_content", 5))
        
        self.installed_label = ctk.CTkLabel(installed_frame, text="📦 Installiert:",
                                          font=("Arial", self.config.get("ui_model_label_size", 9), "bold"))
        self.installed_label.pack(anchor="w", padx=self.config.get("ui_padding_content", 5), pady=2)
        
        # Model Dropdown und Buttons in einer Zeile
        model_controls_frame = ctk.CTkFrame(installed_frame)
        model_controls_frame.pack(fill="x", padx=self.config.get("ui_padding_content", 5), pady=2)
        
        self.model_var = tk.StringVar()
        self.model_dropdown = ctk.CTkComboBox(
            model_controls_frame, 
            variable=self.model_var,
            values=["Keine Modelle verfügbar"],
            command=self.on_model_select,
            height=self.config.get("ui_model_dropdown_height", 32),
            font=("Arial", self.config.get("ui_model_font_size", 11))
        )
        self.model_dropdown.pack(side="left", fill="x", expand=True, padx=(2, 5), pady=2)
        
        # Mausrad-Scrolling für model_dropdown aktivieren
        
        # Delete Button 
        self.delete_btn = ctk.CTkButton(
            model_controls_frame,
            text="🗑️",
            command=self.delete_selected_model,
            fg_color="red",
            hover_color="darkred",
            width=self.config.get("ui_model_button_size", 35),
            font=("Arial", self.config.get("ui_model_label_size", 9))
        )
        self.delete_btn.pack(side="right", padx=2, pady=2)
        
        # Refresh Button  
        self.refresh_btn = ctk.CTkButton(
            model_controls_frame,
            text="🔄",
            command=self.refresh_models,
            width=self.config.get("ui_model_button_size", 35),
            font=("Arial", self.config.get("ui_model_label_size", 9))
        )
        self.refresh_btn.pack(side="right", padx=2, pady=2)
        
        # Verfügbare Modelle zum Download
        download_frame = ctk.CTkFrame(model_frame)
        download_frame.pack(fill="x", padx=self.config.get("ui_padding_main", 10), 
                           pady=self.config.get("ui_padding_content", 5))
        
        self.available_label = ctk.CTkLabel(download_frame, text="⬇️ Download:",
                                          font=("Arial", self.config.get("ui_model_label_size", 9), "bold"))
        self.available_label.pack(anchor="w", padx=self.config.get("ui_padding_content", 5), pady=2)
        
        # Download Controls
        download_controls_frame = ctk.CTkFrame(download_frame)
        download_controls_frame.pack(fill="x", padx=self.config.get("ui_padding_content", 5), pady=2)
        
        # Kategorisiertes Dropdown für verfügbare Modelle
        self.available_var = tk.StringVar()
        self.available_dropdown = CategorizedComboBox(
            download_controls_frame, 
            variable=self.available_var,
            categories_dict={},
            font=("Arial", self.config.get("ui_model_font_size", 9))
        )
        self.available_dropdown.pack(side="left", fill="x", expand=True, padx=(2, 5), pady=2)
        
        # Download Button
        self.download_btn = ctk.CTkButton(
            download_controls_frame,
            text="⬇️",
            command=self.download_selected_model,
            width=self.config.get("ui_model_button_size", 35),
            font=("Arial", self.config.get("ui_model_label_size", 9))
        )
        self.download_btn.pack(side="right", padx=2, pady=2)
        
        # Manueller Download Button  
        self.manual_download_btn = ctk.CTkButton(
            download_controls_frame,
            text="📝",
            command=self.show_download_dialog,
            width=self.config.get("ui_model_button_size", 35),
            font=("Arial", self.config.get("ui_model_label_size", 9))
        )
        self.manual_download_btn.pack(side="right", padx=2, pady=2)
        
        # Progress Bar für Downloads (initial versteckt)
        self.progress_frame = ctk.CTkFrame(model_frame)
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="Download läuft...",
                                         font=("Arial", self.config.get("ui_model_label_size", 9)))
        self.progress_label.pack(pady=2)
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(fill="x", padx=self.config.get("ui_padding_main", 10), pady=2)
        
        # ============================================
        # SESSION MANAGEMENT BEREICH (DARUNTER)
        # ============================================
        
    # (Session Panel Header entfernt)
        
        # Session Liste
        sessions_frame = ctk.CTkFrame(self.session_panel)
        sessions_frame.pack(fill="both", expand=True, 
                           padx=self.config.get("ui_padding_content", 5), 
                           pady=self.config.get("ui_padding_content", 5))
        
        # Header-Frame für Session Liste mit Button nebeneinander
        session_header_frame = ctk.CTkFrame(sessions_frame)
        session_header_frame.pack(fill="x", padx=self.config.get("ui_padding_main", 10), 
                                 pady=(self.config.get("ui_padding_main", 10), self.config.get("ui_padding_content", 5)))
        
        list_label = ctk.CTkLabel(session_header_frame, text="🗂️ Session Liste:", 
                                 font=("Arial", self.config.get("ui_model_title_size", 12), "bold"))
        list_label.pack(side="left", anchor="w", padx=(0, self.config.get("ui_padding_main", 10)))
        
        # Neue Session Button - jetzt neben der Session Liste
        new_session_btn = ctk.CTkButton(
            session_header_frame, 
            text="➕ Neue Session",
            command=self.create_new_session,
            width=self.config.get("ui_session_button_width", 140),
            height=self.config.get("ui_session_button_height", 25),
            font=("Arial", self.config.get("ui_session_button_font", 9), "bold"),
            fg_color="#2B8A3E",
            hover_color="#37A24B"
        )
        new_session_btn.pack(side="right", padx=(self.config.get("ui_padding_main", 10), 0))
        
        # Scrollbare Session-Liste - kleinere Höhe für mehr Platz für andere Elemente
        self.session_listbox = ctk.CTkScrollableFrame(sessions_frame, 
                                                      height=self.config.get("ui_session_item_height", 60) * 2.5)
        self.session_listbox.pack(fill="both", expand=True, 
                                 padx=self.config.get("ui_padding_main", 10), 
                                 pady=self.config.get("ui_padding_content", 5))
        
        # Aktuelle Session Info (mit blauer Umrandung)
        self.current_frame = ctk.CTkFrame(self.session_panel, border_width=3, border_color="#00BFFF")
        self.current_frame.pack(fill="x", 
                               padx=self.config.get("ui_padding_content", 5), 
                               pady=self.config.get("ui_padding_content", 5))

        current_label = ctk.CTkLabel(self.current_frame, text="📌 Aktuelle Session:", 
                                    font=("Arial", self.config.get("ui_model_title_size", 12), "bold"))
        current_label.pack(anchor="w", padx=self.config.get("ui_padding_main", 10), 
                          pady=(self.config.get("ui_padding_main", 10), self.config.get("ui_padding_content", 5)))

        # Session Details
        self.current_session_label = ctk.CTkLabel(
            self.current_frame, 
            text="Keine Session aktiv",
            font=("Arial", self.config.get("ui_session_font_size", 11)),
            anchor="w"
        )
        self.current_session_label.pack(anchor="w", padx=self.config.get("ui_padding_main", 10), pady=2)

        # Model Info
        self.current_model_label = ctk.CTkLabel(
            self.current_frame,
            text="Model: Nicht ausgewählt", 
            font=("Arial", self.config.get("ui_session_font_size", 11)),
            anchor="w"
        )
        self.current_model_label.pack(anchor="w", padx=self.config.get("ui_padding_main", 10), pady=2)

        # BIAS Input
        bias_label = ctk.CTkLabel(self.current_frame, text="🎯 Session BIAS:", 
                                 font=("Arial", self.config.get("ui_session_font_size", 11), "bold"))
        bias_label.pack(anchor="w", padx=self.config.get("ui_padding_main", 10), 
                       pady=(self.config.get("ui_padding_main", 10), 2))

        self.session_bias_entry = ctk.CTkTextbox(
            self.current_frame,
            height=self.config.get("ui_bias_height", 60),
            font=("Arial", self.config.get("ui_bias_font_size", 9))
        )
        self.session_bias_entry.pack(fill="x", padx=self.config.get("ui_padding_main", 10), pady=2)

        # Auto-Save für BIAS bei Textänderung
        self.bias_auto_save_timer = None
        self.session_bias_entry.bind("<KeyRelease>", self.on_bias_text_changed)
        self.session_bias_entry.bind("<Button-1>", self.on_bias_text_changed)

        # BIAS Info Label für aktuellen Status
        self.bias_info_label = ctk.CTkLabel(
            self.current_frame,
            text="💭 BIAS nicht gesetzt",
            font=("Arial", self.config.get("ui_model_label_size", 9)),
            text_color="gray"
        )
        self.bias_info_label.pack(anchor="w", padx=self.config.get("ui_padding_main", 10), pady=2)

        # BIAS speichern Button (jetzt optional, da Auto-Save aktiv ist)
        save_bias_btn = ctk.CTkButton(
            self.current_frame,
            text="💾 BIAS manuell speichern",
            command=self.save_session_bias,
            height=self.config.get("ui_session_button_height", 25),
            font=("Arial", self.config.get("ui_session_button_font", 9))
        )
        save_bias_btn.pack(fill="x", padx=self.config.get("ui_padding_main", 10), 
                          pady=self.config.get("ui_padding_content", 5))

        # Session Actions
        actions_frame = ctk.CTkFrame(self.current_frame)
        actions_frame.pack(fill="x", padx=self.config.get("ui_padding_main", 10), 
                          pady=self.config.get("ui_padding_content", 5))
        
        # Manueller Session-Speichern Button entfernt - Auto-Save ist aktiv
        
        delete_session_btn = ctk.CTkButton(
            actions_frame,
            text="🗑️ Session",
            command=self.delete_current_session,
            height=self.config.get("ui_session_button_height", 25),
            font=("Arial", self.config.get("ui_session_button_font", 9)),
            fg_color="#C92A2A",
            hover_color="#E03131"
        )
        delete_session_btn.pack(side="left", fill="x", expand=True, padx=(0, 2))
        
        # Alle Sessions löschen Button - direkt nebeneinander
        cleanup_btn = ctk.CTkButton(
            actions_frame,
            text="🧹 Alle",
            command=self.delete_all_sessions,
            height=self.config.get("ui_session_button_height", 25),
            font=("Arial", self.config.get("ui_session_button_font", 9)),
            fg_color="#8B0000",
            hover_color="#A52A2A"
        )
        cleanup_btn.pack(side="left", fill="x", expand=True, padx=(2, 0))
        
        # Debug Sessions Button - mit Beschriftung für bessere Usability
        debug_frame = ctk.CTkFrame(self.session_panel)
        debug_frame.pack(fill="x", padx=self.config.get("ui_padding_content", 5), 
                        pady=self.config.get("ui_padding_content", 5))
        
        # Buttons gleichmäßig in Reihen anordnen
        # Erste Reihe: Debug Sessions und Sessions-Ordner
        debug_row1 = ctk.CTkFrame(debug_frame)
        debug_row1.pack(fill="x", pady=2)
        
        debug_btn = ctk.CTkButton(
            debug_row1,
            text="🔍 Debug Sessions",
            command=self.show_session_debug,
            height=self.config.get("ui_debug_button_height", 30),
            font=("Arial", self.config.get("ui_debug_button_font", 9)),
            fg_color="#4A4A4A",
            hover_color="#5A5A5A"
        )
        debug_btn.pack(side="left", fill="x", expand=True, padx=(2, 1))
        
        folder_btn = ctk.CTkButton(
            debug_row1,
            text="📁 Sessions-Ordner",
            command=self.open_sessions_folder,
            height=self.config.get("ui_debug_button_height", 30),
            font=("Arial", self.config.get("ui_debug_button_font", 9)),
            fg_color="#2D5A87",
            hover_color="#3D6A97"
        )
        folder_btn.pack(side="left", fill="x", expand=True, padx=(1, 2))
        
        # (Button '🗑️ Chat-Historie' entfernt)

    def initialize_session_management(self):
        """Initialisiert das Session Management System"""
        # Session-Datenstrukturen (bereits im __init__ initialisiert)
        # self.sessions = {}  # Alle Sessions: {session_id: session_data}
        # self.current_session_id = None
        # self.current_session_bias = ""
        
        # Sessions-Ordner (bereits im __init__ erstellt)
        # self.sessions_dir = os.path.join(os.getcwd(), "sessions")
        # if not os.path.exists(self.sessions_dir):
        #     os.makedirs(self.sessions_dir)
            
        # Chat-Bubbles für Session Management
        self.chat_bubbles = []
        
        # Lade bestehende Sessions
        self.load_all_sessions()
        
        # Zeige Session-Status an
        if not self.sessions:
            self.console_print("📋 Keine bestehenden Sessions gefunden", "info")
            self.console_print("💡 Klicken Sie auf '➕ Neue Session' um zu beginnen", "info")
        else:
            # Lade die neueste Session automatisch
            latest_session = max(self.sessions.keys(), key=lambda x: self.sessions[x].get("created_at", ""))
            self.load_session(latest_session)
            self.console_print(f"📂 Neueste Session automatisch geladen: {latest_session[:12]}...", "success")
        
        # Debug: Session-Analyse
        self.debug_session_analysis()
        
        # Keine automatische Session-Erstellung - Nutzer muss explizit erstellen
        # UI aktualisieren um "Keine Session" Zustand zu zeigen
        self.update_session_list()
        self.update_current_session_display()

    def create_new_session(self):
        """Erstellt eine neue Session"""
        # Session-ID generieren (mit Millisekunden für Eindeutigkeit)
        timestamp = datetime.now()
        session_id = timestamp.strftime("%Y%m%d_%H%M%S") + f"_{timestamp.microsecond // 1000:03d}"
        
        # Prüfen ob Session-ID bereits existiert (Sicherheitscheck)
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
            "color": "#1f538d"  # Standard-Farbe: Blau
        }
        
        # Session speichern
        self.sessions[session_id] = session_data
        self.current_session_id = session_id
        
        # Chat leeren
        self.clear_chat_for_new_session()
        
        # BIAS für neue Session zurücksetzen
        self.current_session_bias = ""
        if hasattr(self, 'session_bias_entry'):
            self.session_bias_entry.delete("1.0", "end")
        # BIAS-Info-Label aktualisieren
        self.update_bias_info_label()
        
        # UI aktualisieren
        self.update_session_list()
        self.update_current_session_display()
        
        # Session persistent speichern mit Feedback
        self.save_session_with_feedback()
        

        self.console_print(f"✅ Neue Session erstellt: {session_id}", "success")


    def debug_session_analysis(self):
        """Debug-Funktion zur Analyse von Session-Problemen"""
        if not self.sessions:
            return
            
        self.console_print(f"🔍 Session-Analyse: {len(self.sessions)} Sessions gefunden", "info")
        
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
        
        # Warne bei möglichen Duplikaten
        for time_key, session_ids in session_times.items():
            if len(session_ids) > 1:
                self.console_print(f"⚠️ Mögliche Duplikate gefunden zur Zeit {time_key}:", "warning")
                for sid in session_ids:
                    session_data = self.sessions[sid]
                    msg_count = session_data.get("total_messages", 0)
                    model = session_data.get("model", "Kein Model")
                    self.console_print(f"   🆔 {sid[-12:]} | 💬 {msg_count} Msg | 🤖 {model}", "info")

    def show_session_debug(self):
        """Zeigt detaillierte Session-Debug-Informationen"""
        debug_text = "🔍 SESSION DEBUG INFORMATION\n" + "="*50 + "\n\n"
        
        if not self.sessions:
            debug_text += "❌ Keine Sessions vorhanden\n"
        else:
            debug_text += f"📊 Anzahl Sessions: {len(self.sessions)}\n"
            debug_text += f"🔄 Aktuelle Session: {self.current_session_id}\n\n"
            
            # Session-Details
            for i, (session_id, session_data) in enumerate(sorted(self.sessions.items(), 
                                                                 key=lambda x: x[1].get("created_at", ""), 
                                                                 reverse=True), 1):
                debug_text += f"SESSION #{i}:\n"
                debug_text += f"   🆔 ID: {session_id}\n"
                debug_text += f"   📅 Erstellt: {session_data.get('created_at', 'Unbekannt')}\n"
                debug_text += f"   ⏰ Geändert: {session_data.get('last_modified', 'Unbekannt')}\n"
                debug_text += f"   🤖 Model: {session_data.get('model', 'Nicht gesetzt')}\n"
                debug_text += f"   💬 Nachrichten: {session_data.get('total_messages', 0)}\n"
                debug_text += f"   📝 BIAS: {'Ja' if session_data.get('bias', '') else 'Nein'}\n"
                
                # Prüfe auf Session-Datei (beliebiger Name, aber mit passender ID)
                matching_files = [f for f in os.listdir(self.sessions_dir) if f.endswith(f"_session_{session_id}.json")]
                file_exists = len(matching_files) > 0
                debug_text += f"   💾 Datei: {'✅ Vorhanden' if file_exists else '❌ Fehlt'}\n"
                if file_exists:
                    try:
                        stat = os.stat(os.path.join(self.sessions_dir, matching_files[0]))
                        debug_text += f"   📏 Dateigröße: {stat.st_size} Bytes\n"
                    except:
                        debug_text += f"   📏 Dateigröße: Unlesbar\n"
                
                debug_text += "\n"
        
        # Zeige Debug-Info in einem Dialog
        debug_dialog = ctk.CTkToplevel(self.root)
        debug_dialog.title("🔍 Session Debug Information")
        debug_dialog.geometry("600x500")
        debug_dialog.transient(self.root)
        debug_dialog.grab_set()
        
        # Text-Widget für Debug-Ausgabe
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
            text="Schließen",
            command=debug_dialog.destroy,
            width=100
        )
        close_btn.pack(pady=10)

    def open_sessions_folder(self):
        """Öffnet das Sessions-Verzeichnis im Windows Explorer"""
        try:
            import subprocess
            import os
            
            # Prüfe ob Sessions-Verzeichnis existiert
            sessions_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions")
            
            if not os.path.exists(sessions_dir):
                # Erstelle das Verzeichnis falls es nicht existiert
                os.makedirs(sessions_dir, exist_ok=True)
                self.console_print(f"📁 Sessions-Verzeichnis erstellt: {sessions_dir}", "success")
            
            # Öffne Explorer mit dem Sessions-Verzeichnis
            subprocess.Popen(f'explorer "{sessions_dir}"', shell=True)
            self.console_print(f"📂 Sessions-Ordner geöffnet: {sessions_dir}", "success")
            
        except Exception as e:
            self.console_print(f"❌ Fehler beim Öffnen des Sessions-Ordners: {e}", "error")

    def clear_chat_history(self):
        """Löscht die Chat-Historie für einen frischen Kontext mit dem Model"""
        result = messagebox.askyesno(
            "Chat-Historie löschen",
            "⚠️ Chat-Historie löschen?\n\n"
            f"Dies löscht den Kontext für das AI-Model.\n"
            f"Die Nachrichten bleiben in der Session sichtbar,\n"
            f"aber das Model vergisst den bisherigen Verlauf.\n\n"
            f"Möchten Sie fortfahren?"
        )
        
        if result:
            old_count = len(self.chat_history)
            self.chat_history = []
            
            self.console_print(f"🗑️ Chat-Historie gelöscht: {old_count} Nachrichten entfernt", "success")
            self.add_to_chat("System", "🗑️ Chat-Historie für AI-Model gelöscht - Frischer Kontext ab sofort")

    def load_session(self, session_id):
        self._session_just_loaded = True
        """Lädt eine bestehende Session"""
        if session_id not in self.sessions:
            return False
            
        # Aktuelle Session wechseln
        self.current_session_id = session_id
        session_data = self.sessions[session_id]
        
        # Chat leeren und Session-Nachrichten laden
        self.clear_chat_for_new_session()
        
        # Chat-Historie für LLM zurücksetzen und neu aufbauen
        self.chat_history = []
        
        # Model setzen wenn vorhanden
        if session_data.get("model"):
            self.current_model = session_data["model"]
            if hasattr(self, 'model_dropdown'):
                self.model_dropdown.set(self.current_model)
        
        # BIAS setzen
        self.current_session_bias = session_data.get("bias", "")
        if hasattr(self, 'session_bias_entry'):
            self.session_bias_entry.delete("1.0", "end")
            self.session_bias_entry.insert("1.0", self.current_session_bias)
        # BIAS-Info-Label aktualisieren
        self.update_bias_info_label()
        
        # Nachrichten laden und Chat-Historie für LLM aufbauen
        message_count = 0
        for msg_data in session_data.get("messages", []):
            # Visuelle Nachricht wiederherstellen
            self.restore_chat_message(msg_data)
            message_count += 1
            
            # Chat-Historie für LLM aufbauen (nur User und AI-Nachrichten, keine System-Nachrichten)
            sender = msg_data.get("sender", "")
            message = msg_data.get("message", "")
            
            if sender == "Sie":
                self.chat_history.append({"role": "user", "content": message})
            elif sender.startswith("🤖") and not sender.startswith("System"):
                # AI-Antwort hinzufügen
                self.chat_history.append({"role": "assistant", "content": message})
        
        # Layout nach dem Laden aller Nachrichten vollständig aktualisieren
        if message_count > 0:
            self.chat_display_frame.update_idletasks()
            if hasattr(self.chat_display_frame, '_parent_canvas'):
                self.chat_display_frame._parent_canvas.update_idletasks()
                # Scrollregion neu berechnen
                self.chat_display_frame._parent_canvas.configure(scrollregion=self.chat_display_frame._parent_canvas.bbox("all"))
        
        # Debug-Info über wiederhergestellte Chat-Historie
        if self.chat_history:
            self.console_print(f"💬 Chat-Historie wiederhergestellt: {len(self.chat_history)} Nachrichten für LLM-Kontext", "success")
        
        # UI aktualisieren
        self.update_current_session_display()
        
        # Zur letzten Nachricht scrollen - mit längerer Verzögerung für vollständiges Layout
        self.root.after(200, self.scroll_to_last_message)
        
        self.console_print(f"📂 Session geladen: {session_id}", "info")
        return True

    def save_current_session(self):
        """Speichert die aktuelle Session"""
        if not self.current_session_id:
            return False
            
        session_data = self.sessions[self.current_session_id]
        
        # Aktuelle Daten sammeln
        session_data["last_modified"] = datetime.now().isoformat()
        session_data["model"] = getattr(self, 'current_model', None)
        session_data["bias"] = self.current_session_bias
        session_data["total_messages"] = self.count_chat_messages()
        
        # Chat-Nachrichten sammeln
        messages = []
        for bubble in self.chat_bubbles:
            msg_data = {
                "timestamp": bubble.timestamp,
                "sender": bubble.sender,
                "message": bubble.message
            }
            messages.append(msg_data)
        
        session_data["messages"] = messages
        
        # Session-Datei speichern: Name am Anfang, dann _session_<SessionID>.json
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
            self.console_print(f"❌ Fehler beim Speichern der Session: {e}", "error")
            return False

    def auto_save_session(self):
        """Automatisches Speichern mit Debounce-Logik"""
        # Lösche vorherigen Timer falls vorhanden
        if self.auto_save_timer:
            self.root.after_cancel(self.auto_save_timer)
        
        # Starte neuen Timer für verzögertes Speichern (200ms)
        self.auto_save_timer = self.root.after(200, self.perform_auto_save)
    
    def perform_auto_save(self):
        """Führt das tatsächliche automatische Speichern durch"""
        try:
            if self.save_current_session():
                # Nur in Debug-Modus anzeigen, um Konsole nicht zu überlasten
                # self.console_print(f"💾 Auto-Save: Session gespeichert", "info")
                pass
        except Exception as e:
            self.console_print(f"❌ Auto-Save Fehler: {e}", "error")
        finally:
            self.auto_save_timer = None

    def save_session_with_feedback(self):
        """Manuelles Speichern mit Konsolen-Feedback"""
        if self.save_current_session():
            self.console_print(f"💾 Session manuell gespeichert: {self.current_session_id}", "success")
            return True
        return False

    def load_all_sessions(self):
        """Lädt alle Sessions aus dem Sessions-Ordner"""
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
                                session_data["color"] = "#1f538d"  # Standard-Blau
                            self.sessions[session_id] = session_data
                except Exception as e:
                    self.console_print(f"❌ Fehler beim Laden der Session {session_file}: {e}", "warning")
            
            self.update_session_list()
            self.console_print(f"📂 {len(self.sessions)} Sessions geladen", "info")
            
        except Exception as e:
            self.console_print(f"❌ Fehler beim Laden der Sessions: {e}", "error")

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
        """Aktualisiert die Session-Liste in der UI"""
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
            
            # Button-Container für Rename und Color
            button_container = ctk.CTkFrame(session_container)
            button_container.pack(side="right")

            # Color-Button  
            session_color = session_data.get("color", "#4A4A4A")  # Standard-Farbe falls keine gesetzt
            color_btn = ctk.CTkButton(
                button_container,
                text="🎨",
                command=lambda sid=session_id: self.choose_session_color(sid),
                width=35,
                height=35,
                font=("Arial", 12),
                fg_color=session_color,
                hover_color="#5A5A5A"
            )
            color_btn.pack(side="top", pady=(0, 5))

            # Rename-Button
            rename_btn = ctk.CTkButton(
                button_container,
                text="✏️",
                command=lambda sid=session_id: self.rename_session(sid),
                width=35,
                height=35,
                font=("Arial", 12),
                fg_color="#4A4A4A",
                hover_color="#5A5A5A"
            )
            rename_btn.pack(side="top")
    
    def rename_session(self, session_id):
        """Zeigt einen Dialog zum Umbenennen einer Session"""
        if session_id not in self.sessions:
            return
            
        session_data = self.sessions[session_id]
        current_name = session_data.get("name", f"Session {session_id[-8:]}")
        
        # Dialog-Fenster erstellen
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Session umbenennen")
        dialog.geometry("400x200")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Dialog zentrieren
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (200 // 2)
        dialog.geometry(f"400x200+{x}+{y}")
        
        # Dialog-Inhalt
        title_label = ctk.CTkLabel(dialog, text="Session umbenennen", 
                                  font=("Arial", 16, "bold"))
        title_label.pack(pady=(20, 10))
        
        info_label = ctk.CTkLabel(dialog, text=f"Session ID: {session_id[-8:]}",
                                 font=("Arial", 10))
        info_label.pack(pady=5)
        
        # Name-Input
        name_label = ctk.CTkLabel(dialog, text="Neuer Name:", 
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
                # Name in Session-Daten aktualisieren
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
                    self.console_print(f"❌ Fehler beim Umbenennen/Speichern der Session-Datei: {e}", "warning")
                # UI aktualisieren
                self.update_session_list()
                self.update_current_session_display()
                self.console_print(f"✅ Session umbenannt: '{new_name}'", "success")
                dialog.destroy()
            elif not new_name:
                # Fehlermeldung für leeren Namen
                error_label = ctk.CTkLabel(dialog, text="⚠️ Name darf nicht leer sein!", 
                                         text_color="red", font=("Arial", 10, "bold"))
                error_label.pack(pady=5)
                dialog.after(2000, error_label.destroy)  # Nach 2 Sekunden entfernen
            else:
                dialog.destroy()  # Kein Änderung
        
        def cancel():
            dialog.destroy()
        
        # Enter-Taste für Speichern binden
        dialog.bind('<Return>', lambda e: save_name())
        dialog.bind('<Escape>', lambda e: cancel())
        
        save_btn = ctk.CTkButton(button_frame, text="💾 Speichern", 
                                command=save_name, fg_color="#2B8A3E", 
                                hover_color="#37A24B")
        save_btn.pack(side="left", padx=5)
        
        cancel_btn = ctk.CTkButton(button_frame, text="❌ Abbrechen", 
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
        color_dialog.title(f"Farbe wählen: {session_name}")
        color_dialog.geometry("700x600")  # Größer gemacht
        color_dialog.transient(self.root)
        color_dialog.grab_set()
        color_dialog.resizable(False, False)  # Feste Größe
        
        # Dialog zentrieren
        color_dialog.update_idletasks()
        x = (color_dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (color_dialog.winfo_screenheight() // 2) - (600 // 2)
        color_dialog.geometry(f"700x600+{x}+{y}")
        
        # Dialog-Inhalt direkt auf dem Dialog (ohne zusätzliche Frames)
        title_label = ctk.CTkLabel(color_dialog, text=f"Farbe für '{session_name}' wählen", 
                                  font=("Arial", 16, "bold"))
        title_label.pack(pady=(20, 5))
        
        info_label = ctk.CTkLabel(color_dialog, text=f"Session ID: {session_id[-8:]}",
                                 font=("Arial", 10))
        info_label.pack(pady=(0, 15))
        
        # Aktuelle Farbe Variable
        selected_color = tk.StringVar(value=current_color)
        
        # Horizontal Layout für Farbkreis und Optionen
        content_frame = tk.Frame(color_dialog, bg='#212121')  # Standard Frame statt CTkFrame
        content_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Linke Seite: Farbkreis
        wheel_frame = tk.Frame(content_frame, bg='#212121')  # Standard Frame
        wheel_frame.pack(side="left", padx=(0, 20))
        
        wheel_label = ctk.CTkLabel(wheel_frame, text="🎨 Farbkreis", font=("Arial", 14, "bold"))
        wheel_label.pack(pady=(20, 10))
        
        # Farbkreis Widget
        color_wheel = ColorWheel(wheel_frame, size=220, initial_color=current_color)  # Größer
        color_wheel.pack(pady=10)
        
        # Rechte Seite: Vorschau und vordefinierte Farben
        options_frame = tk.Frame(content_frame, bg='#212121')  # Standard Frame
        options_frame.pack(side="right", fill="both", expand=True)
        
        # Farbvorschau
        preview_label = ctk.CTkLabel(options_frame, text="Vorschau:", font=("Arial", 14, "bold"))
        preview_label.pack(pady=(20, 10))
        
        # Preview Button (zeigt die aktuell gewählte Farbe)
        def update_preview():
            color = selected_color.get()
            preview_btn.configure(fg_color=color)
            hex_label.configure(text=f"Hex: {color}")
            
        preview_btn = ctk.CTkButton(
            options_frame,
            text=f"📝 {session_name}",
            fg_color=current_color,
            width=200,
            height=60,  # Höher für bessere Sichtbarkeit
            font=("Arial", 14, "bold"),
            state="disabled"  # Nur zur Anzeige
        )
        preview_btn.pack(pady=(10, 10))
        
        # Hex-Wert Anzeige
        hex_label = ctk.CTkLabel(options_frame, text=f"Hex: {current_color}", 
                                font=("Arial", 12))
        hex_label.pack(pady=(0, 20))
        
        # Callback für Farbkreis
        def on_wheel_color_change(color):
            selected_color.set(color)
            update_preview()
            
        color_wheel.set_color_callback(on_wheel_color_change)
        
        # Farbauswahl - Vordefinierte Farben (größer und übersichtlicher)
        colors_label = ctk.CTkLabel(options_frame, text="Vordefinierte Farben:", font=("Arial", 13, "bold"))
        colors_label.pack(pady=(10, 15))
        
        # Beliebte Farben für Sessions
        predefined_colors = [
            ("#1f538d", "Blau"),
            ("#2B8A3E", "Grün"),
            ("#C92A2A", "Rot"), 
            ("#E67700", "Orange"),
            ("#6741D9", "Lila"),
            ("#C2185B", "Pink"),
            ("#00695C", "Türkis"),
            ("#4A4A4A", "Grau")
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
                text=name,  # Text anzeigen für bessere Übersicht
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
                # Farbe in Session-Daten aktualisieren
                self.sessions[session_id]["color"] = new_color
                self.sessions[session_id]["last_modified"] = datetime.now().isoformat()
                # Session speichern
                self.save_session_with_feedback()
                # UI aktualisieren
                self.update_session_list()
                # Wenn die aktuelle Session geändert wurde, Anzeige sofort aktualisieren
                if hasattr(self, 'current_session_id') and self.current_session_id == session_id:
                    self.update_current_session_display()
                self.console_print(f"🎨 Session-Farbe geändert: {new_color}", "success")
            color_dialog.destroy()
        
        def cancel_color():
            color_dialog.destroy()
        
        # Enter/Escape Bindings
        color_dialog.bind('<Return>', lambda e: save_color())
        color_dialog.bind('<Escape>', lambda e: cancel_color())
        
        save_btn = ctk.CTkButton(button_frame, text="💾 Speichern", 
                                command=save_color, fg_color="#2B8A3E", 
                                hover_color="#37A24B",
                                width=120, height=45,  # Größer
                                font=("Arial", 14, "bold"))
        save_btn.pack(side="left", padx=20, pady=10)
        
        cancel_btn = ctk.CTkButton(button_frame, text="❌ Abbrechen", 
                                  command=cancel_color, fg_color="#C92A2A", 
                                  hover_color="#E03131",
                                  width=120, height=45,  # Größer
                                  font=("Arial", 14, "bold"))
        cancel_btn.pack(side="left", padx=20, pady=10)
        
        # Initiale Vorschau aktualisieren
        update_preview()
    
    def compress_chat_history(self, history, max_entries=None):
        """Komprimiert die Chat-History um Tokens zu sparen
        
        Args:
            history (list): Original Chat-History
            max_entries (int): Maximale Anzahl der letzten Nachrichten (None = aus Config)
            
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
        
        # Behalte nur die letzten max_entries Nachrichten
        recent_history = history[-max_entries:] if len(history) > max_entries else history
        
        compressed = []
        for msg in recent_history:
            if msg.get("role") == "system":
                # System-Nachrichten (BIAS) behalten - minimal kürzen
                content = msg.get("content", "").strip()
                compressed.append({"role": "system", "content": content})
                
            elif msg.get("role") == "user":
                # User-Nachrichten: Whitespace normalisieren
                content = msg.get("content", "")
                content = " ".join(content.split())  # Normalisiere Whitespace
                compressed.append({"role": "user", "content": content})
                
            elif msg.get("role") == "assistant":
                # AI-Nachrichten: Stärker komprimieren
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
                # Stille Fehlerbehandlung - nur bei kritischen Fehlern anzeigen
                pass
    
    def update_current_session_display(self):
        """Aktualisiert die Anzeige der aktuellen Session"""
        if not hasattr(self, 'current_session_label'):
            return
            
        if self.current_session_id and self.current_session_id in self.sessions:
            session_data = self.sessions[self.current_session_id]
            session_name = session_data.get("name", f"Session {self.current_session_id[-8:]}")
            created_date = session_data.get("created_at", "Unbekannt")
            
            if created_date != "Unbekannt":
                try:
                    date_obj = datetime.fromisoformat(created_date)
                    date_str = date_obj.strftime("%d.%m.%Y %H:%M")
                except:
                    date_str = created_date[:16]
            else:
                date_str = created_date
            
            # Wort-Anzahl für aktuelle Session berechnen
            word_count = self.calculate_session_word_count(session_data)
            word_display = f"{word_count}W" if word_count < 1000 else f"{word_count//1000:.1f}kW"
            
            session_color = session_data.get("color", "#4A4A4A")
            self.current_session_label.configure(
                text=f"📝 {session_name}\nID: {self.current_session_id[:8]}...\nErstellt: {date_str}\n📊 {word_display}",
                fg_color=session_color,
                text_color="#000000"
            )
            
            # Model Info - handle None values correctly
            model_info = session_data.get("model", None)
            if model_info is None or model_info == "":
                model_display = "Nicht ausgewählt"
            else:
                model_display = model_info
            self.current_model_label.configure(text=f"Model: {model_display}")
        else:
            # Keine aktive Session
            self.current_session_label.configure(
                text="🚫 Keine Session aktiv\n\n💡 Klicken Sie auf '➕ Neue Session'\num zu beginnen"
            )
            self.current_model_label.configure(text="Model: Nicht ausgewählt")

    def save_session_bias(self):
        """Speichert den Session-BIAS"""
        if not hasattr(self, 'session_bias_entry'):
            return
            
        bias_text = self.session_bias_entry.get("1.0", "end-1c")
        self.current_session_bias = bias_text
        
        if self.current_session_id and self.current_session_id in self.sessions:
            self.sessions[self.current_session_id]["bias"] = bias_text
            
        self.console_print("💾 Session-BIAS gespeichert", "success")
        self.update_bias_info_label()
    
    def on_bias_text_changed(self, event=None):
        """Wird aufgerufen, wenn sich der BIAS-Text ändert (Auto-Save mit Verzögerung)"""
        # Vorherigen Timer stoppen
        if hasattr(self, 'bias_auto_save_timer') and self.bias_auto_save_timer:
            self.root.after_cancel(self.bias_auto_save_timer)
        
        # Neuen Timer für verzögerte Speicherung starten (1 Sekunde nach letzter Eingabe)
        self.bias_auto_save_timer = self.root.after(1000, self.auto_save_bias)
    
    def auto_save_bias(self):
        """Automatische BIAS-Speicherung"""
        if not hasattr(self, 'session_bias_entry'):
            return
            
        bias_text = self.session_bias_entry.get("1.0", "end-1c").strip()
        old_bias = self.current_session_bias
        
        # Nur speichern wenn sich der Text geändert hat
        if bias_text != old_bias:
            self.current_session_bias = bias_text
            
            if self.current_session_id and self.current_session_id in self.sessions:
                self.sessions[self.current_session_id]["bias"] = bias_text
                # Session automatisch speichern
                self.silent_save_session()
                
            self.update_bias_info_label()
            
            if bias_text:
                self.console_print("💭 BIAS automatisch aktualisiert", "info")
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
                text=f"💭 BIAS aktiv: {preview}",
                text_color="#4CAF50"  # Grün für aktiv
            )
        else:
            self.bias_info_label.configure(
                text="💭 BIAS nicht gesetzt",
                text_color="gray"
            )

    def delete_current_session(self):
        """Löscht die aktuelle Session"""
        if not self.current_session_id:
            return
            
        # Bestätigungs-Dialog
        result = messagebox.askyesno(
            "Session löschen",
            f"Möchten Sie die Session {self.current_session_id} wirklich löschen?\n\nDieser Vorgang kann nicht rückgängig gemacht werden."
        )
        
        if result:
            deleted_session_id = self.current_session_id
            
            # Alle zugehörigen Session-Dateien löschen (unabhängig vom Namen)
            try:
                deleted_files = 0
                for f in os.listdir(self.sessions_dir):
                    if f.endswith(f"_session_{self.current_session_id}.json"):
                        file_path = os.path.join(self.sessions_dir, f)
                        try:
                            os.remove(file_path)
                            deleted_files += 1
                        except Exception as e:
                            self.console_print(f"❌ Fehler beim Löschen der Session-Datei {f}: {e}", "error")
                if deleted_files == 0:
                    self.console_print(f"⚠️ Keine Session-Datei für {self.current_session_id} gefunden.", "warning")
            except Exception as e:
                self.console_print(f"❌ Fehler beim Löschen der Session-Dateien: {e}", "error")
            
            # Session aus Speicher entfernen
            if self.current_session_id in self.sessions:
                del self.sessions[self.current_session_id]
            
            # Sessions persistent speichern
            try:
                with open("sessions.json", "w", encoding="utf-8") as f:
                    json.dump(self.sessions, f, indent=2, ensure_ascii=False)
            except Exception as e:
                self.console_print(f"❌ Fehler beim Speichern der Session-Liste: {e}", "error")
            
            self.console_print(f"🗑️ Session gelöscht: {deleted_session_id}", "warning")
            
            # Prüfe ob noch andere Sessions vorhanden sind
            if self.sessions:
                # Lade die neueste verfügbare Session
                latest_session = max(self.sessions.keys(), 
                                   key=lambda x: self.sessions[x].get("created_at", ""))
                self.load_session(latest_session)
                self.console_print(f"🔄 Gewechselt zu Session: {latest_session}", "info")
            else:
                # Alle Sessions gelöscht - Chat leeren aber keine neue Session erstellen
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
                    self.model_dropdown.set("Keine Modelle verfügbar")
                
                self.console_print("🔄 Alle Sessions gelöscht - Chat bereit für neue Session", "info")

    def delete_all_sessions(self):
        """Löscht alle Sessions nach Bestätigung"""
        if not self.sessions:
            messagebox.showinfo("Keine Sessions", "Es sind keine Sessions zum Löschen vorhanden.")
            return
        
        session_count = len(self.sessions)
        
        # Bestätigungs-Dialog
        result = messagebox.askyesno(
            "Alle Sessions löschen",
            f"Möchten Sie wirklich ALLE {session_count} Sessions löschen?\n\n⚠️ WARNUNG: Dieser Vorgang kann nicht rückgängig gemacht werden!\nAlle Chat-Verläufe und Session-Daten gehen verloren."
        )
        
        if result:
            # Alle Session-Dateien löschen
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
                            self.console_print(f"❌ Fehler beim Löschen von {f}: {e}", "error")
                if not found_file:
                    self.console_print(f"⚠️ Keine Session-Datei für {session_id} gefunden.", "warning")
            
            # Alle Sessions aus Speicher entfernen
            self.sessions.clear()
            self.current_session_id = None
            
            # Sessions-Datei aktualisieren (leere Datei)
            try:
                with open("sessions.json", "w", encoding="utf-8") as f:
                    json.dump({}, f, indent=2, ensure_ascii=False)
            except Exception as e:
                self.console_print(f"❌ Fehler beim Speichern der leeren Session-Liste: {e}", "error")
            
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
                self.model_dropdown.set("Keine Modelle verfügbar")
            
            # Ergebnis anzeigen
            if failed_count == 0:
                self.console_print(f"🧹 Alle {deleted_count} Sessions erfolgreich gelöscht", "success")
                messagebox.showinfo(
                    "Bereinigung abgeschlossen", 
                    f"✅ Alle {deleted_count} Sessions wurden erfolgreich gelöscht.\n\nKlicken Sie auf '➕ Neue Session' um zu beginnen."
                )
            else:
                self.console_print(f"🧹 {deleted_count} Sessions gelöscht, {failed_count} Fehler", "warning")
                messagebox.showwarning(
                    "Bereinigung mit Fehlern", 
                    f"⚠️ {deleted_count} Sessions gelöscht, aber {failed_count} Fehler aufgetreten.\nSiehe Konsole für Details."
                )

    def clear_chat_for_new_session(self):
        """Leert den Chat für eine neue Session"""
        # Lösche alle Chat-Bubbles
        if hasattr(self, 'chat_bubbles'):
            for bubble in self.chat_bubbles:
                try:
                    bubble.destroy()
                except:
                    pass
            self.chat_bubbles.clear()
        
        # Chat-History leeren
        self.chat_history.clear()
        self.message_history.clear()
        self.history_index = -1
        
        # Layout vollständig aktualisieren nach dem Löschen
        if hasattr(self, 'chat_display_frame'):
            self.chat_display_frame.update_idletasks()
            if hasattr(self.chat_display_frame, '_parent_canvas'):
                self.chat_display_frame._parent_canvas.update_idletasks()
                # Scrollregion zurücksetzen
                self.chat_display_frame._parent_canvas.configure(scrollregion=self.chat_display_frame._parent_canvas.bbox("all"))
                # Nach oben scrollen (für leere Chats)
                self.chat_display_frame._parent_canvas.yview_moveto(0.0)

    def restore_chat_message(self, msg_data):
        """Stellt eine Chat-Nachricht aus Session-Daten wieder her"""
        timestamp = msg_data.get("timestamp", datetime.now().strftime("%H:%M:%S"))
        sender = msg_data.get("sender", "System")
        message = msg_data.get("message", "")
        
        # System-Nachrichten ausblenden wenn Flag gesetzt ist (gleiche Logik wie in add_to_chat)
        if sender == "System" and not self.config.get("show_system_messages", True):
            return  # Keine UI-Bubble erstellen für ausgeblendete System-Nachrichten
        
        # Chat-Bubble erstellen
        bubble = ChatBubble(
            self.chat_display_frame,
            sender=sender,
            message=message,
            timestamp=timestamp,
            app_config=self.config
        )
        
        self.chat_bubbles.append(bubble)

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
        
        # Chat-Bereich (Modell-Management jetzt im Session Panel)
        self.chat_frame = ctk.CTkFrame(self.chat_tab)
        self.chat_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Chat-Verlauf mit Scrollable Frame
        self.chat_display_frame = ctk.CTkScrollableFrame(
            self.chat_frame,
            label_text="Chat-Verlauf"
        )
        self.chat_display_frame.pack(fill="both", expand=True, padx=10, pady=(10, 5))
        
        # Liste für Chat-Bubbles
        self.chat_bubbles = []
        
        # Eingabe-Bereich
        self.input_frame = ctk.CTkFrame(self.chat_frame)
        self.input_frame.pack(fill="x", padx=self.config.get("ui_padding_main", 10), 
                             pady=(self.config.get("ui_padding_content", 5), self.config.get("ui_padding_main", 10)))
        
        self.message_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Nachricht eingeben...",
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
            text="Senden",
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
        config_scroll = ctk.CTkScrollableFrame(config_container, label_text="Konfiguration")
        config_scroll.pack(fill="both", expand=True, padx=10, pady=(10, 10))
        
        # Fixierte Button-Leiste am unteren Rand
        button_frame = ctk.CTkFrame(config_container)
        button_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Container für zentrierte Buttons
        button_container = ctk.CTkFrame(button_frame)
        button_container.pack(expand=True)
        
        # Buttons nebeneinander zentriert
        restart_btn = ctk.CTkButton(button_container, text="🔄 Übernehmen & Neustart", 
                                   command=self.apply_and_restart, 
                                   width=200, height=40, font=("Arial", 13, "bold"),
                                   fg_color="#1f538d", hover_color="#2a6bb0")
        restart_btn.pack(side="left", padx=10, pady=15)
        
        reset_btn = ctk.CTkButton(button_container, text="↩️ Standard", command=self.reset_config, 
                                 width=150, height=40, font=("Arial", 13, "bold"),
                                 fg_color="#722F37", hover_color="#8a3a45")
        reset_btn.pack(side="left", padx=10, pady=15)
        
        # Bubble-Farben Sektion
        bubble_frame = ctk.CTkFrame(config_scroll)
        bubble_frame.pack(fill="x", pady=(0, 20))
        
        bubble_title = ctk.CTkLabel(bubble_frame, text="🎨 Chat-Bubble Farben", font=("Arial", 16, "bold"))
        bubble_title.pack(pady=(15, 10))
        
        # Sie (User) Farben - Komprimiert
        user_main_frame = ctk.CTkFrame(bubble_frame)
        user_main_frame.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(user_main_frame, text="💬 Sie:", font=("Arial", 11, "bold"), width=50).pack(side="left", padx=5)
        
        user_colors_frame = ctk.CTkFrame(user_main_frame)
        user_colors_frame.pack(side="left", fill="x", expand=True, padx=5)
        
        self.user_bg_entry, self.user_bg_preview = self.setup_color_input_with_preview(
            user_colors_frame, "Hintergrund:", "user_bg_color", "#003300")
        self.user_text_entry, self.user_text_preview = self.setup_color_input_with_preview(
            user_colors_frame, "Text:", "user_text_color", "#00FF00")
        
        # AI-Modell Farben - Komprimiert  
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
        
        font_title = ctk.CTkLabel(font_frame, text="🔤 Schriftarten", font=("Arial", 16, "bold"))
        font_title.pack(pady=(10, 5))
        
        # Font-Dropdowns mit individuellen Größen
        font_dropdowns_frame = ctk.CTkFrame(font_frame)
        font_dropdowns_frame.pack(fill="x", padx=20, pady=10)
        
        # User Font mit Größen-Slider
        user_font_frame = ctk.CTkFrame(font_dropdowns_frame)
        user_font_frame.pack(fill="x", pady=3)
        
        # Label und Dropdown
        ctk.CTkLabel(user_font_frame, text="Sie (Matrix):", width=100).pack(side="left", padx=5)
        self.user_font_combo = ctk.CTkComboBox(user_font_frame, 
            values=["Courier New", "Consolas", "Monaco", "Lucida Console"],
            width=130, command=self.update_user_font_preview)
        self.user_font_combo.pack(side="left", padx=5)
        self.user_font_combo.set(self.config["user_font"])
        
        # Mausrad-Scrolling für user_font_combo aktivieren
        
        # Größen-Slider
        ctk.CTkLabel(user_font_frame, text="Größe:", width=40).pack(side="left", padx=(15, 2))
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
        ctk.CTkLabel(ai_font_frame, text="AI-Modell:", width=100).pack(side="left", padx=5)
        self.ai_font_combo = ctk.CTkComboBox(ai_font_frame,
            values=["Consolas", "Courier New", "Arial", "Segoe UI"],
            width=130, command=self.update_ai_font_preview)
        self.ai_font_combo.pack(side="left", padx=5)
        self.ai_font_combo.set(self.config["ai_font"])
        
        # Mausrad-Scrolling für ai_font_combo aktivieren
        
        # Größen-Slider
        ctk.CTkLabel(ai_font_frame, text="Größe:", width=40).pack(side="left", padx=(15, 2))
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
        ctk.CTkLabel(system_font_frame, text="Größe:", width=40).pack(side="left", padx=(15, 2))
        self.system_font_size_slider = ctk.CTkSlider(system_font_frame, from_=8, to=24, number_of_steps=16, width=100)
        self.system_font_size_slider.pack(side="left", padx=3)
        self.system_font_size_slider.set(self.config["system_font_size"])
        self.system_font_size_label = ctk.CTkLabel(system_font_frame, text=f"{self.config['system_font_size']}px", width=30)
        self.system_font_size_label.pack(side="left", padx=3)
        self.system_font_size_slider.configure(command=self.update_system_font_preview)
        
        # Preview
        self.system_font_preview = ctk.CTkLabel(system_font_frame, text="ℹ️ System-Nachricht", 
                                               font=(self.config["system_font"], self.config["system_font_size"]),
                                               text_color="#FFFFFF", width=150)
        self.system_font_preview.pack(side="left", padx=10)
        
        
        # ========== UI-EINSTELLUNGEN SEKTION ==========
        ui_settings_frame = ctk.CTkFrame(config_scroll)
        ui_settings_frame.pack(fill="x", pady=(10, 15))
        
        ui_settings_title = ctk.CTkLabel(ui_settings_frame, text="🎛️ Layout & Größen", font=("Arial", 16, "bold"))
        ui_settings_title.pack(pady=(15, 10))
        
        # Session Panel Breite
        self.create_config_slider(ui_settings_frame, "Session-Panel Breite:", "ui_session_panel_width", 
                                 200, 600, self.config.get('ui_session_panel_width', 350), "px")
        
        # Fenster-Startgröße
        self.create_config_slider(ui_settings_frame, "Fensterbreite (Start):", "ui_window_width", 
                                 1000, 2560, self.config.get('ui_window_width', 1400), "px")
        self.create_config_slider(ui_settings_frame, "Fensterhöhe (Start):", "ui_window_height", 
                                 600, 1440, self.config.get('ui_window_height', 900), "px")
        
        # Input & Buttons
        ui_input_title = ctk.CTkLabel(ui_settings_frame, text="⌨️ Eingabe & Buttons", font=("Arial", 14, "bold"))
        ui_input_title.pack(pady=(15, 5))
        
        self.create_config_slider(ui_settings_frame, "Eingabefeld-Höhe:", "ui_input_height", 
                                 30, 60, self.config.get('ui_input_height', 40), "px")
        self.create_config_slider(ui_settings_frame, "Eingabe-Schriftgröße:", "ui_input_font_size", 
                                 9, 18, self.config.get('ui_input_font_size', 12), "px")
        self.create_config_slider(ui_settings_frame, "Button-Breite:", "ui_button_width", 
                                 60, 150, self.config.get('ui_button_width', 100), "px")
        self.create_config_slider(ui_settings_frame, "Button-Höhe:", "ui_button_height", 
                                 25, 60, self.config.get('ui_button_height', 40), "px")
        
        # Erweiterte Optionen
        ui_options_title = ctk.CTkLabel(ui_settings_frame, text="⚡ Erweiterte Optionen", font=("Arial", 14, "bold"))
        ui_options_title.pack(pady=(15, 5))
        
        options_frame = ctk.CTkFrame(ui_settings_frame)
        options_frame.pack(fill="x", padx=15, pady=(5, 10))
        
        # System-Nachrichten Toggle (verschoben hierher)
        self.show_system_messages_var = ctk.BooleanVar(value=self.config.get("show_system_messages", True))
        system_msg_checkbox = ctk.CTkCheckBox(
            options_frame,
            text="📢 System-Nachrichten im Chat anzeigen",
            variable=self.show_system_messages_var,
            font=("Arial", 11)
        )
        system_msg_checkbox.pack(anchor="w", padx=10, pady=5)
        
        self.auto_scroll_var = ctk.BooleanVar(value=self.config.get("auto_scroll_chat", True))
        auto_scroll_cb = ctk.CTkCheckBox(options_frame, text="📜 Auto-Scroll zu neuen Nachrichten", 
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
                initial_color = "#00FF00"  # Standard-Grün
            
            # Farbwähler öffnen
            color = colorchooser.askcolor(
                color=initial_color,
                title="🎨 Farbe auswählen",
                parent=self.root
            )
            
            # Wenn eine Farbe gewählt wurde, aktualisiere das Entry-Feld
            if color[1]:  # color[1] enthält den Hex-Wert
                entry_widget.delete(0, 'end')
                entry_widget.insert(0, color[1].upper())
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Öffnen des Farbwählers: {e}")
    
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
            
            # Farbwähler öffnen
            color = colorchooser.askcolor(
                color=initial_color,
                title="🎨 Farbe auswählen",
                parent=self.root
            )
            
            # Wenn eine Farbe gewählt wurde, aktualisiere Entry und Preview
            if color[1]:
                hex_color = color[1].upper()
                entry_widget.delete(0, 'end')
                entry_widget.insert(0, hex_color)
                preview_label.configure(fg_color=hex_color)
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Fehler beim Öffnen des Farbwählers: {e}")
    
    def update_user_font_preview(self, value=None):
        """Aktualisiert User Font Preview"""
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
            
            # Speichere Konfiguration in YAML-Datei
            self.save_config()
            
            # Aktualisiere alle bestehenden Chat-Bubbles mit neuer Konfiguration
            self.update_all_chat_bubbles()
            
            # Show success message
            self.add_to_chat("System", "✅ Konfiguration erfolgreich angewendet und gespeichert! Änderungen werden beim nächsten Start vollständig übernommen.")
            
            # Info bei UI-Layout-Änderungen
            if hasattr(self, 'config_sliders'):
                self.add_to_chat("System", "ℹ️ Layout-Änderungen (Panel-Größen, Button-Größen etc.) werden beim nächsten Neustart der App aktiv.")
            
        except Exception as e:
            self.add_to_chat("System", f"❌ Fehler beim Anwenden der Konfiguration: {e}")
    
    def apply_and_restart(self):
        """Wendet Konfiguration an und startet die Anwendung neu"""
        try:
            # Speichere Konfiguration
            self.apply_config()
            
            # Kurze Pause damit Nutzer die Bestätigung sieht
            self.root.after(800, self.restart_application)
            
        except Exception as e:
            self.add_to_chat("System", f"❌ Fehler beim Neustart: {e}")
    
    def restart_application(self):
        """Startet die Anwendung neu mit dem restart.py Script"""
        try:
            import sys
            import subprocess
            import os
            
            self.add_to_chat("System", "🔄 Anwendung wird neu gestartet...")
            self.root.update()
            
            # Speichere aktuelle Session
            if hasattr(self, 'current_session_id') and self.current_session_id:
                if hasattr(self, 'save_session'):
                    self.save_session()
            
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
            self.add_to_chat("System", f"❌ Fehler beim Neustart der Anwendung: {e}")
    
    def update_all_chat_bubbles(self):
        """Aktualisiert das Styling aller bestehenden Chat-Bubbles"""
        try:
            updated_count = 0
            for bubble in self.chat_bubbles:
                bubble.update_style(self.config)
                updated_count += 1
            
            if updated_count > 0:
                self.console_print(f"🎨 {updated_count} Chat-Bubbles mit neuer Konfiguration aktualisiert", "info")
                
                # Scrolle den Chat-Bereich nach unten, um Updates sichtbar zu machen
                self.chat_display_frame._parent_canvas.after(100, 
                    lambda: self.chat_display_frame._parent_canvas.yview_moveto(1.0))
                    
        except Exception as e:
            self.console_print(f"❌ Fehler beim Aktualisieren der Chat-Bubbles: {e}", "error")
    
    
    def reset_config(self):
        """Setzt die Konfiguration auf Standardwerte zurück"""
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
        
        self.add_to_chat("System", "🔄 Konfiguration auf Standardwerte zurückgesetzt und gespeichert!")
    
    def check_ollama_status(self):
        """Prüft Ollama-Status und lädt Modelle"""
        def check():
            if self.ollama.is_ollama_running():
                self.status_label.configure(text="Ollama Status: ✅ Verbunden")
                self.refresh_models()
                self.load_available_models()
            else:
                self.status_label.configure(text="Ollama Status: ❌ Nicht verbunden")
                self.add_to_chat("System", "Ollama ist nicht erreichbar. Stellen Sie sicher, dass Ollama läuft.")
        
        threading.Thread(target=check, daemon=True).start()
    
    def load_available_models(self):
        """Lädt alle verfügbaren Ollama-Modelle und kategorisiert sie"""
        def load():
            self.add_to_chat("System", "🔄 Lade aktuelle Modell-Liste von Ollama...")
            all_models = self.ollama.get_all_ollama_models()
            
            if all_models:
                categories = self.ollama.categorize_models_by_size(all_models)
                self.root.after(0, lambda: self.available_dropdown.set_categories(categories))
                self.root.after(0, lambda: self.available_dropdown.set("🔍 Wählen Sie eine Kategorie oder Modell..."))
                
                # Mausrad-Scrolling nach dem Setzen der Kategorien nochmals sicherstellen
                
                model_count = sum(len(models) for models in categories.values())
                self.root.after(0, lambda: self.add_to_chat("System", 
                    f"✅ {model_count} Modelle in {len([c for c in categories.values() if c])} Kategorien geladen"))
            else:
                empty_categories = {"❌ Keine Modelle verfügbar": []}
                self.root.after(0, lambda: self.available_dropdown.set_categories(empty_categories))
                self.root.after(0, lambda: self.add_to_chat("System", "❌ Keine Modelle verfügbar"))
        
        threading.Thread(target=load, daemon=True).start()
    
    def refresh_models(self):
        """Aktualisiert die Modell-Listen"""
        def update():
            # Installierte Modelle aktualisieren
            models = self.ollama.get_available_models()
            if models:
                self.root.after(0, lambda: self.model_dropdown.configure(values=models))
                if not self.current_model or self.current_model not in models:
                    self.root.after(0, lambda: self.model_dropdown.set(models[0]))
                    self.current_model = models[0]
            else:
                self.root.after(0, lambda: self.model_dropdown.configure(values=["Keine Modelle verfügbar"]))
                self.current_model = None
            
            # Verfügbare Modelle aktualisieren (kategorisiert)
            all_models = self.ollama.get_all_ollama_models()
            if all_models:
                categories = self.ollama.categorize_models_by_size(all_models)
                self.root.after(0, lambda: self.available_dropdown.set_categories(categories))
                if self.available_var.get() in ["Lade Modell-Liste...", ""]:
                    self.root.after(0, lambda: self.available_dropdown.set("🔍 Wählen Sie eine Kategorie oder Modell..."))
        
        threading.Thread(target=update, daemon=True).start()
    
    def on_model_select(self, choice):
        """Behandelt Modell-Auswahl"""
        if choice != "Keine Modelle verfügbar":
            self.current_model = choice
            
            # Chat-Historie nur bei neuen/leeren Sessions zurücksetzen
            # Bei bestehenden Sessions mit Nachrichten die Historie beibehalten
            if not hasattr(self, 'chat_bubbles') or len(self.chat_bubbles) == 0:
                self.chat_history = []  # Nur bei leeren Sessions zurücksetzen
                self.console_print(f"🔄 Neue Session - Chat-Historie zurückgesetzt", "info")
            else:
                self.console_print(f"📚 Bestehende Session - Chat-Historie beibehalten ({len(self.chat_history)} Nachrichten)", "info")
            
            # Model in aktueller Session speichern
            if hasattr(self, 'current_session_id') and self.current_session_id:
                if self.current_session_id in self.sessions:
                    self.sessions[self.current_session_id]["model"] = choice
                    self.sessions[self.current_session_id]["last_modified"] = datetime.now().isoformat()
                    
                    # Session persistent speichern
                    self.save_session_with_feedback()
                    
                    # UI vollständig aktualisieren
                    self.update_current_session_display()
                    self.update_session_list()
            
            self.add_to_chat("System", f"Modell gewechselt zu: {choice}")
            self.console_print(f"🤖 Model gewechselt: {choice}", "info")
    
    def show_download_dialog(self):
        """Zeigt Dialog zum Modell-Download"""
        dialog = ctk.CTkInputDialog(
            text="Geben Sie den Modellnamen ein (z.B. llama2, mistral, codellama):",
            title="Modell herunterladen"
        )
        model_name = dialog.get_input()
        
        if model_name:
            self.download_model(model_name)
    
    def download_selected_model(self):
        """Lädt das ausgewählte Modell aus dem Dropdown herunter"""
        selected_model = self.available_dropdown.get_selected_model()
        
        if not selected_model:
            messagebox.showwarning("Warnung", "Bitte wählen Sie ein Modell zum Download aus!\n\nHinweis: Kategorie-Header (--- Text ---) sind nicht herunterladbar.")
            return
        
        if selected_model in ["🔍 Wählen Sie eine Kategorie oder Modell...", "Keine Modelle verfügbar", "Lade Modell-Liste..."]:
            messagebox.showwarning("Warnung", "Bitte wählen Sie ein gültiges Modell zum Download aus!")
            return
        
        # Prüfen ob das Modell bereits installiert ist
        installed_models = self.ollama.get_available_models()
        if selected_model in installed_models:
            result = messagebox.askyesno(
                "Modell bereits vorhanden", 
                f"'{selected_model}' ist bereits installiert. Trotzdem erneut herunterladen?"
            )
            if not result:
                return
        
        self.download_model(selected_model)
    
    def download_model(self, model_name):
        """Lädt ein Modell mit verbessertem UI-Feedback und Stop-Funktionalität herunter"""
        self.progress_frame.pack(fill="x", padx=10, pady=5)
        self.add_to_chat("System", f"🚀 Download von {model_name} gestartet...")
        self.add_to_chat("System", f"💡 Konsolen-Output für Details öffnen!")
        
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
                    self.add_to_chat("System", f"🛑 Download von {model_name} gestoppt nach {total_time/60:.1f} Minuten")
                elif success:
                    self.add_to_chat("System", f"✅ {model_name} erfolgreich heruntergeladen! ({total_time/60:.1f} Minuten)")
                    self.refresh_models()
                else:
                    self.add_to_chat("System", f"❌ Fehler beim Download von {model_name} nach {total_time/60:.1f} Minuten")
                
                # UI zurücksetzen
                self.reset_download_ui()
            
            self.root.after(0, finish)
        
        # Download-Thread starten und speichern
        self.current_download_thread = threading.Thread(target=download, daemon=True)
        self.current_download_thread.start()
    
    def delete_selected_model(self):
        """Löscht das ausgewählte Modell"""
        if not self.current_model:
            messagebox.showwarning("Warnung", "Kein Modell ausgewählt!")
            return
        
        result = messagebox.askyesno(
            "Modell löschen", 
            f"Möchten Sie '{self.current_model}' wirklich löschen?"
        )
        
        if result:
            def delete():
                success = self.ollama.delete_model(self.current_model)
                def finish():
                    if success:
                        self.add_to_chat("System", f"✅ {self.current_model} wurde gelöscht")
                        self.current_model = None
                        self.refresh_models()
                    else:
                        self.add_to_chat("System", f"❌ Fehler beim Löschen von {self.current_model}")
                
                self.root.after(0, finish)
            
            threading.Thread(target=delete, daemon=True).start()
    
    def send_message(self, event=None):
        """Sendet eine Nachricht mit Stop-Funktionalität und Anti-Redundanz"""
        import time
        
        message = self.message_entry.get().strip()
        if not message:
            return
        
        if not self.current_model:
            messagebox.showwarning("Warnung", "Kein Modell ausgewählt!")
            return
        
        # Reset Stop-Flag
        self.generation_stopped = False
        
        # Nachricht zur Historie hinzufügen (nur wenn nicht leer)
        if message and message not in self.message_history:
            self.message_history.append(message)
        # Reset Historie-Index
        self.history_index = -1
        

        # Prüfe, ob die Session vorher leer war (keine Nachrichten)
        session_empty = False
        if self.current_session_id and self.current_session_id in self.sessions:
            session_data = self.sessions[self.current_session_id]
            if not session_data.get("messages"):
                session_empty = True

        # Nachricht anzeigen
        self.add_to_chat("Sie", message)
        self.message_entry.delete(0, 'end')

        # Wenn Session vorher leer war: Session-Liste, Anzeige und Chat-Konsole sofort aktualisieren
        if session_empty:
            self.update_session_list()
            self.update_current_session_display()
            # Scrolle ans Ende der Chat-Konsole (falls vorhanden)
            if hasattr(self, 'chat_display_frame') and hasattr(self.chat_display_frame, '_parent_canvas'):
                self.chat_display_frame._parent_canvas.yview_moveto(1.0)
        
        # UI während Generation anpassen
        self.stop_btn.configure(state="normal")
        self.send_btn.configure(state="disabled")
        
        # Antwort abrufen
        def get_response():
            try:
                # Denkprozess-Indikator hinzufügen
                self.root.after(0, self.add_thinking_indicator)
                
                # Session-BIAS berücksichtigen
                session_bias = ""
                if hasattr(self, 'current_session_bias') and self.current_session_bias:
                    session_bias = self.current_session_bias.strip()
                    print(f"🎯 BIAS aktiv: {session_bias[:50]}...")
                    self.root.after(0, lambda: self.console_print(f"🎯 BIAS mitgesendet: {session_bias[:30]}...", "info"))
                else:
                    print("🎯 Kein BIAS gesetzt")
                
                # Nur bei Session-Laden: volle History, sonst nur BIAS und aktuelle User-Eingabe
                if getattr(self, '_session_just_loaded', False):
                    print("[INFO] Es wird die komplette Session-History an das Modell geschickt (Session wurde gerade geladen).")
                    modified_history = self.chat_history.copy()
                    if session_bias:
                        modified_history.insert(0, {"role": "system", "content": session_bias})
                    self._session_just_loaded = False
                else:
                    # Nur BIAS (falls gesetzt) und aktuelle User-Eingabe
                    modified_history = []
                    if session_bias:
                        modified_history.append({"role": "system", "content": session_bias})
                # Letzte Model-Eingabe für Debug-Zwecke speichern
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
                            self.root.after(0, lambda: self.add_to_chat("System", "🛑 Generation gestoppt"))
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
                        
                        self.root.after(0, show_final_response)
                        
                        # Chat-Historie aktualisieren (ohne BIAS für permanente Historie)
                        self.chat_history.append({"role": "user", "content": message})
                        self.chat_history.append({"role": "assistant", "content": full_response})
                    else:
                        print(f"⚠️ Leere Antwort: {len(full_response)} Zeichen")
                else:
                    print("❌ Kein Response-Stream erhalten")
                    
            except Exception as e:
                if not self.generation_stopped:
                    self.root.after(0, lambda: self.add_to_chat("System", f"❌ Fehler: {str(e)}"))
            finally:
                # UI zurücksetzen
                self.root.after(0, self.reset_generation_ui)
        
        # Thread starten und speichern
        self.current_generation_thread = threading.Thread(target=get_response, daemon=True)
        self.current_generation_thread.start()
    
    def send_message_programmatic(self, message):
        """Sendet eine Nachricht programmatisch (z.B. aus Textbox statt Entry)"""
        if not message or not message.strip():
            return
        
        message = message.strip()
        
        if not self.current_model:
            messagebox.showwarning("Warnung", "Kein Modell ausgewählt!")
            return
        
        # Reset Stop-Flag
        self.generation_stopped = False
        
        # Nachricht zur Historie hinzufügen
        if message and message not in self.message_history:
            self.message_history.append(message)
        self.history_index = -1
        
        # Prüfe, ob Session leer war
        session_empty = False
        if self.current_session_id and self.current_session_id in self.sessions:
            session_data = self.sessions[self.current_session_id]
            if not session_data.get("messages"):
                session_empty = True
        
        # Nachricht anzeigen
        self.add_to_chat("Sie", message)
        
        # Session-Liste aktualisieren wenn vorher leer
        if session_empty:
            self.update_session_list()
            self.update_current_session_display()
            if hasattr(self, 'chat_display_frame') and hasattr(self.chat_display_frame, '_parent_canvas'):
                self.chat_display_frame._parent_canvas.yview_moveto(1.0)
        
        # UI während Generation anpassen
        if hasattr(self, 'stop_btn'):
            self.stop_btn.configure(state="normal")
        if hasattr(self, 'send_btn'):
            self.send_btn.configure(state="disabled")
        
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
                
                # Nachricht zur Chat-History hinzufügen
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
                    self.root.after(0, lambda: self.add_to_chat("System", f"❌ Fehler: {str(e)}"))
            finally:
                self.root.after(0, self.reset_generation_ui)
        
        # Thread starten
        self.current_generation_thread = threading.Thread(target=get_response, daemon=True)
        self.current_generation_thread.start()
    
    def download_model_by_name(self, model_name):
        """Lädt ein Modell nach Namen herunter"""
        if not model_name or not model_name.strip():
            messagebox.showwarning("Warnung", "Bitte geben Sie einen Modellnamen ein!")
            return
        
        model_name = model_name.strip()
        
        # Prüfe ob Modell bereits existiert
        existing_models = self.ollama.list_models()
        if model_name in existing_models:
            messagebox.showinfo("Info", f"Modell '{model_name}' ist bereits installiert!")
            return
        
        # Reset Download-Stop-Flag
        self.download_stopped = False
        
        def download():
            try:
                self.console_print(f"📥 Download gestartet: {model_name}", "info")
                
                # Download mit Progress
                for progress in self.ollama.download_model_stream(model_name):
                    if self.download_stopped:
                        self.console_print(f"⏹️ Download abgebrochen: {model_name}", "warning")
                        break
                    
                    # Progress anzeigen
                    if "status" in progress:
                        status = progress["status"]
                        if "total" in progress and "completed" in progress:
                            percent = (progress["completed"] / progress["total"]) * 100
                            self.console_print(f"📥 {status}: {percent:.1f}%", "info")
                        else:
                            self.console_print(f"📥 {status}", "info")
                
                if not self.download_stopped:
                    self.console_print(f"✅ Download abgeschlossen: {model_name}", "success")
                    # Modell-Liste aktualisieren
                    self.root.after(0, self.update_model_list)
                    
            except Exception as e:
                self.console_print(f"❌ Download-Fehler: {str(e)}", "error")
        
        # Thread starten
        self.current_download_thread = threading.Thread(target=download, daemon=True)
        self.current_download_thread.start()
    
    def export_session_markdown(self):
        """Exportiert die aktuelle Session als Markdown-Datei"""
        if not self.current_session_id:
            messagebox.showwarning("Warnung", "Keine aktive Session zum Exportieren!")
            return
        
        # Session-Daten holen
        session = self.sessions.get(self.current_session_id)
        if not session:
            return
        
        # Dateiname vorschlagen
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"session_{self.current_session_id}_{timestamp}.md"
        
        # Datei-Dialog
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
                
                # Nachrichten
                for msg in session.get('messages', []):
                    role = msg.get('role', 'unknown')
                    content = msg.get('content', '')
                    
                    if role == 'user':
                        f.write(f"## 👤 Sie\n\n{content}\n\n")
                    elif role == 'assistant':
                        f.write(f"## 🤖 AI ({session.get('model', 'Unknown')})\n\n{content}\n\n")
                    elif role == 'system':
                        f.write(f"## ⚙️ System\n\n{content}\n\n")
                    
                    f.write("---\n\n")
            
            messagebox.showinfo("Erfolg", f"Session exportiert nach:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Export fehlgeschlagen:\n{str(e)}")
    
    def export_session_json(self):
        """Exportiert die aktuelle Session als JSON-Datei"""
        if not self.current_session_id:
            messagebox.showwarning("Warnung", "Keine aktive Session zum Exportieren!")
            return
        
        # Session-Daten holen
        session = self.sessions.get(self.current_session_id)
        if not session:
            return
        
        # Dateiname vorschlagen
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"session_{self.current_session_id}_{timestamp}.json"
        
        # Datei-Dialog
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
            
            messagebox.showinfo("Erfolg", f"Session exportiert nach:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("Fehler", f"Export fehlgeschlagen:\n{str(e)}")
    
    def navigate_history_up(self, event=None):
        """Navigiert in der Nachrichten-Historie nach oben (ältere Nachrichten)"""
        if not self.message_history:
            return "break"  # Verhindert Standard-Verhalten
        
        # Wenn wir am Ende der Historie sind, gehe zum neuesten Eintrag
        if self.history_index <= 0:
            self.history_index = len(self.message_history) - 1
        else:
            self.history_index -= 1
        
        # Setze die Nachricht ins Eingabefeld
        message = self.message_history[self.history_index]
        self.message_entry.delete(0, 'end')
        self.message_entry.insert(0, message)
        
        return "break"  # Verhindert Standard-Verhalten der Pfeiltaste
    
    def navigate_history_down(self, event=None):
        """Navigiert in der Nachrichten-Historie nach unten (neuere Nachrichten)"""
        if not self.message_history:
            return "break"
        
        # Wenn wir am Anfang der Historie sind oder keine Auswahl haben
        if self.history_index < 0 or self.history_index >= len(self.message_history) - 1:
            # Lösche das Eingabefeld (neueste "Nachricht" ist leeres Feld)
            self.message_entry.delete(0, 'end')
            self.history_index = -1
        else:
            self.history_index += 1
            # Setze die Nachricht ins Eingabefeld
            message = self.message_history[self.history_index]
            self.message_entry.delete(0, 'end')
            self.message_entry.insert(0, message)
        
        return "break"  # Verhindert Standard-Verhalten der Pfeiltaste
    
    def on_key_press(self, event=None):
        """Wird bei jeder Tasteneingabe aufgerufen - reset Historie-Index wenn getippt wird"""
        # Reset Historie-Index wenn der Benutzer tippt (außer bei Pfeiltasten)
        if event and event.keysym not in ['Up', 'Down']:
            self.history_index = -1
        return None  # Normale Tastatureingabe fortsetzen
    
    def stop_generation(self):
        """Stoppt die aktuelle Generation oder den Download sofort"""
        if self.current_generation_thread is not None:
            # Stoppe Chat-Generation
            self.generation_stopped = True
            self.reset_generation_ui()
            print("\n🛑 Generation gestoppt durch Benutzer")
        
        if self.current_download_thread is not None:
            # Stoppe Download
            self.download_stopped = True
            self.reset_download_ui()
            print("\n🛑 Download gestoppt durch Benutzer")
    
    def reset_generation_ui(self):
        """Setzt die UI nach Generation zurück"""
        self.stop_btn.configure(state="disabled", text="Stop")
        self.send_btn.configure(state="normal")
        self.current_generation_thread = None
    
    def reset_download_ui(self):
        """Setzt die UI nach Download zurück"""
        self.stop_btn.configure(state="disabled", text="Stop")
        self.send_btn.configure(state="normal")
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
                # Prüfe ob es eine Liste ist
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
        """Zählt nur echte Chat-Nachrichten (User + AI, keine System-Nachrichten)"""
        return len([bubble for bubble in self.chat_bubbles if bubble.sender != "System"])
    
    def add_to_chat(self, sender, message):
        """Fügt eine Chat-Bubble zum Chat hinzu"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # System-Nachrichten ausblenden wenn Flag gesetzt ist
        if sender == "System" and not self.config.get("show_system_messages", True):
            # System-Nachricht wird trotzdem in der Session gespeichert für spätere Verwendung
            if self.current_session_id and self.current_session_id in self.sessions:
                msg_data = {
                    "timestamp": timestamp,
                    "sender": sender,
                    "message": message
                }
                self.sessions[self.current_session_id]["messages"].append(msg_data)
                self.sessions[self.current_session_id]["last_modified"] = datetime.now().isoformat()
                self.auto_save_session()
            return None  # Keine UI-Bubble erstellen
        
        # Erstelle automatisch eine Session falls keine aktiv ist
        if not self.current_session_id or self.current_session_id not in self.sessions:
            self.console_print("🔄 Keine aktive Session gefunden, erstelle neue Session", "info")
            self.create_new_session()
        
        # Prüfe nochmals ob Session existiert (Sicherheitscheck)
        if not self.current_session_id or self.current_session_id not in self.sessions:
            self.console_print("❌ Fehler: Konnte keine Session erstellen!", "error")
            return
        
        # Prüfe ob die letzte Bubble eine System-Nachricht ist und diese erweitert werden kann
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
            self.chat_display_frame._parent_canvas.after(100, 
                lambda: self.chat_display_frame._parent_canvas.yview_moveto(1.0))
            
            # Auto-Save für aktualisierte Nachricht
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
        
        # Füge Bubble zur Liste hinzu
        self.chat_bubbles.append(bubble)
        
        # Füge Nachricht zur aktuellen Session hinzu
        if self.current_session_id and self.current_session_id in self.sessions:
            msg_data = {
                "timestamp": timestamp,
                "sender": sender,
                "message": message
            }
            self.sessions[self.current_session_id]["messages"].append(msg_data)
            self.sessions[self.current_session_id]["total_messages"] = self.count_chat_messages()
            self.sessions[self.current_session_id]["last_modified"] = datetime.now().isoformat()
            
            # ✅ Automatisches Speichern nach jeder Nachricht
            self.auto_save_session()
        
        # Scrolle nach unten
        self.chat_display_frame._parent_canvas.after(100, 
            lambda: self.chat_display_frame._parent_canvas.yview_moveto(1.0))
        
        return bubble
    
    def scroll_to_last_message(self):
        """Scrollt zur letzten Nachricht in der Chat-Ansicht"""
        try:
            if hasattr(self, 'chat_display_frame') and hasattr(self.chat_display_frame, '_parent_canvas'):
                # Zuerst das Layout vollständig aktualisieren
                self.chat_display_frame.update_idletasks()
                self.chat_display_frame._parent_canvas.update_idletasks()
                
                # Dann zur letzten Nachricht scrollen
                self.chat_display_frame._parent_canvas.yview_moveto(1.0)
                
                # Nach kurzer Verzögerung nochmals scrollen für bessere Zuverlässigkeit
                self.root.after(50, lambda: self.force_scroll_to_bottom())
                
                self.console_print("📜 Zur letzten Nachricht gescrollt", "info")
        except Exception as e:
            self.console_print(f"❌ Fehler beim Scrollen zur letzten Nachricht: {e}", "error")
    
    def force_scroll_to_bottom(self):
        """Erzwingt das Scrollen zum Ende der Chat-Ansicht"""
        try:
            if hasattr(self, 'chat_display_frame') and hasattr(self.chat_display_frame, '_parent_canvas'):
                # Vollständige Layout-Aktualisierung
                self.chat_display_frame.update()
                self.chat_display_frame._parent_canvas.update()
                
                # Zum Ende scrollen
                self.chat_display_frame._parent_canvas.yview_moveto(1.0)
                
                # Canvas-Größe neu berechnen
                self.chat_display_frame._parent_canvas.configure(scrollregion=self.chat_display_frame._parent_canvas.bbox("all"))
                
                # Nochmals zum Ende
                self.chat_display_frame._parent_canvas.yview_moveto(1.0)
                
        except Exception as e:
            self.console_print(f"❌ Fehler beim erzwungenen Scrollen: {e}", "error")
    
    def add_thinking_indicator(self):
        """Zeigt dezenten Denkprozess-Indikator an"""
        thinking_message = "💭 Verarbeitet Ihre Anfrage..."
        bubble = self.add_to_chat(f"🤖 {self.current_model}", thinking_message)
        self.current_thinking_bubble = bubble
        return bubble
    
    def remove_last_message(self):
        """Entfernt die letzte Nachricht (Thinking-Indikator)"""
        # Stoppe die ASCII-Animation
        self._thinking_animation_running = False
        if hasattr(self, 'current_thinking_bubble') and self.current_thinking_bubble:
            try:
                self.current_thinking_bubble.destroy()
                if self.current_thinking_bubble in self.chat_bubbles:
                    self.chat_bubbles.remove(self.current_thinking_bubble)
            except:
                pass
            self.current_thinking_bubble = None

    def export_session(self):
        """Exportiert die aktuelle Chat-Session"""
        if not self.chat_bubbles:
            messagebox.showinfo("Export", "Keine Chat-Session zum Exportieren vorhanden!")
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
        title_label = ctk.CTkLabel(main_frame, text="📄 Export-Format auswählen", 
                                  font=("Arial", 20, "bold"))
        title_label.pack(pady=(10, 20))
        
        # Container für Format-Auswahl (Links/Rechts Layout)
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Linke Seite - Format-Buttons
        left_frame = ctk.CTkFrame(content_frame)
        left_frame.pack(side="left", fill="y", padx=(10, 5), pady=10)
        
        ctk.CTkLabel(left_frame, text="Verfügbare Formate:", 
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
            # Highlight aktiven Button  
            json_btn.configure(fg_color="#1f538d", hover_color="#2966a3")
            markdown_btn.configure(fg_color="#4a4a4a", hover_color="#5a5a5a")
        
        # Format-Buttons
        markdown_btn = ctk.CTkButton(left_frame, 
                                   text="📄 Markdown (.md)\n\n🧑‍💼 Menschenfreundlich\n📋 Formatiert & lesbar\n📚 Für Dokumentation",
                                   command=show_markdown_preview,
                                   width=220, height=90,
                                   font=("Arial", 11),
                                   anchor="center")
        markdown_btn.pack(pady=10)
        
        json_btn = ctk.CTkButton(left_frame,
                               text="📊 JSON (.json)\n\n🤖 Maschinenlesbar\n⚙️ Strukturierte Daten\n🔗 Für APIs & Tools", 
                               command=show_json_preview,
                               width=220, height=90,
                               font=("Arial", 11),
                               anchor="center")
        json_btn.pack(pady=10)
        
        # Rechte Seite - Vorschau
        right_frame = ctk.CTkFrame(content_frame)
        right_frame.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)
        
        ctk.CTkLabel(right_frame, text="Format-Vorschau:", 
                    font=("Arial", 14, "bold")).pack(pady=(10, 10))
        
        # Vorschau-Frame
        preview_frame = ctk.CTkFrame(right_frame)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Standard: Markdown-Vorschau anzeigen
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
        
        export_btn = ctk.CTkButton(button_frame, text="📤 Exportieren", 
                                 command=export_selected, 
                                 width=120, height=35,
                                 font=("Arial", 12, "bold"))
        export_btn.pack(side="right", padx=(10, 20), pady=10)
        
        cancel_btn = ctk.CTkButton(button_frame, text="❌ Abbrechen", 
                                 command=dialog.destroy,
                                 width=100, height=35,
                                 fg_color="#666666", hover_color="#555555")
        cancel_btn.pack(side="right", padx=5, pady=10)

    def update_preview(self, preview_frame, format_type):
        """Aktualisiert die Vorschau basierend auf dem gewählten Format"""
        # Alle Widgets im Vorschau-Frame löschen
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
        
        ctk.CTkLabel(header_frame, text="📄 Markdown-Format", 
                    font=("Arial", 14, "bold")).pack(side="left", padx=10, pady=5)
        
        info_label = ctk.CTkLabel(header_frame, 
                                text="✅ Menschenfreundlich  ✅ GitHub-kompatibel  ✅ Übersichtlich",
                                font=("Arial", 10),
                                text_color="#00AA00")
        info_label.pack(side="right", padx=10, pady=5)
        
        # Beispiel-Content
        markdown_example = """# Ki-whisperer Chat Session

**Session-ID:** `20251107_143025`
**Exportiert am:** 07.11.2025 um 14:30:25
**Modell:** llama3.1:8b  
**Anzahl Nachrichten:** 4
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
*Generiert von Ki-whisperer LLM Chat Client*"""

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
        
        ctk.CTkLabel(header_frame, text="📊 JSON-Format", 
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
      "content": "Stellen Sie sich vor, Sie bringen einem Kind bei..."
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
        """Exportiert die Chat-Session als Markdown-Datei"""
        try:
            # Session-ID mit Datum und Zeitstempel erstellen
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Sessions-Ordner erstellen falls nicht vorhanden
            sessions_dir = os.path.join(os.getcwd(), "sessions")
            if not os.path.exists(sessions_dir):
                os.makedirs(sessions_dir)
            
            # Standard-Dateiname mit Session-ID
            default_filename = f"session_{session_id}.md"
            default_path = os.path.join(sessions_dir, default_filename)
            
            # Datei-Dialog mit Sessions-Ordner als Standard
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
                
                messagebox.showinfo("Export erfolgreich", 
                                  f"Chat-Session wurde erfolgreich exportiert:\n{file_path}\n\nSession-ID: {session_id}")
        except Exception as e:
            messagebox.showerror("Export-Fehler", f"Fehler beim Exportieren: {str(e)}")

    def export_to_json(self):
        """Exportiert die Chat-Session als JSON-Datei"""
        try:
            # Session-ID mit Datum und Zeitstempel erstellen
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Sessions-Ordner erstellen falls nicht vorhanden
            sessions_dir = os.path.join(os.getcwd(), "sessions")
            if not os.path.exists(sessions_dir):
                os.makedirs(sessions_dir)
            
            # Standard-Dateiname mit Session-ID
            default_filename = f"session_{session_id}.json"
            
            # Datei-Dialog mit Sessions-Ordner als Standard
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
                
                messagebox.showinfo("Export erfolgreich", 
                                  f"Chat-Session wurde erfolgreich exportiert:\n{file_path}\n\nSession-ID: {session_id}")
        except Exception as e:
            messagebox.showerror("Export-Fehler", f"Fehler beim Exportieren: {str(e)}")

    def _generate_markdown_content(self, session_id=None):
        """Generiert Markdown-Content für den Export"""
        lines = []
        
        # Session-ID falls nicht übergeben
        if session_id is None:
            session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Header mit Session-ID
        lines.append("# Ki-whisperer Chat Session")
        lines.append("")
        lines.append(f"**Session-ID:** `{session_id}`")
        lines.append(f"**Exportiert am:** {datetime.now().strftime('%d.%m.%Y um %H:%M:%S')}")
        lines.append(f"**Modell:** {getattr(self, 'current_model', 'Unbekannt')}")
        lines.append(f"**Anzahl Nachrichten:** {self.count_chat_messages()}")
        
        # Session-Zeitraum
        if self.chat_bubbles:
            session_start = self.chat_bubbles[0].timestamp
            session_end = self.chat_bubbles[-1].timestamp
            lines.append(f"**Session-Start:** {session_start}")
            lines.append(f"**Session-Ende:** {session_end}")
        
        lines.append("")
        lines.append("---")
        lines.append("")
        
        # Chat-Nachrichten
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
            
            # Trennlinie zwischen Nachrichten (außer bei der letzten)
            if i < len(self.chat_bubbles):
                lines.append("---")
                lines.append("")
        
        # Footer
        lines.append("---")
        lines.append("")
        lines.append(f"*Session-ID: {session_id}*")
        lines.append("*Generiert von Ki-whisperer LLM Chat Client*")
        
        return '\n'.join(lines)
    
    def setup_keyboard_shortcuts(self):
        """Richtet Keyboard Shortcuts ein"""
        # Ctrl+N - Neue Session
        self.root.bind("<Control-n>", lambda e: self.create_new_session())
        
        # Ctrl+L - Chat leeren
        self.root.bind("<Control-l>", lambda e: self.clear_current_chat())
        
        # Ctrl+E - Export
        self.root.bind("<Control-e>", lambda e: self.export_session_markdown())
        
        # Ctrl+B - BIAS fokussieren
        self.root.bind("<Control-b>", lambda e: self.session_bias_entry.focus() if hasattr(self, 'session_bias_entry') else None)
        
        # Escape - Generation stoppen
        self.root.bind("<Escape>", lambda e: self.stop_generation())
        
        print("⌨️ Keyboard Shortcuts aktiviert:")
        print("  Ctrl+N: Neue Session")
        print("  Ctrl+L: Chat leeren")
        print("  Ctrl+E: Export")
        print("  Ctrl+B: BIAS fokussieren")
        print("  Escape: Generation stoppen")
    
    def clear_current_chat(self):
        """Leert den aktuellen Chat"""
        if not self.current_session_id:
            return
        
        response = messagebox.askyesno(
            "Chat leeren",
            "Möchten Sie den gesamten Chat-Verlauf dieser Session löschen?"
        )
        
        if response:
            # Chat-History leeren
            self.chat_history = []
            
            # Session aktualisieren
            if self.current_session_id in self.sessions:
                self.sessions[self.current_session_id]["messages"] = []
                self.save_current_session()
            
            # Chat-Anzeige leeren
            for bubble in self.chat_bubbles:
                bubble.destroy()
            self.chat_bubbles.clear()
            
            # System-Nachricht
            self.add_to_chat("System", "✨ Chat wurde geleert")
    
    def run(self):
        """Startet die Anwendung"""
        self.root.mainloop()
