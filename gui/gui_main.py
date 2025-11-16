import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from .core.controller import AppController
from .windows.main_window import MainWindow
from .core.config import Config
from .core.state import AppState


def load_stylesheet():
    """Load the stylesheet from assets/styles.qss."""
    try:
        with open(Config.ASSETS_DIR / "styles.qss", "r", encoding="utf-8") as f:
            return f.read()

    except FileNotFoundError:
        print("[WARN] styles.qss not found. Continuing without stylesheet.")
        return ""


def launch_gui():
    """Main GUI startup entry point."""
    app = QApplication(sys.argv)

    # ---------------------------
    # APP ICON
    # ---------------------------
    icon_path = Config.ASSETS_DIR / "icon.png"
    try:
        app.setWindowIcon(QIcon(str(icon_path)))
    except Exception:
        print(f"[WARN] Failed to load icon: {icon_path}")

    # ---------------------------
    # STYLESHEET
    # ---------------------------
    stylesheet = load_stylesheet()
    if stylesheet:
        app.setStyleSheet(stylesheet)

    # ---------------------------
    # GLOBAL STATE + CONTROLLER
    # ---------------------------
    state = AppState()
    controller = AppController(state)

    # ---------------------------
    # MAIN WINDOW
    # ---------------------------
    window = MainWindow(controller)
    window.show()

    # ---------------------------
    # EXEC LOOP
    # ---------------------------
    sys.exit(app.exec())


# Standalone script entry
if __name__ == "__main__":
    launch_gui()
