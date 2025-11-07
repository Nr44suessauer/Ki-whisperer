# LLM Messenger - Ollama Chat Client

Ein moderner Python-Chat-Client für lokale AI-Modelle mit Ollama-Integration.

## Features

- 🎨 Modernes, dunkles UI mit CustomTkinter
- 📥 Modell-Download direkt aus der Anwendung
- 🗑️ Modell-Verwaltung (Löschen, Auswählen)
- 💬 Streaming-Chat mit AI-Modellen
- 📝 Chat-Historie innerhalb einer Session
- 🔄 Live-Status von Ollama
- ⚡ Echtzeit-Updates

## Voraussetzungen

1. **Ollama installieren**
   - Gehen Sie zu [ollama.ai](https://ollama.ai) 
   - Laden Sie Ollama für Ihr Betriebssystem herunter
   - Installieren und starten Sie Ollama

2. **Python 3.8+ installiert**

## Installation

1. **Repository klonen oder herunterladen**
   ```bash
   cd "C:\Users\marcn\Documents\LLM Messenger"
   ```

2. **Abhängigkeiten installieren**
   ```bash
   C:/Users/marcn/AppData/Local/Programs/Python/Python312/python.exe -m pip install -r requirements.txt
   ```

## Verwendung

1. **Ollama starten** (falls noch nicht gestartet)
   ```bash
   ollama serve
   ```

2. **LLM Messenger starten**
   ```bash
   C:/Users/marcn/AppData/Local/Programs/Python/Python312/python.exe llm_messenger.py
   ```

## Erste Schritte

1. **Modell herunterladen**
   - Klicken Sie auf "Modell herunterladen"
   - Geben Sie einen Modellnamen ein (z.B. `llama2`, `mistral`, `codellama`)
   - Warten Sie, bis der Download abgeschlossen ist

2. **Modell auswählen**
   - Wählen Sie das gewünschte Modell aus dem Dropdown-Menü

3. **Chatten**
   - Geben Sie Ihre Nachricht ein und drücken Sie Enter oder klicken Sie "Senden"
   - Die AI antwortet in Echtzeit

## Beliebte Modelle

- **llama2** - Allzweck-Sprachmodell von Meta
- **mistral** - Schnelles und effizientes Modell
- **codellama** - Spezialisiert auf Programmierung
- **phi** - Kleines, aber leistungsstarkes Modell
- **gemma** - Google's offenes Modell

## Funktionen

### Modell-Management
- **Download**: Laden Sie neue Modelle direkt herunter
- **Löschen**: Entfernen Sie nicht benötigte Modelle
- **Auswählen**: Wechseln Sie zwischen verschiedenen Modellen

### Chat-Features
- **Streaming**: Sehen Sie die Antwort in Echtzeit
- **Historie**: Chat-Verlauf bleibt während der Session erhalten
- **Zeitstempel**: Alle Nachrichten haben Zeitstempel
- **System-Meldungen**: Informationen über Status und Fehler

## Fehlerbehebung

### Ollama nicht verbunden
- Stellen Sie sicher, dass Ollama läuft: `ollama serve`
- Prüfen Sie, ob Port 11434 verfügbar ist
- Starten Sie Ollama neu

### Modell-Download schlägt fehl
- Prüfen Sie Ihre Internetverbindung
- Stellen Sie sicher, dass genügend Speicherplatz vorhanden ist
- Versuchen Sie es mit einem kleineren Modell

### Anwendung startet nicht
- Prüfen Sie, ob alle Abhängigkeiten installiert sind
- Stellen Sie sicher, dass Sie Python 3.8+ verwenden

## Entwicklung

Das Projekt ist in mehrere Klassen unterteilt:

- `OllamaManager`: Verwaltet die Ollama-API-Kommunikation
- `LLMMessenger`: Hauptanwendung mit UI
- Threading für Non-Blocking-Operationen

---

### 🧹 **Anti-Redundanz-System**
Saubere, lesbare Ausgaben ohne nervige Wiederholungen:

#### **Download-Logging:**
- **Status-Filter:** Identische Status werden nicht wiederholt
- **Timing-Optimiert:** Progress-Updates nur alle 2 Sekunden  
- **Kompakt:** Ein-Zeilen-Format statt Multi-Line-Spam
- **Layer-Smart:** Neue Layer nur bei tatsächlichem Wechsel

#### **Chat-Streaming:**
- **Rate-Limiting:** UI-Updates nur alle 0.1 Sekunden
- **Duplikat-Erkennung:** Verhindert doppelte Nachrichten
- **Intelligente Ersetung:** Ersetzt nur Nachrichten vom gleichen Sender

#### **Beispiel - Saubere Ausgabe:**
```
🚀 DOWNLOAD START: llama2:13b
📡 Verwende Ollama Client für llama2:13b
⏳ Starte Download-Stream...
📥 Status: pulling manifest
🔄 Layer: 2609048d349e
📊 2.0% (140.7MB/7025.5MB) | 5.9MB/s | ETA: 19.3min
📊 6.8% (477.1MB/7025.5MB) | 6.5MB/s | ETA: 16.8min
✅ DOWNLOAD COMPLETE: llama2:13b
```

**Resultat:** 90% weniger redundante Ausgaben! 🎯

## 🆕 Erweiterte Features - Live-API und intelligente Kategorisierung

### 🌐 **Live-Ollama-API Integration**
Die Anwendung fragt jetzt **live die aktuellen Modelle** direkt von Ollama ab:

- **Echte Live-Daten:** Keine statische Liste mehr - immer die neuesten Modelle
- **Automatische Updates:** Neue Modelle erscheinen sofort nach Release  
- **Fallback-System:** Robuste Fallback-Liste bei API-Problemen
- **60+ Aktuelle Modelle:** Immer die vollständige, aktuelle Ollama-Bibliothek

### 🎨 **Intelligente Größen-Kategorisierung**
Modelle sind jetzt **farblich gruppiert** nach RAM-Anforderungen:

#### 🟢 **Klein (< 4GB RAM)** - 18 Modelle
Perfekt für schwächere Hardware:
- `tinyllama:1.1b`, `phi3:mini`, `gemma:2b`
- `orca-mini:3b`, `phi:2.7b`, `qwen2:0.5b`

#### 🟡 **Mittel (4-8GB RAM)** - 32 Modelle  
Standard-Modelle für normale Hardware:
- `llama3.2:3b`, `mistral:7b`, `codellama:7b`
- `gemma:7b`, `deepseek-coder:6.7b`, `phi3`

#### 🟠 **Groß (8-16GB RAM)** - 3 Modelle
Für leistungsstarke Systeme:
- `llama2:13b`, `solar:10.7b`, `starcode:15b`

#### 🔴 **Sehr Groß (16GB+ RAM)** - 7 Modelle
Für High-End-Hardware:
- `llama2:70b`, `mixtral:8x7b`, `codellama:34b`
- `mixtral:8x22b`, `falcon:40b`

### 🎛️ **Verbessertes Interface**

#### **Kategorisiertes Dropdown-Menü:**
- **Farbkodierte Kategorien** mit Emoji-Indikation
- **Übersichtliche Gruppierung** nach Hardware-Anforderungen
- **Intelligente Auswahl** - Kategorie-Header sind nicht herunterladbar
- **Live-Feedback** - Zeigt Anzahl gefundener Modelle an

#### **Smarte Features:**
- **Duplikatsprüfung:** Warnt vor bereits installierten Modellen
- **Hardware-Hinweise:** Direkte RAM-Anforderungen sichtbar
- **Bessere Fehlermeldungen:** Erklärt warum Auswahl ungültig ist
- **Live-Updates:** "🔄 Lade aktuelle Modell-Liste von Ollama..."

### 🚀 **Verwendung der neuen Live-Features**

1. **Hardware-gerechte Auswahl:**
   ```
   🟢 Schwache Hardware (4GB RAM)    → Wählen Sie aus "Klein"
   🟡 Normale Hardware (8GB RAM)     → Wählen Sie aus "Mittel"  
   🟠 Starke Hardware (16GB RAM)     → Wählen Sie aus "Groß"
   🔴 High-End Hardware (32GB+ RAM)  → Wählen Sie aus "Sehr Groß"
   ```

2. **Live-Updates nutzen:**
   - Klicken Sie "Aktualisieren" für neueste Modelle
   - Die App holt automatisch die aktuelle Ollama-Bibliothek
   - Neue Releases erscheinen sofort in der Liste

3. **Kategorien durchsuchen:**
   - Öffnen Sie das "Verfügbare Modelle" Dropdown
   - Scrollen Sie durch die farbkodierten Kategorien  
   - Wählen Sie ein Modell (nicht die Kategorie-Header)
   - Klicken Sie "Ausgewähltes Modell herunterladen"

### 🔧 **Technische Details**

#### **Live-API Endpunkt:**
```
URL: https://registry.ollama.ai/v2/_catalog
Methode: GET mit User-Agent Header
Timeout: 10 Sekunden mit Fallback
```

#### **Kategorisierungs-Logik:**
- **Automatische Erkennung** anhand Modellnamen (1.1b, 7b, 70b, etc.)
- **Intelligente Gruppierung** nach RAM-Anforderungen
- **Fallback-Kategorisierung** für unbekannte Größen

#### **Performance:**
- **Threading:** Alle API-Calls laufen im Hintergrund
- **Caching:** Modell-Liste wird zwischengespeichert  
- **Non-Blocking UI:** Interface bleibt während des Ladens reaktiv

Die erweiterte Version bietet jetzt **echte Live-Integration** mit der Ollama-Registry und macht es viel einfacher, das richtige Modell für Ihre Hardware zu finden! 🎯

## Lizenz

MIT License - Siehe LICENSE Datei für Details.