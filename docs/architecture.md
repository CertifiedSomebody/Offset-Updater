# Offset Updater — Architecture Overview

This document explains the internal architecture, module interactions, and
data flow of the Offset Updater project.

---

## 📂 Project Structure

offset-updater/
│
├── offset_updater/
│ ├── init.py
│ ├── dump_parser.py
│ ├── source_scanner.py
│ ├── offset_analyzer.py
│ ├── generators.py
│ ├── reporter.py
│ ├── utils.py
│ └── constants.py
│
├── cli/
│ └── main.py
│
└── tests/


---

## 🔧 Module Responsibilities

### **1. dump_parser.py**
Extracts symbol/function names and offsets from:
- IL2CPP dumps
- JSON dumps (if supported)
- Custom text exports

**Input:** dump file path  
**Output:** `{ function_name: offset }`

---

### **2. source_scanner.py**
Recursively scans a source-code directory for:
- `.cpp`
- `.h`

Provides the list of files that contain existing offset definitions and hooks.

**Input:** path to project src  
**Output:** list of file paths

---

### **3. offset_analyzer.py**
Compares parsed dump offsets with existing offsets collected from the source.

**Input:** parsed dump offsets + existing code offsets  
**Output:** list/dict of changes to apply:
{
"FunctionName": ("old_offset", "new_offset"),
...
}


---

### **4. generators.py**
Produces updated output formats, such as:
- Updated C++ headers (`#define FUNCTION 0xOFFSET`)
- JSON file output for external tools

**Input:** changes dict  
**Output:** text or dict, later saved by CLI

---

### **5. reporter.py**
Creates human-readable change summaries.

Example:
FunctionA: 0x11111 → 0x22222

NewFunction: NEW → 0xAAAAA


**Input:** changes dict  
**Output:** formatted text

---

### **6. utils.py**
Contains shared helper functions such as:
- file reading
- formatting helpers
- offset normalization

---

### **7. constants.py**
Stores constant values, patterns, and regex definitions used across modules.

---

## 🚀 Data Flow Diagram

      +-----------------------+
      |       CLI (main.py)   |
      +-----------+-----------+
                  |
                  v
      +-----------------------+
      |     DumpParser        |
      | (parse dump offsets)  |
      +-----------+-----------+
                  |
                  v
      +-----------------------+
      |   SourceScanner       |
      | (find code files)     |
      +-----------+-----------+
                  |
                  v
      +-----------------------+
      | load_existing_offsets |
      | (extract #defines)    |
      +-----------+-----------+
                  |
                  v
      +-----------------------+
      |   OffsetAnalyzer      |
      | (compare changes)     |
      +-----------+-----------+
                  |
      +-----------v-----------+
      |      Reporter         |
      +-----------+-----------+
                  |
                  v
      +-----------------------+
      |     Generators        |
      | (produce output)      |
      +-----------------------+

---

## 🧱 Architectural Goals

- Modularity  
- Easy unit testing  
- Extendable for new dump formats  
- Maintainable for future contributors  
- Clear separation between CLI and core logic

---

## 🔮 Future Direction

- Add GUI front-end  
- Add IL2CPP metadata scanner  
- Add automated hooking generator  
- Integrate with IDA/Frida scripts  

---

