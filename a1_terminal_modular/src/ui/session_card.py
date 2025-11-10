"""Modern Session Card Widget"""

import customtkinter as ctk
from datetime import datetime

class SessionCard(ctk.CTkFrame):
    """Moderne Karte für Session-Anzeige"""
    
    def __init__(self, master, session_id, session_data, on_select=None, on_delete=None, 
                 is_active=False, **kwargs):
        super().__init__(master, **kwargs)
        
        self.session_id = session_id
        self.session_data = session_data
        self.on_select = on_select
        self.on_delete = on_delete
        self.is_active = is_active
        
        # Styling basierend auf Active-Status
        if is_active:
            self.configure(
                fg_color="#1f538d",
                border_width=2,
                border_color="#00BFFF",
                corner_radius=10
            )
        else:
            self.configure(
                fg_color="#2b2b2b",
                border_width=1,
                border_color="#4a4a4a",
                corner_radius=10
            )
        
        # Hover-Effekt
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        
        self._build_card()
    
    def _build_card(self):
        """Erstellt den Card-Inhalt"""
        
        # Header mit Session-ID (gekürzt)
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # Icon + Session-ID
        display_id = self.session_id.replace("session_", "")
        if len(display_id) > 25:
            display_id = display_id[:22] + "..."
        
        icon = "📌" if self.is_active else "📄"
        session_label = ctk.CTkLabel(
            header_frame,
            text=f"{icon} {display_id}",
            font=("Arial", 11, "bold"),
            anchor="w"
        )
        session_label.pack(side="left", fill="x", expand=True)
        
        # Delete Button
        if self.on_delete is not None:
            delete_btn = ctk.CTkButton(
                header_frame,
                text="🗑️",
                width=30,
                height=25,
                command=lambda: self.on_delete(self.session_id) if self.on_delete else None,
                fg_color="transparent",
                hover_color="#722F37",
                border_width=1,
                border_color="#722F37"
            )
            delete_btn.pack(side="right")
        
        # Info Frame
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(fill="x", padx=10, pady=5)
        
        # Model Info
        model = self.session_data.get('model', 'Kein Model')
        model_label = ctk.CTkLabel(
            info_frame,
            text=f"🤖 {model}",
            font=("Arial", 9),
            anchor="w",
            text_color="#aaaaaa"
        )
        model_label.pack(anchor="w")
        
        # Message Count
        msg_count = len(self.session_data.get('messages', []))
        msg_label = ctk.CTkLabel(
            info_frame,
            text=f"💬 {msg_count} Messages",
            font=("Arial", 9),
            anchor="w",
            text_color="#aaaaaa"
        )
        msg_label.pack(anchor="w")
        
        # Timestamp
        created = self.session_data.get('created_at', '')
        if created:
            try:
                dt = datetime.fromisoformat(created)
                time_str = dt.strftime("%d.%m.%Y %H:%M")
            except:
                time_str = created
        else:
            time_str = "Unbekannt"
        
        time_label = ctk.CTkLabel(
            info_frame,
            text=f"🕐 {time_str}",
            font=("Arial", 8),
            anchor="w",
            text_color="#888888"
        )
        time_label.pack(anchor="w")
        
        # BIAS Preview (falls vorhanden)
        bias = self.session_data.get('bias', '')
        if bias:
            bias_preview = bias[:40] + "..." if len(bias) > 40 else bias
            bias_label = ctk.CTkLabel(
                info_frame,
                text=f"🎯 {bias_preview}",
                font=("Arial", 8),
                anchor="w",
                text_color="#666666",
                wraplength=250
            )
            bias_label.pack(anchor="w", pady=(5, 0))
        
        # Click-Handler für Selection
        if self.on_select is not None:
            self.bind("<Button-1>", lambda e: self.on_select(self.session_id) if self.on_select else None)
            for child in self.winfo_children():
                child.bind("<Button-1>", lambda e: self.on_select(self.session_id) if self.on_select else None)
    
    def _on_enter(self, event):
        """Hover-Effekt beim Eintreten"""
        if not self.is_active:
            self.configure(border_color="#00BFFF")
    
    def _on_leave(self, event):
        """Hover-Effekt beim Verlassen"""
        if not self.is_active:
            self.configure(border_color="#4a4a4a")
    
    def set_active(self, active):
        """Setzt den Active-Status"""
        self.is_active = active
        if active:
            self.configure(
                fg_color="#1f538d",
                border_width=2,
                border_color="#00BFFF"
            )
        else:
            self.configure(
                fg_color="#2b2b2b",
                border_width=1,
                border_color="#4a4a4a"
            )
