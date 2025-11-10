#!/usr/bin/env python3
"""
Bulk UI Translation Script for German -> English
Translates UI labels, buttons, and message boxes
"""

import re
import os

# UI translations dictionary
UI_TRANSLATIONS = {
    # Dialog titles and labels
    r'"Session umbenennen"': '"Rename session"',
    r'"Neuer Name:"': '"New name:"',
    r'"⚠️ Name darf nicht leer sein!"': '"⚠️ Name must not be empty!"',
    r'"Farbe für .+ select"': lambda m: m.group(0).replace("Farbe für", "Color for").replace("select", ""),
    r'"🎨 Farbkreis"': '"🎨 Color Wheel"',
    r'"Vorschau:"': '"Preview:"',
    r'"Vordefinierte Farben:"': '"Predefined colors:"',
    r'"Schnellauswahl:"': '"Quick selection:"',
    r'"⚙️ Einstellungen: (.+)"': r'"⚙️ Settings: \1"',
    r'"✏️ Session-Name"': '"✏️ Session Name"',
    r'"🎨 Session-Farbe"': '"🎨 Session Color"',
    
    # Color names
    r'Blau': 'Blue',
    r'Grün': 'Green',
    r'Rot': 'Red',
    r'Orange': 'Orange',
    r'Lila': 'Purple',
    r'Türkis': 'Turquoise',
    r'Gelb': 'Yellow',
    r'Rosa': 'Pink',
    r'Grau': 'Gray',
    r'Schwarz': 'Black',
    r'Weiß': 'White',
    
    # Configuration window
    r'"🔄 Übernehmen & Neustart"': '"🔄 Apply & Restart"',
    r'"↩️ Standard"': '"↩️ Default"',
    r'"🎨 Chat-Bubble Farben"': '"🎨 Chat Bubble Colors"',
    r'"🔤 Schriftarten"': '"🔤 Fonts"',
    r'"Größe:"': '"Size:"',
    r'"🎛️ Layout & Größen"': '"🎛️ Layout & Sizes"',
    r'"⌨️ Input & Buttons"': '"⌨️ Input & Buttons"',
    r'"⚡ Erweiterte Optionen"': '"⚡ Advanced Options"',
    r'"Hallo Welt! 123"': '"Hello World! 123"',
    
    # Export dialog
    r'"📄 Export-Format auswählen"': '"📄 Select Export Format"',
    r'"Verfügbare Formate:"': '"Available Formats:"',
    r'"Format-Vorschau:"': '"Format Preview:"',
    r'"📤 Exportieren"': '"📤 Export"',
    r'"📄 Markdown-Format"': '"📄 Markdown Format"',
    r'"📊 JSON-Format"': '"📊 JSON Format"',
    r'"Menschenfreundlich"': '"Human-friendly"',
    r'"Maschinenlesbar"': '"Machine-readable"',
    r'"Formatiert & lesbar"': '"Formatted & readable"',
    r'"Für Dokumentation"': '"For documentation"',
    r'"Strukturierte Daten"': '"Structured data"',
    r'"Für APIs & Tools"': '"For APIs & Tools"',
    r'"GitHub-kompatibel"': '"GitHub-compatible"',
    r'"Übersichtlich"': '"Clear"',
    r'"Vollständiger Daten-Export inkl. Metadaten"': '"Complete data export incl. metadata"',
    
    # Model dropdown
    r'"Model auswählen..."': '"Select model..."',
    r'"⬇️ Neues Model hinzufügen"': '"⬇️ Add new model"',
    r'"➕ Neues Model hinzufügen"': '"➕ Add new model"',
    
    # Message boxes
    r'"Warnung"': '"Warning"',
    r'"Bitte select You ein Model zum Download aus!"': '"Please select a model to download!"',
    r'"Kein Model ausgewählt!"': '"No model selected!"',
    r'"Bitte geben You einen Modellnamen ein!"': '"Please enter a model name!"',
    r'"ist bereits installed!"': '"is already installed!"',
    r'"Keine aktive Session zum Exportieren!"': '"No active session to export!"',
    r'"Erfolg"': '"Success"',
    r'"Session exportiert nach:"': '"Session exported to:"',
    r'"Keine Chat-Session zum Exportieren vorhanden!"': '"No chat session available to export!"',
    r'"Export erfolgreich"': '"Export successful"',
    r'"Export"': '"Export"',
    
    # Session warnings
    r'"Möchten Sie"': '"Do you want"',
    r'"wirklich löschen"': '"really delete"',
    r'"Alle Sessions löschen"': '"Delete all sessions"',
    r'"Möchten Sie ALLE Sessions löschen"': '"Do you want to delete ALL sessions"',
    
    # Additional labels
    r'Setzen You den Kontext': 'Set the context',
    r'und die Instruktionen für diese Session': 'and instructions for this session',
    
    # Config text
    r'Farbkonfiguration über Config-Tab': 'Color configuration via Config tab',
    r'in der alten Version available': 'available in old version',
    r'Modernes Theme is being verwendet': 'Modern theme is being used',
}

def translate_file(filepath):
    """Translates a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply all translations
        for pattern, replacement in UI_TRANSLATIONS.items():
            if callable(replacement):
                content = re.sub(pattern, replacement, content)
            else:
                content = re.sub(pattern, replacement, content)
        
        # Only write if changes were made
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
            
    except Exception as e:
        print(f"❌ Error translating {filepath}: {e}")
        return False

def main():
    """Main translation function"""
    files_to_translate = [
        "a1_terminal_modular/src/core/a1_terminal.py",
        "a1_terminal_modular/src/ui/model_info_dropdown.py",
        "a1_terminal_modular/src/ui/ultimate_ui.py",
        "a1_terminal_modular/src/ui/modern_ui.py",
        "a1_terminal_modular/src/ui/model_selector.py",
        "a1_terminal_modular/src/ui/color_wheel.py",
    ]
    
    modified_count = 0
    for filepath in files_to_translate:
        if os.path.exists(filepath):
            if translate_file(filepath):
                print(f"✅ Translated: {filepath}")
                modified_count += 1
            else:
                print(f"ℹ️ No changes: {filepath}")
        else:
            print(f"⚠️ File not found: {filepath}")
    
    print(f"\n✨ Translation complete! {modified_count} files modified.")

if __name__ == "__main__":
    main()
