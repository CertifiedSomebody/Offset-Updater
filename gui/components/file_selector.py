from PyQt6.QtWidgets import QWidget, QLabel, QHBoxLayout, QFileDialog, QLineEdit
from .buttons import SecondaryButton
from .theme import Theme


class FileSelector(QWidget):
    """Widget: label + readonly textbox + browse button."""

    def __init__(self, label_text, file_filter="All Files (*)"):
        super().__init__()

        self.filter = file_filter

        self.label = QLabel(label_text)
        self.label.setFont(Theme.FONT_BOLD)

        self.path_box = QLineEdit()
        self.path_box.setReadOnly(True)
        self.path_box.setPlaceholderText("No file selected...")

        self.button = SecondaryButton("Browse")
        self.button.clicked.connect(self.browse)

        layout = QHBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.path_box)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def browse(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select File", "", self.filter
        )
        if path:
            self.path_box.setText(path)

    def get_path(self):
        return self.path_box.text()
