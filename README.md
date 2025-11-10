# A1-Terminal# A1-Terminal



**Professioneller Chat-Client für lokale AI-Modelle via Ollama****Professioneller Chat-Client für lokale AI-Modelle via Ollama**



Version 2.0 - Modulare ArchitekturVersion 2.0 - Modulare Architektur



---## 📁 Projektstruktur



## 📖 Dokumentation---



Die vollständige technische Dokumentation finden Sie hier:Das Projekt ist jetzt **modular** aufgebaut:



**➡️ [DOKUMENTATION.md](./DOKUMENTATION.md)**## 📋 Inhaltsverzeichnis



---```



## 🚀 Schnellstart1. [Überblick](#überblick)Ki-whisperer/



### 1. Ollama installieren2. [System-Architektur](#system-architektur)├── a1_terminal_modular/     # ✨ NEUE MODULARE VERSION (empfohlen)

Besuchen Sie [ollama.ai](https://ollama.ai) und installieren Sie Ollama.

3. [Installation](#installation)│   ├── start.bat            # Einfach doppelklicken zum Starten!

### 2. Dependencies installieren

```powershell4. [Schnellstart](#schnellstart)│   ├── main.py

cd a1_terminal_modular

pip install -r requirements.txt5. [Modulare Struktur](#modulare-struktur)│   └── src/

```

6. [Technische Dokumentation](#technische-dokumentation)│       ├── ui/              # UI-Komponenten

### 3. Starten

```powershell7. [Features](#features)│       └── core/            # Kernlogik

.\start.bat

```8. [Konfiguration](#konfiguration)│



oder9. [API-Referenz](#api-referenz)└── OLD_VERSION/             # Archivierte alte Version



```powershell10. [Performance & Monitoring](#performance--monitoring)    └── llm_messenger.py     # Original monolithische Datei

python main.py

```11. [Troubleshooting](#troubleshooting)```



---



## ✨ Features---## Installation



- 🎯 Modulare Architektur

- 🚀 Echtzeit-Streaming

- 💾 Session-Management## Überblick1. **Repository klonen oder herunterladen**

- 🎨 Vollständig anpassbar

- 📊 Model-Management   ```bash

- 🔄 Offline-fähig

**A1-Terminal** ist ein moderner, modularer Chat-Client für lokale AI-Modelle, der über die Ollama-API kommuniziert. Die Anwendung bietet eine intuitive GUI mit umfangreichen Anpassungsmöglichkeiten, Session-Management und Echtzeit-Streaming-Funktionalität.   cd "C:\Users\marcn\Documents\Ki-whisperer"

---

   ```

Weitere Informationen, API-Referenz, Troubleshooting und mehr in der **[vollständigen Dokumentation](./DOKUMENTATION.md)**.

### Hauptmerkmale

2. **Abhängigkeiten installieren**

- 🎯 **Modular & Wartbar** - Saubere Architektur mit klarer Trennung   ```bash

- 🚀 **Echtzeit-Streaming** - Live-Anzeige der AI-Antworten   cd a1_terminal_modular

- 💾 **Session-Management** - Persistente Chat-Sitzungen   pip install -r requirements.txt

- 🎨 **Vollständig anpassbar** - Farben, Fonts, Layout   ```

- 📊 **Monitoring** - Performance- und Nutzungsstatistiken

- 🔄 **Model-Management** - Download, Auswahl, Kategorisierung## 🚀 Verwendung (Neue Version)



### Technologie-Stack1. **Ollama starten** (falls noch nicht gestartet)

   ```bash

```   ollama serve

┌─────────────────────────────────────────┐   ```

│         CustomTkinter (GUI)             │

├─────────────────────────────────────────┤2. **A1 Terminal starten**

│   A1 Terminal Core Application          │   ```bash

├──────────────┬──────────────────────────┤   cd a1_terminal_modular

│ UI-Module    │  Ollama Manager          │   start.bat

│              │  (API-Client)            │   ```

├──────────────┴──────────────────────────┤   

│         Ollama API (localhost:11434)    │   Oder direkt:

├─────────────────────────────────────────┤   ```bash

│    Lokale AI-Modelle (llama, mistral,  │   python main.py

│      codellama, gemma, phi, etc.)       │   ```

└─────────────────────────────────────────┘

```## Erste Schritte



---1. **Modell herunterladen**

   - Klicken Sie auf "Modell herunterladen"

## System-Architektur   - Geben Sie einen Modellnamen ein (z.B. `llama2`, `mistral`, `codellama`)

   - Warten Sie, bis der Download abgeschlossen ist

### Gesamtübersicht

2. **Modell auswählen**

```   - Wählen Sie das gewünschte Modell aus dem Dropdown-Menü

A1-Terminal/

│3. **Chatten**

├── a1_terminal_modular/          # Hauptanwendung   - Geben Sie Ihre Nachricht ein und drücken Sie Enter oder klicken Sie "Senden"

│   ├── main.py                   # Einstiegspunkt   - Die AI antwortet in Echtzeit

│   ├── start.bat                 # Windows-Launcher

│   ├── requirements.txt          # Python-Dependencies## Beliebte Modelle

│   │

│   ├── src/- **llama2** - Allzweck-Sprachmodell von Meta

│   │   ├── core/                 # Kernlogik- **mistral** - Schnelles und effizientes Modell

│   │   │   ├── a1_terminal.py    # Hauptanwendung (3200+ Zeilen)- **codellama** - Spezialisiert auf Programmierung

│   │   │   └── ollama_manager.py # API-Client (320 Zeilen)- **phi** - Kleines, aber leistungsstarkes Modell

│   │   │- **gemma** - Google's offenes Modell

│   │   └── ui/                   # UI-Komponenten

│   │       ├── color_wheel.py    # Farbwähler (194 Zeilen)## Funktionen

│   │       ├── chat_bubble.py    # Chat-Nachricht (264 Zeilen)

│   │       └── categorized_combobox.py  # Dropdown (60 Zeilen)### Modell-Management

│   │- **Download**: Laden Sie neue Modelle direkt herunter

│   └── sessions/                 # Session-Daten (JSON)- **Löschen**: Entfernen Sie nicht benötigte Modelle

│- **Auswählen**: Wechseln Sie zwischen verschiedenen Modellen

├── a1_terminal_config.yaml      # Zentrale Konfiguration

└── OLD_VERSION/                  # Archiv (monolithische Version)### Chat-Features

```- **Streaming**: Sehen Sie die Antwort in Echtzeit

- **Historie**: Chat-Verlauf bleibt während der Session erhalten

### Komponenten-Diagramm- **Zeitstempel**: Alle Nachrichten haben Zeitstempel

- **System-Meldungen**: Informationen über Status und Fehler

```

┌─────────────────────────────────────────────────────┐### 🎨 Konfiguration & Anpassung

│                    main.py                          │- **Config-Tab**: Vollständig anpassbare Benutzeroberfläche

│              (Application Entry Point)              │- **Fixierte Buttons**: "Anwenden" und "Standard" buttons immer am unteren Rand sichtbar

└──────────────────┬──────────────────────────────────┘- **RGB-Farbwähler**: Klick auf 🎨-Buttons öffnet visuellen Farbwähler

                   │- **Farb-Preview-Icons**: Live-Vorschau der gewählten Farben mit farbigen Quadraten

                   ▼- **Komprimiertes Layout**: Mehr Optionen nebeneinander für bessere Übersicht

┌─────────────────────────────────────────────────────┐- **Live-Updates**: Farb-Previews aktualisieren sich beim Tippen

│               A1Terminal                            │- **Individuelle Farben**: Separate Farben für User, AI und System-Nachrichten

│          (Core Application Class)                   │- **Schriftarten**: Anpassbare Fonts und Schriftgrößen

│                                                     │- **Reset-Funktion**: Zurücksetzen auf Standardwerte

│  ┌──────────────────────────────────────────────┐ │

│  │         UI-Management                        │ │## 📖 Verwendung

│  │  • Tabs (Chat, Config, BIAS, Export)        │ │

│  │  • Event-Handling                           │ │### Konfiguration anpassen

│  │  • Layout-Orchestrierung                    │ │1. **Config-Tab öffnen**: Klicken Sie auf den "Config" Reiter

│  └──────────────────────────────────────────────┘ │2. **Farben wählen**:

│                                                     │   - **Farb-Preview**: Farbige Quadrate ■ zeigen aktuelle Farben

│  ┌──────────────────────────────────────────────┐ │   - **Manuelle Eingabe**: Geben Sie Hex-Codes direkt ein (#FF0000) ODER

│  │      Session-Management                      │ │   - **RGB-Farbwähler**: Klicken Sie auf 🎨-Buttons für visuellen Farbwähler

│  │  • Laden/Speichern von Sessions             │ │   - **Live-Updates**: Preview-Icons aktualisieren sich beim Tippen

│  │  • BIAS-System                              │ │3. **Schriftarten**: Wählen Sie aus horizontalen Dropdown-Menüs

│  │  • Auto-Save (60s Intervall)                │ │4. **Kompakte Ansicht**: Alle Optionen übersichtlich nebeneinander

│  └──────────────────────────────────────────────┘ │5. **Fixierte Buttons**: "✅ Anwenden" und "🔄 Standard" bleiben beim Scrollen immer am unteren Rand sichtbar

│                                                     │6. **Schnelle Anwendung**: Buttons immer erreichbar ohne Scrollen

│  ┌──────────────────────────────────────────────┐ │

│  │    Konfigurations-Management                 │ │## Fehlerbehebung

│  │  • YAML-Laden/Speichern                     │ │

│  │  • Live-Updates                             │ │### Ollama nicht verbunden

│  │  • Standard-Werte                           │ │- Stellen Sie sicher, dass Ollama läuft: `ollama serve`

│  └──────────────────────────────────────────────┘ │- Prüfen Sie, ob Port 11434 verfügbar ist

└───────┬─────────────────────────────────────┬──────┘- Starten Sie Ollama neu

        │                                     │

        ▼                                     ▼### Modell-Download schlägt fehl

┌──────────────────┐              ┌──────────────────┐- Prüfen Sie Ihre Internetverbindung

│  OllamaManager   │              │   UI-Widgets     │- Stellen Sie sicher, dass genügend Speicherplatz vorhanden ist

│                  │              │                  │- Versuchen Sie es mit einem kleineren Modell

│ • API-Calls      │              │ • ColorWheel     │

│ • Streaming      │              │ • ChatBubble     │### Anwendung startet nicht

│ • Model-Mgmt     │              │ • Combobox       │- Prüfen Sie, ob alle Abhängigkeiten installiert sind

└──────────────────┘              └──────────────────┘- Stellen Sie sicher, dass Sie Python 3.8+ verwenden

        │

        ▼## Entwicklung

┌──────────────────────────────────────────┐

│        Ollama REST API                   │Das Projekt ist in mehrere Klassen unterteilt:

│      (http://localhost:11434)            │

└──────────────────────────────────────────┘- `OllamaManager`: Verwaltet die Ollama-API-Kommunikation

```- `LLMMessenger`: Hauptanwendung mit UI

- Threading für Non-Blocking-Operationen

### Datenfluss-Diagramm

---

```

User Input### 🧹 **Anti-Redundanz-System**

   │Saubere, lesbare Ausgaben ohne nervige Wiederholungen:

   ▼

┌─────────────────────────────────────┐#### **Download-Logging:**

│  UI Event Handler                   │- **Status-Filter:** Identische Status werden nicht wiederholt

│  (send_message)                     │- **Timing-Optimiert:** Progress-Updates nur alle 2 Sekunden  

└────────────┬────────────────────────┘- **Kompakt:** Ein-Zeilen-Format statt Multi-Line-Spam

             │- **Layer-Smart:** Neue Layer nur bei tatsächlichem Wechsel

             ▼

┌─────────────────────────────────────┐#### **Chat-Streaming:**

│  Validation & Preprocessing         │- **Rate-Limiting:** UI-Updates nur alle 0.1 Sekunden

│  • Model-Check                      │- **Duplikat-Erkennung:** Verhindert doppelte Nachrichten

│  • Message-History                  │- **Intelligente Ersetung:** Ersetzt nur Nachrichten vom gleichen Sender

│  • BIAS-Integration                 │

└────────────┬────────────────────────┘#### **Beispiel - Saubere Ausgabe:**

             │```

             ▼🚀 DOWNLOAD START: llama2:13b

┌─────────────────────────────────────┐📡 Verwende Ollama Client für llama2:13b

│  OllamaManager.chat()               │⏳ Starte Download-Stream...

│  • API-Request                      │📥 Status: pulling manifest

│  • Stream-Processing                │🔄 Layer: 2609048d349e

└────────────┬────────────────────────┘📊 2.0% (140.7MB/7025.5MB) | 5.9MB/s | ETA: 19.3min

             │📊 6.8% (477.1MB/7025.5MB) | 6.5MB/s | ETA: 16.8min

             ▼ (Generator)✅ DOWNLOAD COMPLETE: llama2:13b

┌─────────────────────────────────────┐```

│  Progressive Update                 │

│  • Token-by-Token Display           │**Resultat:** 90% weniger redundante Ausgaben! 🎯

│  • UI-Update (after_idle)           │

│  • Performance-Tracking             │## 🆕 Erweiterte Features - Live-API und intelligente Kategorisierung

└────────────┬────────────────────────┘

             │### 🌐 **Live-Ollama-API Integration**

             ▼Die Anwendung fragt jetzt **live die aktuellen Modelle** direkt von Ollama ab:

┌─────────────────────────────────────┐

│  Session-Persistence                │- **Echte Live-Daten:** Keine statische Liste mehr - immer die neuesten Modelle

│  • Auto-Save Timer (60s)            │- **Automatische Updates:** Neue Modelle erscheinen sofort nach Release  

│  • JSON-Export                      │- **Fallback-System:** Robuste Fallback-Liste bei API-Problemen

└─────────────────────────────────────┘- **60+ Aktuelle Modelle:** Immer die vollständige, aktuelle Ollama-Bibliothek

```

### 🎨 **Intelligente Größen-Kategorisierung**

---Modelle sind jetzt **farblich gruppiert** nach RAM-Anforderungen:



## Installation#### 🟢 **Klein (< 4GB RAM)** - 18 Modelle

Perfekt für schwächere Hardware:

### Voraussetzungen- `tinyllama:1.1b`, `phi3:mini`, `gemma:2b`

- `orca-mini:3b`, `phi:2.7b`, `qwen2:0.5b`

| Komponente | Version | Beschreibung |

|------------|---------|--------------|#### 🟡 **Mittel (4-8GB RAM)** - 32 Modelle  

| **Python** | 3.8+ | Programmiersprache |Standard-Modelle für normale Hardware:

| **Ollama** | Latest | Lokaler AI-Server |- `llama3.2:3b`, `mistral:7b`, `codellama:7b`

| **RAM** | 8GB+ | Mindestens für mittlere Modelle |- `gemma:7b`, `deepseek-coder:6.7b`, `phi3`

| **OS** | Windows/Linux/Mac | Plattformübergreifend |

#### 🟠 **Groß (8-16GB RAM)** - 3 Modelle

### Schritt 1: Ollama installierenFür leistungsstarke Systeme:

- `llama2:13b`, `solar:10.7b`, `starcode:15b`

```bash

# Windows/Mac: Download von https://ollama.ai#### 🔴 **Sehr Groß (16GB+ RAM)** - 7 Modelle

# Linux:Für High-End-Hardware:

curl -fsSL https://ollama.ai/install.sh | sh- `llama2:70b`, `mixtral:8x7b`, `codellama:34b`

- `mixtral:8x22b`, `falcon:40b`

# Ollama starten

ollama serve### 🎛️ **Verbessertes Interface**

```

#### **Kategorisiertes Dropdown-Menü:**

### Schritt 2: Repository klonen- **Farbkodierte Kategorien** mit Emoji-Indikation

- **Übersichtliche Gruppierung** nach Hardware-Anforderungen

```bash- **Intelligente Auswahl** - Kategorie-Header sind nicht herunterladbar

git clone https://github.com/Nr44suessauer/Ki-whisperer.git- **Live-Feedback** - Zeigt Anzahl gefundener Modelle an

cd Ki-whisperer/a1_terminal_modular

```#### **Smarte Features:**

- **Duplikatsprüfung:** Warnt vor bereits installierten Modellen

### Schritt 3: Dependencies installieren- **Hardware-Hinweise:** Direkte RAM-Anforderungen sichtbar

- **Bessere Fehlermeldungen:** Erklärt warum Auswahl ungültig ist

```bash- **Live-Updates:** "🔄 Lade aktuelle Modell-Liste von Ollama..."

pip install -r requirements.txt

```### 🚀 **Verwendung der neuen Live-Features**



**requirements.txt:**1. **Hardware-gerechte Auswahl:**

```   ```

customtkinter>=5.2.0   🟢 Schwache Hardware (4GB RAM)    → Wählen Sie aus "Klein"

ollama>=0.1.0   🟡 Normale Hardware (8GB RAM)     → Wählen Sie aus "Mittel"  

PyYAML>=6.0   🟠 Starke Hardware (16GB RAM)     → Wählen Sie aus "Groß"

requests>=2.31.0   🔴 High-End Hardware (32GB+ RAM)  → Wählen Sie aus "Sehr Groß"

```   ```



### Schritt 4: Erstes Modell herunterladen2. **Live-Updates nutzen:**

   - Klicken Sie "Aktualisieren" für neueste Modelle

```bash   - Die App holt automatisch die aktuelle Ollama-Bibliothek

# Beispiel: Llama 3.2 (empfohlen für Start)   - Neue Releases erscheinen sofort in der Liste

ollama pull llama3.2:3b

```3. **Kategorien durchsuchen:**

   - Öffnen Sie das "Verfügbare Modelle" Dropdown

---   - Scrollen Sie durch die farbkodierten Kategorien  

   - Wählen Sie ein Modell (nicht die Kategorie-Header)

## Schnellstart   - Klicken Sie "Ausgewähltes Modell herunterladen"



### Windows (empfohlen)### 🔧 **Technische Details**



```bash#### **Live-API Endpunkt:**

cd a1_terminal_modular```

start.batURL: https://registry.ollama.ai/v2/_catalog

```Methode: GET mit User-Agent Header

Timeout: 10 Sekunden mit Fallback

### Direkt mit Python```



```bash#### **Kategorisierungs-Logik:**

python main.py- **Automatische Erkennung** anhand Modellnamen (1.1b, 7b, 70b, etc.)

```- **Intelligente Gruppierung** nach RAM-Anforderungen

- **Fallback-Kategorisierung** für unbekannte Größen

### Erste Schritte

#### **Performance:**

1. **Modell auswählen** - Dropdown-Menü im Chat-Tab- **Threading:** Alle API-Calls laufen im Hintergrund

2. **Nachricht senden** - Textfeld unten, Enter-Taste- **Caching:** Modell-Liste wird zwischengespeichert  

3. **BIAS setzen** (optional) - Tab "BIAS" für Session-Kontext- **Non-Blocking UI:** Interface bleibt während des Ladens reaktiv

4. **Session speichern** - Automatisch alle 60 Sekunden

Die erweiterte Version bietet jetzt **echte Live-Integration** mit der Ollama-Registry und macht es viel einfacher, das richtige Modell für Ihre Hardware zu finden! 🎯

---

## Lizenz

## Modulare Struktur

MIT License - Siehe LICENSE Datei für Details.
### Core-Module

#### 1. `a1_terminal.py` (Hauptanwendung)

**Verantwortlichkeiten:**
- UI-Orchestrierung und Layout
- Event-Handling (Buttons, Eingaben)
- Session-Management (Laden, Speichern, Wechseln)
- Konfigurations-Management (YAML)
- Chat-Logik (Nachrichten senden/empfangen)
- Export-Funktionen (Markdown, JSON)

**Wichtige Methoden:**

| Methode | Beschreibung |
|---------|--------------|
| `__init__()` | Initialisierung, Config-Laden |
| `setup_ui()` | GUI-Erstellung (Tabs, Widgets) |
| `send_message()` | Nachricht an AI senden |
| `create_new_session()` | Neue Chat-Session erstellen |
| `save_session()` | Session persistieren |
| `apply_config()` | Konfiguration anwenden |

**Codebeispiel - Nachricht senden:**
```python
def send_message(self, event=None):
    message = self.message_entry.get()
    if not message.strip():
        return
    
    # Nachricht zur Historie hinzufügen
    self.message_history.append(message)
    self.history_index = -1
    
    # User-Bubble anzeigen
    self.add_chat_bubble("Sie", message)
    
    # AI-Antwort in Thread generieren
    threading.Thread(
        target=self._generate_response,
        args=(message,),
        daemon=True
    ).start()
```

#### 2. `ollama_manager.py` (API-Client)

**Verantwortlichkeiten:**
- Kommunikation mit Ollama REST API
- Model-Management (Liste, Download, Löschen)
- Chat-Funktionalität (Streaming)
- Model-Kategorisierung nach Größe
- Verbindungs-Status-Prüfung

**Wichtige Methoden:**

| Methode | Beschreibung |
|---------|--------------|
| `is_ollama_running()` | Prüft Ollama-Service-Status |
| `get_available_models()` | Listet installierte Modelle |
| `chat()` | Sendet Chat-Request (Generator) |
| `download_model()` | Lädt Modell herunter (Progress) |
| `categorize_models_by_size()` | Gruppiert Modelle nach RAM-Bedarf |

**Codebeispiel - Chat mit Streaming:**
```python
def chat(self, model, messages, stop_flag=None):
    """Generator für Streaming-Chat-Antworten"""
    try:
        response = self.client.chat(
            model=model,
            messages=messages,
            stream=True
        )
        
        for chunk in response:
            if stop_flag and stop_flag():
                break
            
            if 'message' in chunk:
                content = chunk['message'].get('content', '')
                if content:
                    yield content
    except Exception as e:
        yield f"Fehler: {str(e)}"
```

**Model-Kategorisierung:**
```
┌────────────────────────────────────────────┐
│ 🟢 Klein (< 4GB RAM)                       │
│  • tinyllama:1.1b, phi3:mini, gemma:2b    │
├────────────────────────────────────────────┤
│ 🟡 Mittel (4-8GB RAM)                      │
│  • llama3.2:3b, mistral:7b, codellama:7b  │
├────────────────────────────────────────────┤
│ 🟠 Groß (8-16GB RAM)                       │
│  • llama2:13b, vicuna:13b, solar:10.7b    │
├────────────────────────────────────────────┤
│ 🔴 Sehr Groß (16GB+ RAM)                   │
│  • llama2:70b, mixtral:8x7b, codellama:34b│
└────────────────────────────────────────────┘
```

### UI-Module

#### 3. `color_wheel.py` (Farbwähler)

**Features:**
- Interaktiver HSV-Farbkreis
- RGB-Hex-Ausgabe
- Marker für ausgewählte Farbe
- Callback-System für Farbänderungen

**Technische Details:**
```python
# HSV zu RGB Konvertierung
def hsv_to_rgb(self, h, s, v):
    h = h / 360.0
    c = v * s
    x = c * (1 - abs((h * 6) % 2 - 1))
    m = v - c
    
    # Sextant-basierte Konvertierung
    # ... (6 Sektoren für Farbkreis)
    
    return (int((r + m) * 255), 
            int((g + m) * 255), 
            int((b + m) * 255))
```

#### 4. `chat_bubble.py` (Nachricht)

**Features:**
- Dynamische Höhenberechnung
- Kopier-Funktionalität
- Sender-spezifisches Styling
- Konfigurierbares Layout

**Styling-Logik:**
```
┌──────────────────────────────────────────┐
│ Sender: Sie                              │
│ • Rechts ausgerichtet                    │
│ • Matrix-Farben (Dunkelgrün + Neongrün) │
│ • Courier New Font                       │
│ • Border-Effekt                          │
├──────────────────────────────────────────┤
│ Sender: AI (🤖)                          │
│ • Links ausgerichtet                     │
│ • Blau-Töne                              │
│ • Consolas Font (Code)                   │
│ • Kein Border                            │
├──────────────────────────────────────────┤
│ Sender: System                           │
│ • Links ausgerichtet                     │
│ • Rot-Töne (Warnung)                     │
│ • Arial Font                             │
│ • Kompakte Darstellung                   │
└──────────────────────────────────────────┘
```

#### 5. `categorized_combobox.py` (Dropdown)

**Features:**
- Hierarchische Darstellung
- Kategorie-Header (nicht auswählbar)
- Flattening für Kompatibilität

**Struktur:**
```python
categories = {
    "🟢 Klein (< 4GB RAM)": ["phi:2.7b", "gemma:2b"],
    "🟡 Mittel (4-8GB RAM)": ["llama3.2:3b", "mistral:7b"],
    # ...
}

# Flat-Liste für CTkComboBox:
# ["--- 🟢 Klein (< 4GB RAM) ---", "phi:2.7b", "gemma:2b",
#  "--- 🟡 Mittel (4-8GB RAM) ---", "llama3.2:3b", ...]
```

---

## Technische Dokumentation

### Session-Management

#### Session-Format (JSON)

```json
{
  "session_id": "session_20251109_203448_442",
  "created_at": "2025-11-09T20:34:48",
  "modified_at": "2025-11-09T21:15:32",
  "model": "llama3.2:3b",
  "bias": "Du bist ein hilfreicher Assistent für Python-Programmierung.",
  "messages": [
    {
      "role": "user",
      "content": "Wie funktioniert Multithreading?",
      "timestamp": "2025-11-09T20:35:12"
    },
    {
      "role": "assistant",
      "content": "Multithreading ermöglicht...",
      "timestamp": "2025-11-09T20:35:18"
    }
  ],
  "statistics": {
    "message_count": 12,
    "total_tokens": 3420,
    "average_response_time": 2.3
  }
}
```

#### Session-Lifecycle

```
┌─────────────────────────────────────────────────┐
│ 1. CREATE SESSION                               │
│    • Generate unique ID (timestamp + random)    │
│    • Initialize empty message list              │
│    • Set default BIAS                           │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│ 2. ACTIVE SESSION                               │
│    • Add messages to history                    │
│    • Update statistics                          │
│    • Auto-save every 60s                        │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│ 3. SAVE SESSION                                 │
│    • Serialize to JSON                          │
│    • Write to sessions/ directory               │
│    • Update modified_at timestamp               │
└────────────┬────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────┐
│ 4. LOAD SESSION                                 │
│    • Deserialize from JSON                      │
│    • Restore chat history                       │
│    • Recreate UI bubbles                        │
│    • Set model and BIAS                         │
└─────────────────────────────────────────────────┘
```

### BIAS-System

**BIAS** = Background Information And System instructions

Das BIAS-System ermöglicht Session-spezifischen Kontext:

```
┌────────────────────────────────────────────────┐
│ BIAS Input (User)                              │
│ "Du bist ein Python-Experte..."               │
└──────────────┬─────────────────────────────────┘
               │
               ▼
┌────────────────────────────────────────────────┐
│ Integration in jeden Request                   │
│                                                │
│ messages = [                                   │
│   {"role": "system", "content": BIAS},        │
│   {"role": "user", "content": "Frage 1"},    │
│   {"role": "assistant", "content": "..."},   │
│   {"role": "user", "content": "Frage 2"}     │
│ ]                                              │
└────────────────────────────────────────────────┘
```

**BIAS Best Practices:**

| Anwendungsfall | Beispiel |
|----------------|----------|
| **Rollenspiel** | "Du bist ein Senior-Developer mit 10 Jahren Erfahrung." |
| **Spezialwissen** | "Du bist Experte für Cybersecurity und Penetration Testing." |
| **Tonalität** | "Antworte immer knapp und präzise, ohne Erklärungen." |
| **Format** | "Gib Code-Beispiele immer in Markdown-Format aus." |

### Konfigurations-System

#### YAML-Struktur

```yaml
# Farben für Chat-Bubbles (Hex-Codes)
user_bg_color: "#003300"      # Dunkelgrün
user_text_color: "#00FF00"    # Neongrün
ai_bg_color: "#1E3A5F"        # Dunkelblau
ai_text_color: "white"
system_bg_color: "#722F37"    # Dunkelrot
system_text_color: "white"

# Schriftarten
user_font: "Courier New"      # Matrix-Style
user_font_size: 11
ai_font: "Consolas"           # Code-Font
ai_font_size: 11
system_font: "Arial"
system_font_size: 10

# UI-Optionen
show_system_messages: true    # System-Nachrichten anzeigen
```

#### Live-Update-Mechanismus

```python
def apply_config(self):
    """Wendet Konfiguration ohne Neustart an"""
    
    # 1. Config in YAML speichern
    self.save_config()
    
    # 2. Alle Chat-Bubbles aktualisieren
    for bubble in self.chat_bubbles:
        bubble.update_style(self.config)
    
    # 3. UI-Elemente refreshen
    self.chat_display.update()
    
    # 4. Vorschau-Icons aktualisieren
    self.update_color_previews()
```

---

## Features

### 1. Model-Management

#### Modell-Download

```python
# Download mit Progress-Tracking
def download_model(self, model_name, progress_callback=None):
    """
    Args:
        model_name: z.B. "llama3.2:3b"
        progress_callback: Funktion(current, total, status)
    """
    try:
        for progress in ollama.pull(model_name, stream=True):
            if progress_callback:
                progress_callback(
                    progress.get('completed', 0),
                    progress.get('total', 0),
                    progress.get('status', '')
                )
    except Exception as e:
        raise Exception(f"Download fehlgeschlagen: {e}")
```

**UI-Darstellung:**
```
┌──────────────────────────────────────────┐
│ Modell herunterladen                     │
├──────────────────────────────────────────┤
│ Model: llama3.2:3b                       │
│                                          │
│ ████████████░░░░░░░░ 60%                 │
│ 1.2 GB / 2.0 GB                          │
│                                          │
│ Status: Pulling manifest                 │
│                                          │
│ [ Abbrechen ]                            │
└──────────────────────────────────────────┘
```

### 2. Chat-Funktionalität

#### Echtzeit-Streaming

```
User Message
     │
     ▼
┌─────────────────────────────┐
│ Thread-Start                │
│ _generate_response()        │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ API-Call (Generator)        │
│ ollama_manager.chat()       │
└──────────┬──────────────────┘
           │ (Yields Tokens)
           ▼
┌─────────────────────────────┐
│ Progressive Update          │
│ • Append to buffer          │
│ • UI update (after_idle)    │
│ • 100ms throttle            │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Complete Response           │
│ • Final bubble update       │
│ • Add to history            │
│ • Trigger auto-save         │
└─────────────────────────────┘
```

#### Nachricht-Historie (Pfeiltasten-Navigation)

```python
# ↑ Pfeiltaste = Vorherige Nachricht
# ↓ Pfeiltaste = Nächste Nachricht

def on_up_arrow(self, event):
    if self.message_history:
        self.history_index += 1
        if self.history_index < len(self.message_history):
            msg = self.message_history[-(self.history_index + 1)]
            self.message_entry.delete(0, tk.END)
            self.message_entry.insert(0, msg)
```

### 3. Export-Funktionen

#### Markdown-Export

```markdown
# Session: session_20251109_203448_442
**Erstellt:** 2025-11-09 20:34:48
**Modell:** llama3.2:3b

## BIAS
Du bist ein hilfreicher Python-Assistent.

---

### Sie (20:35:12)
Wie funktioniert Multithreading in Python?

### 🤖 llama3.2:3b (20:35:18)
Multithreading in Python ermöglicht...
```

#### JSON-Export

Vollständiger Export aller Session-Daten (siehe [Session-Format](#session-format-json)).

### 4. Anpassbare UI

#### Farbschemas

**Matrix-Theme (Standard):**
```yaml
user_bg_color: "#003300"
user_text_color: "#00FF00"
ai_bg_color: "#1E3A5F"
ai_text_color: "white"
```

**Midnight-Theme:**
```yaml
user_bg_color: "#1a1a2e"
user_text_color: "#eee"
ai_bg_color: "#16213e"
ai_text_color: "#0f3460"
```

**Solarized-Theme:**
```yaml
user_bg_color: "#002b36"
user_text_color: "#839496"
ai_bg_color: "#073642"
ai_text_color: "#93a1a1"
```

---

## Konfiguration

### Config-Tab (UI)

```
┌────────────────────────────────────────────────────┐
│ ⚙️ Konfiguration                                   │
├────────────────────────────────────────────────────┤
│                                                    │
│ ┌─ Sie (User) ──────────────────────────────────┐ │
│ │ Hintergrund: [#003300] 🎨                     │ │
│ │ Text:        [#00FF00] 🎨                     │ │
│ │ Schriftart:  [Courier New ▼] Größe: [11]     │ │
│ └───────────────────────────────────────────────┘ │
│                                                    │
│ ┌─ AI-Modell ────────────────────────────────────┐ │
│ │ Hintergrund: [#1E3A5F] 🎨                     │ │
│ │ Text:        [white   ] 🎨                     │ │
│ │ Schriftart:  [Consolas ▼] Größe: [11]        │ │
│ └───────────────────────────────────────────────┘ │
│                                                    │
│ ┌─ System-Nachrichten ───────────────────────────┐ │
│ │ Hintergrund: [#722F37] 🎨                     │ │
│ │ Text:        [white   ] 🎨                     │ │
│ │ Schriftart:  [Arial ▼] Größe: [10]           │ │
│ │ Anzeigen:    [✓]                              │ │
│ └───────────────────────────────────────────────┘ │
│                                                    │
│         [ Anwenden ]  [ Standard ]                │
└────────────────────────────────────────────────────┘
```

---

## API-Referenz

### OllamaManager

#### Konstruktor
```python
manager = OllamaManager()
```

#### Methoden

##### `is_ollama_running() -> bool`
Prüft ob Ollama-Service läuft.

**Returns:** `True` wenn erreichbar, sonst `False`

---

##### `get_available_models() -> List[str]`
Holt Liste aller installierten Modelle.

**Returns:** Liste von Modellnamen

---

##### `chat(model: str, messages: List[dict], stop_flag: Callable = None) -> Generator`
Sendet Chat-Request mit Streaming.

**Parameters:**
- `model`: Modellname (z.B. "llama3.2:3b")
- `messages`: Liste von Message-Dicts
- `stop_flag`: Optional - Funktion die `True` zurückgibt zum Stoppen

**Yields:** Token-Strings (einzelne Text-Chunks)

---

## Performance & Monitoring

### Performance-Metriken

| Metrik | Beschreibung | Typischer Wert |
|--------|--------------|----------------|
| **Response Time** | Zeit bis erste Token | 0.5-2.0s |
| **Token Rate** | Tokens pro Sekunde | 20-50 tokens/s |
| **Memory Usage** | RAM-Verbrauch App | 100-200 MB |
| **Model Memory** | RAM-Verbrauch Modell | 2-16 GB |

---

## Troubleshooting

### Problem: "Ollama nicht erreichbar"

**Lösung:**
```bash
# Ollama starten
ollama serve

# Status prüfen
curl http://localhost:11434/api/tags
```

---

### Problem: UI friert ein

**Lösung:**
```yaml
# In config erhöhen:
performance:
  update_throttle_ms: 200  # Standard: 100
```

---

## Beste Praktiken

### Model-Auswahl

| Anwendungsfall | Empfohlenes Modell | Begründung |
|----------------|-------------------|------------|
| **Schnelle Tests** | `phi3:mini` (1.5GB) | Extrem schnell |
| **Allgemein** | `llama3.2:3b` (2GB) | Guter Kompromiss |
| **Code** | `codellama:7b` (4GB) | Optimiert für Programmierung |
| **Lange Texte** | `mistral:7b` (4GB) | Großes Kontext-Fenster |
| **Maximale Qualität** | `llama2:70b` (40GB) | Beste Qualität |

---

## Lizenz

MIT License

---

## Credits

**Entwickelt von:** Nr44suessauer  
**Framework:** CustomTkinter  
**AI-Backend:** Ollama  

---

**Version:** 2.0.0  
**Last Updated:** 2025-11-09
