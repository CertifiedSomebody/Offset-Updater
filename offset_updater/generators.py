from typing import Dict, List


class CodeGenerator:
    """
    Produces:
        - Updated HOOK(...) lines
        - Updated LOGD(...) lines
        - Mapping for auto-patching source files
        - GUI/CLI-friendly report payloads
    """

    # ------------------------------------------------------------------
    def _normalize_offset(self, hex_str: str) -> str:
        """Ensure always '0xDEADBEEF' format."""
        hex_str = hex_str.strip().lower().replace("0x", "")
        return f"0x{hex_str.upper()}"

    # ------------------------------------------------------------------
    def generate_hook_snippets(self, updates: List[Dict]) -> str:
        """
        Generate HOOK lines.

        Input:
            [{"func": "Subtract", "offset": "31557C0", "orig": "orig_Subtract"}]

        Output:
            HOOK("libil2cpp.so", 0x31557C0, Subtract, orig_Subtract);
        """

        lines = []
        for entry in updates:
            func = entry["func"]
            orig = entry.get("orig", "") or ""
            offset = self._normalize_offset(entry["offset"])

            if orig:
                line = f'HOOK("libil2cpp.so", {offset}, {func}, {orig});'
            else:
                line = f'HOOK("libil2cpp.so", {offset}, {func});'

            lines.append(line)

        return "\n".join(lines)

    # ------------------------------------------------------------------
    def generate_logd_snippets(self, updates: List[Dict]) -> str:
        """
        Generate LOGD offsets

        Input:
            [{"func": "Subtract", "offset": "31557C0"}]

        Output:
            LOGD(OBFUSCATE("Updated Offset | Subtract : 0x31557C0"));
        """

        lines = []
        for entry in updates:
            func = entry["func"]
            offset = self._normalize_offset(entry["offset"])

            line = (
                f'LOGD(OBFUSCATE("Updated Offset | {func} : {offset}"));'
            )
            lines.append(line)

        return "\n".join(lines)

    # ------------------------------------------------------------------
    def generate_replacement_map(self, outdated_list: List[Dict]) -> Dict[str, str]:
        """
        Build a mapping of old offsets → new offsets

        Input:
            [{"old_offset": "123456", "new_offset": "31557C0"}]

        Output:
            {
                "0x123456": "0x31557C0"
            }
        """

        replace_map = {}

        for entry in outdated_list:
            old_hex = self._normalize_offset(entry["old_offset"])
            new_hex = self._normalize_offset(entry["new_offset"])

            # Prevent duplicates
            if old_hex != new_hex:
                replace_map[old_hex] = new_hex

        return replace_map

    # ------------------------------------------------------------------
    def generate_report_payload(
        self,
        updated: List[Dict],
        outdated: List[Dict],
        missing: List[Dict],
        unused: List[str]
    ) -> Dict:
        """
        Build final exportable structure for GUI / CLI.
        """

        return {
            "updated": updated,
            "outdated": outdated,
            "missing_in_dump": missing,
            "unused_dump_methods": unused,
            "generated_hook_snippets": self.generate_hook_snippets(updated),
            "generated_logd_snippets": self.generate_logd_snippets(updated),
            "replacement_map": self.generate_replacement_map(outdated)
        }

