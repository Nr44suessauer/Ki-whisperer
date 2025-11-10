"""OllamaManager für Ollama-API-Interaktionen"""

import ollama
import requests
import time

class OllamaManager:
    def _get_fallback_models(self):
        """Fallback-List mit bewährten Modellen"""
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
    """Klasse für Ollama-API-Interaktionen"""
    
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.client = ollama.Client()
    
    def is_ollama_running(self):
        """Prüft ob Ollama running"""
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
            print(f"Error beim Abrufen der Modelle: {e}")
            return []
    
    def get_all_ollama_models(self):
        """Holt alle verfügbaren Ollama-Modelle direkt von der offiziellen API"""
        try:
            # Versuche zuerst die offizielle Ollama Library API
            url = "https://registry.ollama.ai/v2/_catalog"
            headers = {
                'User-Agent': 'A1-Terminal/1.0',
                'Accept': 'application/json'
            }
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = data.get('repositories', [])
                # Erweitere mit beliebten Varianten falls available
                expanded_models = []
                for model in models:
                    expanded_models.append(model)
                    for size in [':7b', ':13b', ':34b', ':70b']:
                        variant = f"{model}{size}"
                        if variant not in expanded_models:
                            expanded_models.append(variant)
                return sorted(expanded_models)
            else:
                # Fallback auf bewährte Model-List
                return self._get_fallback_models()
        except Exception as e:
            print(f"Error beim Abrufen der Live-Modelle: {e}")
            return self._get_fallback_models()
    
    def download_model(self, model_name, progress_callback=None, parent_messenger=None):
        """Lädt ein Model mit optimierter Performance, detailliertem Logging und Stop-Funktionalität herunter"""
        import time
        
        print(f"\n🚀 DOWNLOAD START: {model_name}")
        start_time = time.time()
        
        try:
            # Use modern ollama client API instead of requests
            print(f"📡 Using Ollama client for {model_name}")
            print(f"🔗 Base URL: {self.base_url}")
            
            # Stream-based download with ollama client
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
                
                # Status-Output nur bei Änderungen (keine Redundanz!)
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
                        
                        # Geschwindigkeitsberechnung und Output nur alle 2 Sekunden
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
                            
                            # Kompakte Output in einer Zeile
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
        """Löscht ein Model"""
        try:
            url = f"{self.base_url}/api/delete"
            data = {"name": model_name}
            response = requests.delete(url, json=data)
            return response.status_code == 200
        except Exception as e:
            print(f"Error beim Delete: {e}")
            return False
    
    def list_models(self):
        """Alias für get_available_models"""
        return self.get_available_models()
    
    def chat_stream(self, model_name, messages):
        """Stream-Chat mit einem Model - gibt nur Content-Chunks back"""
        try:
            response = self.client.chat(
                model=model_name,
                messages=messages,
                stream=True
            )
            
            for chunk in response:
                if 'message' in chunk:
                    content = chunk['message'].get('content', '')
                    if content:
                        yield content
        except Exception as e:
            print(f"Chat-Stream-Error: {e}")
            yield ""
    
    def download_model_stream(self, model_name):
        """Download eines Modells mit Progress-Stream"""
        try:
            response = self.client.pull(model_name, stream=True)
            for chunk in response:
                yield chunk
        except Exception as e:
            print(f"Download-Error: {e}")
            yield {"status": "error", "error": str(e)}
    
    def chat_with_model(self, model_name, message, chat_history=None):
        """Chat mit einem Model mit Anti-Redundanz Konsolen-Output"""
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
                                    
                                    # Überschreibe nur wenn sich der Inhalt wesentlich changed hat
                                    if display != self.last_display:
                                        # Lösche vorherige Zeile und schreibe new
                                        if self.last_display:
                                            sys.stdout.write('\r' + ' ' * len(self.last_display) + '\r')
                                        sys.stdout.write(display[:100])  # Max 100 Zeichen
                                        sys.stdout.flush()
                                        self.last_display = display[:100]
                                    
                                    self.char_count = 0  # Reset counter
                        
                        return chunk
                        
                    except StopIteration:
                        # Finale Output
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
            print(f"\n❌ Error beim Chat: {e}")
            return None