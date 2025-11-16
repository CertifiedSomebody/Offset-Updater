from PyQt6.QtGui import QFont


class Theme:
    """Centralized theme settings."""

    FONT_REGULAR = QFont("Roboto", 10)
    FONT_BOLD = QFont("Roboto", 10, QFont.Weight.Bold)

    COLOR_PRIMARY = "#0078D7"
    COLOR_SECONDARY = "#444444"
    COLOR_BACKGROUND = "#1e1e1e"
    COLOR_TEXT = "#ffffff"

    PADDING = 10
    BORDER_RADIUS = 6
