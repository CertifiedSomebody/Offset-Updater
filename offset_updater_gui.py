#!/usr/bin/env python3
"""
offset_tool_pro.py
Pro Offset Updater + Dump Inspector + Offline AI Assistant
- Tab 1: Offset Checker (read-only) -> generates offset_changes.txt
- Tab 2: Dump Inspector (search/filter/export, copy HOOK/LOGD)
- Tab 3: Offline AI Assistant (fuzzy suggestions + one-click generate HOOK/LOGD)
No online calls. Uses difflib for fuzzy matching.
"""

import re
import os
import csv
import difflib
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext

HEX_RE = r'0x[0-9A-Fa-f]+'

# ---------------------------
# Parsing dump.cs (robust)
# ---------------------------
def parse_dump(dump_path):
    """
    Returns mapping: {func_name: {"offset": "0x...", "rva": "0x...", "line": raw_line}}
    Handles lines like:
  // RVA: 0x1386024 Offset: 0x1382024 VA: 0x1386024
  public void AddCommonKey(int key, string location) { }
    and inline patterns.
    """
    mapping = {}
    last_offset = None
    last_rva = None
    with open(dump_path, 'r', encoding='utf-8', errors='ignore') as f:
        for raw in f:
            line = raw.rstrip('\n')
            s = line.strip()
            if not s:
                continue

            # Look for RVA/Offset comment lines
            if ('RVA:' in s) or ('Offset:' in s) or ('VA:' in s):
                m_off = re.search(r'Offset:\s*(0x[0-9A-Fa-f]+)', s)
                m_rva = re.search(r'RVA:\s*(0x[0-9A-Fa-f]+)', s)
                last_offset = m_off.group(1).upper() if m_off else None
                last_rva = m_rva.group(1).upper() if m_rva else None
                continue

            # Match method signatures (common C# decompiled style)
            m_func = re.match(r'(?:public|private|protected|internal|static|\s)+[\w<>\[\]]+\s+(?P<name>[A-Za-z_][A-Za-z0-9_:<>]*)\s*\(.*\)', s)
            if m_func:
                name = m_func.group('name').strip()
                if last_offset or last_rva:
                    mapping[name] = {"offset": last_offset, "rva": last_rva, "line": line}
                last_offset = last_rva = None
                continue

            # Inline pattern: method(...) ... 0x123ABC
            m_inline = re.search(r'(?P<name>[A-Za-z_][A-Za-z0-9_:<>]*)\s*\([^)]*\).*?(?P<addr>' + HEX_RE + r')', s)
            if m_inline:
                mapping[m_inline.group('name')] = {"offset": m_inline.group('addr').upper(), "rva": None, "line": line}
                continue

            # Alternate: 0xHEX : Name
            m_alt = re.search(r'(0x[0-9A-Fa-f]+)\s*[:\-]\s*([A-Za-z_][A-Za-z0-9_:<>]*)', s)
            if m_alt:
                mapping[m_alt.group(2)] = {"offset": m_alt.group(1).upper(), "rva": None, "line": line}
                continue

    return mapping


# ---------------------------
# Compare offsets in main.cpp
# ---------------------------
def compare_offsets(src_path, mapping):
    """Find all LOGD/HOOK lines in source that differ from dump mapping (read-only)."""
    with open(src_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()

    results = []
    missing = []
    used_dump = set()

    def find_best_match(func):
        func_low = func.lower()
        for key in mapping:
            if key.lower() == func_low or key.split("::")[-1].lower() == func_low:
                return mapping[key], key
        return None, None

    # patterns
    pat_logd = re.compile(r'Method:\s*([A-Za-z_][A-Za-z0-9_:]*)\s*,\s*Offset:\s*(' + HEX_RE + r')', re.IGNORECASE)
    pat_hook = re.compile(r'HOOK\([^,]+,\s*str2Offset\s*\(\s*OBFUSCATE\(\s*"?(' + HEX_RE + r')"?\s*\)\s*\)\s*,\s*([A-Za-z_:][A-Za-z0-9_:]*)', re.IGNORECASE)

    for i, line in enumerate(lines):
        m = pat_logd.search(line)
        if m:
            func, old_off = m.group(1), m.group(2).upper()
            found, key = find_best_match(func)
            if found and found.get("offset") and found["offset"].upper() != old_off:
                results.append({"type": "LOGD", "name": key or func, "old": old_off, "new": found["offset"].upper(), "src_line": i+1})
                used_dump.add(key or func)
            elif not found:
                missing.append(func)
            continue

        m2 = pat_hook.search(line)
        if m2:
            old_off, func = m2.group(1).upper(), m2.group(2)
            found, key = find_best_match(func)
            if found and found.get("offset") and found["offset"].upper() != old_off:
                results.append({"type": "HOOK", "name": key or func, "old": old_off, "new": found["offset"].upper(), "src_line": i+1})
                used_dump.add(key or func)
            elif not found:
                missing.append(func)
            continue

    # create manual list file
    manual_file = os.path.join(os.path.dirname(src_path), "offset_changes.txt")
    with open(manual_file, "w", encoding="utf-8") as mf:
        mf.write("Offset Checker - Manual Patch List\n")
        mf.write("="*48 + "\n\n")
        if results:
            for r in results:
                mf.write(f"{r['type']} | {r['name']} | line:{r['src_line']} | old: {r['old']} -> new: {r['new']}\n")
        else:
            mf.write("✅ All offsets appear up to date!\n")

        if missing:
            mf.write("\n# Missing (not found in dump):\n")
            for m in sorted(set(missing)):
                mf.write(m + "\n")

    return {
        "manual": manual_file,
        "changes": results,
        "missing": sorted(set(missing)),
        "unused_dump": [k for k in mapping if k not in used_dump]
    }


# ---------------------------
# Dump Inspector helpers
# ---------------------------
def generate_hook_line(offset, func_name, orig_name=None):
    orig_name = orig_name or f"orig_{func_name}"
    return f'HOOK("libil2cpp.so", str2Offset(OBFUSCATE("{offset}")), {func_name}, {orig_name});'

def generate_logd_line(offset, func_name):
    return f'LOGD(OBFUSCATE("Method: {func_name}, Offset: {offset}"));'


# ---------------------------
# Offline AI Assistant (fuzzy matches)
# ---------------------------
def fuzzy_suggest(func_name, mapping, topn=6):
    """Return list of (candidate_name, offset, score) sorted by score desc."""
    names = list(mapping.keys())
    # Use difflib get_close_matches for quick filtering, then ratio
    close = difflib.get_close_matches(func_name, names, n=topn, cutoff=0.1)
    scored = []
    for c in close:
        score = difflib.SequenceMatcher(None, func_name.lower(), c.lower()).ratio()
        scored.append((c, mapping[c].get("offset"), round(score, 3)))
    # Also include tokens-based contains matches (class::method or method substring)
    for c in names:
        if func_name.lower() in c.lower() and c not in [x[0] for x in scored]:
            score = difflib.SequenceMatcher(None, func_name.lower(), c.lower()).ratio()
            scored.append((c, mapping[c].get("offset"), round(score, 3)))
    scored.sort(key=lambda x: x[2], reverse=True)
    return scored[:topn]


# ---------------------------
# GUI
# ---------------------------
class OffsetToolPro:
    def __init__(self, root):
        self.root = root
        root.title("Offset Updater Pro — Offline (Inspector + AI)")
        root.geometry("1100x740")

        # Notebook for tabs
        self.nb = ttk.Notebook(root)
        self.nb.pack(fill="both", expand=True)

        # Tab 1: Checker
        self.tab_checker = ttk.Frame(self.nb)
        self.nb.add(self.tab_checker, text="Offset Checker")

        # Tab 2: Inspector
        self.tab_inspector = ttk.Frame(self.nb)
        self.nb.add(self.tab_inspector, text="Dump Inspector")

        # Tab 3: AI Assistant
        self.tab_ai = ttk.Frame(self.nb)
        self.nb.add(self.tab_ai, text="AI Assistant (offline)")

        self._build_checker_tab()
        self._build_inspector_tab()
        self._build_ai_tab()

        # shared data
        self.mapping = {}
        self.dump_path = None
        self.src_path = None

    # -------------------------
    # Build Checker Tab UI
    # -------------------------
    def _build_checker_tab(self):
        frame = self.tab_checker
        top = ttk.Frame(frame)
        top.pack(fill='x', padx=8, pady=8)

        ttk.Label(top, text="Dump (dump.cs):").grid(row=0, column=0, sticky='w')
        self.checker_dump_entry = ttk.Entry(top, width=80)
        self.checker_dump_entry.grid(row=0, column=1, padx=6)
        ttk.Button(top, text="Browse", command=lambda: self._browse_file(self.checker_dump_entry, mode='dump')).grid(row=0, column=2)

        ttk.Label(top, text="Source (main.cpp):").grid(row=1, column=0, sticky='w')
        self.checker_src_entry = ttk.Entry(top, width=80)
        self.checker_src_entry.grid(row=1, column=1, padx=6)
        ttk.Button(top, text="Browse", command=lambda: self._browse_file(self.checker_src_entry, mode='src')).grid(row=1, column=2)

        ttk.Button(frame, text="Check Offsets (read-only)", command=self.run_check, width=24).pack(pady=8)

        cols = ("type", "name", "old", "new", "line")
        self.checker_tree = ttk.Treeview(frame, columns=cols, show='headings', height=14)
        for c in cols:
            self.checker_tree.heading(c, text=c.title())
            self.checker_tree.column(c, width=160 if c!='type' else 90, anchor='center')
        self.checker_tree.pack(fill='both', padx=8, pady=6, expand=False)

        # report area
        ttk.Label(frame, text="Report:").pack(anchor='w', padx=8)
        self.checker_report = scrolledtext.ScrolledText(frame, height=10)
        self.checker_report.pack(fill='both', padx=8, pady=6, expand=True)

    # -------------------------
    # Build Inspector Tab UI
    # -------------------------
    def _build_inspector_tab(self):
        frame = self.tab_inspector
        top = ttk.Frame(frame)
        top.pack(fill='x', padx=8, pady=6)

        ttk.Label(top, text="Dump (dump.cs):").grid(row=0, column=0, sticky='w')
        self.inspect_dump_entry = ttk.Entry(top, width=72)
        self.inspect_dump_entry.grid(row=0, column=1, padx=6)
        ttk.Button(top, text="Browse", command=lambda: self._browse_file(self.inspect_dump_entry, mode='dump')).grid(row=0, column=2)

        ttk.Label(top, text="Search:").grid(row=1, column=0, sticky='w', pady=6)
        self.inspect_search = ttk.Entry(top, width=50)
        self.inspect_search.grid(row=1, column=1, sticky='w')
        ttk.Button(top, text="Find", command=self.run_inspector_search).grid(row=1, column=2, sticky='w')

        # filter checkboxes
        self.chk_methods = tk.BooleanVar(value=True)
        ttk.Checkbutton(top, text="Methods", variable=self.chk_methods).grid(row=2, column=1, sticky='w')

        # table
        cols = ("name", "offset", "rva", "sample")
        self.inspect_tree = ttk.Treeview(frame, columns=cols, show='headings', height=18)
        for c in cols:
            self.inspect_tree.heading(c, text=c.title())
            self.inspect_tree.column(c, width=220 if c=='name' else 130, anchor='w')
        self.inspect_tree.pack(fill='both', padx=8, pady=6, expand=True)
        self.inspect_tree.bind("<Double-1>", self._inspect_row_copy)

        # action buttons
        acts = ttk.Frame(frame)
        acts.pack(fill='x', padx=8, pady=6)
        ttk.Button(acts, text="Copy HOOK line", command=self.copy_selected_hook).pack(side='left', padx=6)
        ttk.Button(acts, text="Copy LOGD line", command=self.copy_selected_logd).pack(side='left', padx=6)
        ttk.Button(acts, text="Export CSV", command=self.export_inspector_csv).pack(side='left', padx=6)
        ttk.Button(acts, text="Load All Dump Entries", command=self.load_dump_into_inspector).pack(side='left', padx=6)

    # -------------------------
    # Build AI Tab UI
    # -------------------------
    def _build_ai_tab(self):
        frame = self.tab_ai
        top = ttk.Frame(frame)
        top.pack(fill='x', padx=8, pady=8)

        ttk.Label(top, text="Dump (dump.cs):").grid(row=0, column=0, sticky='w')
        self.ai_dump_entry = ttk.Entry(top, width=72)
        self.ai_dump_entry.grid(row=0, column=1, padx=6)
        ttk.Button(top, text="Browse", command=lambda: self._browse_file(self.ai_dump_entry, mode='dump')).grid(row=0, column=2)

        ttk.Label(top, text="Enter missing function name:").grid(row=1, column=0, sticky='w', pady=6)
        self.ai_query = ttk.Entry(top, width=60)
        self.ai_query.grid(row=1, column=1, sticky='w')

        ttk.Button(top, text="Suggest Matches (offline)", command=self.run_ai_suggest).grid(row=1, column=2, padx=6)

        # suggestion list
        self.ai_suggestions = ttk.Treeview(frame, columns=("cand","offset","score"), show='headings', height=8)
        for c in ("cand","offset","score"):
            self.ai_suggestions.heading(c, text=c.title())
            self.ai_suggestions.column(c, width=300 if c=='cand' else 120, anchor='w')
        self.ai_suggestions.pack(fill='both', padx=8, pady=8)
        self.ai_suggestions.bind("<Double-1>", self.ai_copy_choice)

        # generate buttons
        gen_frame = ttk.Frame(frame)
        gen_frame.pack(fill='x', padx=8, pady=6)
        ttk.Button(gen_frame, text="Generate HOOK for selected", command=self.ai_generate_hook).pack(side='left', padx=6)
        ttk.Button(gen_frame, text="Generate LOGD for selected", command=self.ai_generate_logd).pack(side='left', padx=6)

        # output area
        ttk.Label(frame, text="Generated lines (click to copy):").pack(anchor='w', padx=8)
        self.ai_output = scrolledtext.ScrolledText(frame, height=8)
        self.ai_output.pack(fill='both', padx=8, pady=6, expand=True)
        self.ai_output.bind("<Double-1>", self.ai_output_copy)

    # -------------------------
    # Shared helpers
    # -------------------------
    def _browse_file(self, entry, mode='dump'):
        path = filedialog.askopenfilename(filetypes=[("All files","*.*")])
        if path:
            entry.delete(0, tk.END)
            entry.insert(0, path)
            if mode == 'dump':
                self.dump_path = path
                # pre-parse mapping so all tabs can use it
                try:
                    self.mapping = parse_dump(path)
                except Exception as e:
                    messagebox.showerror("Error parsing dump", str(e))
            elif mode == 'src':
                self.src_path = path

    # -------------------------
    # Checker actions
    # -------------------------
    def run_check(self):
        dump = self.checker_dump_entry.get().strip() or self.dump_path
        src = self.checker_src_entry.get().strip() or self.src_path
        if not dump or not src:
            messagebox.showwarning("Missing files", "Select both dump.cs and main.cpp first.")
            return
        try:
            self.mapping = parse_dump(dump)
            res = compare_offsets(src, self.mapping)
            # show
            for i in self.checker_tree.get_children(): self.checker_tree.delete(i)
            for r in res["changes"]:
                self.checker_tree.insert("", tk.END, values=(r["type"], r["name"], r["old"], r["new"], r.get("src_line")))
            self.checker_report.delete(1.0, tk.END)
            self.checker_report.insert(tk.END, f"Manual patch list: {res['manual']}\n")
            self.checker_report.insert(tk.END, f"Offsets needing change: {len(res['changes'])}\n")
            if res["missing"]:
                self.checker_report.insert(tk.END, f"\nMissing in dump: {len(res['missing'])}\n")
                self.checker_report.insert(tk.END, "\n".join(res['missing']) + "\n")
            messagebox.showinfo("Done", f"Check complete. Manual patch: {res['manual']}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # -------------------------
    # Inspector actions
    # -------------------------
    def load_dump_into_inspector(self):
        dump = self.inspect_dump_entry.get().strip() or self.dump_path
        if not dump:
            messagebox.showwarning("No dump", "Select dump.cs first.")
            return
        try:
            self.mapping = parse_dump(dump)
            self._populate_inspector_tree(self.mapping)
            messagebox.showinfo("Loaded", f"Loaded {len(self.mapping)} entries from dump.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _populate_inspector_tree(self, mapping, filter_text=None):
        for i in self.inspect_tree.get_children(): self.inspect_tree.delete(i)
        keys = sorted(mapping.keys(), key=lambda x: x.lower())
        for k in keys:
            if filter_text:
                if filter_text.lower() not in k.lower(): continue
            v = mapping[k]
            offset = v.get("offset") or ""
            rva = v.get("rva") or ""
            sample = v.get("line") or ""
            self.inspect_tree.insert("", tk.END, values=(k, offset, rva, sample[:80]))

    def run_inspector_search(self):
        term = self.inspect_search.get().strip()
        if not self.mapping:
            dump = self.inspect_dump_entry.get().strip() or self.dump_path
            if not dump:
                messagebox.showwarning("No dump", "Select dump.cs first.")
                return
            self.mapping = parse_dump(dump)
        self._populate_inspector_tree(self.mapping, filter_text=term)

    def _inspect_row_copy(self, event):
        sel = self.inspect_tree.selection()
        if not sel: return
        vals = self.inspect_tree.item(sel[0], 'values')
        func, offset = vals[0], vals[1]
        text = f"{func} -> {offset}"
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Copied", text)

    def copy_selected_hook(self):
        sel = self.inspect_tree.selection()
        if not sel:
            messagebox.showwarning("Select row", "Select an entry in the inspector table.")
            return
        vals = self.inspect_tree.item(sel[0], 'values')
        func, offset = vals[0], vals[1]
        if not offset:
            messagebox.showerror("No offset", "Selected entry has no offset.")
            return
        line = generate_hook_line(offset, func)
        self.root.clipboard_clear()
        self.root.clipboard_append(line)
        messagebox.showinfo("Copied HOOK", line)

    def copy_selected_logd(self):
        sel = self.inspect_tree.selection()
        if not sel:
            messagebox.showwarning("Select row", "Select an entry in the inspector table.")
            return
        vals = self.inspect_tree.item(sel[0], 'values')
        func, offset = vals[0], vals[1]
        if not offset:
            messagebox.showerror("No offset", "Selected entry has no offset.")
            return
        line = generate_logd_line(offset, func)
        self.root.clipboard_clear()
        self.root.clipboard_append(line)
        messagebox.showinfo("Copied LOGD", line)

    def export_inspector_csv(self):
        if not self.mapping:
            messagebox.showwarning("No data", "Load dump entries first.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files","*.csv")])
        if not path: return
        try:
            with open(path, 'w', newline='', encoding='utf-8') as csvf:
                writer = csv.writer(csvf)
                writer.writerow(["Function","Offset","RVA","SampleLine"])
                for k,v in sorted(self.mapping.items(), key=lambda x:x[0].lower()):
                    writer.writerow([k, v.get("offset") or "", v.get("rva") or "", (v.get("line") or "")[:200]])
            messagebox.showinfo("Exported", f"Exported inspector data to {path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # -------------------------
    # AI actions (offline fuzzy)
    # -------------------------
    def run_ai_suggest(self):
        dump = self.ai_dump_entry.get().strip() or self.dump_path
        if not dump:
            messagebox.showwarning("No dump", "Select dump.cs first.")
            return
        self.mapping = parse_dump(dump)
        q = self.ai_query.get().strip()
        if not q:
            messagebox.showwarning("Empty", "Type a function name to search.")
            return
        sugg = fuzzy_suggest(q, self.mapping, topn=12)
        for i in self.ai_suggestions.get_children(): self.ai_suggestions.delete(i)
        for cand, off, score in sugg:
            self.ai_suggestions.insert("", tk.END, values=(cand, off or "", score))

    def ai_copy_choice(self, event):
        sel = self.ai_suggestions.selection()
        if not sel: return
        vals = self.ai_suggestions.item(sel[0], 'values')
        text = f"{vals[0]} -> {vals[1]} (score {vals[2]})"
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Copied", text)

    def ai_generate_hook(self):
        sel = self.ai_suggestions.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a suggestion first.")
            return
        vals = self.ai_suggestions.item(sel[0], 'values')
        cand, off = vals[0], vals[1]
        if not off:
            messagebox.showerror("No offset", "Selected candidate has no offset.")
            return
        line = generate_hook_line(off, cand)
        self.ai_output.insert(tk.END, line + "\n")
        self.root.clipboard_clear()
        self.root.clipboard_append(line)
        messagebox.showinfo("Generated & Copied", line)

    def ai_generate_logd(self):
        sel = self.ai_suggestions.selection()
        if not sel:
            messagebox.showwarning("Select", "Select a suggestion first.")
            return
        vals = self.ai_suggestions.item(sel[0], 'values')
        cand, off = vals[0], vals[1]
        if not off:
            messagebox.showerror("No offset", "Selected candidate has no offset.")
            return
        line = generate_logd_line(off, cand)
        self.ai_output.insert(tk.END, line + "\n")
        self.root.clipboard_clear()
        self.root.clipboard_append(line)
        messagebox.showinfo("Generated & Copied", line)

    def ai_output_copy(self, event):
        text = self.ai_output.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("No text", "No generated lines to copy.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Copied", "All generated lines copied to clipboard.")

# ---------------------------
# Run app
# ---------------------------
if __name__ == '__main__':
    root = tk.Tk()
    app = OffsetToolPro(root)
    root.mainloop()
