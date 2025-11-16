# Offset Updater — Project Roadmap

This roadmap outlines upcoming features, improvements, and long-term goals
for the Offset Updater project.

---

## ✅ Completed (Phase 1)

- Project folder structure
- Full module architecture
- CLI interface (`main.py`)
- Offset parsing from dumps
- Source code scanning system
- Offset comparison engine
- Output generators for C++ & JSON
- Automatic reporting
- Complete test suite

---

## 🚧 Phase 2 — Core Enhancements (In Progress)

### 1. Add More Dump Format Support
- [ ] IL2CPP Scaffolding dumps
- [ ] UnityEditor generated dumps
- [ ] SymbolMap `.txt` variants
- [ ] Custom modding community formats

### 2. Improve Offset Detection Accuracy
- [ ] Add regex-based symbol extraction
- [ ] Auto-detect function signatures
- [ ] Detect renames and aliasing

### 3. Smarter Existing Offset Extraction
- [ ] Scan for `HOOK("Func")` patterns
- [ ] Extract offsets from inline functions
- [ ] Support `constexpr`, `static` variables

---

## 🚀 Phase 3 — Developer Tools Expansion

### CLI Upgrade
- [ ] Add colored terminal output
- [ ] Add verbose/debug logging
- [ ] Add `--dry-run` mode
- [ ] Packaging for `pip install offset-updater`

### GUI Version (Optional)
- [ ] Qt or Tkinter based UI  
- [ ] Drag & drop dump and project folder  
- [ ] Live change summary  
- [ ] One-click patch generation  

---

## 🌐 Phase 4 — Integration Tools

### IDE Plugins
- [ ] VSCode Extension: Auto-update offsets  
- [ ] CLion helper plugin  

### Exporters
- [ ] Output Il2CppInspector patch format  
- [ ] Generate IDA Python scripts  
- [ ] Generate Unity mod templates  

---

## 🛰 Phase 5 — Advanced Features

- [ ] Auto-detect obfuscated classes  
- [ ] Pattern scanning (AoB) for offsets  
- [ ] Memory scanning for live games  
- [ ] Multi-offset delta analysis  
- [ ] Version tracking system  
- [ ] Collaboration sync on multiple devices  

---

## 🏁 Long-Term Vision

To build the most reliable, universal, lightweight
**offset updating automation tool for Unity/IL2CPP games**, usable by:

- mod developers  
- reverse engineers  
- game exploit researchers  
- automated build pipelines  

---

