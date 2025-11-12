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
