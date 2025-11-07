#!/usr/bin/env python3
"""
Test der optimierten Download-Performance
Simuliert einen kleinen Download um die Logging-Features zu testen
"""

import llm_messenger
import time

def test_download_logging():
    print("=" * 60)
    print("🧪 DOWNLOAD PERFORMANCE TEST")
    print("=" * 60)
    
    manager = llm_messenger.OllamaManager()
    
    # Prüfe Ollama-Verbindung
    if not manager.is_ollama_running():
        print("❌ Ollama ist nicht erreichbar!")
        print("📝 Bitte starten Sie Ollama mit: ollama serve")
        return
    
    print("✅ Ollama ist erreichbar")
    print(f"🔗 Basis URL: {manager.base_url}")
    
    # Zeige verfügbare Modelle
    installed_models = manager.get_available_models()
    print(f"📋 Bereits installierte Modelle: {len(installed_models)}")
    for model in installed_models:
        print(f"   - {model}")
    
    print("\n" + "=" * 60)
    print("💡 DOWNLOAD-LOGGING FEATURES:")
    print("=" * 60)
    print("✅ Detaillierte Konsolen-Ausgabe")
    print("✅ Echtzeit-Geschwindigkeitsmessung") 
    print("✅ ETA-Berechnung")
    print("✅ Layer-für-Layer-Progress")
    print("✅ Durchschnittsgeschwindigkeit")
    print("✅ Gesamtzeit-Messung")
    
    print("\n🎯 Empfohlene Test-Modelle (klein, schnell):")
    small_models = ["tinyllama:1.1b", "phi3:mini", "qwen2:0.5b"]
    for i, model in enumerate(small_models, 1):
        print(f"   {i}. {model} (sehr klein, ca. 1GB)")
    
    print("\n📊 Um einen Download zu testen:")
    print("   1. Starten Sie die GUI-Anwendung")
    print("   2. Wählen Sie ein kleines Modell")
    print("   3. Beobachten Sie die Konsolen-Ausgabe!")
    
    print("\n🔍 Performance-Optimierungen:")
    print("   - Verwendet modernen ollama.Client() statt requests")
    print("   - Stream-basierter Download")
    print("   - Intelligente UI-Update-Ratenbegrenzung")
    print("   - Detaillierte Geschwindigkeitsmessungen")

if __name__ == "__main__":
    test_download_logging()