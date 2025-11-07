#!/usr/bin/env python3
"""Test der neuen Live-API und Kategorisierung"""

import llm_messenger

def test_live_api():
    print("🧪 Teste Live-Ollama-API und Kategorisierung...")
    
    manager = llm_messenger.OllamaManager()
    
    # Live-Modelle abrufen
    print("📡 Lade aktuelle Modelle...")
    models = manager.get_all_ollama_models()
    print(f"✅ {len(models)} Modelle gefunden")
    
    # Kategorisierung testen
    print("\n📊 Kategorisiere nach Größe...")
    categories = manager.categorize_models_by_size(models)
    
    for category_name, category_models in categories.items():
        print(f"{category_name}: {len(category_models)} Modelle")
        if category_models:
            print(f"   Beispiele: {', '.join(category_models[:3])}")
            if len(category_models) > 3:
                print(f"   ... und {len(category_models) - 3} weitere")
        print()
    
    print(f"🎯 Gesamt: {sum(len(models) for models in categories.values())} Modelle in {len(categories)} Kategorien")

if __name__ == "__main__":
    test_live_api()