import os
import json
from typing import Optional


class FileService:
    """Handles file read/write operations."""

    @staticmethod
    def read_text(file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def write_text(file_path: str, content: str):
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

    @staticmethod
    def read_json(file_path: str) -> dict:
        data = FileService.read_text(file_path)
        return json.loads(data)

    @staticmethod
    def write_json(file_path: str, obj: dict):
        data = json.dumps(obj, indent=4)
        FileService.write_text(file_path, data)

    @staticmethod
    def ensure_dir(path: str):
        if not os.path.exists(path):
            os.makedirs(path)
