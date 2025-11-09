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
        if sender == "Sie":
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
        
        # Regenerate Button (nur für AI-Nachrichten)
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
        
        # Berechne Höhe
        chars_per_line = 80
        lines = message.split('\n')
        actual_lines = sum(max(1, len(line) // chars_per_line) for line in lines)
        line_height = font_size + 4
        calculated_height = max(60, min(400, actual_lines * line_height + 30))
        
        self.text_widget = ctk.CTkTextbox(
            main_container,
            font=message_font,
            text_color=text_color,
            fg_color="transparent",
            wrap="word",
            height=calculated_height,
            activate_scrollbars=False
        )
        self.text_widget.pack(fill="both", expand=True)
        self.text_widget.insert("1.0", message)
        self.text_widget.configure(state="disabled")
        
        # Hover-Effekte
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        main_container.bind("<Enter>", self._on_enter)
        main_container.bind("<Leave>", self._on_leave)
        header_frame.bind("<Enter>", self._on_enter)
        header_frame.bind("<Leave>", self._on_leave)
        self.text_widget.bind("<Enter>", self._on_enter)
        self.text_widget.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        """Zeige Action-Buttons bei Hover"""
        self.action_frame.pack(side="right")
    
    def _on_leave(self, event):
        """Verstecke Action-Buttons"""
        self.action_frame.pack_forget()
    
    def _on_copy(self):
        """Kopiere Nachricht in Zwischenablage"""
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
