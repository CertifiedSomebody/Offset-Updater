import json
from typing import Dict, List


class Reporter:
    """
    Generates human-readable and machine-readable reports from:
        - offset analyzer results
        - code generator results
    """

    # ---------------------------------------------------------
    def build_text_report(self, analysis_data: Dict) -> str:
        """
        Create a clean text summary of:
            - updated offsets
            - outdated offsets (old -> new)
            - missing functions in dump
            - unused dump methods
        """

        lines = []
        lines.append("======= OFFSET UPDATE REPORT =======\n")

        # Summary section
        summary = analysis_data.get("summary", {})
        lines.append("SUMMARY:")
        lines.append(f"  Total Methods in Dump     : {summary.get('total_in_dump', 0)}")
        lines.append(f"  Total Methods in Source   : {summary.get('total_in_source', 0)}")
        lines.append(f"  Updated Offsets           : {summary.get('updated_count', 0)}")
        lines.append(f"  Outdated Offsets          : {summary.get('outdated_count', 0)}")
        lines.append(f"  Missing In Dump           : {summary.get('missing_in_dump', 0)}")
        lines.append(f"  Unused Dump Methods       : {summary.get('unused_dump_methods', 0)}\n")

        # Updated section
        lines.append("UPDATED OFFSETS:")
        updated = analysis_data.get("updated", [])
        if updated:
            for u in updated:
                lines.append(f"  {u['func']}  ->  0x{u['offset']}")
        else:
            lines.append("  NONE")
        lines.append("")

        # Outdated section
        lines.append("OUTDATED (Old -> New):")
        outdated = analysis_data.get("outdated", [])
        if outdated:
            for o in outdated:
                lines.append(f"  {o['func']}: 0x{o['old_offset']}  → 0x{o['new_offset']}")
        else:
            lines.append("  NONE")
        lines.append("")

        # Missing section
        lines.append("MISSING IN DUMP:")
        missing = analysis_data.get("missing_in_dump", [])
        if missing:
            for m in missing:
                lines.append(f"  {m['func']}  (source offset: 0x{m['source_offset']})")
        else:
            lines.append("  NONE")
        lines.append("")

        # Unused section
        lines.append("UNUSED METHODS IN DUMP:")
        unused = analysis_data.get("unused_dump_methods", [])
        if unused:
            for fn in unused:
                lines.append(f"  {fn}")
        else:
            lines.append("  NONE")
        lines.append("")

        return "\n".join(lines)

    # ---------------------------------------------------------
    def build_json_report(self, generator_payload: Dict) -> str:
        """
        Convert report/output dictionary to compact JSON string.
        """
        return json.dumps(generator_payload, indent=4)

    # ---------------------------------------------------------
    def save_text(self, path: str, content: str) -> None:
        """
        Save plain text report to a file.
        """
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    # ---------------------------------------------------------
    def save_json(self, path: str, data: Dict) -> None:
        """
        Save JSON report to a file.
        """
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    # ---------------------------------------------------------
    def save_combo_report(self, folder: str, analysis_data: Dict, generator_payload: Dict) -> None:
        """
        Saves:
            - human-readable text report
            - machine-readable JSON report
            - code snippets (hook + logd)
        """
        # Text and JSON reports
        text_report = self.build_text_report(analysis_data)
        json_report = self.build_json_report(generator_payload)

        self.save_text(f"{folder}/offset_report.txt", text_report)
        self.save_json(f"{folder}/offset_report.json", generator_payload)

        # Hook snippets
        with open(f"{folder}/hook_snippets.txt", "w", encoding="utf-8") as f:
            f.write(generator_payload.get("generated_hook_snippets", ""))

        # LOGD snippets
        with open(f"{folder}/logd_snippets.txt", "w", encoding="utf-8") as f:
            f.write(generator_payload.get("generated_logd_snippets", ""))
