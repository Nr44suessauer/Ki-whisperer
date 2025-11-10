# A1-Terminal - Technical Documentation

**Version:** 2.0 (Modular Architecture)  
**Date:** November 2025  
**Type:** Chat client for local AI models via Ollama

---

## Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Installation](#installation)
4. [Architecture](#architecture)
5. [Project Structure](#project-structure)
6. [Core Components](#core-components)
7. [Configuration](#configuration)
8. [API Reference](#api-reference)
9. [User Interface](#user-interface)
10. [Session Management](#session-management)
11. [Usage](#usage)
12. [Development](#development)
13. [Troubleshooting](#troubleshooting)

---

## Overview

**A1-Terminal** is a professional, modular chat client for local AI models that communicates via the Ollama API. The application offers an intuitive graphical user interface with extensive customization options, session management, and real-time streaming functionality.

### Main Features

- 🎯 **Modular Architecture** - Clean separation of UI and business logic
- 🚀 **Real-time Streaming** - Live display of AI responses during generation
- 💾 **Session Management** - Persistent chat sessions with saving and restoration
- 🎨 **Fully Customizable** - Colors, fonts, layout individually configurable
- 📊 **Model Management** - Download, selection, and categorization of AI models
- 🔄 **Offline Capable** - All models run locally without internet connection
- ⚡ **Stop Functionality** - Generation and downloads can be stopped at any time
- 📝 **BIAS System** - System prompts for controlling AI behavior

### Technology Stack

```
┌─────────────────────────────────────────┐
│         CustomTkinter (GUI)             │
├─────────────────────────────────────────┤
│   A1 Terminal Core Application          │
├──────────────┬──────────────────────────┤
│ UI Modules   │  Ollama Manager          │
│              │  (API Client)            │
├──────────────┴──────────────────────────┤
│         Ollama API (localhost:11434)    │
├─────────────────────────────────────────┤
│    Local AI Models                      │
│    (llama, mistral, codellama, etc.)    │
└─────────────────────────────────────────┘
```

---

## System Requirements

### Software

- **Python:** 3.8 or higher
- **Ollama:** Latest version (runs as background service)
- **Operating System:** Windows, Linux, or macOS

### Hardware (Minimum Requirements)

- **RAM:** 8 GB (16 GB recommended for larger models)
- **Storage:** 10 GB free disk space
- **CPU:** Multi-core processor recommended

### Model-specific Requirements

| Model Size | RAM Required | Examples |
|-------------|------------|-----------|
| 🟢 Small (< 4GB) | 4-8 GB | tinyllama:1.1b, phi3:mini, gemma:2b |
| 🟡 Medium (4-8GB) | 8-12 GB | llama3.2:3b, mistral:7b, codellama:7b |
| 🟠 Large (8-16GB) | 16-24 GB | llama2:13b, codellama:13b |
| 🔴 Very Large (16GB+) | 32+ GB | llama2:70b, mixtral:8x7b |

---

## Installation

### Fully Automatic Installation (Recommended)

The project includes installation scripts that install **ALL dependencies fully automatically** - ideal for blank systems. **No manual Ollama installation needed!**

#### Windows

1. **Clone or download repository**
```powershell
cd "C:\Users\<Username>\Documents"
git clone https://github.com/Nr44suessauer/A1-Terminal.git
cd A1-Terminal
```

2. **Run installation script as Administrator**
```powershell
# Right-click on install.bat -> "Run as Administrator"
.\install.bat
```

3. **Start application**
```powershell
cd a1_terminal_modular
.\start.bat
```

#### Linux/macOS

1. **Clone or download repository**
```bash
cd ~/Documents
git clone https://github.com/Nr44suessauer/Ki-whisperer.git
cd Ki-whisperer
```

2. **Make script executable and run**
```bash
chmod +x install.sh
./install.sh
```

3. **Start application**
```bash
cd a1_terminal_modular
./start.sh
```

### Manual Installation

If you prefer manual installation:

1. **Install Ollama**
   - Visit [ollama.ai](https://ollama.ai)
   - Download and install for your operating system
   - Start Ollama (runs automatically in background)

2. **Install Python dependencies**
```bash
cd Ki-whisperer/a1_terminal_modular
pip install -r requirements.txt
```

3. **Download a model (optional)**
```bash
ollama pull tinyllama:1.1b
# or
ollama pull llama3.2:3b
```

4. **Start application**
```bash
python main.py
```

---

## Architecture

### Modular Structure

```
A1Terminal (Main Class)
├── Configuration Management (YAML)
├── Ollama Manager (API Communication)
├── Session Management
│   ├── Save/Load Sessions
│   ├── BIAS System
│   └── Chat History
├── UI Components
│   ├── Model Selector
│   ├── Chat Display
│   ├── Session List
│   └── Configuration Panel
└── Event Handling
    ├── User Input
    ├── Model Selection
    └── Session Switching
```

### Component Overview

1. **Core Components**
   - `a1_terminal.py`: Main application class with all logic
   - `ollama_manager.py`: API client for Ollama communication

2. **UI Components**
   - `chat_bubble.py`: Individual chat messages
   - `session_card.py`: Session list entries
   - `model_selector.py`: Model selection and info
   - `categorized_combobox.py`: Categorized dropdowns
   - `resizable_pane.py`: Adjustable panel dividers

3. **Configuration**
   - `a1_terminal_config.yaml`: Central configuration file
   - `requirements.txt`: Python dependencies

---

## Configuration

### Configuration File (a1_terminal_config.yaml)

The configuration is automatically created on first start and can be customized:

```yaml
# Chat Bubble Colors
user_bg_color: "#003300"      # You - Background
user_text_color: "#00FF00"    # You - Text (Matrix)
ai_bg_color: "#1E3A5F"        # AI - Background
ai_text_color: "white"        # AI - Text

# Fonts
user_font: "Courier New"
user_font_size: 11
ai_font: "Consolas"
ai_font_size: 11

# UI Layout
ui_window_width: 1400
ui_window_height: 900
ui_session_panel_width: 350

# General Options
show_system_messages: true
auto_scroll_chat: true
show_timestamps: true
```

### Customization

All colors, fonts, and layouts can be adjusted:
1. Open `a1_terminal_config.yaml`
2. Modify values
3. Restart application

---

## API Reference

### OllamaManager

Main class for API communication with Ollama:

```python
class OllamaManager:
    def is_ollama_running() -> bool
        """Checks if Ollama is running"""
        
    def get_available_models() -> list
        """Returns list of installed models"""
        
    def download_model(model_name: str, progress_callback=None)
        """Downloads a model"""
        
    def generate_response(model: str, messages: list, stream=True)
        """Generates AI response"""
```

### Key Methods

- **Model Management**
  - `get_available_models()`: List installed models
  - `get_all_ollama_models()`: List all available models
  - `download_model()`: Download model
  - `delete_model()`: Delete model

- **Chat Functionality**
  - `generate_response()`: Generate response
  - `stop_generation()`: Stop generation

---

## Session Management

### Session Structure

Each session is saved as JSON file:

```json
{
  "session_id": "unique_id",
  "created_at": "2025-11-10T12:00:00",
  "name": "Session Name",
  "bias": "System prompt",
  "messages": [
    {
      "role": "user",
      "content": "Message",
      "timestamp": "..."
    }
  ]
}
```

### Functions

- **Create Session**: `create_new_session()`
- **Load Session**: `load_session(session_id)`
- **Save Session**: `save_current_session()`
- **Delete Session**: `delete_session(session_id)`

---

## Usage

### Basic Workflow

1. **Start Application**
   - Run `start.bat` (Windows) or `./start.sh` (Linux/macOS)
   - Or: `python main.py`

2. **Select Model**
   - Choose from installed models
   - Or download new model

3. **Start Chat**
   - Create new session
   - Enter message
   - Send with Enter or button

4. **Session Management**
   - Save current session
   - Load previous session
   - Set BIAS for system prompts

### Keyboard Shortcuts

- **Enter**: Send message
- **Shift+Enter**: New line in message
- **Arrow Up/Down**: Navigate message history
- **Ctrl+N**: New session
- **Ctrl+S**: Save session

---

## Development

### Setup Development Environment

```bash
git clone https://github.com/Nr44suessauer/Ki-whisperer.git
cd Ki-whisperer/a1_terminal_modular
pip install -r requirements.txt
```

### Project Structure

```
src/
├── core/
│   ├── a1_terminal.py       # Main application logic
│   └── ollama_manager.py    # Ollama API client
└── ui/
    ├── chat_bubble.py       # Chat message display
    ├── session_card.py      # Session list entries
    ├── model_selector.py    # Model selection
    └── ...                  # Other UI components
```

### Adding Features

1. UI components go in `src/ui/`
2. Business logic goes in `src/core/`
3. Follow existing patterns
4. Document changes

---

## Troubleshooting

### Ollama Not Running

**Problem**: "Ollama Status: Offline"

**Solution**:
```bash
# Check if Ollama is running
ollama list

# If not running, start Ollama
ollama serve
```

### Model Download Failed

**Problem**: Download fails or hangs

**Solution**:
1. Check internet connection
2. Try manual download: `ollama pull model_name`
3. Check disk space
4. Check firewall settings

### Application Won't Start

**Problem**: Python errors on startup

**Solution**:
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade

# Check Python version
python --version  # Should be 3.8+
```

### Session Won't Load

**Problem**: Error loading session

**Solution**:
1. Check `sessions/` directory exists
2. Verify JSON file is valid
3. Delete corrupted session file
4. Create new session

### Performance Issues

**Problem**: Slow response times

**Solutions**:
- Use smaller model (tinyllama, phi3:mini)
- Close other applications
- Check system resources (RAM, CPU)
- Ensure Ollama is running locally

---

## Support

For additional help:
- 📖 Check this documentation
- 🐛 [Report issues on GitHub](https://github.com/Nr44suessauer/Ki-whisperer/issues)
- 💬 Ask in discussions

---

**Version 2.0** - November 2025
