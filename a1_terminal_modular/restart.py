#!/usr/bin/env python3
"""
Restart Script für Ki-Whisperer
Startet die Anwendung nach einer kurzen Verzögerung neu
"""

import sys
import subprocess
import time
import os

def restart_application():
    """Startet die Anwendung neu"""
    try:
        print("🔄 Starte Ki-Whisperer neu...")
        time.sleep(0.5)  # Kurze Pause damit die alte Instanz schließen kann
        
        # Aktuelles Arbeitsverzeichnis
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Python-Executable
        python_exe = sys.executable
        
        # Starte die Hauptanwendung
        main_script = os.path.join(current_dir, "main.py")
        
        if os.path.exists(main_script):
            # Starte neue Instanz
            subprocess.Popen([python_exe, main_script], 
                           cwd=current_dir,
                           creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0)
            print("✅ Ki-Whisperer wurde neu gestartet")
        else:
            print(f"❌ Fehler: main.py nicht gefunden in {current_dir}")
            
    except Exception as e:
        print(f"❌ Fehler beim Neustart: {e}")

if __name__ == "__main__":
    restart_application()
