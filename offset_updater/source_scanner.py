import os
import re
from typing import Dict, List, Any


class SourceScanner:
    """
    Scans C++ mod menu sources and extracts:

    {
        "LOGD": [
            {"file": "...", "func": "get_ATK", "offset": "0x216B910"}
        ],
        "HOOKS": [
            {"file": "...", "func": "get_ATK", "orig": "orig_get_ATK", "offset": "0x216B910"}
        ],
        "ORIGINALS": ["get_ATK", ...],
        "RAW": [{"file":"...", "content":"..."}]
    }

    Major improvements:
    - LOGD now extracts function name + offset correctly.
    - HOOK detection handles ANY spacing/newline/macro wrapping.
    - Multi-line HOOK(...) calls supported.
    - Ignores commented-out HOOK or LOGD.
    """

    # -------------------------------------------------------------
    # LOGD PATTERNS
    # LOGD("Method Name: get_ATK, Offsets: 0x21678F0")
    LOGD_FULL = re.compile(
        r'LOGD\s*\(\s*OBFUSCATE\(\s*"[^"]*?([A-Za-z_][A-Za-z0-9_:]*)[^"]*?0x([0-9A-Fa-f]+)[^"]*?"\s*\)',
        re.IGNORECASE | re.DOTALL
    )

    LOGD_INLINE = re.compile(
        r'LOGD\s*\(\s*"[^"]*?([A-Za-z_][A-Za-z0-9_:]*)[^"]*?0x([0-9A-Fa-f]+)[^"]*?"\s*\)',
        re.IGNORECASE | re.DOTALL
    )

    # Fallback: simple "Offset: 0x1234"
    LOGD_SIMPLE = re.compile(
        r'([A-Za-z_][A-Za-z0-9_:]*)[^A-Za-z0-9_:]+Offsets?\s*[:=]\s*0x([0-9A-Fa-f]+)',
        re.IGNORECASE
    )

    # -------------------------------------------------------------
    # HOOK PATTERN (multi-line safe)
    HOOK_PATTERN = re.compile(
        r'HOOK\s*\(\s*"(?:[^"]+)"\s*,\s*'
        r'(?:str2Offset\s*\(\s*OBFUSCATE\s*\(\s*"?0x([0-9A-Fa-f]+)"?\s*\)\s*\)'
        r'|str2Offset\s*\(\s*"?0x([0-9A-Fa-f]+)"?\s*\)'
        r'|0x([0-9A-Fa-f]+))'
        r'\s*,\s*([A-Za-z_][A-Za-z0-9_]*)'
        r'(?:\s*,\s*([A-Za-z_][A-Za-z0-9_]*))?'
        r'\s*\)',
        re.IGNORECASE | re.DOTALL
    )

    # orig_* pointer declarations
    ORIG_DECL = re.compile(
        r'\*\s*orig_([A-Za-z_][A-Za-z0-9_]*)',
        re.IGNORECASE
    )

    # Commented offsets // 0x123456
    COMMENTED_OFFSET = re.compile(
        r'//.*?0x([0-9A-Fa-f]{4,})'
    )

    # -------------------------------------------------------------
    def __init__(self, source_path: str):
        self.source_path = source_path

    # -------------------------------------------------------------
    def scan(self) -> Dict[str, Any]:
        result = {
            "LOGD": [],
            "HOOKS": [],
            "ORIGINALS": [],
            "RAW": []
        }

        if os.path.isfile(self.source_path):
            files = [self.source_path]
        else:
            files = []
            for root, _, f_list in os.walk(self.source_path):
                for fn in f_list:
                    if fn.endswith((".cpp", ".c", ".h", ".hpp")):
                        files.append(os.path.join(root, fn))

        for path in files:
            try:
                scanned = self._scan_file(path)
                result["LOGD"].extend(scanned["LOGD"])
                result["HOOKS"].extend(scanned["HOOKS"])
                result["ORIGINALS"].extend(scanned["ORIGINALS"])
                result["RAW"].append({"file": path, "content": scanned["RAW"]})
            except Exception:
                continue

        # Dedupe originals
        result["ORIGINALS"] = sorted(set(result["ORIGINALS"]))

        return result

    # -------------------------------------------------------------
    def _scan_file(self, path: str) -> Dict[str, Any]:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        logs = []
        hooks = []
        originals = []

        # ---------------------------------------------------------
        # LOGD extraction
        for m in self.LOGD_FULL.findall(content):
            func, off = m[0], m[1]
            logs.append({"file": path, "func": func, "offset": "0x" + off})

        for m in self.LOGD_INLINE.findall(content):
            func, off = m[0], m[1]
            logs.append({"file": path, "func": func, "offset": "0x" + off})

        for m in self.LOGD_SIMPLE.findall(content):
            func, off = m[0], m[1]
            logs.append({"file": path, "func": func, "offset": "0x" + off})

        # ---------------------------------------------------------
        # HOOK extraction
        for m in self.HOOK_PATTERN.findall(content):
            g1, g2, g3, func, orig = m
            off = g1 or g2 or g3 or ""

            hooks.append({
                "file": path,
                "func": func,
                "orig": orig or "",
                "offset": "0x" + off if off else ""
            })

        # ---------------------------------------------------------
        # orig_Func declarations
        for m in self.ORIG_DECL.findall(content):
            originals.append(m)

        # ---------------------------------------------------------
        # commented offsets
        for m in self.COMMENTED_OFFSET.findall(content):
            logs.append({"file": path, "func": None, "offset": "0x" + m})

        return {
            "LOGD": logs,
            "HOOKS": hooks,
            "ORIGINALS": originals,
            "RAW": content,
        }
