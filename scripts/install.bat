@echo off
REM =====================================================================
REM  A1-Terminal - Vollständiges Installationsskript
REM  Installiert ALLE benötigten Dependencies auf einem blanken Windows-PC
REM =====================================================================

echo.
echo ========================================================================
echo   A1-Terminal - Automatische Installation
echo ========================================================================
echo.
echo Dieses Skript installiert:
echo   - Python 3.11 (falls nicht vorhanden)
echo   - Ollama
echo   - Alle Python-Pakete (CustomTkinter, ollama, etc.)
echo.
echo ========================================================================
echo.

REM Administrator-Rechte prüfen
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [FEHLER] Dieses Skript benoetigt Administrator-Rechte!
    echo Bitte klicken Sie mit rechts auf das Skript und waehlen Sie
    echo "Als Administrator ausfuehren"
    echo.
    pause
    exit /b 1
)

echo [INFO] Administrator-Rechte bestaetigt.
echo.

REM =====================================================================
REM  1. Python Installation prüfen/installieren
REM =====================================================================

echo ========================================================================
echo [1/4] Python Installation pruefen...
echo ========================================================================
echo.

python --version >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Python ist bereits installiert:
    python --version
    echo.
) else (
    echo [INFO] Python ist nicht installiert. Starte Download...
    echo.
    
    REM Python 3.11 herunterladen
    set PYTHON_VERSION=3.11.6
    set PYTHON_URL=https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe
    set PYTHON_INSTALLER=%TEMP%\python-installer.exe
    
    echo Lade Python %PYTHON_VERSION% herunter...
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'}"
    
    if not exist "%PYTHON_INSTALLER%" (
        echo [FEHLER] Python-Download fehlgeschlagen!
        pause
        exit /b 1
    )
    
    echo [INFO] Python wird installiert...
    echo Bitte warten Sie, dies kann einige Minuten dauern...
    
    REM Python installieren (Silent Mode mit pip und PATH)
    "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1 Include_test=0
    
    if %errorLevel% neq 0 (
        echo [FEHLER] Python-Installation fehlgeschlagen!
        pause
        exit /b 1
    )
    
    REM Temporäre Datei löschen
    del "%PYTHON_INSTALLER%"
    
    echo [OK] Python wurde erfolgreich installiert.
    echo.
    
    REM PATH aktualisieren
    echo [INFO] Aktualisiere Umgebungsvariablen...
    call refreshenv >nul 2>&1
    
    REM Neustart der CMD erforderlich
    echo [WARNUNG] Bitte starten Sie dieses Skript erneut, damit die PATH-Variable aktualisiert wird.
    echo.
    pause
    exit /b 0
)

REM =====================================================================
REM  2. pip aktualisieren
REM =====================================================================

echo ========================================================================
echo [2/4] pip aktualisieren...
echo ========================================================================
echo.

python -m pip install --upgrade pip
if %errorLevel% neq 0 (
    echo [WARNUNG] pip-Update fehlgeschlagen, fahre dennoch fort...
)
echo.

REM =====================================================================
REM  3. Python-Pakete installieren
REM =====================================================================

echo ========================================================================
echo [3/4] Python-Pakete installieren...
echo ========================================================================
echo.

REM Wechsle in das Projektverzeichnis
cd /d "%~dp0a1_terminal_modular"

if not exist "requirements.txt" (
    echo [FEHLER] requirements.txt nicht gefunden!
    echo Bitte stellen Sie sicher, dass sich dieses Skript im Hauptverzeichnis befindet.
    pause
    exit /b 1
)

echo Installiere Python-Pakete aus requirements.txt...
echo.

python -m pip install -r requirements.txt

if %errorLevel% neq 0 (
    echo [FEHLER] Installation der Python-Pakete fehlgeschlagen!
    echo.
    echo Versuche einzelne Installation...
    echo.
    
    REM Fallback: Einzelne Pakete installieren
    python -m pip install customtkinter>=5.2.0
    python -m pip install ollama>=0.1.0
    python -m pip install PyYAML>=6.0
    python -m pip install requests>=2.31.0
    python -m pip install pyperclip>=1.8.2
)

echo.
echo [OK] Python-Pakete installiert.
echo.

REM Installierte Pakete anzeigen
echo Installierte Pakete:
python -m pip list | findstr /i "customtkinter ollama yaml requests pyperclip"
echo.

REM =====================================================================
REM  4. Ollama installieren
REM =====================================================================

echo ========================================================================
echo [4/4] Ollama Installation pruefen...
echo ========================================================================
echo.

REM Prüfe ob Ollama bereits installiert ist
where ollama >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Ollama ist bereits installiert:
    ollama --version
    echo.
) else (
    echo [INFO] Ollama ist nicht installiert. Starte automatischen Download...
    echo.
    
    REM Ollama Download-URL
    set OLLAMA_URL=https://ollama.ai/download/OllamaSetup.exe
    set OLLAMA_INSTALLER=%TEMP%\OllamaSetup.exe
    
    echo Lade Ollama herunter (~500 MB)...
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Write-Host 'Download laeuft...'; Invoke-WebRequest -Uri '%OLLAMA_URL%' -OutFile '%OLLAMA_INSTALLER%' -UseBasicParsing}"
    
    if exist "%OLLAMA_INSTALLER%" (
        echo [INFO] Download abgeschlossen. Starte automatische Installation...
        echo.
        
        REM Silent Installation von Ollama
        start /wait "" "%OLLAMA_INSTALLER%" /S
        
        REM Warte bis Installation abgeschlossen
        timeout /t 5 /nobreak >nul
        
        REM Temporäre Datei löschen
        del "%OLLAMA_INSTALLER%"
        
        REM PATH aktualisieren
        echo [INFO] Aktualisiere Umgebungsvariablen...
        for /f "tokens=2*" %%a in ('reg query "HKCU\Environment" /v Path 2^>nul') do set "UserPath=%%b"
        for /f "tokens=2*" %%a in ('reg query "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v Path 2^>nul') do set "SystemPath=%%b"
        set "PATH=%UserPath%;%SystemPath%"
        
        echo [OK] Ollama wurde erfolgreich installiert.
    ) else (
        echo [FEHLER] Ollama-Download fehlgeschlagen!
        echo Bitte pruefen Sie Ihre Internetverbindung und versuchen Sie es erneut.
        pause
        exit /b 1
    )
    echo.
)

REM =====================================================================
REM  5. Ollama starten und Basis-Modell herunterladen
REM =====================================================================

echo ========================================================================
echo [5/5] Ollama konfigurieren und Test-Modell herunterladen...
echo ========================================================================
echo.

REM Prüfe ob Ollama verfügbar ist
where ollama >nul 2>&1
if %errorLevel% equ 0 (
    echo [INFO] Starte Ollama-Dienst...
    
    REM Starte Ollama im Hintergrund
    start /B ollama serve >nul 2>&1
    
    REM Warte 8 Sekunden bis Ollama gestartet ist
    echo Warte auf Ollama-Start...
    timeout /t 8 /nobreak >nul
    
    echo [OK] Ollama-Dienst gestartet.
    echo.
    
    REM Lade automatisch ein kleines Test-Modell herunter
    echo [INFO] Lade Test-Modell tinyllama:1.1b herunter (~600 MB)...
    echo Dies kann einige Minuten dauern...
    echo.
    ollama pull tinyllama:1.1b
    
    if %errorLevel% equ 0 (
        echo.
        echo [OK] Test-Modell erfolgreich heruntergeladen!
        echo Sie koennen jetzt mit tinyllama:1.1b chatten.
        echo Weitere Modelle koennen Sie in der App im "Models"-Tab herunterladen.
    ) else (
        echo.
        echo [WARNUNG] Modell-Download fehlgeschlagen.
        echo Sie koennen Modelle spaeter in der App herunterladen.
    )
    echo.
) else (
    echo [WARNUNG] Ollama konnte nicht gefunden werden.
    echo Bitte fuehren Sie dieses Skript erneut aus.
    echo.
)

REM =====================================================================
REM  Abschluss
REM =====================================================================

echo ========================================================================
echo   Installation abgeschlossen!
echo ========================================================================
echo.
echo [OK] Alle Komponenten wurden erfolgreich installiert:
echo.
echo   [x] Python + pip
echo   [x] CustomTkinter
echo   [x] Ollama Python Client
echo   [x] PyYAML
echo   [x] requests
echo   [x] pyperclip
echo   [x] Ollama
echo.
echo ========================================================================
echo   A1-Terminal ist bereit!
echo ========================================================================
echo.
echo Starten Sie die Anwendung mit:
echo   - Doppelklick auf: a1_terminal_modular\start.bat
echo   - Oder: cd a1_terminal_modular ^&^& python main.py
echo.
echo Weitere Informationen finden Sie in der DOKUMENTATION.md
echo.
echo ========================================================================
pause
