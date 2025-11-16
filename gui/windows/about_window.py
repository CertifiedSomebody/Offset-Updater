from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel
from ..core.config import Config
from ..components.theme import Theme


class AboutWindow(QDialog):
    """About Window."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setFixedSize(350, 220)

        layout = QVBoxLayout()
        self.setLayout(layout)

        title = QLabel(f"{Config.APP_NAME}")
        title.setFont(Theme.FONT_BOLD)
        title.setStyleSheet("font-size: 18px;")

        version = QLabel(f"Version: {Config.VERSION}")
        author = QLabel("Created by: YourName")

        info = QLabel("Offset Updater analyzes offset changes\n"
                      "between dumps and source files and\ngenerates patch snippets automatically.")
        info.setWordWrap(True)

        layout.addWidget(title)
        layout.addWidget(version)
        layout.addWidget(author)
        layout.addSpacing(10)
        layout.addWidget(info)
