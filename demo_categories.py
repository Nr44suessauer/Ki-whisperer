#!/usr/bin/env python3
"""
Demo der kategorisierten Modell-Anzeige
Zeigt wie die Kategorien im Dropdown aussehen würden
"""

import llm_messenger

def show_categorized_demo():
    print("=" * 60)
    print("🎨 LLM MESSENGER - KATEGORISIERTE MODELL-ÜBERSICHT")
    print("=" * 60)
    
    manager = llm_messenger.OllamaManager()
    models = manager.get_all_ollama_models()
    categories = manager.categorize_models_by_size(models)
    
    print(f"\n📊 Live-Daten: {len(models)} Modelle aus der Ollama-Registry")
    print("\n🎛️ Dropdown-Menü Vorschau:")
    print("┌─────────────────────────────────────────────────┐")
    print("│ Verfügbare Modelle (nach Größe):            ▼ │")
    print("├─────────────────────────────────────────────────┤")
    print("│ 🔍 Wählen Sie eine Kategorie oder Modell...    │")
    
    for category_name, category_models in categories.items():
        if category_models:
            print(f"│ --- {category_name} ---")
            # Zeige nur die ersten 5 Modelle pro Kategorie für Demo
            for model in category_models[:5]:
                print(f"│   {model}")
            if len(category_models) > 5:
                print(f"│   ... und {len(category_models) - 5} weitere Modelle")
            print("│")
    
    print("└─────────────────────────────────────────────────┘")
    
    print("\n💡 Features:")
    print("✅ Live-API Integration - Immer aktuelle Modelle")  
    print("✅ Farbkodierte Kategorien nach RAM-Bedarf")
    print("✅ Intelligente Größen-Erkennung") 
    print("✅ Benutzerfreundliche Gruppenierung")
    print("✅ Hardware-gerechte Modell-Auswahl")
    
    print(f"\n📈 Statistiken:")
    for category_name, category_models in categories.items():
        print(f"   {category_name}: {len(category_models)} Modelle")

if __name__ == "__main__":
    show_categorized_demo()