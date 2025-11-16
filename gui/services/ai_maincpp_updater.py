# services/ai_maincpp_updater.py
import re
from typing import Dict, Any, Optional

from .api_service import GeminiAPI


class AIMainCppUpdater:
    """
    Use Gemini to produce an updated main.cpp where outdated numeric offsets
    (0xHEX) are replaced by values taken from the dump mapping.

    - dump_data can be a mapping {name: offset} OR {name: DumpEntry(...)}
    - cpp_text is the full text of main.cpp
    """

    # Patterns to capture offsets and function names from typical mod menu code
    # Matches: HOOK("libil2cpp.so", str2Offset(OBFUSCATE("0x216B910")), get_ATK, orig_get_ATK);
    HOOK_OBF_PATTERN = re.compile(
        r'HOOK\s*\(\s*".+?"\s*,\s*str2Offset\s*\(\s*OBFUSCATE\s*\(\s*"(0x[0-9A-Fa-f]+)"\s*\)\s*\)\s*,\s*([A-Za-z_][A-Za-z0-9_]*)',
        re.MULTILINE
    )

    # Matches HOOK("libil2cpp.so", 0x216B910, get_ATK);
    HOOK_PLAIN_PATTERN = re.compile(
        r'HOOK\s*\(\s*".+?"\s*,\s*(0x[0-9A-Fa-f]+)\s*,\s*([A-Za-z_][A-Za-z0-9_]*)',
        re.MULTILINE
    )

    # LOGD lines like: LOGD(OBFUSCATE("Method Name: get_ATK, Offsets: 0x21678F0"));
    LOGD_PATTERN = re.compile(
        r'LOGD\s*\(\s*.*?Method\s+Name\s*[:\-]\s*([A-Za-z0-9_:<>]+).*?Offset[s]?\s*[:\-]?\s*(0x[0-9A-Fa-f]+)',
        re.IGNORECASE | re.DOTALL
    )

    # catch any 0xHEX occurrences next to function names in comment-like patterns
    COMMENT_FUNC_PATTERN = re.compile(
        r'(?:\/\/\s*)?([A-Za-z_][A-Za-z0-9_:<>]*)[^\n\r]{0,60}?(0x[0-9A-Fa-f]{4,})'
    )

    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-2.5-flash"):
        # allow overriding api key / model
        self.model = model
        self.api = GeminiAPI(api_key) if api_key is not None else GeminiAPI()

    # -----------------------
    # Helpers
    # -----------------------
    def _normalize_dump(self, dump_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Convert dump_data entries to a simple {func_name: 0xHEX} mapping.
        Accepts:
            - {"get_ATK": "0x216C648"}
            - {"get_ATK": DumpEntry(...)} where DumpEntry.offset may be "0x216C648" or "216C648"
        """
        out = {}
        for k, v in dump_data.items():
            if v is None:
                continue
            if isinstance(v, str):
                off = v
            else:
                # object with .offset attribute (like DumpEntry)
                off = getattr(v, "offset", None) or getattr(v, "rva", None) or None
            if not off:
                continue
            off = str(off).strip()
            # ensure 0x prefix
            if not off.lower().startswith("0x"):
                off = "0x" + off
            out[k] = off.lower()
        return out

    def extract_offsets(self, cpp_text: str) -> Dict[str, str]:
        """
        Extract function -> current_offset mapping from the provided main.cpp text.
        Returns mapping where offsets are normalized like '0x216b910' (lowercase).
        """
        mapping: Dict[str, str] = {}

        # HOOK patterns (OBFUSCATE str2Offset and plain)
        for match in self.HOOK_OBF_PATTERN.findall(cpp_text):
            off, func = match
            mapping[func] = off.lower()

        for match in self.HOOK_PLAIN_PATTERN.findall(cpp_text):
            off, func = match
            # If function already seen via OBF pattern, keep first (prioritize OBF)
            if func not in mapping:
                mapping[func] = off.lower()

        # LOGD style entries
        for match in self.LOGD_PATTERN.findall(cpp_text):
            func, off = match
            if func and off:
                if func not in mapping:
                    mapping[func] = off.lower()

        # As a last resort, scan comment-ish patterns for function + 0xHEX
        for match in self.COMMENT_FUNC_PATTERN.findall(cpp_text):
            func, off = match
            if func and off and func not in mapping:
                mapping[func] = off.lower()

        return mapping

    # -----------------------
    # Main function
    # -----------------------
    def generate_updated_cpp(self, dump_data: Dict[str, Any], cpp_text: str, max_prompt_chars: int = 120_000) -> str:
        """
        Build a clear prompt for Gemini and request a full updated main.cpp back.
        - dump_data: mapping or DumpEntry objects
        - cpp_text: full source text
        - max_prompt_chars: guard to avoid sending enormous prompts (truncates bottom of file if needed)
        """

        dump_map = self._normalize_dump(dump_data)
        src_map = self.extract_offsets(cpp_text)

        # Build compact table of functions that appear in source (and corresponding dump offsets if any)
        func_rows = []
        for func, old in sorted(src_map.items()):
            new = dump_map.get(func, "[NOT_IN_DUMP]")
            func_rows.append(f"{func} | source_old={old} | dump_new={new}")

        func_summary = "\n".join(func_rows) if func_rows else "(no functions detected)"

        # Trim the cpp_text if extremely long — prefer head (definitions) + foot (hooks) — but we keep simple truncation
        cpp_for_prompt = cpp_text
        if len(cpp_for_prompt) > max_prompt_chars:
            # keep first N and last M to preserve hook table and declarations
            head = cpp_for_prompt[: int(max_prompt_chars * 0.6)]
            tail = cpp_for_prompt[-int(max_prompt_chars * 0.4):]
            cpp_for_prompt = head + "\n\n/* === TRUNCATED MIDDLE === */\n\n" + tail

        prompt = f"""
You are an assistant that must update numeric offsets in a C++ source file (main.cpp) used for IL2CPP hooking.
Do NOT change code structure, variable names, comments or formatting — only update numeric offsets (hex values like 0x216B910).
Where the dump provides a newer offset for a function, replace the corresponding numeric value in main.cpp.

-- FUNCTIONS (detected in source) --
{func_summary}

-- INSTRUCTIONS --
1) ONLY change hex numbers (0x...) which represent offsets.
2) Preserve OBFUSCATE(...) wrappers and str2Offset(...) calls exactly as-is, only change the inner hex digits.
3) If dump has a newer offset for a function, substitute the dump value.
4) For functions marked [NOT_IN_DUMP], do not invent new offsets — leave them unchanged.
5) Return the FULL updated main.cpp source file as plain text. Do not add explanation, do not include JSON or metadata — the response must be exactly the updated file contents.

-- ORIGINAL main.cpp (BEGIN) --
{cpp_for_prompt}
-- ORIGINAL main.cpp (END) --
"""

        # Make the API call (model & api handled by GeminiAPI wrapper)
        updated = self.api.generate(prompt, model=self.model)

        # Basic validation: ensure we got something with 'HOOK' or 'LOGD'
        if not updated or ("HOOK(" not in updated and "LOGD(" not in updated):
            raise RuntimeError("AI returned no valid C++ output. Response may be truncated or invalid.")

        return updated
