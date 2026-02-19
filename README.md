<img width="804" height="249" alt="bnr" src="https://github.com/user-attachments/assets/63d98de7-416e-493c-876b-f76d1ee8599b" />

# 🎹 nanoMIDIPlayerPlus

**nanoMIDIPlayerPlus** is a heavily modified fork of the original [nanoMIDIPlayer](https://github.com/NotHammer043/nanoMIDIPlayer).

This project focuses on expanding functionality, improving performance, refining usability, and introducing new systems while keeping compatibility with core concepts from the original project.

Huge credits to **NotHammer043** and all contributors of the original nanoMIDIPlayer for creating the foundation this project builds upon.

---

## 🚀 Features

### ⭐ Core Features (from original project)
- MIDI → QWERTY simulation
- MIDI → Output device support
- MIDI INPUT to QWERTY
- Velocity & Sustain support
- Full 88 key support
- Drums support
- Modifiable keymaps
- Cross-platform (Windows / Linux / macOS)
- No time drift

---

### 🔥 nanoMIDIPlayerPlus Improvements

> Features below include current improvements and planned additions for the Plus version.

- ⚡ Performance optimizations for smoother playback
- 🧠 Improved MIDI processing system
- 🐧 Enhanced Linux compatibility & backend adjustments
- 🔧 Internal engine refactors for easier expansion
- 🎹 Better event handling and timing precision
- 🧩 Modular architecture improvements
- 🧪 Experimental new MIDI utilities (beta systems)
- 🎛️ Expanded customization options
- 🔄 Improved internal stability and reliability
- 🆕 Future UI and workflow improvements (WIP)

---

## 📸 Showcase

🚧 **Coming Soon**

Screenshots and demonstrations will be added after upcoming updates.

---

## 🛠️ Setup

1. Download the latest release (when available)
2. Launch the application
3. Select a MIDI file
4. Focus your target piano/app
5. Press **PLAY**

---

## ⚠️ About This Fork

This repository is a **fork** of the original nanoMIDIPlayer project.

While many internal systems have been modified or rewritten, this project still uses ideas and components from the original implementation.

If you're looking for the original project, visit:

➡️ https://github.com/NotHammer043/nanoMIDIPlayer

---

## 🛠️ Building  
### 🔧 Requirements  
- [VS BuildTools C++](https://visualstudio.microsoft.com/visual-cpp-build-tools/) (Optional)
- [Python](https://www.python.org/)  

#### 1. Clone The Repository  
```bash
git clone https://github.com/NotHammer043/nanoMIDIPlayer.git
cd nanoMIDIPlayer
```

#### 2. Install Dependencies  
```bash
pip install -r requirements.txt
```
```bash
# For Linux (Bash Shell)
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
# For Linux (Fish Shell)
python -m venv venv && source venv/bin/activate.fish && pip install -r requirements.txt
```
  
#### 3. Build
```bash
build.bat
```
```python
# For macOS
./build-mac.sh
```
```python
# For Linux
./build-mac.sh
```

#### 🐞 Debugging Mode  
```bash
nanoMIDIPlayer.exe --debug
```