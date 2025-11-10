#!/usr/bin/env python3
"""
Bulk translation script for German to English
Translates all German strings in the project
"""

import re
import os

# Translation dictionary (German -> English)
TRANSLATIONS = {
    # Common words
    "Fehler": "Error",
    "Konfiguration": "Configuration",
    "Modell": "Model",
    "Session": "Session",
    "Speichern": "Save",
    "speichern": "save",
    "gespeichert": "saved",
    "Löschen": "Delete",
    "löschen": "delete",
    "gelöscht": "deleted",
    "Laden": "Load",
    "laden": "load",
    "geladen": "loaded",
    "Installiert": "Installed",
    "installiert": "installed",
    "Verfügbar": "Available",
    "verfügbar": "available",
    "Download": "Download",
    "Aktualisieren": "Refresh",
    "aktualisieren": "refresh",
    "Erstellen": "Create",
    "erstellen": "create",
    "erstellt": "created",
    "Öffnen": "Open",
    "öffnen": "open",
    "Schließen": "Close",
    "schließen": "close",
    "Wählen": "Select",
    "wählen": "select",
    "Ordner": "Folder",
    "Datei": "File",
    "Verzeichnis": "Directory",
    "Status": "Status",
    "Nachrichten": "Messages",
    "Nachricht": "Message",
    "Senden": "Send",
    "senden": "send",
    "gesendet": "sent",
    "Empfangen": "Receive",
    "empfangen": "receive",
    "empfangen": "received",
    "Eingabe": "Input",
    "Ausgabe": "Output",
    "Bereich": "Area",
    "Liste": "List",
    "Anzeigen": "Show",
    "anzeigen": "show",
    "Verbergen": "Hide",
    "verbergen": "hide",
    "Ändern": "Change",
    "ändern": "change",
    "geändert": "changed",
    "Starten": "Start",
    "starten": "start",
    "gestartet": "started",
    "Stoppen": "Stop",
    "stoppen": "stop",
    "gestoppt": "stopped",
    "Abbrechen": "Cancel",
    "abbrechen": "cancel",
    "abgebrochen": "canceled",
    "Fortsetzen": "Continue",
    "fortsetzen": "continue",
    "Neu": "New",
    "neu": "new",
    "Alt": "Old",
    "alt": "old",
    "Aktiv": "Active",
    "aktiv": "active",
    "Inaktiv": "Inactive",
    "inaktiv": "inactive",
    "Fertig": "Done",
    "fertig": "done",
    "Bereit": "Ready",
    "bereit": "ready",
    "Warten": "Waiting",
    "warten": "waiting",
    "Läuft": "Running",
    "läuft": "running",
    "Wird": "Is being",
    "wird": "is being",
    "geprüft": "checked",
    "Prüfen": "Check",
    "prüfen": "check",
    "Debug": "Debug",
    "Manuell": "Manual",
    "manuell": "manual",
    "Automatisch": "Automatic",
    "automatisch": "automatic",
    
    # Phrases and sentences
    "Wird geprüft": "Checking",
    "wird geprüft": "is being checked",
    "Wählen Sie ein Modell aus": "Select a model",
    "um Details anzuzeigen": "to show details",
    "Download läuft": "Download running",
    "Neue Session": "New Session",
    "Session löschen": "Delete Session",
    "Alle löschen": "Delete All",
    "Debug Sessions": "Debug Sessions",
    "Sessions-Ordner": "Sessions Folder",
    "Session Liste": "Session List",
    "Session BIAS": "Session BIAS",
    "BIAS nicht gesetzt": "BIAS not set",
    "Auto-Save aktiv": "Auto-save active",
    "Keine bestehenden Sessions gefunden": "No existing sessions found",
    "Klicken Sie auf": "Click on",
    "um zu beginnen": "to begin",
    "Neueste Session automatisch geladen": "Latest session automatically loaded",
    "Keine Session": "No Session",
    "Modell Management": "Model Management",
    "Session Management": "Session Management",
    "Ollama Status": "Ollama Status",
    "Standard-Konfiguration": "Default configuration",
    "Standardwerte": "Default values",
    "zurück": "back",
    "Hauptanwendungsklasse": "Main application class",
    "Hauptklasse": "Main class",
    "Modulare Version": "Modular Version",
    "Haupteinstiegspunkt": "Main entry point",
    "Erscheinungsbild konfigurieren": "Configure appearance",
    "Konfigurationsdatei": "Configuration file",
    "Diese Datei wird automatisch erstellt und aktualisiert": "This file is automatically created and updated",
    "Alle Änderungen werden beim Anwenden in der GUI gespeichert": "All changes are saved when applying in the GUI",
    "CHAT-BUBBLE FARBEN": "CHAT BUBBLE COLORS",
    "Farben für Chat-Bubbles": "Colors for chat bubbles",
    "Sie": "You",
    "Matrix-Style": "Matrix-Style",
    "AI-Modell": "AI Model",
    "System-Nachrichten": "System Messages",
    "Terminal/Konsolen-Ausgabe Styling": "Terminal/Console Output Styling",
    "Flache Struktur für Kompatibilität": "Flat structure for compatibility",
    "wird automatisch generiert": "automatically generated",
    "geladen aus": "loaded from",
    "Gibt die Standard-Konfiguration zurück": "Returns the default configuration",
    "Lädt die Konfiguration aus der YAML-Datei oder erstellt Standard-Config": "Loads the configuration from the YAML file or creates default config",
    "Fülle fehlende Werte mit Standardwerten auf": "Fill missing values with default values",
    "Fallback auf Standard-Konfiguration": "Fallback to default configuration",
    "Verwende Standard-Konfiguration": "Using default configuration",
    "Speichert die Konfiguration in die YAML-Datei": "Saves the configuration to the YAML file",
    "Erstelle YAML mit Kommentaren": "Create YAML with comments",
    "Schreibe manuelle YAML-Struktur für bessere Kommentare": "Write manual YAML structure for better comments",
    "Füge flache Struktur hinzu für einfache Kompatibilität": "Add flat structure for easy compatibility",
    "Setzt die Konfiguration auf Standardwerte zurück und speichert sie": "Resets the configuration to default values and saves it",
    "Einfache Konsolen-Ausgabe": "Simple console output",
    "ohne Styling": "without styling",
    "Erstellt das Session Management Panel": "Creates the Session Management Panel",
    "MODELL MANAGEMENT BEREICH": "MODEL MANAGEMENT AREA",
    "ganz oben": "at the top",
    "SESSION MANAGEMENT BEREICH": "SESSION MANAGEMENT AREA",
    "darunter": "below",
    "SESSION MANAGEMENT SYSTEM": "SESSION MANAGEMENT SYSTEM",
    "Modell Management Frame": "Model Management Frame",
    "Installierte Modelle": "Installed Models",
    "Verfügbare Modelle zum Download": "Available Models for Download",
    "Neues ModelInfoDropdown für verfügbare Modelle zum Download": "New ModelInfoDropdown for available models to download",
    "Session Panel Header entfernt": "Session Panel Header removed",
    "Header-Frame für Session Liste mit Button nebeneinander": "Header frame for session list with button side by side",
    "Neue Session Button - jetzt neben der Session Liste": "New Session button - now next to session list",
    "Scrollbare Session-Liste - mehr Platz durch Entfernung des": "Scrollable session list - more space by removing the",
    "Aktuelle Session": "Current Session",
    "Session Actions unter der Session-Liste": "Session Actions below session list",
    "Debug-Buttons unter der Session-Liste": "Debug buttons below session list",
    "Auto-Save für BIAS bei Textänderung": "Auto-save for BIAS on text change",
    "BIAS Info Label für aktuellen Status": "BIAS info label for current status",
    "Initialisiert das Session Management System": "Initializes the session management system",
    "Session-Datenstrukturen": "Session data structures",
    "bereits im __init__ initialisiert": "already initialized in __init__",
    "bereits im __init__ erstellt": "already created in __init__",
    "Chat-Bubbles für Session Management": "Chat bubbles for session management",
    "Lade bestehende Sessions": "Load existing sessions",
    "Zeige Session-Status an": "Show session status",
    "Lade die neueste Session automatisch": "Load the latest session automatically",
    "Debug: Session-Analyse": "Debug: Session analysis",
    "Keine automatische Session-Erstellung - Nutzer muss explizit erstellen": "No automatic session creation - user must explicitly create",
    "UI aktualisieren um": "Update UI to",
    "Zustand zu zeigen": "show state",
}

def translate_file(filepath):
    """Translate German strings in a file to English"""
    print(f"Processing: {filepath}")
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply translations
        for german, english in TRANSLATIONS.items():
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(german) + r'\b'
            content = re.sub(pattern, english, content)
        
        # Check if anything changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Translated: {filepath}")
            return True
        else:
            print(f"ℹ️  No changes: {filepath}")
            return False
    
    except Exception as e:
        print(f"❌ Error processing {filepath}: {e}")
        return False

def main():
    """Main function to translate all Python files"""
    base_dir = "a1_terminal_modular"
    translated_count = 0
    
    # Walk through all Python files
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if translate_file(filepath):
                    translated_count += 1
    
    print(f"\n✨ Translation complete! {translated_count} files modified.")

if __name__ == "__main__":
    main()
