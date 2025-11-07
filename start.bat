@echo off
echo Starting LLM Messenger...
echo.

REM Check if Ollama is running
echo Checking Ollama status...
curl -s http://localhost:11434/api/tags > nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Ollama does not seem to be running on port 11434
    echo Please start Ollama first by running: ollama serve
    echo.
    pause
)

REM Start the application
echo Starting LLM Messenger application...
C:\Users\marcn\AppData\Local\Programs\Python\Python312\python.exe llm_messenger.py

pause