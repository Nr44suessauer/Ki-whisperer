#!/usr/bin/env python3
"""
LLM Messenger - Ein Chat-Client für Ollama
Ein moderner Chat-Client mit Ollama-Integration für lokale AI-Modelle
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, scrolledtext
import requests
import json
import threading
import time
from datetime import datetime
import ollama
import os

# Erscheinungsbild konfigurieren
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

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
        
        self.setup_ui()
        self.check_ollama_status()
    
    def setup_ui(self):
        """Erstellt die Benutzeroberfläche"""
        
        # Hauptframe
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Oberes Panel für Modell-Management
        self.top_panel = ctk.CTkFrame(self.main_frame)
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
        self.chat_frame = ctk.CTkFrame(self.main_frame)
        self.chat_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Chat-Verlauf
        self.chat_display = ctk.CTkTextbox(
            self.chat_frame,
            wrap="word",
            font=("Consolas", 12)
        )
        self.chat_display.pack(fill="both", expand=True, padx=10, pady=(10, 5))
        
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
        
        # Progress Bar (initial versteckt)
        self.progress_frame = ctk.CTkFrame(self.main_frame)
        self.progress_label = ctk.CTkLabel(self.progress_frame, text="Download läuft...")
        self.progress_label.pack(pady=5)
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.pack(fill="x", padx=20, pady=5)
        
        # Initial Chat-Nachricht
        self.add_to_chat("System", "Willkommen im LLM Messenger! Wählen Sie ein Modell aus oder laden Sie eines herunter.")
    
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
                    self.response_message_widget = None
                    self.current_response_text = ""  # Reset für neue Antwort
                    
                    # Echte progressive Anzeige - nur neue Tokens anhängen
                    for chunk in response_stream:
                        # Stop-Check
                        if self.generation_stopped:
                            self.root.after(0, lambda: self.add_to_chat("System", "🛑 Generation gestoppt"))
                            break
                            
                        if 'message' in chunk:
                            content = chunk['message'].get('content', '')
                            if content:
                                full_response += content
                                
                                # Finde nur die NEUEN Tokens
                                new_tokens = full_response[len(self.current_response_text):]
                                
                                if new_tokens:  # Nur wenn wirklich neue Tokens da sind
                                    def append_new_tokens(tokens=new_tokens):
                                        if self.response_message_widget is None:
                                            # Erste Tokens: Entferne "Denkt..." und starte Antwort
                                            self.remove_last_message()
                                            # Formatiere nur die ersten Tokens
                                            formatted_content = self.format_ai_response(tokens)
                                            self.response_message_widget = self.add_to_chat(f"🤖 {self.current_model}", formatted_content)
                                            self.current_response_text = tokens
                                        else:
                                            # Weitere Tokens: Hänge NUR neue an
                                            self.append_to_last_message(tokens)
                                            self.current_response_text += tokens
                                    
                                    self.root.after(0, append_new_tokens)
                    
                    # Chat-Historie aktualisieren
                    if full_response and not self.generation_stopped:
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
    
    def add_thinking_indicator(self):
        """Zeigt dezenten Denkprozess-Indikator an"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        thinking_text = f"[{timestamp}] 🤖 {self.current_model}\n```\n💭 Verarbeitet Ihre Anfrage...\n```\n\n"
        self.chat_display.insert("end", thinking_text)
        self.chat_display.see("end")
        self.last_message_start = self.chat_display.index("end-2c linestart")
        self.last_sender = f"🤖 {self.current_model}"
        return self.last_message_start
    
    def add_to_chat(self, sender, message):
        """Fügt eine Nachricht zum Chat hinzu mit verbesserter Formatierung"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if sender == "Sie":
            formatted = f"[{timestamp}] 👤 Sie:\n{message}\n\n"
            self.chat_display.insert("end", formatted)
        elif sender == "System":
            formatted = f"[{timestamp}] ℹ️  System: {message}\n\n"
            self.chat_display.insert("end", formatted)
        else:
            # AI-Antwort mit strukturierter Formatierung
            formatted_content = self.format_ai_response(message)
            formatted = f"[{timestamp}] {sender}:\n{formatted_content}\n\n"
            self.chat_display.insert("end", formatted)
        
        self.chat_display.see("end")
        self.last_message_start = self.chat_display.index("end-2c linestart")
        return self.last_message_start
    
    def update_last_message(self, new_content):
        """Aktualisiert die letzte Nachricht mit neuem Inhalt (für progressive Anzeige)"""
        if hasattr(self, 'last_message_start') and self.last_message_start:
            try:
                # Entferne nur den Inhalt der letzten Nachricht, nicht den Timestamp/Header
                current_content = self.chat_display.get(self.last_message_start, "end")
                
                # Finde den Start des eigentlichen Nachrichteninhalts (nach dem Header)
                lines = current_content.split('\n')
                if len(lines) > 1:
                    # Header behalten, nur Inhalt ersetzen
                    header_line = lines[0]  # z.B. "[14:30:25] 🤖 llama2:13b:"
                    
                    # Lösche die alte Nachricht
                    self.chat_display.delete(self.last_message_start, "end")
                    
                    # Formatiere den neuen Inhalt
                    formatted_content = self.format_ai_response(new_content)
                    
                    # Füge Header + neuen Inhalt hinzu
                    updated_message = f"{header_line}\n{formatted_content}\n\n"
                    self.chat_display.insert(self.last_message_start, updated_message)
                    self.chat_display.see("end")
                    
            except Exception as e:
                # Fallback: Einfach anhängen falls Update fehlschlägt
                print(f"Update-Fehler: {e}")
                formatted_content = self.format_ai_response(new_content)
                self.chat_display.insert("end", formatted_content)
                self.chat_display.see("end")
    
    def append_to_last_message(self, new_tokens):
        """Hängt NUR neue Tokens an die letzte Nachricht an (echtes Streaming)"""
        try:
            # Formatiere die neuen Tokens (ohne komplettes Re-Format)
            formatted_new_tokens = new_tokens
            
            # Füge die neuen Tokens direkt am Ende der letzten Nachricht hinzu
            # Gehe zum Ende der letzten Nachricht (vor dem abschließenden \n\n)
            end_pos = self.chat_display.index("end-1c")
            
            # Suche den Punkt vor den letzten beiden Newlines
            current_content = self.chat_display.get("1.0", end_pos)
            
            # Finde die Position zum Anhängen (vor den letzten \n\n)
            if current_content.endswith('\n\n'):
                insert_pos = self.chat_display.index("end-3c")  # Vor \n\n
            else:
                insert_pos = self.chat_display.index("end-1c")  # Am Ende
            
            # Füge nur die neuen Tokens hinzu
            self.chat_display.insert(insert_pos, formatted_new_tokens)
            self.chat_display.see("end")
            
        except Exception as e:
            # Fallback: Anhängen am Ende
            print(f"Append-Fehler: {e}")
            self.chat_display.insert("end-1c", new_tokens)
            self.chat_display.see("end")
    
    def update_streaming_response(self, sender, content):
        """Legacy-Methode für Kompatibilität - leitet an smarte Version weiter"""
        self.update_streaming_response_smart(sender, content)
    
    def update_streaming_response_smart(self, sender, content):
        """Intelligente Streaming-Antwort Updates - Anti-Redundanz für GUI"""
        # Entferne die letzte Antwort nur wenn sie vom selben Sender ist
        try:
            if hasattr(self, 'last_message_start') and hasattr(self, 'last_sender'):
                if self.last_sender == sender:
                    self.chat_display.delete(self.last_message_start, "end")
        except:
            pass
        
        # Verwende einen FESTEN Timestamp für diese Streaming-Session
        if not hasattr(self, 'current_stream_timestamp'):
            self.current_stream_timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Zeige nur die letzten ~200 Zeichen für bessere Performance
        display_content = content
        if len(content) > 200:
            # Zeige "..." + letzte 190 Zeichen
            display_content = "..." + content[-190:]
        
        # Formatiere AI-Antwort strukturiert
        formatted_content = self.format_ai_response(display_content)
        
        # Füge aktualisierte Antwort mit FESTEM Timestamp hinzu
        formatted = f"[{self.current_stream_timestamp}] {sender}:\n{formatted_content}\n\n"
        self.chat_display.insert("end", formatted)
        self.chat_display.see("end")
        self.last_message_start = self.chat_display.index("end-2c linestart")
        self.last_sender = sender
    
    def finalize_streaming_response(self, sender, content):
        """Finalisiert die Streaming-Antwort mit komplettem Inhalt"""
        # Entferne die letzte temporäre Antwort
        try:
            if hasattr(self, 'last_message_start') and hasattr(self, 'last_sender'):
                if self.last_sender == sender:
                    self.chat_display.delete(self.last_message_start, "end")
        except:
            pass
        
        # Verwende den ursprünglichen Stream-Timestamp
        timestamp = getattr(self, 'current_stream_timestamp', datetime.now().strftime("%H:%M:%S"))
        
        # Formatiere komplette AI-Antwort strukturiert
        formatted_content = self.format_ai_response(content)
        
        # Füge finale vollständige Antwort hinzu
        formatted = f"[{timestamp}] {sender}:\n{formatted_content}\n\n"
        self.chat_display.insert("end", formatted)
        self.chat_display.see("end")
        self.last_message_start = self.chat_display.index("end-2c linestart")
        self.last_sender = sender
        
        # Reset Stream-Timestamp für nächste Session
        if hasattr(self, 'current_stream_timestamp'):
            delattr(self, 'current_stream_timestamp')
    
    def remove_last_message(self):
        """Entfernt die letzte Nachricht"""
        try:
            if hasattr(self, 'last_message_start'):
                self.chat_display.delete(self.last_message_start, "end")
        except:
            pass
    
    def run(self):
        """Startet die Anwendung"""
        self.root.mainloop()

if __name__ == "__main__":
    app = LLMMessenger()
    app.run()