from typing import Dict, List, Any


class OffsetAnalyzer:
    """
    Takes:
        dump_data  → parsed from dump.cs
        source_data → parsed from main.cpp (HOOKS, LOGD, ORIGINALS)

    Produces:
        updated_offsets
        missing offsets
        outdated offsets
        unused dump entries
    """

    def __init__(self, dump_data: Dict[str, Any], source_data: Dict):
        self.dump_raw = dump_data or {}

        # Normalize: method → "hex"
        self.dump = {}
        for k, v in (dump_data or {}).items():
            off = self._extract_offset_value(v)
            self.dump[k] = self._normalize(off)

        self.src = source_data or {}

    # ===================================================================
    def analyze(self) -> Dict[str, Any]:
        hook_map = self._extract_hook_map()      # func → old_offset
        log_map = self._extract_log_map()        # func → log_offset

        updated = []
        outdated = []
        missing = []

        for func, old_offset in hook_map.items():
            old_norm = self._normalize(old_offset)

            # 1) exact lookup
            new_off = self.dump.get(func)

            # 2) fuzzy match if not found
            if not new_off:
                new_off = self._fuzzy_lookup(func)

            # 3) nothing found anywhere
            if not new_off:
                missing.append({
                    "func": func,
                    "old_offset": old_norm,
                    "log_offset": log_map.get(func)
                })
                continue

            # 4) compare old vs new
            if old_norm != new_off:
                outdated.append({
                    "func": func,
                    "old_offset": old_norm,
                    "new_offset": new_off,
                    "log_offset": log_map.get(func)
                })

                updated.append({
                    "func": func,
                    "offset": new_off
                })

        # dump methods never used in hooks
        unused_dump = [k for k in self.dump.keys() if k not in hook_map]

        return {
            "updated": updated,
            "outdated": outdated,
            "missing": missing,
            "unused_dump": unused_dump,
            "summary": self._create_summary(updated, outdated, missing, unused_dump)
        }

    # ===================================================================
    def _extract_hook_map(self) -> Dict[str, str]:
        """
        SourceScanner returns:
            HOOKS = [{ "func": "...", "offset": "0x1234", "file": ... }]
        Return clean map {func: offset}
        """
        hooks = {}
        for item in self.src.get("HOOKS", []):
            if not isinstance(item, dict):
                continue
            func = item.get("func")
            off = item.get("offset", "")
            if func:
                hooks[func] = off
        return hooks

    # ===================================================================
    def _extract_log_map(self) -> Dict[str, str]:
        """
        LOGD entries usually look like:
           {"file": "xxx.cpp", "func": "Player::Jump", "offset": "0xDEADBEEF"}

        We return:
           { func → normalized_offset }
        """
        logs = {}
        for item in self.src.get("LOGD", []):
            if not isinstance(item, dict):
                continue
            func = item.get("func")
            off = item.get("offset")
            if func and off:
                logs[func] = self._normalize(off)
        return logs

    # ===================================================================
    def _extract_offset_value(self, v: Any) -> str:
        if not v:
            return ""
        if hasattr(v, "offset"):
            return getattr(v, "offset", "")
        if isinstance(v, dict):
            return v.get("offset") or v.get("rva") or ""
        if isinstance(v, str):
            return v
        try:
            return str(v)
        except:
            return ""

    # ===================================================================
    def _normalize(self, off: str) -> str:
        if not off:
            return ""
        off = str(off).strip().lower()
        if off.startswith("0x"):
            off = off[2:]
        # ensure even length hex
        if all(c in "0123456789abcdef" for c in off):
            if len(off) % 2 != 0:
                off = "0" + off
        return off

    # ===================================================================
    def _fuzzy_lookup(self, func_name: str) -> str:
        """
        Match by last segment:
        e.g., "Player::TakeDamage" matches dump entry "TakeDamage"
        """
        key = func_name.split("::")[-1].lower()
        for dump_key, val in self.dump.items():
            if dump_key.lower().endswith(key) and val:
                return val
        return ""

    # ===================================================================
    def _create_summary(self, updated, outdated, missing, unused):
        return {
            "total_dump_entries": len(self.dump_raw),
            "total_hooks": len(self.src.get("HOOKS", [])),
            "updated_count": len(updated),
            "outdated_count": len(outdated),
            "missing_count": len(missing),
            "unused_dump_count": len(unused),
        }
