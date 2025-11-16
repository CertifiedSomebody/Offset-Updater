from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar
from .theme import Theme


class ProgressWindow(QDialog):
    """Simple modal progress dialog."""

    def __init__(self, title="Processing...", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(300, 120)

        self.label = QLabel("Please wait...")
        self.label.setFont(Theme.FONT_BOLD)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Infinite progress

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.progress)
        self.setLayout(layout)

        self.setModal(True)
