"""Enhanced Chat Bubble with Action Buttons"""

import customtkinter as ctk
from tkinter import messagebox
import pyperclip

class EnhancedChatBubble(ctk.CTkFrame):
    """Moderne Chat-Bubble mit Action-Buttons und Hover-Effekten"""
    
    def __init__(self, master, sender, message, timestamp, app_config=None, 
                 on_copy=None, on_regenerate=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.sender = sender
        self.message = message
        self.timestamp = timestamp
        self.app_config = app_config or {}
        self.on_copy = on_copy
        self.on_regenerate = on_regenerate
        
        # Bestimme Bubble-Stil
        if sender == "You":
            bubble_color = self.app_config.get("user_bg_color", "#2B8A3E")
            text_color = self.app_config.get("user_text_color", "white")
            font = self.app_config.get("user_font", "Arial")
            font_size = self.app_config.get("user_font_size", 11)
            anchor = "e"
            self.is_user = True
        elif "🤖" in sender:
            bubble_color = self.app_config.get("ai_bg_color", "#1f538d")
            text_color = self.app_config.get("ai_text_color", "white")
            font = self.app_config.get("ai_font", "Arial")
            font_size = self.app_config.get("ai_font_size", 11)
            anchor = "w"
            self.is_user = False
        else:
            bubble_color = self.app_config.get("system_bg_color", "#3a3a3a")
            text_color = self.app_config.get("system_text_color", "#aaaaaa")
            font = self.app_config.get("system_font", "Arial")
            font_size = self.app_config.get("system_font_size", 9)
            anchor = "w"
            self.is_user = False
        
        self.configure(fg_color=bubble_color, corner_radius=10)
        
        # Haupt-Container
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header mit Sender und Timestamp
        header_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 5))
        
        sender_label = ctk.CTkLabel(
            header_frame,
            text=f"{sender}",
            font=(font, 10, "bold"),
            text_color=text_color
        )
        sender_label.pack(side="left")
        
        time_label = ctk.CTkLabel(
            header_frame,
            text=timestamp,
            font=(font, 8),
            text_color="#888888"
        )
        time_label.pack(side="left", padx=(10, 0))
        
        # Action Buttons Container (initial versteckt)
        self.action_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        self.action_frame.pack(side="right")
        self.action_frame.pack_forget()  # Initial verstecken
        
        # Copy Button
        self.copy_btn = ctk.CTkButton(
            self.action_frame,
            text="📋",
            width=30,
            height=25,
            command=self._on_copy,
            fg_color="transparent",
            hover_color="#4a4a4a",
            border_width=1,
            border_color=text_color,
            corner_radius=5
        )
        self.copy_btn.pack(side="left", padx=2)
        
        # Regenerate Button (nur für AI-Messages)
        if not self.is_user and sender != "System" and self.on_regenerate:
            self.regen_btn = ctk.CTkButton(
                self.action_frame,
                text="🔄",
                width=30,
                height=25,
                command=self._on_regenerate,
                fg_color="transparent",
                hover_color="#4a4a4a",
                border_width=1,
                border_color=text_color,
                corner_radius=5
            )
            self.regen_btn.pack(side="left", padx=2)
        
        # Message Content
        message_font = (font, font_size)
        
        # Erstelle Textbox mit initialer Minimalhöhe
        self.text_widget = ctk.CTkTextbox(
            main_container,
            font=message_font,
            text_color=text_color,
            fg_color="transparent",
            wrap="word",
            height=60,  # Initiale Minimalhöhe
            activate_scrollbars=False
        )
        self.text_widget.pack(fill="both", expand=True)
        self.text_widget.insert("1.0", message)
        self.text_widget.configure(state="disabled")
        
        # Nach dem Rendering: Passe Höhe automatic an den gesamten Inhalt an
        self.after(10, self.adjust_height_to_content)
        
        # Hover-Effekte
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        main_container.bind("<Enter>", self._on_enter)
        main_container.bind("<Leave>", self._on_leave)
        header_frame.bind("<Enter>", self._on_enter)
        header_frame.bind("<Leave>", self._on_leave)
        self.text_widget.bind("<Enter>", self._on_enter)
        self.text_widget.bind("<Leave>", self._on_leave)
    
    def adjust_height_to_content(self):
        """Passt die Höhe der Textbox dynamisch an den gesamten Inhalt an - kein Scrollen nötig"""
        try:
            # Warte bis Widget vollständig gerendert ist
            self.update_idletasks()
            
            # Aktiviere temporär für Messungen
            self.text_widget.configure(state="normal")
            
            # Hole die aktuelle Schriftgröße und Font
            if self.is_user:
                font_size = self.app_config.get("user_font_size", 11)
                font_name = self.app_config.get("user_font", "Arial")
            elif "🤖" in self.sender:
                font_size = self.app_config.get("ai_font_size", 11)
                font_name = self.app_config.get("ai_font", "Arial")
            else:
                font_size = self.app_config.get("system_font_size", 9)
                font_name = self.app_config.get("system_font", "Arial")
            
            # Hole die aktuelle Breite der Textbox in Pixeln
            textbox_width = self.text_widget.winfo_width()
            
            # Falls Breite noch nicht bekannt (Widget nicht gerendert), verwende Standardwert
            if textbox_width <= 1:
                textbox_width = 600  # Schätzwert, is being beim nächsten Update korrigiert
                # Plane erneute Anpassung nach vollständigem Rendering
                self.after(100, self.adjust_height_to_content)
            
            # Berechne durchschnittliche Zeichenbreite basierend auf Font
            # Monospace-Fonts haben feste Breite, andere variabel
            if font_name in ["Courier New", "Consolas", "Courier"]:
                char_width = font_size * 0.6  # Monospace
            else:
                char_width = font_size * 0.5  # Proportionale Schrift (etwas kleiner für mehr Genauigkeit)
            
            # Berechne Zeichen pro Zeile basierend auf Textbox-Breite (minus Padding)
            usable_width = textbox_width - 20  # Reduziertes Padding für genauere Berechnung
            chars_per_line = max(20, int(usable_width / char_width))
            
            # Analysiere den Text und zähle die tatsächlichen Zeilen nach Umbruch
            lines = self.message.split('\n')
            total_wrapped_lines = 0
            
            for line in lines:
                if len(line) == 0:
                    # Leere Zeile (Absatz) - zählt als volle Zeile für Spacing
                    total_wrapped_lines += 1
                else:
                    # Berechne wie viele Zeilen diese Zeile nach Umbruch benötigt
                    line_length = len(line)
                    wrapped_lines = max(1, (line_length + chars_per_line - 1) // chars_per_line)
                    total_wrapped_lines += wrapped_lines
            
            # Berechne die benötigte Höhe - präziser für CTkTextbox
            line_height = font_size + 3  # Etwas mehr Zeilenabstand für bessere Lesbarkeit
            # CTkTextbox hat intern ca. 12px Padding
            needed_height = total_wrapped_lines * line_height + 12
            
            # Setze Mindesthöhe von 50px
            needed_height = max(needed_height, 50)
            
            # Aktualisiere die Höhe der Textbox
            self.text_widget.configure(height=needed_height)
            
            # Disable again
            self.text_widget.configure(state="disabled")
            
        except Exception as e:
            print(f"Error during automatic height adjustment: {e}")
            # On error: Disable textbox anyway
            try:
                self.text_widget.configure(state="disabled")
            except:
                pass
    
    def _on_enter(self, event):
        """Zeige Action-Buttons bei Hover"""
        self.action_frame.pack(side="right")
    
    def _on_leave(self, event):
        """Verstecke Action-Buttons"""
        self.action_frame.pack_forget()
    
    def _on_copy(self):
        """Kopiere Message in Zwischenablage"""
        try:
            pyperclip.copy(self.message)
            # Kurzes Feedback
            original_text = self.copy_btn.cget("text")
            self.copy_btn.configure(text="✅")
            self.after(1000, lambda: self.copy_btn.configure(text=original_text))
        except:
            # Fallback ohne pyperclip
            self.master.clipboard_clear()
            self.master.clipboard_append(self.message)
            self.copy_btn.configure(text="✅")
            self.after(1000, lambda: self.copy_btn.configure(text="📋"))
    
    def _on_regenerate(self):
        """Regeneriere AI-Antwort"""
        if self.on_regenerate:
            self.on_regenerate(self.message)
    
    def update_style(self, config):
        """Aktualisiert Style basierend auf neuer Config"""
        # Implementierung wie vorher
        pass
