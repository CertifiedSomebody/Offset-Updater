"""
Global constants for the Offset Updater project.
Central place for:
    - folder paths
    - file patterns
    - regex signatures
    - supported file types
"""

import os

# -------------------------------------------------------------
# 🎯 Default folders (relative to the project root)

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

DUMP_FOLDER = os.path.join(PROJECT_ROOT, "input_dumps")
SOURCE_FOLDER = os.path.join(PROJECT_ROOT, "input_source")
OUTPUT_FOLDER = os.path.join(PROJECT_ROOT, "output")

# The user can override these if needed
DEFAULT_DUMP_FILE = "dump.cs"

# -------------------------------------------------------------
# 🎯 Source scanning patterns (generic C/C++)

# Hook pattern:
# HOOK("libil2cpp.so", 0x123ABC, FunctionName);
HOOK_PATTERN = r"HOOK\([^,]+,\s*0x([0-9A-Fa-f]+),\s*([A-Za-z0-9_]+)\s*\)"

# IL2CPP get-offset from logs or statements:
# LOGD("Updated Offset | Func : 0x123ABC");
LOG_OFFSET_PATTERN = r"0x([0-9A-Fa-f]+)"

# C-like function signature used to detect references:
FUNCTION_NAME_PATTERN = r"[A-Za-z0-9_]+"

# -------------------------------------------------------------
# 🎯 Supported file extensions
SOURCE_FILE_EXTENSIONS = [
    ".cpp",
    ".c",
    ".h",
    ".hpp",
    ".txt",  # allow config-like text scanning
]

# -------------------------------------------------------------
# 🎯 File names
REPORT_TEXT = "offset_report.txt"
REPORT_JSON = "offset_report.json"
HOOK_SNIPPETS = "hook_snippets.txt"
LOGD_SNIPPETS = "logd_snippets.txt"

