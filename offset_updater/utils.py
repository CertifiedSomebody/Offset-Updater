import os
import re
import json
from typing import Optional, Dict, List
from .constants import SOURCE_FILE_EXTENSIONS


# -------------------------------------------------------------
# 📂 File utilities
# -------------------------------------------------------------

def read_file(path: str) -> str:
    """Read a file and return pure text."""
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def write_file(path: str, text: str) -> None:
    """Write text to a file."""
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def ensure_folder(path: str) -> None:
    """Create folder if missing."""
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def find_files(folder: str, extensions: List[str] = None) -> List[str]:
    """
    Return list of file paths in a folder that match given extensions.
    """
    if extensions is None:
        extensions = SOURCE_FILE_EXTENSIONS

    found = []
    for root, _, files in os.walk(folder):
        for f in files:
            if any(f.endswith(ext) for ext in extensions):
                found.append(os.path.join(root, f))
    return found


# -------------------------------------------------------------
# 🔢 Hex utilities
# -------------------------------------------------------------

def clean_hex(hex_str: str) -> Optional[str]:
    """
    Normalize and validate hex string.
    Accepts:
        "0x1234", "1234", "ABCDEF"
    Returns:
        "1234" (without 0x)
    """
    if not hex_str:
        return None

    hex_str = hex_str.strip().lower()

    if hex_str.startswith("0x"):
        hex_str = hex_str[2:]

    if re.fullmatch(r"[0-9a-f]+", hex_str):
        return hex_str.upper()

    return None


def to_hex(value: int) -> str:
    """
    Convert integer to uppercase hex without 0x prefix.
    """
    return hex(value)[2:].upper()


# -------------------------------------------------------------
# 🧪 Regex / scanning utilities
# -------------------------------------------------------------

def regex_find_all(pattern: str, text: str, flags=0) -> List[re.Match]:
    """Return all regex matches."""
    return list(re.finditer(pattern, text, flags))


def regex_find_one(pattern: str, text: str, flags=0) -> Optional[re.Match]:
    """Return first regex match or None."""
    return re.search(pattern, text, flags)


# -------------------------------------------------------------
# 🧩 JSON utilities
# -------------------------------------------------------------

def load_json(path: str) -> Dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str, data: Dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


# -------------------------------------------------------------
# 📣 Simple Logger
# -------------------------------------------------------------

def log(msg: str) -> None:
    """
    Lightweight internal logger so it doesn't conflict with user logs.
    """
    print(f"[OffsetUpdater] {msg}")
