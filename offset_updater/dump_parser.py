import re
from dataclasses import dataclass


@dataclass
class DumpEntry:
    name: str
    offset: str
    rva: str
    va: str
    slot: str
    line_no: int
    raw: str


class DumpParser:
    """
    Robust IL2CPP dump.cs parser.

    Handles all real dump.cs patterns:

       // RVA: 0x216EA3C Offset: 0x216EA3C VA: 0x216EA3C Slot: 42
       public virtual int get_attack() { }

    Works even when:
       - Metadata is ABOVE the function
       - Metadata is BELOW the function
       - Metadata & function not adjacent
       - Missing slot
       - Fallback signatures (int get_attack())
    """

    # --- Metadata regex ---
    RE_META = re.compile(
        r"RVA:\s*(0x[0-9A-Fa-f]+)\s*"
        r"Offset:\s*(0x[0-9A-Fa-f]+)\s*"
        r"VA:\s*(0x[0-9A-Fa-f]+)"
        r"(?:\s*Slot:\s*([0-9]+))?"
    )

    # --- Full signature extraction ---
    RE_FUNCTION_NAME = re.compile(
        r"(?:public|private|protected|internal|static|\s)+\s*"
        r"(?:[\w<>\[\], ]+)\s+([A-Za-z0-9_]+)\s*\(",
        re.IGNORECASE
    )

    # --- Fallback signature ---
    RE_FUNCTION_FALLBACK = re.compile(
        r"\b([A-Za-z0-9_]+)\s*\("
    )

    def parse(self, path: str) -> dict:

        dump_map = {}
        pending_meta = None     # store metadata until function appears
        line_no = 0

        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line_no += 1
                stripped = line.strip()

                # --------------------------
                # 1. Detect metadata FIRST
                # --------------------------
                meta = self.RE_META.search(stripped)
                if meta:
                    pending_meta = {
                        "rva": meta.group(1),
                        "offset": meta.group(2),
                        "va": meta.group(3),
                        "slot": meta.group(4) or "",
                        "raw": stripped,
                        "line": line_no
                    }
                    # Do NOT continue — metadata may be on same line as function
                    # Continue scanning for function name
                

                # --------------------------
                # 2. Detect function name
                # --------------------------
                m = self.RE_FUNCTION_NAME.search(stripped)
                if not m:
                    m = self.RE_FUNCTION_FALLBACK.search(stripped)

                if m:
                    func_name = m.group(1)

                    # No metadata found earlier → invalid function entry
                    if not pending_meta:
                        continue

                    # Store final mapping
                    dump_map[func_name] = DumpEntry(
                        name=func_name,
                        offset=pending_meta["offset"],
                        rva=pending_meta["rva"],
                        va=pending_meta["va"],
                        slot=pending_meta["slot"],
                        line_no=pending_meta["line"],
                        raw=pending_meta["raw"]
                    )

                    # Reset metadata after use
                    pending_meta = None

        return dump_map
