# 🛠️ Offset Updater

Offset Updater is a powerful tool designed for analyzing memory offsets within dump files and C++ source code. It automates the process of identifying changes, generating necessary patch snippets, and producing detailed reports. It features both a Command Line Interface (CLI) and a user-friendly GUI built with PyQt6.

## ✨ Features

* Parse dump files and C++ source files for offset analysis.
* Analyze offsets to detect discrepancies and automatically generate fix code/patch snippets.
* Generate detailed, easy-to-read text reports of the analysis.
* PyQt6 GUI for intuitive file selection, progress visualization, and quick operation.
* Customizable settings, including an **API key input for Google Gemini integration** to enhance analysis capabilities.

## ⬇️ Installation

### Prerequisites

* Python 3.10+

### Steps

1. Clone the repository:

```bash
git clone <your-repo-url>
cd offset_updater
```

2. Create a virtual environment and install dependencies in one command:

**Linux/macOS:**

```bash
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```

**Windows (Command Prompt/PowerShell):**

```bash
python -m venv venv && .\venv\Scripts\activate && pip install -r requirements.txt
```

## 🚀 Usage

### CLI

Run the tool by specifying the paths to your dump and source files:

```bash
python cli/main.py --dump path/to/dump.txt --source path/to/source.cpp
```

### GUI

Launch the graphical interface:

```bash
python -m gui.gui_main
```

* Open the Settings menu to enter your Google Gemini API key.
* Use the interface to load your dump and source files.
* Run the analysis to generate patch snippets and a full report.

## 📁 Directory Structure

```
offset_updater/
├── cli/                 # Command Line Interface scripts
├── gui/                 # PyQt6 Graphical User Interface scripts
├── offset_updater/      # Core parsing and analysis modules
├── tests/               # Unit and integration tests
├── docs/                # Documentation (if any)
├── README.md            # This file
└── requirements.txt     # Project dependencies
```

## ⚙️ Dependencies

The project relies on the following packages (specified in `requirements.txt`):

* PyQt6 >= 6.5.0
* requests >= 2.30.0

## 📜 License

This project is licensed under the MIT License.
