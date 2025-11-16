from pathlib import Path
import json

class Config:
    """Global configuration and constants for GUI, including API key handling."""

    # Base directory of the entire project (auto-detected)
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    # GUI directory
    GUI_DIR = BASE_DIR / "gui"

    # Assets folder
    ASSETS_DIR = GUI_DIR / "assets"

    # Fonts folder
    FONTS_DIR = ASSETS_DIR / "fonts"

    # Window settings
    APP_NAME = "Offset Updater"
    VERSION = "1.0.0"
    DEFAULT_WIDTH = 900
    DEFAULT_HEIGHT = 600

    # File filters
    FILTER_DUMP = "Dump Files (*.txt *.cs)"
    FILTER_SOURCE = "C++ Source (*.cpp *.h *.hpp *.txt)"

    # Config file path
    CONFIG_FILE = BASE_DIR / "config.json"

    # Internal storage for config data
    _config_data = {}

    # Class-level convenience attribute for API key
    GEMINI_API_KEY = ""

    # -------------------------
    # Config load/save methods
    # -------------------------

    @classmethod
    def load_config(cls):
        """Load existing config if available."""
        try:
            if cls.CONFIG_FILE.exists():
                with open(cls.CONFIG_FILE, "r", encoding="utf-8") as f:
                    cls._config_data = json.load(f)
            else:
                cls._config_data = {}
        except (FileNotFoundError, json.JSONDecodeError):
            cls._config_data = {}

        # Update convenience attribute
        cls.GEMINI_API_KEY = cls._config_data.get("gemini_api_key", "")

    @classmethod
    def save_config(cls):
        """Save current config to file."""
        try:
            with open(cls.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(cls._config_data, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    # -------------------------
    # API key accessors
    # -------------------------

    @classmethod
    def get_api_key(cls) -> str:
        return cls._config_data.get("gemini_api_key", "")

    @classmethod
    def set_api_key(cls, key: str):
        cls._config_data["gemini_api_key"] = key
        cls.GEMINI_API_KEY = key  # update convenience attribute
        cls.save_config()


# Load config automatically on import
Config.load_config()
