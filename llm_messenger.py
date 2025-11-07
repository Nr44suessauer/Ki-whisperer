#!/usr/bin/env python3
"""
LLM Messenger - Ein Chat-Client für Ollama
Ein moderner Chat-Client mit Ollama-Integration für lokale AI-Modelle
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, scrolledtext, colorchooser, filedialog
import requests
import json
import threading
import time
from datetime import datetime
import ollama
import yaml
import os
import os

# Erscheinungsbild konfigurieren
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

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
        
        # Nachrichteninhalt
        message_font = (font, font_size)
        self.message_label = ctk.CTkTextbox(
            self,
            wrap="word",
            font=message_font,
            text_color=text_color,
            fg_color="transparent",
            height=min(max(len(message) // 60 + 1, 2) * 20, 200)  # Dynamische Höhe
        )
        self.message_label.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Füge Nachricht hinzu und deaktiviere Bearbeitung
        self.message_label.insert("1.0", message)
        self.message_label.configure(state="disabled")
        
        # Packe Bubble mit korrekter Ausrichtung
        self.pack(fill="x", padx=20 if anchor == "e" else 5, 
                 pady=5, anchor=anchor)
    
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

class OllamaManager:
    """Klasse für Ollama-API-Interaktionen"""
    
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.client = ollama.Client()
    
    def is_ollama_running(self):
        """Prüft ob Ollama läuft"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_available_models(self):
        """Holt verfügbare Modelle"""
        try:
            if not self.is_ollama_running():
                return []
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except Exception as e:
            print(f"Fehler beim Abrufen der Modelle: {e}")
            return []
    
    def get_all_ollama_models(self):
        """Holt alle verfügbaren Ollama-Modelle direkt von der offiziellen API"""
        try:
            # Versuche zuerst die offizielle Ollama Library API
            url = "https://registry.ollama.ai/v2/_catalog"
            headers = {
                'User-Agent': 'LLM-Messenger/1.0',
                'Accept': 'application/json'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                models = data.get('repositories', [])
                
                # Erweitere mit beliebten Varianten falls verfügbar
                expanded_models = []
                for model in models:
                    expanded_models.append(model)
                    # Füge häufige Größenvarianten hinzu
                    for size in [':7b', ':13b', ':34b', ':70b']:
                        variant = f"{model}{size}"
                        if variant not in expanded_models:
                            expanded_models.append(variant)
                
                return sorted(expanded_models)
            else:
                # Fallback auf bewährte Modell-Liste
                return self._get_fallback_models()
                
        except Exception as e:
            print(f"Fehler beim Abrufen der Live-Modelle: {e}")
            return self._get_fallback_models()
    
    def _get_fallback_models(self):
        """Fallback-Liste mit bewährten Modellen"""
        return sorted([
            # Kleine Modelle (< 4GB)
            "tinyllama:1.1b", "phi3:mini", "gemma:2b", "orca-mini:3b",
            "phi:2.7b", "qwen2:0.5b", "qwen2:1.5b",
            
            # Mittlere Modelle (4-8GB) 
            "llama3.2:3b", "mistral:7b", "llama2:7b", "codellama:7b",
            "gemma:7b", "neural-chat:7b", "zephyr:7b", "openchat:7b",
            "nous-hermes:7b", "starcode:7b", "deepseek-coder:6.7b",
            "magicoder:6.7b", "sqlcoder:7b", "vicuna:7b", "llava:7b",
            "orca-mini:7b", "dolphin-mistral:7b", "wizard-math:7b",
            "medllama2:7b", "stable-beluga:7b", "falcon:7b", "aya:8b",
            
            # Große Modelle (8-16GB)
            "llama2:13b", "codellama:13b", "vicuna:13b", "nous-hermes:13b",
            "orca-mini:13b", "llava:13b", "stable-beluga:13b", "starcode:15b",
            "solar:10.7b", "sqlcoder:15b",
            
            # Sehr große Modelle (16GB+)
            "llama2:70b", "codellama:34b", "vicuna:33b", "llava:34b",
            "deepseek-coder:33b", "mixtral:8x7b", "aya:35b", "falcon:40b",
            "mixtral:8x22b", "llama2-uncensored:70b",
            
            # Basis-Modelle ohne Größenangabe
            "llama3.2", "llama2", "mistral", "codellama", "gemma", "phi3",
            "neural-chat", "zephyr", "openchat", "tinyllama", "mixtral"
        ])
    
    def categorize_models_by_size(self, models):
        """Kategorisiert Modelle nach ihrer Größe"""
        categories = {
            "🟢 Klein (< 4GB RAM)": [],
            "🟡 Mittel (4-8GB RAM)": [],  
            "🟠 Groß (8-16GB RAM)": [],
            "🔴 Sehr Groß (16GB+ RAM)": []
        }
        
        for model in models:
            model_lower = model.lower()
            
            # Kleine Modelle
            if any(size in model_lower for size in ['0.5b', '1b', '1.1b', '1.5b', '2b', '2.7b', '3b', ':mini']):
                categories["🟢 Klein (< 4GB RAM)"].append(model)
            # Sehr große Modelle  
            elif any(size in model_lower for size in ['70b', '34b', '33b', '35b', '40b', '22b', '8x']):
                categories["🔴 Sehr Groß (16GB+ RAM)"].append(model)
            # Große Modelle
            elif any(size in model_lower for size in ['13b', '15b', '10.7b']):
                categories["🟠 Groß (8-16GB RAM)"].append(model)
            # Mittlere Modelle (7b und ähnliche)
            elif any(size in model_lower for size in ['7b', '6.7b', '8b']) or ':' not in model:
                categories["🟡 Mittel (4-8GB RAM)"].append(model)
            else:
                # Fallback für unbekannte Größen
                categories["🟡 Mittel (4-8GB RAM)"].append(model)
        
        # Sortiere jede Kategorie
        for category in categories:
            categories[category] = sorted(categories[category])
        
        return categories
    
    def download_model(self, model_name, progress_callback=None, parent_messenger=None):
        """Lädt ein Modell mit optimierter Performance, detailliertem Logging und Stop-Funktionalität herunter"""
        import time
        
        print(f"\n🚀 DOWNLOAD START: {model_name}")
        start_time = time.time()
        
        try:
            # Verwende die moderne ollama-client API statt requests
            print(f"📡 Verwende Ollama Client für {model_name}")
            print(f"🔗 Basis URL: {self.base_url}")
            
            # Stream-basierter Download mit ollama client
            response_stream = self.client.pull(model_name, stream=True)
            
            total_size = 0
            downloaded_size = 0
            current_layer = ""
            last_status = ""
            download_speed_samples = []
            last_time = time.time()
            last_downloaded = 0
            last_progress_update = time.time()
            
            print(f"⏳ Starte Download-Stream...")
            
            for chunk in response_stream:
                # Stop-Check für Downloads
                if parent_messenger and parent_messenger.download_stopped:
                    print(f"\n🛑 DOWNLOAD STOPPED: {model_name}")
                    print(f"⏱️  Stopped after: {time.time() - start_time:.1f} seconds")
                    return False
                
                current_time = time.time()
                
                # Status-Ausgabe nur bei Änderungen (keine Redundanz!)
                if 'status' in chunk:
                    status = chunk['status']
                    
                    # Nur neuen Status ausgeben, keine Wiederholungen
                    if status != last_status:
                        print(f"📥 Status: {status}")
                        last_status = status
                    
                    # Progress-Informationen nur alle 2 Sekunden
                    if 'total' in chunk and 'completed' in chunk:
                        total_size = chunk['total']
                        downloaded_size = chunk['completed']
                        
                        # Geschwindigkeitsberechnung und Ausgabe nur alle 2 Sekunden
                        time_diff = current_time - last_progress_update
                        if time_diff >= 2.0:  # Reduziert auf alle 2 Sekunden
                            speed_bytes = (downloaded_size - last_downloaded) / time_diff
                            download_speed_samples.append(speed_bytes)
                            
                            # Nur die letzten 5 Messungen für stabilere Durchschnittsgeschwindigkeit
                            if len(download_speed_samples) > 5:
                                download_speed_samples.pop(0)
                            
                            avg_speed = sum(download_speed_samples) / len(download_speed_samples)
                            
                            # Formatierung der Größenangaben
                            downloaded_mb = downloaded_size / (1024 * 1024)
                            total_mb = total_size / (1024 * 1024)
                            speed_mb = avg_speed / (1024 * 1024)
                            
                            progress_percent = (downloaded_size / total_size * 100) if total_size > 0 else 0
                            
                            # ETA Berechnung
                            remaining_bytes = total_size - downloaded_size
                            eta_seconds = remaining_bytes / avg_speed if avg_speed > 0 else 0
                            eta_minutes = eta_seconds / 60
                            
                            # Kompakte Ausgabe in einer Zeile
                            print(f"📊 {progress_percent:.1f}% ({downloaded_mb:.1f}/{total_mb:.1f}MB) | {speed_mb:.1f}MB/s | ETA: {eta_minutes:.1f}min")
                            
                            last_progress_update = current_time
                            last_downloaded = downloaded_size
                
                # Layer-Informationen nur bei Wechsel
                if 'digest' in chunk:
                    layer = chunk['digest'][:12]  # Kurze Layer-ID
                    if layer != current_layer:
                        current_layer = layer
                        print(f"🔄 Layer: {layer}")
                
                # Callback für UI-Updates (weniger häufig)
                if progress_callback:
                    progress_callback(chunk)
                
                # Erfolgs-Check
                if chunk.get('status') == 'success':
                    elapsed_time = time.time() - start_time
                    print(f"✅ DOWNLOAD COMPLETE: {model_name}")
                    print(f"⏱️  Total time: {elapsed_time:.1f}s ({elapsed_time/60:.1f}min)")
                    if total_size > 0:
                        total_mb = total_size / (1024 * 1024)
                        avg_speed_total = total_mb / (elapsed_time / 60)  # MB/min
                        print(f"📈 Average speed: {avg_speed_total:.1f} MB/min")
                    return True
                    
            return False
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"❌ DOWNLOAD FAILED: {model_name}")
            print(f"🚫 Error: {e}")
            print(f"⏱️  Failed after: {elapsed_time:.1f} seconds")
            return False
    
    def delete_model(self, model_name):
        """Löscht ein Modell"""
        try:
            url = f"{self.base_url}/api/delete"
            data = {"name": model_name}
            response = requests.delete(url, json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"Fehler beim Löschen: {e}")
            return False
    
    def chat_with_model(self, model_name, message, chat_history=None):
        """Chat mit einem Modell mit Anti-Redundanz Konsolen-Ausgabe"""
        import sys
        try:
            messages = chat_history or []
            messages.append({"role": "user", "content": message})
            
            # Startmeldung in Konsole
            print(f"\n🤖 {model_name}: ", end="", flush=True)
            
            response = self.client.chat(
                model=model_name,
                messages=messages,
                stream=True
            )
            
            # Anti-Redundanz Wrapper
            class AntiRedundancyWrapper:
                def __init__(self, response_stream):
                    self.response_stream = response_stream
                    self.total_content = ""
                    self.last_display = ""
                    self.char_count = 0
                
                def __iter__(self):
                    return self
                
                def __next__(self):
                    try:
                        chunk = next(self.response_stream)
                        
                        if 'message' in chunk:
                            content = chunk['message'].get('content', '')
                            if content:
                                self.total_content += content
                                self.char_count += len(content)
                                
                                # Update nur alle ~50 Zeichen für weniger Redundanz
                                if self.char_count >= 50 or '\n' in content:
                                    # Zeige aktuelle Position in der Antwort
                                    words = self.total_content.split()
                                    if len(words) > 15:
                                        # Zeige nur die letzten ~15 Wörter
                                        display = "... " + " ".join(words[-15:])
                                    else:
                                        display = self.total_content
                                    
                                    # Überschreibe nur wenn sich der Inhalt wesentlich geändert hat
                                    if display != self.last_display:
                                        # Lösche vorherige Zeile und schreibe neu
                                        if self.last_display:
                                            sys.stdout.write('\r' + ' ' * len(self.last_display) + '\r')
                                        sys.stdout.write(display[:100])  # Max 100 Zeichen
                                        sys.stdout.flush()
                                        self.last_display = display[:100]
                                    
                                    self.char_count = 0  # Reset counter
                        
                        return chunk
                        
                    except StopIteration:
                        # Finale Ausgabe
                        if self.total_content:
                            sys.stdout.write('\r' + ' ' * len(self.last_display) + '\r')
                            final_words = self.total_content.split()
                            if len(final_words) > 20:
                                final_display = "..." + " ".join(final_words[-20:]) + " ✓"
                            else:
                                final_display = self.total_content + " ✓"
                            print(final_display[:120])  # Finale Zeile mit Checkmark
                        else:
                            print("✓")
                        raise
            
            return AntiRedundancyWrapper(response)
            
        except Exception as e:
            print(f"\n❌ Fehler beim Chat: {e}")
            return None

class CategorizedComboBox(ctk.CTkComboBox):
    """Eine erweiterte ComboBox die kategorisierte Optionen unterstützt"""
    
    def __init__(self, master, categories_dict=None, **kwargs):
        self.categories_dict = categories_dict or {}
        self.flat_values = []
        self.update_values_from_categories()
        super().__init__(master, values=self.flat_values, **kwargs)
    
    def update_values_from_categories(self):
        """Erstellt eine flache Liste aus den kategorisierten Werten"""
        self.flat_values = []
        for category_name, models in self.categories_dict.items():
            if models:  # Nur Kategorien mit Inhalten anzeigen
                self.flat_values.append(f"--- {category_name} ---")
                self.flat_values.extend(models)
    
    def set_categories(self, categories_dict):
        """Aktualisiert die Kategorien"""
        self.categories_dict = categories_dict
        self.update_values_from_categories()
        self.configure(values=self.flat_values)
    
    def get_selected_model(self):
        """Gibt das ausgewählte Modell zurück (ohne Kategorie-Headers)"""
        selected = self.get()
        if selected.startswith("--- ") and selected.endswith(" ---"):
            return None  # Kategorie-Header ausgewählt
        return selected

class LLMMessenger:
    """Hauptanwendungsklasse"""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("LLM Messenger - Ollama Chat Client")
        self.root.geometry("1200x800")
        
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
        self.current_response_text = ""  # Verfolge bereits angezeigte Tokens
        
        # Nachrichten-Historie für Pfeiltasten-Navigation
        self.message_history = []  # Liste aller gesendeten Nachrichten
        self.history_index = -1    # Aktueller Index in der Historie (-1 = keine Auswahl)
        
        # YAML-Konfigurationsdatei
        self.config_file = "ki_whisperer_config.yaml"
        
        # Lade Konfiguration aus YAML-Datei
        self.config = self.load_config()
        
        self.setup_ui()
        self.check_ollama_status()
        self.setup_console_styling()
    
    def get_default_config(self):
        """Gibt die Standard-Konfiguration zurück"""
        return {
            # Bubble-Farben
            "user_bg_color": "#003300",      # Sie - Hintergrund
            "user_text_color": "#00FF00",    # Sie - Text (Matrix)
            "ai_bg_color": "#1E3A5F",        # AI - Hintergrund
            "ai_text_color": "white",        # AI - Text
            "system_bg_color": "#722F37",    # System - Hintergrund
            "system_text_color": "white",    # System - Text
            
            # Schriftarten und individuelle Größen
            "user_font": "Courier New",      # Sie - Matrix-Font
            "user_font_size": 11,            # Sie - Individuelle Größe
            "ai_font": "Consolas",           # AI - Code-Font
            "ai_font_size": 11,              # AI - Individuelle Größe
            "system_font": "Arial",          # System - Standard-Font
            "system_font_size": 10,          # System - Individuelle Größe
            
            # Konsolen-Farben
            "console_bg": "#000000",         # Konsolen-Hintergrund
            "console_text": "#FFFFFF",       # Konsolen-Text
            "console_font": "Consolas"       # Konsolen-Schriftart
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
            
            yaml_content += "\n# ========================================\n"
            yaml_content += "# SCHRIFTARTEN & GRÖßEN\n"
            yaml_content += "# ========================================\n"
            
            # Font-Konfiguration
            font_config = {k: v for k, v in config_to_save.items() if 'font' in k and 'console' not in k}
            yaml_content += "# Schriftarten und individuelle Größen\nfonts:\n"
            
            for key, value in font_config.items():
                comment = ""
                if "user" in key:
                    comment = "  # Sie (Matrix-Style)"
                elif "ai" in key:
                    comment = "  # AI-Modell"  
                elif "system" in key:
                    comment = "  # System-Nachrichten"
                
                if isinstance(value, str):
                    yaml_content += f"  {key}: \"{value}\"{comment}\n"
                else:
                    yaml_content += f"  {key}: {value}{comment}\n"
            
            yaml_content += "\n# ========================================\n"
            yaml_content += "# KONSOLEN-EINSTELLUNGEN\n"
            yaml_content += "# ========================================\n"
            
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
        print("🔄 Konfiguration auf Standardwerte zurückgesetzt und gespeichert")
    
    def setup_console_styling(self):
        """Richtet Konsolen-Styling mit ANSI-Codes ein"""
        import os
        # Aktiviere ANSI-Escape-Sequenzen für Windows
        if os.name == 'nt':
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    
    def console_print(self, text, style="normal"):
        """Konsolen-Ausgabe mit konfigurierten Farben und Styling"""
        try:
            # Hole Konsolen-Konfiguration
            bg_color = self.config.get("console_bg", "#000000")
            text_color = self.config.get("console_text", "#FFFFFF")
            
            # Konvertiere Hex zu ANSI-Codes
            def hex_to_ansi_fg(hex_color):
                """Konvertiert Hex-Farbe zu ANSI-Vordergrund-Code"""
                hex_color = hex_color.lstrip('#')
                if len(hex_color) == 6:
                    r = int(hex_color[0:2], 16)
                    g = int(hex_color[2:4], 16)
                    b = int(hex_color[4:6], 16)
                    return f"\033[38;2;{r};{g};{b}m"
                return "\033[37m"  # Weiß als Fallback
            
            def hex_to_ansi_bg(hex_color):
                """Konvertiert Hex-Farbe zu ANSI-Hintergrund-Code"""
                hex_color = hex_color.lstrip('#')
                if len(hex_color) == 6:
                    r = int(hex_color[0:2], 16)
                    g = int(hex_color[2:4], 16)
                    b = int(hex_color[4:6], 16)
                    return f"\033[48;2;{r};{g};{b}m"
                return "\033[40m"  # Schwarz als Fallback
            
            # ANSI-Codes für Styling
            reset_code = "\033[0m"
            fg_code = hex_to_ansi_fg(text_color)
            bg_code = hex_to_ansi_bg(bg_color)
            
            # Style-spezifische Codes
            style_codes = {
                "normal": "",
                "bold": "\033[1m",
                "italic": "\033[3m", 
                "underline": "\033[4m",
                "success": "\033[1m\033[32m",  # Grün + Bold
                "error": "\033[1m\033[31m",    # Rot + Bold
                "warning": "\033[1m\033[33m",  # Gelb + Bold
                "info": "\033[1m\033[36m"      # Cyan + Bold
            }
            
            style_code = style_codes.get(style, "")
            
            # Formatierte Ausgabe mit konfigurierten Farben
            if style in ["success", "error", "warning", "info"]:
                # Für spezielle Styles verwende die eingebauten Farben
                formatted_text = f"{style_code}{text}{reset_code}"
            else:
                # Für normale Ausgabe verwende konfigurierte Farben
                formatted_text = f"{bg_code}{fg_code}{style_code}{text}{reset_code}"
            
            print(formatted_text)
            
        except Exception:
            # Fallback auf normale print-Funktion
            print(text)
    
    def setup_ui(self):
        """Erstellt die Benutzeroberfläche"""
        
        # Hauptframe
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tab-System erstellen
        self.tab_view = ctk.CTkTabview(self.main_frame)
        self.tab_view.pack(fill="both", expand=True)
        
        # Chat-Tab hinzufügen
        self.chat_tab = self.tab_view.add("Chat")
        self.setup_chat_tab()
        
        # Config-Tab hinzufügen  
        self.config_tab = self.tab_view.add("Config")
        self.setup_config_tab()
        
        # Standard-Tab setzen
        self.tab_view.set("Chat")
    
    def setup_chat_tab(self):
        """Erstellt den Chat-Tab mit allen Elementen"""
        
        # Oberes Panel für Modell-Management
        self.top_panel = ctk.CTkFrame(self.chat_tab)
        self.top_panel.pack(fill="x", padx=10, pady=(10, 5))
        
        # Erste Zeile: Status und installierte Modelle
        self.first_row = ctk.CTkFrame(self.top_panel)
        self.first_row.pack(fill="x", padx=10, pady=5)
        
        # Ollama Status
        self.status_label = ctk.CTkLabel(self.first_row, text="Ollama Status: Wird geprüft...")
        self.status_label.pack(side="left", padx=10, pady=10)
        
        # Installierte Modell-Dropdown
        self.model_var = tk.StringVar()
        self.installed_label = ctk.CTkLabel(self.first_row, text="Installiert:")
        self.installed_label.pack(side="left", padx=(20, 5), pady=10)
        
        self.model_dropdown = ctk.CTkComboBox(
            self.first_row, 
            variable=self.model_var,
            values=["Keine Modelle verfügbar"],
            command=self.on_model_select,
            width=200
        )
        self.model_dropdown.pack(side="left", padx=5, pady=10)
        
        # Delete und Refresh Buttons
        self.delete_btn = ctk.CTkButton(
            self.first_row,
            text="Löschen",
            command=self.delete_selected_model,
            fg_color="red",
            hover_color="darkred",
            width=80
        )
        self.delete_btn.pack(side="left", padx=5, pady=10)
        
        self.refresh_btn = ctk.CTkButton(
            self.first_row,
            text="Aktualisieren",
            command=self.refresh_models,
            width=100
        )
        self.refresh_btn.pack(side="left", padx=5, pady=10)
        
        # Zweite Zeile: Verfügbare Modelle zum Download
        self.second_row = ctk.CTkFrame(self.top_panel)
        self.second_row.pack(fill="x", padx=10, pady=5)
        
        # Verfügbare Modelle Dropdown (kategorisiert)
        self.available_var = tk.StringVar()
        self.available_label = ctk.CTkLabel(self.second_row, text="Verfügbare Modelle (nach Größe):")
        self.available_label.pack(side="left", padx=10, pady=10)
        
        self.available_dropdown = CategorizedComboBox(
            self.second_row,
            variable=self.available_var,
            categories_dict={},
            width=350
        )
        self.available_dropdown.pack(side="left", padx=10, pady=10)
        
        # Download Button
        self.download_btn = ctk.CTkButton(
            self.second_row, 
            text="Ausgewähltes Modell herunterladen",
            command=self.download_selected_model,
            width=200
        )
        self.download_btn.pack(side="left", padx=5, pady=10)
        
        # Manueller Download Button
        self.manual_download_btn = ctk.CTkButton(
            self.second_row, 
            text="Manuell...",
            command=self.show_download_dialog,
            width=80
        )
        self.manual_download_btn.pack(side="left", padx=5, pady=10)
        self.refresh_btn.pack(side="left", padx=5, pady=10)
        
        # Chat-Bereich
        self.chat_frame = ctk.CTkFrame(self.chat_tab)
        self.chat_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
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
        self.input_frame.pack(fill="x", padx=10, pady=(5, 10))
        
        self.message_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Nachricht eingeben...",
            font=("Arial", 12)
        )
        self.message_entry.pack(side="left", fill="x", expand=True, padx=(0, 10), pady=10)
        self.message_entry.bind("<Return>", self.send_message)
        self.message_entry.bind("<Up>", self.navigate_history_up)
        self.message_entry.bind("<Down>", self.navigate_history_down)
        self.message_entry.bind("<Key>", self.on_key_press)
        
        self.send_btn = ctk.CTkButton(
            self.input_frame,
            text="Senden",
            command=self.send_message
        )
        self.send_btn.pack(side="right", pady=10)
        
        # Stop Button (initial deaktiviert)
        self.stop_btn = ctk.CTkButton(
            self.input_frame,
            text="Stop",
            command=self.stop_generation,
            fg_color="red",
            hover_color="darkred",
            width=60,
            state="disabled"
        )
        self.stop_btn.pack(side="right", padx=(0, 10), pady=10)
        
        # Export Button
        self.export_btn = ctk.CTkButton(
            self.input_frame,
            text="📄 Export",
            command=self.export_session,
            width=80,
            fg_color="#4a4a4a",
            hover_color="#5a5a5a"
        )
        self.export_btn.pack(side="right", padx=(0, 5), pady=10)
        
        # Progress Bar (initial versteckt) - im Chat-Tab
        self.progress_frame = ctk.CTkFrame(self.chat_tab)
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="Download läuft...")
        self.progress_label.pack(pady=5)
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(fill="x", padx=20, pady=5)
        
        # Initial Chat-Nachricht
        self.add_to_chat("System", "Willkommen im LLM Messenger! Wählen Sie ein Modell aus oder laden Sie eines herunter.")
    
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
        apply_btn = ctk.CTkButton(button_container, text="✅ Anwenden", command=self.apply_config, 
                                 width=140, height=35, font=("Arial", 12, "bold"))
        apply_btn.pack(side="left", padx=(15, 10), pady=15)
        
        reset_btn = ctk.CTkButton(button_container, text="🔄 Standard", command=self.reset_config, 
                                 width=140, height=35, font=("Arial", 12, "bold"))
        reset_btn.pack(side="left", padx=(10, 15), pady=15)
        
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
        
        # Konsolen-Einstellungen Sektion - Direkt nach Schriftarten
        console_frame = ctk.CTkFrame(config_scroll)
        console_frame.pack(fill="x", pady=(10, 15))
        
        console_title = ctk.CTkLabel(console_frame, text="⚫ Konsole", font=("Arial", 16, "bold"))
        console_title.pack(pady=(10, 5))
        
        # Konsolen-Farben - Horizontal Layout
        console_main_frame = ctk.CTkFrame(console_frame)
        console_main_frame.pack(fill="x", padx=15, pady=5)
        
        console_colors_frame = ctk.CTkFrame(console_main_frame)
        console_colors_frame.pack(side="left", fill="x", expand=True, padx=5)
        
        self.console_bg_entry, self.console_bg_preview = self.setup_color_input_with_preview(
            console_colors_frame, "Hintergrund:", "console_bg", "#000000")
        self.console_text_entry, self.console_text_preview = self.setup_color_input_with_preview(
            console_colors_frame, "Text:", "console_text", "#FFFFFF")
        
        # Konsolen-Font - Horizontal 
        console_font_frame = ctk.CTkFrame(console_main_frame)
        console_font_frame.pack(side="right", padx=5, pady=2)
        ctk.CTkLabel(console_font_frame, text="Font:", width=40).pack(side="left", padx=2)
        self.console_font_combo = ctk.CTkComboBox(console_font_frame,
            values=["Consolas", "Courier New", "Lucida Console", "Monaco"], width=120)
        self.console_font_combo.pack(side="left", padx=2)
        self.console_font_combo.set(self.config["console_font"])
    
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
            # Update Config-Dictionary
            self.config["user_bg_color"] = self.user_bg_entry.get() or "#003300"
            self.config["user_text_color"] = self.user_text_entry.get() or "#00FF00"
            self.config["ai_bg_color"] = self.ai_bg_entry.get() or "#1E3A5F"
            self.config["ai_text_color"] = self.ai_text_entry.get() or "white"
            self.config["system_bg_color"] = self.system_bg_entry.get() or "#722F37"
            self.config["system_text_color"] = self.system_text_entry.get() or "white"
            
            # Individuelle Schriftarten und Größen
            self.config["user_font"] = self.user_font_combo.get()
            self.config["user_font_size"] = int(self.user_font_size_slider.get())
            self.config["ai_font"] = self.ai_font_combo.get()
            self.config["ai_font_size"] = int(self.ai_font_size_slider.get())
            self.config["system_font"] = self.system_font_combo.get()
            self.config["system_font_size"] = int(self.system_font_size_slider.get())
            
            self.config["console_bg"] = self.console_bg_entry.get() or "#000000"
            self.config["console_text"] = self.console_text_entry.get() or "#FFFFFF"
            self.config["console_font"] = self.console_font_combo.get()
            
            # Speichere Konfiguration in YAML-Datei
            self.save_config()
            
            # Show success message
            self.add_to_chat("System", "✅ Konfiguration erfolgreich angewendet und gespeichert! Neue Nachrichten verwenden die neuen Einstellungen.")
            
            # Teste Konsolen-Ausgabe mit neuen Einstellungen
            self.test_console_output()
            
        except Exception as e:
            self.add_to_chat("System", f"❌ Fehler beim Anwenden der Konfiguration: {e}")
    
    def test_console_output(self):
        """Testet die Konsolen-Ausgabe mit den aktuellen Einstellungen"""
        try:
            self.console_print("\n" + "="*50, "normal")
            self.console_print("🎨 KONSOLEN-EINSTELLUNGEN TEST", "info")
            self.console_print("="*50, "normal")
            self.console_print(f"Hintergrund: {self.config['console_bg']}", "normal")
            self.console_print(f"Textfarbe: {self.config['console_text']}", "normal")
            self.console_print(f"Schriftart: {self.config['console_font']}", "normal")
            self.console_print("✅ Erfolgsmeldung", "success")
            self.console_print("⚠️ Warnungsmeldung", "warning") 
            self.console_print("❌ Fehlermeldung", "error")
            self.console_print("ℹ️ Informationsmeldung", "info")
            self.console_print("📝 Normale Ausgabe", "normal")
            self.console_print("="*50, "normal")
        except Exception as e:
            print(f"Konsolen-Test fehlgeschlagen: {e}")
    
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
        
        # Konsole
        self.console_bg_entry.delete(0, 'end')
        self.console_bg_entry.insert(0, self.config["console_bg"])
        self.console_text_entry.delete(0, 'end')
        self.console_text_entry.insert(0, self.config["console_text"])
        self.console_font_combo.set(self.config["console_font"])
        
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
            self.chat_history = []  # Chat-Historie zurücksetzen
            self.add_to_chat("System", f"Modell gewechselt zu: {choice}")
    
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
        
        # Nachricht anzeigen
        self.add_to_chat("Sie", message)
        self.message_entry.delete(0, 'end')
        
        # UI während Generation anpassen
        self.stop_btn.configure(state="normal")
        self.send_btn.configure(state="disabled")
        
        # Antwort abrufen
        def get_response():
            try:
                # Denkprozess-Indikator hinzufügen
                self.root.after(0, self.add_thinking_indicator)
                
                response_stream = self.ollama.chat_with_model(
                    self.current_model, 
                    message, 
                    self.chat_history.copy()
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
                        
                        # Chat-Historie aktualisieren
                        self.chat_history.append({"role": "user", "content": message})
                        self.chat_history.append({"role": "assistant", "content": full_response})
                    
            except Exception as e:
                if not self.generation_stopped:
                    self.root.after(0, lambda: self.add_to_chat("System", f"❌ Fehler: {str(e)}"))
            finally:
                # UI zurücksetzen
                self.root.after(0, self.reset_generation_ui)
        
        # Thread starten und speichern
        self.current_generation_thread = threading.Thread(target=get_response, daemon=True)
        self.current_generation_thread.start()
    
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
    
    def add_to_chat(self, sender, message):
        """Fügt eine Chat-Bubble zum Chat hinzu"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Erstelle neue Chat-Bubble mit aktueller Config
        bubble = ChatBubble(
            self.chat_display_frame,
            sender=sender,
            message=message,
            timestamp=timestamp,
            app_config=self.config
        )
        
        # Füge Bubble zur Liste hinzu
        self.chat_bubbles.append(bubble)
        
        # Scrolle nach unten
        self.chat_display_frame._parent_canvas.after(100, 
            lambda: self.chat_display_frame._parent_canvas.yview_moveto(1.0))
        
        return bubble
    
    def add_thinking_indicator(self):
        """Zeigt dezenten Denkprozess-Indikator an"""
        thinking_message = "💭 Verarbeitet Ihre Anfrage..."
        bubble = self.add_to_chat(f"🤖 {self.current_model}", thinking_message)
        self.current_thinking_bubble = bubble
        return bubble
    
    def remove_last_message(self):
        """Entfernt die letzte Nachricht (Thinking-Indikator)"""
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
                        "total_messages": len(self.chat_bubbles)
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
        lines.append(f"**Anzahl Nachrichten:** {len(self.chat_bubbles)}")
        
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
    
    def run(self):
        """Startet die Anwendung"""
        self.root.mainloop()

if __name__ == "__main__":
    app = LLMMessenger()
    app.run()