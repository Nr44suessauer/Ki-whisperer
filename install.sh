#!/bin/bash

# =====================================================================
#  A1-Terminal - Vollständiges Installationsskript (Linux/macOS)
#  Installiert ALLE benötigten Dependencies auf einem blanken System
# =====================================================================

set -e  # Bei Fehler abbrechen

echo ""
echo "========================================================================"
echo "  A1-Terminal - Automatische Installation"
echo "========================================================================"
echo ""
echo "Dieses Skript installiert:"
echo "  - Python 3.8+ (falls nicht vorhanden)"
echo "  - pip (Python Package Manager)"
echo "  - Ollama"
echo "  - Alle Python-Pakete (CustomTkinter, ollama, etc.)"
echo ""
echo "========================================================================"
echo ""

# Betriebssystem erkennen
OS="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    echo "[FEHLER] Nicht unterstütztes Betriebssystem: $OSTYPE"
    exit 1
fi

echo "[INFO] Erkanntes Betriebssystem: $OS"
echo ""

# =====================================================================
#  1. Python Installation prüfen/installieren
# =====================================================================

echo "========================================================================"
echo "[1/4] Python Installation prüfen..."
echo "========================================================================"
echo ""

if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "[OK] Python ist bereits installiert: $PYTHON_VERSION"
    echo ""
else
    echo "[INFO] Python ist nicht installiert. Starte Installation..."
    echo ""
    
    if [ "$OS" == "linux" ]; then
        # Linux: Verwende apt (Debian/Ubuntu) oder dnf (Fedora)
        if command -v apt &> /dev/null; then
            echo "[INFO] Verwende apt (Debian/Ubuntu)"
            sudo apt update
            sudo apt install -y python3 python3-pip python3-tk
        elif command -v dnf &> /dev/null; then
            echo "[INFO] Verwende dnf (Fedora)"
            sudo dnf install -y python3 python3-pip python3-tkinter
        elif command -v yum &> /dev/null; then
            echo "[INFO] Verwende yum (CentOS/RHEL)"
            sudo yum install -y python3 python3-pip python3-tkinter
        else
            echo "[FEHLER] Kein unterstützter Paketmanager gefunden!"
            echo "Bitte installieren Sie Python 3.8+ manuell."
            exit 1
        fi
    elif [ "$OS" == "macos" ]; then
        # macOS: Verwende Homebrew
        if ! command -v brew &> /dev/null; then
            echo "[INFO] Homebrew ist nicht installiert. Installiere Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        
        echo "[INFO] Installiere Python mit Homebrew..."
        brew install python@3.11 python-tk@3.11
    fi
    
    echo "[OK] Python wurde erfolgreich installiert."
    echo ""
fi

# Python-Befehl setzen
PYTHON_CMD="python3"

# =====================================================================
#  2. pip aktualisieren
# =====================================================================

echo "========================================================================"
echo "[2/4] pip aktualisieren..."
echo "========================================================================"
echo ""

$PYTHON_CMD -m pip install --upgrade pip --user || {
    echo "[WARNUNG] pip-Update fehlgeschlagen, fahre dennoch fort..."
}

echo ""

# =====================================================================
#  3. Python-Pakete installieren
# =====================================================================

echo "========================================================================"
echo "[3/4] Python-Pakete installieren..."
echo "========================================================================"
echo ""

# Wechsle in das Projektverzeichnis
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR/a1_terminal_modular"

if [ ! -f "requirements.txt" ]; then
    echo "[FEHLER] requirements.txt nicht gefunden!"
    echo "Bitte stellen Sie sicher, dass sich dieses Skript im Hauptverzeichnis befindet."
    exit 1
fi

echo "Installiere Python-Pakete aus requirements.txt..."
echo ""

$PYTHON_CMD -m pip install -r requirements.txt --user || {
    echo "[FEHLER] Installation der Python-Pakete fehlgeschlagen!"
    echo ""
    echo "Versuche einzelne Installation..."
    echo ""
    
    # Fallback: Einzelne Pakete installieren
    $PYTHON_CMD -m pip install "customtkinter>=5.2.0" --user
    $PYTHON_CMD -m pip install "ollama>=0.1.0" --user
    $PYTHON_CMD -m pip install "PyYAML>=6.0" --user
    $PYTHON_CMD -m pip install "requests>=2.31.0" --user
    $PYTHON_CMD -m pip install "pyperclip>=1.8.2" --user
}

echo ""
echo "[OK] Python-Pakete installiert."
echo ""

# Installierte Pakete anzeigen
echo "Installierte Pakete:"
$PYTHON_CMD -m pip list | grep -iE "customtkinter|ollama|yaml|requests|pyperclip"
echo ""

# =====================================================================
#  4. Ollama installieren
# =====================================================================

echo "========================================================================"
echo "[4/4] Ollama Installation prüfen..."
echo "========================================================================"
echo ""

if command -v ollama &> /dev/null; then
    OLLAMA_VERSION=$(ollama --version)
    echo "[OK] Ollama ist bereits installiert: $OLLAMA_VERSION"
    echo ""
else
    echo "[INFO] Ollama ist nicht installiert. Starte automatische Installation..."
    echo ""
    
    if [ "$OS" == "linux" ]; then
        echo "[INFO] Installiere Ollama für Linux..."
        curl -fsSL https://ollama.ai/install.sh | sh
    elif [ "$OS" == "macos" ]; then
        echo "[INFO] Installiere Ollama für macOS..."
        
        if command -v brew &> /dev/null; then
            echo "[INFO] Installation via Homebrew..."
            brew install ollama
        else
            echo "[INFO] Installation via offizielles Skript..."
            curl -fsSL https://ollama.ai/install.sh | sh
        fi
    fi
    
    if [ $? -eq 0 ]; then
        echo "[OK] Ollama wurde erfolgreich installiert."
    else
        echo "[FEHLER] Ollama-Installation fehlgeschlagen!"
        echo "Bitte pruefen Sie Ihre Internetverbindung und versuchen Sie es erneut."
        exit 1
    fi
    echo ""
fi

# =====================================================================
#  5. Ollama starten und Test-Modell herunterladen
# =====================================================================

echo "========================================================================"
echo "[5/5] Ollama konfigurieren und Test-Modell herunterladen..."
echo "========================================================================"
echo ""

if command -v ollama &> /dev/null; then
    echo "[INFO] Starte Ollama-Dienst..."
    
    # Starte Ollama im Hintergrund
    if [ "$OS" == "linux" ]; then
        # Linux: Starte als Service oder im Hintergrund
        if systemctl is-active --quiet ollama 2>/dev/null; then
            echo "[INFO] Ollama läuft bereits als Service."
        else
            nohup ollama serve > /dev/null 2>&1 &
            sleep 8
        fi
    elif [ "$OS" == "macos" ]; then
        # macOS: Starte im Hintergrund
        if pgrep -x "ollama" > /dev/null; then
            echo "[INFO] Ollama läuft bereits."
        else
            nohup ollama serve > /dev/null 2>&1 &
            sleep 8
        fi
    fi
    
    echo "[OK] Ollama-Dienst gestartet."
    echo ""
    
    # Lade automatisch ein kleines Test-Modell herunter
    echo "[INFO] Lade Test-Modell tinyllama:1.1b herunter (~600 MB)..."
    echo "Dies kann einige Minuten dauern..."
    echo ""
    
    ollama pull tinyllama:1.1b
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "[OK] Test-Modell erfolgreich heruntergeladen!"
        echo "Sie können jetzt mit tinyllama:1.1b chatten."
        echo "Weitere Modelle können Sie in der App im 'Models'-Tab herunterladen."
    else
        echo ""
        echo "[WARNUNG] Modell-Download fehlgeschlagen."
        echo "Sie können Modelle später in der App herunterladen."
    fi
    echo ""
else
    echo "[WARNUNG] Ollama konnte nicht gefunden werden."
    echo "Bitte führen Sie dieses Skript erneut aus."
    echo ""
fi

# =====================================================================
#  Start-Skript erstellen
# =====================================================================

echo "[INFO] Erstelle Start-Skript..."

cat > "$SCRIPT_DIR/a1_terminal_modular/start.sh" << 'EOF'
#!/bin/bash

# A1-Terminal Start-Skript für Linux/macOS

echo "Starte A1-Terminal..."

# Wechsle ins Skript-Verzeichnis
cd "$(dirname "$0")"

# Starte Ollama falls nicht läuft
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starte Ollama-Dienst..."
    nohup ollama serve > /dev/null 2>&1 &
    sleep 3
fi

# Starte A1-Terminal
python3 main.py
EOF

chmod +x "$SCRIPT_DIR/a1_terminal_modular/start.sh"

echo "[OK] Start-Skript erstellt: a1_terminal_modular/start.sh"
echo ""

# =====================================================================
#  Abschluss
# =====================================================================

echo "========================================================================"
echo "  Installation abgeschlossen!"
echo "========================================================================"
echo ""
echo "[OK] Alle Komponenten wurden erfolgreich installiert:"
echo ""
echo "  [x] Python + pip"
echo "  [x] CustomTkinter"
echo "  [x] Ollama Python Client"
echo "  [x] PyYAML"
echo "  [x] requests"
echo "  [x] pyperclip"
echo "  [x] Ollama"
echo ""
echo "========================================================================"
echo "  A1-Terminal ist bereit!"
echo "========================================================================"
echo ""
echo "Starten Sie die Anwendung mit:"
echo "  cd a1_terminal_modular && ./start.sh"
echo "  oder: cd a1_terminal_modular && python3 main.py"
echo ""
echo "Weitere Informationen finden Sie in der DOKUMENTATION.md"
echo ""
echo "========================================================================"
echo ""
