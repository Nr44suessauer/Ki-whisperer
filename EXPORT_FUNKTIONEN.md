# 📄 Export-Funktionen in Ki-whisperer

## Überblick

Die Export-Funktionen ermöglichen es, komplette Chat-Sessions in verschiedenen Formaten zu speichern. Dies ist nützlich für:

- **Dokumentation** von Gesprächen mit KI-Modellen
- **Archivierung** wichtiger Unterhaltungen
- **Sharing** von Ergebnissen mit anderen
- **Backup** von wertvollen Chat-Verläufen

## Verfügbare Export-Formate

### 📄 Markdown Export (.md)

**Zweck:** Menschenfreundliche, formatierte Dokumentation
**Dateiformat:** `.md` (Markdown)

**Inhalt:**
- Vollständige Chat-Session mit Zeitstempeln
- Übersichtliche Formatierung mit Headers
- Sender-Kennzeichnung (👤 Benutzer, 🤖 Modell)
- Metadaten (Exportzeit, verwendetes Modell, Anzahl Nachrichten)

**Beispiel-Struktur:**
```markdown
# Ki-whisperer Chat Session

**Exportiert am:** 15.12.2024 um 14:30:25
**Modell:** llama3.1:8b
**Anzahl Nachrichten:** 6

---

**[14:25:12]**

### 👤 Benutzer

Erkläre mir Machine Learning in einfachen Worten

**[14:25:15]**

### 🤖 llama3.1:8b

Machine Learning ist wie das Lernen von Mustern...
```

### 📊 JSON Export (.json)

**Zweck:** Strukturierte Daten für Weiterverarbeitung
**Dateiformat:** `.json` (JavaScript Object Notation)

**Inhalt:**
- Maschinenlesbare Datenstruktur
- Metadaten und Nachrichten-Array
- Sender-Rollen (user, assistant, system)
- Zeitstempel für jede Nachricht

**Beispiel-Struktur:**
```json
{
  "export_info": {
    "timestamp": "2024-12-15T14:30:25.123456",
    "model": "llama3.1:8b",
    "total_messages": 6
  },
  "messages": [
    {
      "timestamp": "14:25:12",
      "role": "user",
      "sender": "Benutzer",
      "content": "Erkläre mir Machine Learning in einfachen Worten"
    },
    {
      "timestamp": "14:25:15", 
      "role": "assistant",
      "sender": "llama3.1:8b",
      "content": "Machine Learning ist wie das Lernen von Mustern..."
    }
  ]
}
```

## Verwendung

### Export-Button verwenden

1. **Button finden:** Der `📄 Export`-Button befindet sich im Chat-Tab neben dem "Stop"-Button
2. **Format wählen:** Nach dem Klick öffnet sich ein Dialog zur Formatauswahl
3. **Datei speichern:** Standard-Dateiname wird vorgeschlagen (Format: `chat_session_YYYYMMDD_HHMMSS`)
4. **Bestätigung:** Eine Erfolgsmeldung zeigt den gespeicherten Dateipfad

### Automatische Dateibenennung

- **Markdown:** `chat_session_20241215_143025.md`
- **JSON:** `chat_session_20241215_143025.json`
- Zeitstempel sorgt für eindeutige Dateinamen

## Technische Details

### Unterstützte Features

- ✅ **UTF-8 Encoding** - Korrekte Darstellung von Umlauten und Emojis
- ✅ **Zeitstempel-Preservation** - Originale Chat-Zeiten werden beibehalten
- ✅ **Sender-Erkennung** - Automatische Unterscheidung User/AI/System
- ✅ **Metadaten** - Export-Info und verwendetes Modell
- ✅ **Error Handling** - Benutzerfreundliche Fehlermeldungen

### Implementierung

**Hauptfunktionen:**
- `export_session()` - Hauptdialog für Formatauswahl
- `export_to_markdown()` - Markdown-Export mit Dateidialog
- `export_to_json()` - JSON-Export mit Dateidialog
- `_generate_markdown_content()` - Markdown-Formatierung

**Integration:**
- Direkt in der originalen `llm_messenger.py` integriert
- Nutzt bestehende `chat_bubbles`-Datenstruktur
- Erweitert die UI um Export-Button

## Anwendungsfälle

### 📚 Dokumentation
```
Nutzen Sie Markdown-Export für:
- Projektdokumentation
- Tutorials und Anleitungen
- Forschungsnotizen
- Präsentationen
```

### 🔧 Datenanalyse
```
Nutzen Sie JSON-Export für:
- Automatische Verarbeitung
- Import in andere Tools
- Datenanalyse
- API-Integration
```

### 💾 Archivierung
```
Beide Formate für:
- Langzeitspeicherung
- Backup-Zwecke
- Versionskontrolle
- Team-Sharing
```

## Fehlerbehebung

### Häufige Probleme

**"Keine Chat-Session zum Exportieren vorhanden!"**
- Führen Sie mindestens eine Unterhaltung bevor dem Export durch

**Datei-Zugriffsfehler**
- Prüfen Sie Schreibberechtigungen im Zielordner
- Schließen Sie eventuell geöffnete Dateien

**Encoding-Probleme**
- Alle Exporte nutzen UTF-8 Encoding automatisch
- Verwenden Sie moderne Text-Editoren zum Anzeigen

---

*Generiert für Ki-whisperer LLM Chat Client*