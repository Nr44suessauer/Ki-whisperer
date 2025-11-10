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
        
        # Nachrichteninhalt - CTkTextbox mit dynamischer Höhenberechnung
        message_font = (font, font_size)
        
        # Erstelle Textbox mit initialer Minimalhöhe
        self.message_label = ctk.CTkTextbox(
            self,
            wrap="word",
            font=message_font,
            text_color=text_color,
            fg_color="transparent",
            height=60  # Initiale Minimalhöhe
        )
        self.message_label.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Füge Nachricht hinzu und deaktiviere Bearbeitung
        self.message_label.insert("1.0", message)
        self.message_label.configure(state="disabled")
        
        # Nach dem Rendering: Passe Höhe automatisch an den gesamten Inhalt an
        self.after(10, self.adjust_height_to_content)
        
        # Packe Bubble mit korrekter Ausrichtung
        self.pack(fill="x", padx=20 if anchor == "e" else 5, 
                 pady=5, anchor=anchor)
    
    def adjust_height_to_content(self):
        """Passt die Höhe der Textbox dynamisch an den gesamten Inhalt an - kein Scrollen nötig"""
        try:
            # Warte bis Widget vollständig gerendert ist
            self.update_idletasks()
            
            # Aktiviere temporär für Messungen
            self.message_label.configure(state="normal")
            
            # Hole die aktuelle Schriftgröße und Font
            if self.sender == "Sie":
                font_size = self.app_config.get("user_font_size", 11)
                font_name = self.app_config.get("user_font", "Courier New")
            elif "🤖" in self.sender:
                font_size = self.app_config.get("ai_font_size", 11)
                font_name = self.app_config.get("ai_font", "Consolas")
            else:
                font_size = self.app_config.get("system_font_size", 10)
                font_name = self.app_config.get("system_font", "Arial")
            
            # Hole die aktuelle Breite der Textbox in Pixeln
            textbox_width = self.message_label.winfo_width()
            
            # Falls Breite noch nicht bekannt (Widget nicht gerendert), verwende Standardwert
            if textbox_width <= 1:
                textbox_width = 600  # Schätzwert, wird beim nächsten Update korrigiert
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
            self.message_label.configure(height=needed_height)
            
            # Deaktiviere wieder
            self.message_label.configure(state="disabled")
            
        except Exception as e:
            print(f"Fehler bei automatischer Höhenanpassung: {e}")
            # Bei Fehler: Deaktiviere trotzdem die Textbox
            try:
                self.message_label.configure(state="disabled")
            except:
                pass
    
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
            
            # Minimum 60px, keine Maximalbegrenzung mehr
            new_height = max(new_height, 60)
            
            # Aktualisiere die Höhe
            self.message_label.configure(height=new_height)
            
            # Nach kurzer Zeit exakte Nachmessung
            self.after(25, self.adjust_height_to_content)
            
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