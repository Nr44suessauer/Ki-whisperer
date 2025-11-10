# A1-Terminal

**Professional Chat Client for Local AI Models via Ollama**

Version 2.0 - Modular Architecture

---

## 🚀 Fully Automatic Installation

### One Command - Everything Installed!

**Windows:**
```powershell
# Run as Administrator (Right-click -> "Run as Administrator")
.\scripts\install.bat
```

**Linux/macOS:**
```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

### What Gets Installed?

The script installs **fully automatically**:
- ✅ Python 3.8+ (if not present)
- ✅ All Python packages (CustomTkinter, ollama, PyYAML, requests, pyperclip)
- ✅ **Ollama** (completely automatic, **no manual installation needed!**)
- ✅ Test model **tinyllama:1.1b** (~600 MB, ready to use immediately)

### Start After Installation

```powershell
.\start.bat          # Windows (from main folder)
```

**Done!** The app starts with a working test model. 🎉

---

## ✨ Features

- 🎯 **Modular Architecture** - Clean code structure
- 🚀 **Real-time Streaming** - Live display of AI responses
- 💾 **Session Management** - Save & load chats
- 🎨 **Fully Customizable** - Colors, fonts, layout
- 📊 **Model Management** - Download & categorization of models
- 🔄 **100% Offline** - All models run locally, no cloud
- ⚡ **Stop Function** - Generation can be interrupted at any time
- 📝 **BIAS System** - System prompts for AI control

---

## 📁 Project Structure

The project is now **modularly** structured:

```
A1-Terminal/
├── start.bat                   # Windows: Quick start
├── README.md                   # This file
├── DOCUMENTATION_EN.md         # Complete technical documentation
│
├── scripts/                    # Installation scripts
│   ├── install.bat             # Windows installation
│   └── install.sh              # Linux/macOS installation
│
└── a1_terminal_modular/        # Main application
    ├── main.py                 # Entry point
    ├── requirements.txt        # Python dependencies
    ├── a1_terminal_config.yaml # Configuration
    │
    ├── sessions/               # Saved chat sessions
    │
    └── src/                    # Source code
        ├── core/               # Core logic
        │   ├── a1_terminal.py      # Main class
        │   └── ollama_manager.py   # Ollama API client
        │
        └── ui/                 # UI components
            ├── chat_bubble.py
            ├── session_card.py
            ├── model_selector.py
            └── ...
```

---

## 📖 Documentation

**[Complete Technical Documentation (DOCUMENTATION_EN.md)](./DOCUMENTATION_EN.md)**

Contains:
- ⚙️ Detailed architecture description
- 📡 API reference & Ollama integration
- 🎨 Configuration options
- 👨‍💻 Developer guide
- 🐛 Troubleshooting & problem solving

---

## 💡 Recommended Models

After installation, **tinyllama:1.1b** is already installed. You can download more models in the "Models" tab of the app:

| Model | Size | RAM | Description |
|--------|-------|-----|--------------|
| **tinyllama:1.1b** | 600 MB | 4 GB | ✅ Already installed! Very fast |
| phi3:mini | 2 GB | 8 GB | Good quality, balanced |
| llama3.2:3b | 2 GB | 8 GB | Latest version, very good |
| mistral:7b | 4 GB | 12 GB | High quality |
| codellama:7b | 4 GB | 12 GB | Specialized for code |

---

## 🎮 GPU/CUDA Support (Optional)

**A1-Terminal automatically uses your NVIDIA GPU if available - no code changes needed!**

### Benefits with CUDA:
- ⚡ **Much faster inference** - Models respond 5-10x faster
- 🚀 **Larger models** - Run 13B+ models smoothly
- 💾 **Less RAM usage** - GPU VRAM is used instead of system RAM

### Setup:

1. **Install NVIDIA GPU drivers** from [nvidia.com/drivers](https://www.nvidia.com/drivers)
2. **That's it!** Ollama automatically detects and uses your GPU

### Verify GPU usage:
```powershell
# Check if GPU is being used (run while model is active)
nvidia-smi
```

**No configuration needed in A1-Terminal** - Ollama handles everything automatically! 🎉

---

## 🔧 System Requirements

**Minimum:**
- Windows 10/11, Linux (Ubuntu 20.04+), macOS 11+
- 8 GB RAM
- 10 GB free storage
- Internet connection (only for installation)

**Recommended:**
- 16 GB RAM (for larger models)
- 50 GB free storage (for multiple models)

---

## 🚀 Quick Start

### Automatic Installation (Recommended)

**Windows:**
```powershell
# Run as Administrator (Right-click -> "Run as Administrator")
.\scripts\install.bat
```

**Linux/macOS:**
```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

The installation script automatically installs:
- ✅ Python 3.8+ (if not present)
- ✅ All Python packages (CustomTkinter, ollama, etc.)
- ✅ Ollama
- ✅ Optional: Test model (tinyllama, phi3, llama3.2)

### Manual Installation

<details>
<summary>Click to show manual installation</summary>

#### 1. Install Ollama

Visit [ollama.ai](https://ollama.ai) and install Ollama.

#### 2. Install Dependencies

```powershell
pip install -r a1_terminal_modular\requirements.txt
```

#### 3. Start

```powershell
.\start.bat
```

</details>

### After Installation

**Windows:**
```powershell
.\start.bat
```

**Linux/macOS:**
```bash
./start.bat
```

---

## 🤝 Support

For problems see:
- 📖 [Troubleshooting in the documentation](./DOCUMENTATION_EN.md#troubleshooting)
- 🐛 [GitHub Issues](https://github.com/Nr44suessauer/A1-Terminal/issues)

---

**Have fun with A1-Terminal! 🚀**

*Completely automatic installation • No manual configuration • Ready to use immediately*
