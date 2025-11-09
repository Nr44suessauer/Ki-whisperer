"""ChatBubble Widget für Chat-Nachrichten"""

import customtkinter as ctk
from tkinter import messagebox

class ChatBubble(ctk.CTkFrame):
    """Ein einzelne Chat-Bubble mit Kopier-Funktionalität"""
    
    def __init__(self, master, sender, message, timestamp, app_config=None, **kwargs):
        super().__init__(master, **kwargs)
        
        self.sender = sender
        self.message = message
        self.timestamp = timestamp
        self.app_config = app_config or {}
        
        # Bestimme Bubble-Stil basierend auf Sender und Config
        if sender == "Sie":
            bubble_color = self.app_config.get("user_bg_color", "#003300")
            text_color = self.app_config.get("user_text_color", "#00FF00")
            font = self.app_config.get("user_font", "Courier New")
            font_size = self.app_config.get("user_font_size", 11)
            anchor = "e"  # Rechts ausrichten
        elif "🤖" in sender:
            bubble_color = self.app_config.get("ai_bg_color", "#1E3A5F")
            text_color = self.app_config.get("ai_text_color", "white")
            font = self.app_config.get("ai_font", "Consolas")
            font_size = self.app_config.get("ai_font_size", 11)
            anchor = "w"  # Links ausrichten
        else:  # System
            bubble_color = self.app_config.get("system_bg_color", "#722F37")
            text_color = self.app_config.get("system_text_color", "white")
            font = self.app_config.get("system_font", "Arial")
            font_size = self.app_config.get("system_font_size", 10)
            anchor = "w"
        
        self.configure(fg_color=bubble_color, corner_radius=10)
        
        # Matrix-Effekt für "Sie"-Bubbles
        if sender == "Sie":
            border_color = self.app_config.get("user_text_color", "#00FF00")
            self.configure(border_width=2, border_color=border_color)
        
        # Header mit Sender und Kopier-Button
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        # Sender und Timestamp
        header_text = f"{sender} • {timestamp}"
        header_font = (font, 10, "bold")
        self.sender_label = ctk.CTkLabel(
            self.header_frame, 
            text=header_text,
            font=header_font,
            text_color=text_color
        )
        self.sender_label.pack(side="left")
        
        # Kopier-Button
        copy_btn_color = "transparent"
        copy_border_color = text_color
        self.copy_btn = ctk.CTkButton(
            self.header_frame,
            text="📋 Kopieren",
            command=self.copy_message,
            width=80,
            height=20,
            font=(font, 9),
            fg_color=copy_btn_color,
            hover_color="#505050",  # Feste graue Farbe für Hover
            border_width=1,
            border_color=copy_border_color
        )
        self.copy_btn.pack(side="right")
        
        # Nachrichteninhalt - CTkTextbox mit optimierter Höhenberechnung
        message_font = (font, font_size)
        
        # Berechne die benötigte Höhe realistisch basierend auf Textinhalt
        chars_per_line = 70
        
        # Analysiere jede Zeile einzeln für genauere Schätzung
        lines = message.split('\n')
        actual_lines = 0
        for line in lines:
            if len(line.strip()) == 0:  # Leere Zeile
                actual_lines += 1
            else:
                # Berechne Umbrüche für diese Zeile
                line_wraps = max(1, len(line) // chars_per_line)
                actual_lines += line_wraps
        
        # Berechne Höhe mit optimiertem Puffer
        line_height = font_size + 3  # Noch kompakter
        calculated_height = actual_lines * line_height + 25  # Minimaler Puffer
        
        # Minimum 60px, Maximum 350px für sehr lange Nachrichten  
        calculated_height = max(min(calculated_height, 350), 60)
        
        # Erstelle Textbox mit ausreichender Höhe (kein Scrolling nötig)
        self.message_label = ctk.CTkTextbox(
            self,
            wrap="word",
            font=message_font,
            text_color=text_color,
            fg_color="transparent",
            height=calculated_height
        )
        self.message_label.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Füge Nachricht hinzu und deaktiviere Bearbeitung
        self.message_label.insert("1.0", message)
        self.message_label.configure(state="disabled")
        
        # Nach dem Rendering: Stelle sicher, dass die Höhe ausreicht
        self.after(50, self.ensure_full_content_visible)
        
        # Packe Bubble mit korrekter Ausrichtung
        self.pack(fill="x", padx=20 if anchor == "e" else 5, 
                 pady=5, anchor=anchor)
    
    def ensure_full_content_visible(self):
        """Stellt sicher, dass der gesamte Inhalt ohne Scrolling sichtbar ist"""
        try:
            # Aktiviere temporär für Messungen
            self.message_label.configure(state="normal")
            
            # Hole die aktuelle Textbox-Höhe und prüfe, ob Scrolling nötig ist
            self.message_label.see("end")  # Gehe zum Ende
            
            # Messe die tatsächlich benötigte Höhe - optimiert
            try:
                total_lines = int(self.message_label.index('end-1c').split('.')[0])
                font_size = self.app_config.get("ai_font_size" if "🤖" in self.sender 
                                               else "system_font_size" if self.sender == "System"
                                               else "user_font_size", 11)
                
                # Optimierte, kompaktere Berechnung
                needed_height = total_lines * (font_size + 3) + 25  # Minimaler Puffer
                current_height = self.message_label.cget("height")
                
                # Maximale Höhe begrenzen und nur erweitern wenn wirklich nötig
                max_height = 350  # Reduzierte maximale Bubble-Höhe
                needed_height = min(needed_height, max_height)
                
                # Nur erweitern wenn deutlich mehr Höhe benötigt wird (Toleranz: 20px)
                if needed_height > current_height + 20:
                    self.message_label.configure(height=needed_height)
                    
            except Exception as e:
                # Falls Messung fehlschlägt, behalte aktuelle Höhe
                print(f"Höhenmessung fehlgeschlagen: {e}")
                
            # Deaktiviere wieder
            self.message_label.configure(state="disabled")
            
        except Exception as e:
            print(f"Vollständige Sichtbarkeit konnte nicht sichergestellt werden: {e}")
    
    def update_style(self, new_config):
        """Aktualisiert das Bubble-Styling basierend auf neuer Konfiguration"""
        self.app_config = new_config
        
        # Bestimme neue Styling-Parameter
        if self.sender == "Sie":
            bubble_color = self.app_config.get("user_bg_color", "#003300")
            text_color = self.app_config.get("user_text_color", "#00FF00")
            font = self.app_config.get("user_font", "Courier New")
            font_size = self.app_config.get("user_font_size", 11)
            border_color = text_color
        elif "🤖" in self.sender:
            bubble_color = self.app_config.get("ai_bg_color", "#1E3A5F")
            text_color = self.app_config.get("ai_text_color", "white")
            font = self.app_config.get("ai_font", "Consolas")
            font_size = self.app_config.get("ai_font_size", 11)
            border_color = None
        else:  # System
            bubble_color = self.app_config.get("system_bg_color", "#722F37")
            text_color = self.app_config.get("system_text_color", "white")
            font = self.app_config.get("system_font", "Arial")
            font_size = self.app_config.get("system_font_size", 10)
            border_color = None
        
        # Aktualisiere Bubble-Farben
        self.configure(fg_color=bubble_color)
        if self.sender == "Sie" and border_color:
            self.configure(border_color=border_color)
        
        # Aktualisiere Header-Styling
        header_font = (font, 10, "bold")
        self.sender_label.configure(font=header_font, text_color=text_color)
        
        # Aktualisiere Kopier-Button
        self.copy_btn.configure(
            font=(font, 9),
            border_color=text_color if border_color else text_color
        )
        
        # Aktualisiere Message-Styling
        message_font = (font, font_size)
        self.message_label.configure(
            font=message_font,
            text_color=text_color,
            state="normal"  # Temporär aktivieren für Updates
        )
        
        # Neuberechnung der Höhe mit neuer Schriftgröße
        self.recalculate_height(font_size)
        
        # Wieder deaktivieren
        self.message_label.configure(state="disabled")
    
    def recalculate_height(self, font_size):
        """Berechnet die Bubble-Höhe neu basierend auf neuer Schriftgröße"""
        try:
            # Optimierte Höhenberechnung - identisch zur initialen Berechnung
            chars_per_line = 70
            
            # Analysiere jede Zeile einzeln für genauere Schätzung
            lines = self.message.split('\n')
            actual_lines = 0
            for line in lines:
                if len(line.strip()) == 0:  # Leere Zeile
                    actual_lines += 1
                else:
                    # Berechne Umbrüche für diese Zeile
                    line_wraps = max(1, len(line) // chars_per_line)
                    actual_lines += line_wraps
            
            # Berechne Höhe mit optimiertem Puffer
            line_height = font_size + 3  # Kompakter Zeilenabstand
            # Berechne Höhe mit optimiertem Puffer
            line_height = font_size + 3  # Kompakter Zeilenabstand
            new_height = actual_lines * line_height + 25  # Minimaler Puffer
            
            # Minimum 60px, Maximum 350px
            new_height = max(min(new_height, 350), 60)
            
            # Aktualisiere die Höhe
            self.message_label.configure(height=new_height)
            
            # Nach kurzer Zeit exakte Nachmessung
            self.after(25, self.ensure_full_content_visible)
            
        except Exception as e:
            print(f"Höhenneuberechnung fehlgeschlagen: {e}")
    
    def copy_message(self):
        """Kopiert die Nachricht in die Zwischenablage"""
        try:
            self.clipboard_clear()
            self.clipboard_append(self.message)
            self.update()  # Stelle sicher, dass Clipboard-Änderung verarbeitet wird
            
            # Kurzes visuelles Feedback
            original_text = self.copy_btn.cget("text")
            self.copy_btn.configure(text="✅ Kopiert!")
            self.after(1000, lambda: self.copy_btn.configure(text=original_text))
            
        except Exception as e:
            print(f"Fehler beim Kopieren: {e}")
            # Fallback: Zeige Fehlermeldung
            self.copy_btn.configure(text="❌ Fehler")
            self.after(1000, lambda: self.copy_btn.configure(text="📋 Kopieren"))