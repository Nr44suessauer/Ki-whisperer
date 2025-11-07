# 📁 Session Management System

## 🎯 Übersicht

Das neue Session Management System organisiert alle exportierten Chat-Sessions automatisch in einem dedizierten `sessions/` Ordner mit eindeutigen Session-IDs.

## 🆔 Session-ID Format

**Format:** `YYYYMMDD_HHMMSS`
- `YYYY` - Jahr (4-stellig)
- `MM` - Monat (2-stellig) 
- `DD` - Tag (2-stellig)
- `HH` - Stunde (24h-Format)
- `MM` - Minute
- `SS` - Sekunde

**Beispiel:** `20251107_143025` = 7. November 2025, 14:30:25

## 📁 Ordnerstruktur

```
Ki-whisperer/
├── sessions/                    # ← Automatisch erstellt
│   ├── session_20251107_143025.md
│   ├── session_20251107_143025.json
│   ├── session_20251107_150112.md
│   └── session_20251107_150112.json
├── llm_messenger.py
├── ki_whisperer_config.yaml
└── ...
```

## 🔧 Technische Features

### 📄 Automatische Ordner-Erstellung

```python
# Sessions-Ordner erstellen falls nicht vorhanden
sessions_dir = os.path.join(os.getcwd(), "sessions")
if not os.path.exists(sessions_dir):
    os.makedirs(sessions_dir)
```

### 🆔 Session-ID Generierung

```python
# Session-ID mit Datum und Zeitstempel erstellen
session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
```

### 📂 Dateinamen-Konvention

**Markdown:** `session_{session_id}.md`
**JSON:** `session_{session_id}.json`

**Beispiele:**
- `session_20251107_143025.md`
- `session_20251107_143025.json`

## 📄 Markdown Export Updates

### 🏷️ Erweiterte Session-Informationen

```markdown
# Ki-whisperer Chat Session

**Session-ID:** `20251107_143025`
**Exportiert am:** 07.11.2025 um 14:30:25
**Modell:** llama3.1:8b  
**Anzahl Nachrichten:** 4
**Session-Start:** 14:25:12
**Session-Ende:** 14:26:05

---

[Chat-Inhalt...]

---

*Session-ID: 20251107_143025*
*Generiert von Ki-whisperer LLM Chat Client*
```

## 📊 JSON Export Updates

### 🗂️ Erweiterte Session-Metadaten

```json
{
  "session_info": {
    "session_id": "20251107_143025",
    "export_timestamp": "2025-11-07T14:30:25.123456",
    "session_start": "14:25:12",
    "session_end": "14:26:05", 
    "model": "llama3.1:8b",
    "total_messages": 4
  },
  "messages": [...]
}
```

## 💡 Benutzerführung

### 🎯 Export-Dialog

1. **Export-Button klicken** → Dialog öffnet sich
2. **Format wählen** → Markdown oder JSON
3. **Exportieren klicken** → Datei-Dialog öffnet sich
4. **Automatische Vorgaben:**
   - **Ordner:** `sessions/` (wird automatisch erstellt)
   - **Dateiname:** `session_20251107_143025.md`
   - **Session-ID:** Zeitbasiert generiert

### ✅ Erfolgs-Meldung

```
Chat-Session wurde erfolgreich exportiert:
C:\...\Ki-whisperer\sessions\session_20251107_143025.md

Session-ID: 20251107_143025
```

## 🔍 Session-ID Extraktion

Das System kann Session-IDs automatisch aus Dateinamen extrahieren:

```python
# Session-ID aus Dateiname extrahieren
filename = os.path.basename(file_path)
if filename.startswith("session_") and filename.endswith(".md"):
    session_id = filename[8:-3]  # Entferne "session_" und ".md"
```

## 📈 Vorteile

### 🗂️ Organisation
- **Zentrale Sammlung** aller Sessions im `sessions/` Ordner
- **Eindeutige Identifikation** durch Session-IDs
- **Chronologische Sortierung** durch Zeitstempel-Format

### 🔍 Nachverfolgung
- **Session-Start/Ende** Zeiten werden gespeichert
- **Verwendetes Modell** wird dokumentiert
- **Export-Zeitstempel** für Versionierung

### 🤝 Kompatibilität
- **Rückwärtskompatibel** - bestehende Funktionen unverändert
- **Flexible Speicherorte** - Nutzer kann anderen Ordner wählen
- **Standard-Vorgaben** - aber überschreibbar

## 🎨 Vorschau-Updates

Die Export-Dialog Vorschau wurde aktualisiert und zeigt die neuen Session-Features:

**Markdown-Vorschau:**
```markdown
**Session-ID:** `20251107_143025`
**Session-Start:** 14:25:12  
**Session-Ende:** 14:26:05
```

**JSON-Vorschau:**
```json
"session_info": {
  "session_id": "20251107_143025",
  "session_start": "14:25:12",
  "session_end": "14:26:05"
}
```

## 🚀 Workflow-Beispiel

1. **Chat führen** mit KI-Modell
2. **"📄 Export" klicken** 
3. **Markdown wählen** → Vorschau zeigt Session-ID
4. **"📤 Exportieren" klicken**
5. **Automatisch geöffneter Dialog:**
   - 📁 Ordner: `Ki-whisperer/sessions/`
   - 📄 Datei: `session_20251107_143025.md`
6. **Speichern** → Session ist organisiert abgelegt

Das neue System macht Session-Management automatisch und benutzerfreundlich! 🎉