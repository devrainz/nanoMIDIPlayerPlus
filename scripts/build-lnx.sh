#!/bin/bash
set -e

echo "=> Cleaning up previous builds..."
rm -rf build dist venv-lnx *.spec __pycache__

echo "=> Creating virtual environment..."
python3 -m venv venv-lnx
source venv-lnx/bin/activate

echo "=> Installing dependencies..."
pip install --upgrade pip pyinstaller
pip install -r requirements.txt

echo "=> Running PyInstaller..."

python -m PyInstaller \
    --onedir \
    --noconsole \
    --noconfirm \
    --name nanoMIDIPlayer \
    --paths "$(pwd)" \
    --collect-all ui \
    --collect-all modules \
    --collect-all customtkinter \
    --collect-submodules PIL \
    --hidden-import=mido.backends.rtmidi \
    --hidden-import=PIL._tkinter_finder \
    --hidden-import=PIL._imagingtk \
    --add-data "assets:assets" \
    main.py

echo "=> Build finished."

echo "=> Checking if ui/customTheme was bundled..."
find dist -name "customTheme*"

echo "=> Packaging..."
cd dist
tar -czvf nanoMIDIPlayer.tar.gz nanoMIDIPlayer
cd ..

echo "✅ DONE."
