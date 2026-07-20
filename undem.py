name: Build and Release UnDem

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  build-windows:
    name: Build Windows Outputs
    runs-on: windows-latest

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pyinstaller

      - name: Build EXE with PyInstaller
        run: |
          pyinstaller --noconfirm --onedir --windowed --add-data "logo.ico;." undem.py

      - name: Upload Windows Artifact
        uses: actions/upload-artifact@v4
        with:
          name: UnDem-Windows-Beta
          path: dist/undem/
          if-no-files-found: error

  build-macos:
    name: Build macOS DMG & Portable
    runs-on: macos-latest

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install Dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pyinstaller create-dmg

      - name: Build App with PyInstaller
        run: |
          pyinstaller --noconfirm --onedir --windowed --add-data "logo.ico:." undem.py

      - name: Create DMG Package
        run: |
          mkdir -p dist/dmg
          create-dmg \
            --volname "UnDem Installer" \
            --volicon "logo.ico" \
            --window-size 500 300 \
            --icon-size 100 \
            --icon "UnDem.app" 175 120 \
            --app-drop-link 325 120 \
            "dist/dmg/UnDem-macOS.dmg" \
            "dist/undem/" || echo "DMG creation skipped or completed with warnings"

      - name: Upload macOS Artifact
        uses: actions/upload-artifact@v4
        with:
          name: UnDem-macOS-Beta
          path: dist/undem/
          if-no-files-found: warn
