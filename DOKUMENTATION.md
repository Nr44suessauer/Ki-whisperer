# A1-Terminal - Technische Dokumentation

**Version:** 2.0 (Modulare Architektur)  
**Datum:** November 2025  
**Typ:** Chat-Client für lokale AI-Modelle via Ollama

---

## Inhaltsverzeichnis

1. [Übersicht](#übersicht)
2. [Systemanforderungen](#systemanforderungen)
3. [Installation](#installation)
4. [Architektur](#architektur)
5. [Projektstruktur](#projektstruktur)
6. [Kernkomponenten](#kernkomponenten)
7. [Konfiguration](#konfiguration)
8. [API-Referenz](#api-referenz)
9. [Benutzeroberfläche](#benutzeroberfläche)
10. [Session-Management](#session-management)
11. [Verwendung](#verwendung)
12. [Entwicklung](#entwicklung)
13. [Troubleshooting](#troubleshooting)

---

## Übersicht

**A1-Terminal** ist ein professioneller, modularer Chat-Client für lokale AI-Modelle, der über die Ollama-API kommuniziert. Die Anwendung bietet eine intuitive grafische Benutzeroberfläche mit umfangreichen Anpassungsmöglichkeiten, Session-Management und Echtzeit-Streaming-Funktionalität.

### Hauptmerkmale

- 🎯 **Modulare Architektur** - Saubere Trennung von UI und Geschäftslogik
- 🚀 **Echtzeit-Streaming** - Live-Anzeige der AI-Antworten während der Generierung
- 💾 **Session-Management** - Persistente Chat-Sitzungen mit Speicherung und Wiederherstellung
- 🎨 **Vollständig anpassbar** - Farben, Schriftarten, Layout individuell konfigurierbar
- 📊 **Model-Management** - Download, Auswahl und Kategorisierung von AI-Modellen
- 🔄 **Offline-fähig** - Alle Modelle laufen lokal ohne Internetverbindung
- ⚡ **Stop-Funktionalität** - Generierung und Downloads können jederzeit gestoppt werden
- 📝 **BIAS-System** - System-Prompts zur Steuerung des AI-Verhaltens

### Technologie-Stack

```
┌─────────────────────────────────────────┐
│         CustomTkinter (GUI)             │
├─────────────────────────────────────────┤
│   A1 Terminal Core Application          │
├──────────────┬──────────────────────────┤
│ UI-Module    │  Ollama Manager          │
│              │  (API-Client)            │
├──────────────┴──────────────────────────┤
│         Ollama API (localhost:11434)    │
├─────────────────────────────────────────┤
│    Lokale AI-Modelle                    │
│    (llama, mistral, codellama, etc.)    │
└─────────────────────────────────────────┘
```

---

## Systemanforderungen

### Software

- **Python:** 3.8 oder höher
- **Ollama:** Neueste Version (läuft als Hintergrunddienst)
- **Betriebssystem:** Windows, Linux oder macOS

### Hardware (Mindestanforderungen)

- **RAM:** 8 GB (16 GB empfohlen für größere Modelle)
- **Speicher:** 10 GB freier Festplattenspeicher
- **CPU:** Multi-Core Prozessor empfohlen

### Modell-spezifische Anforderungen

| Modellgröße | RAM-Bedarf | Beispiele |
|-------------|------------|-----------|
| 🟢 Klein (< 4GB) | 4-8 GB | tinyllama:1.1b, phi3:mini, gemma:2b |
| 🟡 Mittel (4-8GB) | 8-12 GB | llama3.2:3b, mistral:7b, codellama:7b |
| 🟠 Groß (8-16GB) | 16-24 GB | llama2:13b, codellama:13b |
| 🔴 Sehr Groß (16GB+) | 32+ GB | llama2:70b, mixtral:8x7b |

---

## Installation

### 1. Ollama installieren

Besuchen Sie [ollama.ai](https://ollama.ai) und installieren Sie Ollama für Ihr Betriebssystem.

**Verifizierung:**
```powershell
ollama --version
```

### 2. Repository klonen

```powershell
cd "C:\Users\<Benutzername>\Documents"
git clone https://github.com/Nr44suessauer/Ki-whisperer.git
cd Ki-whisperer\a1_terminal_modular
```

### 3. Abhängigkeiten installieren

```powershell
pip install -r requirements.txt
```

**requirements.txt:**
```
customtkinter>=5.2.0
ollama>=0.1.0
PyYAML>=6.0
requests>=2.31.0
pyperclip>=1.8.2
```

### 4. Ollama starten

```powershell
ollama serve
```

Ollama läuft auf `http://localhost:11434`

---

## Architektur

### Design-Prinzipien

1. **Modularität** - Jede Komponente hat eine klare Verantwortlichkeit
2. **Separation of Concerns** - UI und Geschäftslogik sind getrennt
3. **Konfigurierbarkeit** - Alle Einstellungen über YAML-Konfiguration
4. **Erweiterbarkeit** - Neue UI-Komponenten können einfach hinzugefügt werden

### Schichtenarchitektur

```
┌──────────────────────────────────┐
│  main.py (Entry Point)           │
└──────────────┬───────────────────┘
               │
┌──────────────▼───────────────────┐
│  core/a1_terminal.py             │
│  (Hauptanwendungsklasse)         │
└──────┬───────────────────┬───────┘
       │                   │
┌──────▼────────┐   ┌──────▼──────────┐
│  ui/          │   │  core/          │
│  - chat_bubble│   │  - ollama_mgr   │
│  - session_card│  │                 │
│  - model_sel  │   │                 │
│  - etc.       │   │                 │
└───────────────┘   └─────────────────┘
```

---

## Projektstruktur

```
Ki-whisperer/
├── a1_terminal_modular/                    # ✨ Hauptanwendung
│   ├── main.py                             # Entry Point
│   ├── start.bat                           # Windows Start-Skript
│   ├── restart.py                          # Neustart-Helfer
│   ├── requirements.txt                    # Python-Abhängigkeiten
│   ├── a1_terminal_config.yaml             # Konfigurationsdatei
│   ├── sessions.json                       # Session-Metadaten
│   │
│   ├── sessions/                           # Gespeicherte Chat-Sessions
│   │   └── Session_<datum>_<zeit>.json
│   │
│   └── src/                                # Quellcode
│       ├── __init__.py
│       │
│       ├── core/                           # Kernlogik
│       │   ├── __init__.py
│       │   ├── a1_terminal.py              # Hauptklasse (4200+ Zeilen)
│       │   └── ollama_manager.py           # Ollama-API-Client
│       │
│       └── ui/                             # UI-Komponenten
│           ├── __init__.py
│           ├── chat_bubble.py              # Chat-Nachrichtenanzeige
│           ├── enhanced_chat_bubble.py     # Erweiterte Chat-Bubbles
│           ├── session_card.py             # Session-Karten
│           ├── model_selector.py           # Model-Auswahl-Widget
│           ├── model_info_dropdown.py      # Model-Info-Anzeige
│           ├── categorized_combobox.py     # Kategorisierte Dropdown
│           ├── color_wheel.py              # Farbauswahl-Widget
│           ├── resizable_pane.py           # Größenänderbare Panels
│           ├── modern_ui.py                # Modernes UI-Design
│           └── ultimate_ui.py              # Ultimate UI-Setup
│
├── ki_whisperer_config.yaml                # Legacy-Konfiguration
└── README.md                               # Dokumentation (zu löschen)
```

---

## Kernkomponenten

### 1. A1Terminal (core/a1_terminal.py)

**Hauptklasse** der Anwendung mit ~4200 Zeilen Code.

#### Hauptverantwortlichkeiten:
- Initialisierung der Anwendung
- UI-Setup und Event-Handling
- Session-Management
- Chat-Historie-Verwaltung
- Konfigurationsverwaltung

#### Wichtige Methoden:

```python
class A1Terminal:
    def __init__(self):
        """Initialisiert die Anwendung"""
        
    def setup_ui(self):
        """Erstellt die Benutzeroberfläche"""
        
    def send_message(self):
        """Sendet eine Nachricht an das AI-Modell"""
        
    def generate_response(self, model, messages):
        """Generiert eine AI-Antwort (mit Streaming)"""
        
    def save_session(self):
        """Speichert die aktuelle Session"""
        
    def load_session(self, session_id):
        """Lädt eine gespeicherte Session"""
        
    def load_config(self):
        """Lädt die YAML-Konfiguration"""
        
    def save_config(self, config):
        """Speichert die YAML-Konfiguration"""
```

#### Wichtige Attribute:

```python
self.root              # CTk Hauptfenster
self.ollama            # OllamaManager Instanz
self.current_model     # Aktuell ausgewähltes Modell
self.chat_history      # Liste der Chat-Nachrichten
self.chat_bubbles      # Liste der UI Chat-Bubbles
self.sessions          # Dict aller Sessions
self.current_session_id # ID der aktuellen Session
self.config            # Konfiguration (Dict)
self.generation_stopped # Flag für Stop-Funktionalität
```

---

### 2. OllamaManager (core/ollama_manager.py)

**API-Client** für die Kommunikation mit dem Ollama-Server.

#### Hauptverantwortlichkeiten:
- Verbindung zu Ollama-API
- Modell-Download und -Verwaltung
- Streaming-Antworten
- Modell-Kategorisierung

#### Wichtige Methoden:

```python
class OllamaManager:
    def __init__(self):
        """Initialisiert den Ollama-Client"""
        self.base_url = "http://localhost:11434"
        self.client = ollama.Client()
    
    def is_ollama_running(self):
        """Prüft ob Ollama-Server läuft"""
        
    def get_available_models(self):
        """Holt lokal installierte Modelle"""
        
    def get_all_ollama_models(self):
        """Holt alle verfügbaren Modelle von Registry"""
        
    def download_model(self, model_name, progress_callback):
        """Lädt ein Modell mit Progress-Tracking herunter"""
        
    def categorize_models_by_size(self, models):
        """Kategorisiert Modelle nach RAM-Bedarf"""
        
    def generate_response(self, model, messages, stream=True):
        """Generiert AI-Antwort mit Streaming"""
```

#### Modell-Kategorisierung:

```python
categories = {
    "🟢 Klein (< 4GB RAM)": [],      # 0.5b-3b Parameter
    "🟡 Mittel (4-8GB RAM)": [],     # 7b Parameter
    "🟠 Groß (8-16GB RAM)": [],      # 13b-15b Parameter
    "🔴 Sehr Groß (16GB+ RAM)": []   # 70b+ Parameter
}
```

---

### 3. UI-Komponenten (ui/)

#### ChatBubble (chat_bubble.py)
Darstellung einzelner Chat-Nachrichten mit Rolle-basiertem Styling.

```python
class ChatBubble:
    def __init__(self, parent, message, role, config):
        """
        Args:
            parent: Parent-Widget
            message: Nachrichtentext
            role: "user", "assistant", "system"
            config: Konfigurations-Dict
        """
```

#### SessionCard (session_card.py)
Visuelle Darstellung einer Chat-Session in der Sidebar.

```python
class SessionCard:
    def __init__(self, parent, session_id, session_data, on_select, on_delete):
        """
        Args:
            session_id: Eindeutige Session-ID
            session_data: Session-Metadaten (Dict)
            on_select: Callback beim Anklicken
            on_delete: Callback beim Löschen
        """
```

#### ModelSelector (model_selector.py)
Widget zur Modell-Auswahl mit Kategorisierung.

```python
class ModelSelector:
    def __init__(self, parent, models, on_select):
        """
        Args:
            models: Liste verfügbarer Modelle
            on_select: Callback bei Modell-Auswahl
        """
```

#### ColorWheel (color_wheel.py)
Farbauswahl-Widget für UI-Customization.

#### ResizablePane (resizable_pane.py)
Größenänderbare Panel-Komponente für flexible Layouts.

---

## Konfiguration

### Konfigurationsdatei: a1_terminal_config.yaml

Die Konfiguration wird automatisch erstellt und beim Starten geladen. Alle Änderungen in der GUI werden persistent gespeichert.

#### Struktur:

```yaml
# ========== BUBBLE-FARBEN ==========
bubble_colors:
  user_bg_color: "#003300"        # Matrix-Grün
  user_text_color: "#00FF00"
  ai_bg_color: "#1E3A5F"          # Dunkelblau
  ai_text_color: "white"
  system_bg_color: "#722F37"      # Dunkelrot
  system_text_color: "white"

# ========== SCHRIFTARTEN ==========
fonts:
  user_font: "Courier New"
  user_font_size: 11
  ai_font: "Consolas"
  ai_font_size: 11
  system_font: "Arial"
  system_font_size: 10

# ========== UI-LAYOUT ==========
ui_session_panel_width: 350
ui_window_width: 1400
ui_window_height: 900
ui_padding_main: 10
ui_padding_content: 5

# ========== CHAT-DISPLAY ==========
ui_chat_bubble_corner_radius: 10
ui_chat_bubble_padding_x: 15
ui_chat_bubble_padding_y: 10
ui_chat_spacing: 10
ui_chat_max_width_ratio: 0.8

# ========== FARBEN & THEME ==========
ui_bg_color: "#1a1a1a"
ui_fg_color: "#2b2b2b"
ui_accent_color: "#2B8A3E"
ui_hover_color: "#37A24B"
ui_text_color: "white"
ui_border_color: "#3a3a3a"

# ========== OPTIONEN ==========
show_system_messages: true
auto_scroll_chat: true
show_timestamps: true
compact_mode: false
```

### Konfiguration programmatisch ändern:

```python
# Konfiguration laden
config = app.load_config()

# Werte ändern
config['user_bg_color'] = '#FF0000'
config['ui_window_width'] = 1600

# Speichern
app.save_config(config)
```

---

## API-Referenz

### Ollama API Endpoints

A1-Terminal kommuniziert mit folgenden Ollama-Endpoints:

#### 1. Status prüfen
```
GET http://localhost:11434/api/tags
```

#### 2. Modelle auflisten
```
GET http://localhost:11434/api/tags
Response: {
  "models": [
    {
      "name": "llama3.2:3b",
      "modified_at": "2024-11-10T12:00:00Z",
      "size": 2000000000
    }
  ]
}
```

#### 3. Modell herunterladen
```
POST http://localhost:11434/api/pull
Body: {
  "name": "llama3.2:3b",
  "stream": true
}
```

#### 4. Chat-Anfrage (Streaming)
```
POST http://localhost:11434/api/chat
Body: {
  "model": "llama3.2:3b",
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "stream": true
}
```

### Python Ollama Client

A1-Terminal nutzt den offiziellen `ollama` Python-Client:

```python
import ollama

# Client initialisieren
client = ollama.Client()

# Chat mit Streaming
response = client.chat(
    model='llama3.2:3b',
    messages=[
        {'role': 'user', 'content': 'Hello!'}
    ],
    stream=True
)

for chunk in response:
    if 'message' in chunk:
        print(chunk['message']['content'], end='')
```

---

## Benutzeroberfläche

### Layout-Struktur

```
┌────────────────────────────────────────────────────────┐
│  Hauptfenster (1400x900 px)                           │
├──────────────┬─────────────────────────────────────────┤
│              │  ┌──────────────────────────────────┐   │
│  Session     │  │  Model Selector                  │   │
│  Panel       │  └──────────────────────────────────┘   │
│  (350px)     │  ┌──────────────────────────────────┐   │
│              │  │                                  │   │
│  ┌────────┐  │  │  Chat Display Area               │   │
│  │Session │  │  │  (Auto-Scroll)                   │   │
│  │Card 1  │  │  │                                  │   │
│  └────────┘  │  │                                  │   │
│  ┌────────┐  │  └──────────────────────────────────┘   │
│  │Session │  │  ┌──────────────────────────────────┐   │
│  │Card 2  │  │  │  Message Input (40px)            │   │
│  └────────┘  │  └──────────────────────────────────┘   │
│              │  [Send] [Stop] [Clear]                  │
│  [New]       │                                          │
│  [Delete]    │  Tabs: Chat | Config | Models | Debug   │
└──────────────┴─────────────────────────────────────────┘
```

### Tab-System

#### 1. Chat-Tab
- Hauptbereich für Chat-Konversation
- Message Input mit Multi-Line-Support
- Buttons: Send, Stop, Clear
- Model Selector Dropdown

#### 2. Config-Tab
- Farbauswahl für User/AI/System
- Schriftart-Einstellungen
- Layout-Anpassungen
- Speichern/Laden von Presets

#### 3. Models-Tab
- Liste aller verfügbaren Modelle
- Download-Funktion mit Progress-Bar
- Modell-Info (Größe, Parameter)
- Kategorisierung nach RAM-Bedarf

#### 4. Debug-Tab
- Logs und System-Meldungen
- Performance-Metriken
- API-Status
- Session-Daten-Inspektion

### Keyboard Shortcuts

| Shortcut | Funktion |
|----------|----------|
| `Enter` | Nachricht senden |
| `Shift+Enter` | Neue Zeile im Input |
| `↑` / `↓` | Nachrichtenverlauf durchsuchen |
| `Ctrl+L` | Chat leeren |
| `Ctrl+N` | Neue Session |
| `Ctrl+S` | Session speichern |
| `Escape` | Generation stoppen |

---

## Session-Management

### Session-Struktur

Jede Session wird als JSON-Datei gespeichert:

```json
{
  "session_id": "session_20251110_153045_123",
  "title": "Chat über Python",
  "model": "llama3.2:3b",
  "created_at": "2025-11-10T15:30:45",
  "last_modified": "2025-11-10T15:45:30",
  "bias": "Du bist ein hilfreicher Python-Experte.",
  "messages": [
    {
      "role": "user",
      "content": "Wie erstelle ich eine Liste?",
      "timestamp": "2025-11-10T15:31:00"
    },
    {
      "role": "assistant",
      "content": "Du kannst eine Liste mit [] erstellen...",
      "timestamp": "2025-11-10T15:31:05"
    }
  ]
}
```

### Session-Metadaten (sessions.json)

```json
{
  "sessions": {
    "session_20251110_153045_123": {
      "title": "Chat über Python",
      "model": "llama3.2:3b",
      "created_at": "2025-11-10T15:30:45",
      "last_modified": "2025-11-10T15:45:30",
      "message_count": 4,
      "file_path": "sessions/Session_10.11_15-30_session_20251110_153045_123.json"
    }
  },
  "current_session": "session_20251110_153045_123"
}
```

### Session-Operationen

#### Neue Session erstellen:
```python
app.create_new_session()
```

#### Session laden:
```python
app.load_session(session_id)
```

#### Session speichern:
```python
app.save_session()
```

#### Session löschen:
```python
app.delete_session(session_id)
```

### Auto-Save

Sessions werden automatisch gespeichert:
- Nach jeder Nachricht (mit 2s Verzögerung)
- Beim Schließen der Anwendung
- Beim Wechsel der Session

---

## Verwendung

### Schnellstart

#### 1. Anwendung starten

**Windows:**
```powershell
cd a1_terminal_modular
.\start.bat
```

**Oder manuell:**
```powershell
python main.py
```

#### 2. Modell auswählen

- Klicken Sie auf das Model-Selector Dropdown
- Wählen Sie ein installiertes Modell
- Oder laden Sie ein neues Modell im "Models"-Tab herunter

#### 3. Chat beginnen

- Geben Sie Ihre Nachricht im Input-Feld ein
- Drücken Sie `Enter` oder klicken Sie auf "Send"
- Die AI-Antwort erscheint in Echtzeit (Streaming)

### BIAS-System

BIAS ist ein System-Prompt, der das Verhalten der AI steuert:

**Beispiele:**

```
Du bist ein hilfsbereiter Python-Programmierer.
```

```
Antworte immer auf Deutsch und sei präzise.
```

```
Du bist ein Experte für Machine Learning.
Erkläre Konzepte einfach und mit Beispielen.
```

**BIAS setzen:**
1. Geben Sie den BIAS-Text im Textfeld unten links ein
2. Der BIAS wird automatisch bei jeder Anfrage mitgesendet
3. Änderungen werden per Auto-Save gespeichert

### Modell-Download

1. Wechseln Sie zum "Models"-Tab
2. Klicken Sie auf "Refresh Model Library"
3. Wählen Sie ein Modell aus der Liste
4. Klicken Sie auf "Download Selected Model"
5. Progress-Bar zeigt den Fortschritt
6. Nach Abschluss ist das Modell verfügbar

**Download stoppen:**
- Klicken Sie auf "Stop Download"

### Chat-Befehle

| Befehl | Beschreibung |
|--------|--------------|
| `Send` | Nachricht senden |
| `Stop` | Generierung stoppen |
| `Clear` | Chat leeren (behält Session) |
| `New Session` | Neue Session erstellen |
| `Delete Session` | Aktuelle Session löschen |

---

## Entwicklung

### Entwicklungsumgebung einrichten

```powershell
# Repository klonen
git clone https://github.com/Nr44suessauer/Ki-whisperer.git
cd Ki-whisperer/a1_terminal_modular

# Virtual Environment erstellen
python -m venv venv
.\venv\Scripts\Activate.ps1

# Dependencies installieren
pip install -r requirements.txt

# Anwendung starten
python main.py
```

### Neue UI-Komponente hinzufügen

1. **Erstellen Sie eine neue Datei** in `src/ui/`:
```python
# src/ui/my_component.py
import customtkinter as ctk

class MyComponent(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.setup_ui()
    
    def setup_ui(self):
        # UI erstellen
        pass
```

2. **Importieren** in `a1_terminal.py`:
```python
from src.ui.my_component import MyComponent
```

3. **Verwenden** in `setup_ui()`:
```python
self.my_component = MyComponent(self.root)
self.my_component.pack()
```

### Konfigurationsparameter hinzufügen

1. **Standard-Wert** in `get_default_config()` definieren:
```python
def get_default_config(self):
    return {
        # ... existing config ...
        "my_new_parameter": "default_value",
    }
```

2. **Verwenden** in der Anwendung:
```python
value = self.config.get('my_new_parameter', 'fallback_value')
```

3. **Speichern** bei Änderung:
```python
self.config['my_new_parameter'] = new_value
self.save_config(self.config)
```

### Code-Stil

- **PEP 8** konform
- **Docstrings** für alle Klassen und Methoden
- **Type Hints** wo möglich
- **Fehlerbehandlung** mit try-except
- **Logging** mit print() für Debug-Ausgaben

### Testing

```python
# Ollama-Verbindung testen
if not self.ollama.is_ollama_running():
    print("❌ Ollama ist nicht erreichbar")

# Modell-Download testen
self.ollama.download_model(
    "tinyllama:1.1b",
    progress_callback=lambda p: print(f"Progress: {p}%")
)

# Config testen
config = self.load_config()
assert 'user_bg_color' in config
```

---

## Troubleshooting

### Problem: Ollama nicht erreichbar

**Symptom:** "Ollama ist nicht erreichbar" beim Start

**Lösung:**
```powershell
# Ollama starten
ollama serve

# In neuem Terminal testen
ollama list
```

### Problem: Modell-Download schlägt fehl

**Symptom:** Download bricht ab oder friert ein

**Lösung:**
1. Internetverbindung prüfen
2. Festplattenspeicher prüfen
3. Ollama neu starten
4. Download erneut versuchen

### Problem: UI wird nicht korrekt angezeigt

**Symptom:** Komponenten fehlen oder sind falsch positioniert

**Lösung:**
1. Konfigurationsdatei löschen (wird neu erstellt)
```powershell
Remove-Item a1_terminal_config.yaml
```
2. Anwendung neu starten

### Problem: Session kann nicht geladen werden

**Symptom:** Fehler beim Laden einer gespeicherten Session

**Lösung:**
1. Prüfen Sie die Session-Datei auf Syntaxfehler
2. Backup wiederherstellen falls vorhanden
3. Session neu erstellen

### Problem: Hoher RAM-Verbrauch

**Symptom:** System wird langsam bei großen Modellen

**Lösung:**
1. Kleineres Modell wählen (z.B. tinyllama statt llama2:70b)
2. Andere Anwendungen schließen
3. Swap-Space erhöhen (Linux/macOS)

### Logs und Debug-Informationen

**Debug-Modus aktivieren:**
Wechseln Sie zum "Debug"-Tab für detaillierte Logs.

**Console-Ausgaben:**
Alle Systemausgaben erscheinen im Terminal-Fenster, von dem die Anwendung gestartet wurde.

---

## Anhang

### Unterstützte Modelle (Auswahl)

#### Kleine Modelle (< 4GB RAM)
- `tinyllama:1.1b` - Sehr schnell, einfache Aufgaben
- `phi3:mini` - Microsoft, gute Qualität
- `gemma:2b` - Google, balanced
- `qwen2:1.5b` - Alibaba, mehrsprachig

#### Mittlere Modelle (4-8GB RAM)
- `llama3.2:3b` - Meta, neueste Version
- `mistral:7b` - Mistral AI, sehr gut
- `codellama:7b` - Meta, spezialisiert auf Code
- `gemma:7b` - Google, balanced

#### Große Modelle (8-16GB RAM)
- `llama2:13b` - Meta, hohe Qualität
- `codellama:13b` - Erweiterte Code-Fähigkeiten
- `vicuna:13b` - Community fine-tune

#### Sehr große Modelle (16GB+ RAM)
- `llama2:70b` - Top-Qualität
- `mixtral:8x7b` - Mixture-of-Experts
- `codellama:34b` - Professional Code

### Performance-Tipps

1. **Modellgröße wählen:**
   - Für Chat: 7b Modelle ausreichend
   - Für Code: codellama empfohlen
   - Für Qualität: 13b+ Modelle

2. **RAM optimieren:**
   - Schließen Sie unnötige Programme
   - Verwenden Sie kleinere Modelle für schnelle Tests
   - Aktivieren Sie Swap/Pagefile

3. **Ollama optimieren:**
   - Starten Sie Ollama neu bei Problemen
   - Löschen Sie ungenutzte Modelle: `ollama rm <model>`
   - Cache leeren falls nötig

### Ressourcen

- **Ollama Dokumentation:** https://ollama.ai/docs
- **GitHub Repository:** https://github.com/Nr44suessauer/Ki-whisperer
- **CustomTkinter Docs:** https://github.com/TomSchimansky/CustomTkinter
- **Python Ollama Client:** https://github.com/ollama/ollama-python

### Lizenz

Dieses Projekt ist Open Source. Siehe Repository für Details.

### Kontakt

Bei Fragen oder Problemen erstellen Sie bitte ein Issue im GitHub Repository.

---

**Letzte Aktualisierung:** November 2025  
**Dokumentations-Version:** 1.0
