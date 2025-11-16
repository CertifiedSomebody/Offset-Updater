from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import Qt
from .theme import Theme


class BaseButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)
        self.setFont(Theme.FONT_BOLD)
        self.setFixedHeight(36)
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class PrimaryButton(BaseButton):
    def __init__(self, text=""):
        super().__init__(text)
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {Theme.COLOR_PRIMARY};
                color: white;
                border-radius: {Theme.BORDER_RADIUS}px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: #0A84FF;
            }}
        """
        )


class SecondaryButton(BaseButton):
    def __init__(self, text=""):
        super().__init__(text)
        self.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {Theme.COLOR_SECONDARY};
                color: white;
                border-radius: {Theme.BORDER_RADIUS}px;
                padding: 6px 12px;
            }}
            QPushButton:hover {{
                background-color: #555555;
            }}
        """
        )
