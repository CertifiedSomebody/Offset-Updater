from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QCheckBox, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from ..core.config import Config
from ..components.theme import Theme
from ..services.api_service import GeminiAPI  # import your API wrapper


class SettingsWindow(QDialog):
    """Settings Window for Offset Updater."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Title
        title = QLabel("Settings")
        title.setFont(Theme.FONT_BOLD)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Dark theme toggle
        self.theme_toggle = QCheckBox("Enable Dark Theme")
        self.theme_toggle.setChecked(True)  # Or load from state/config if implemented

        # API key input
        api_label = QLabel("Google Gemini API Key:")
        self.api_input = QLineEdit()
        self.api_input.setText(Config.get_api_key())  # use getter
        self.api_input.setPlaceholderText("Enter your API key here")

        # Buttons
        test_btn = QPushButton("Test API Key")
        test_btn.clicked.connect(self.test_api_key)

        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)

        # Add widgets to layout
        layout.addWidget(title)
        layout.addWidget(self.theme_toggle)
        layout.addWidget(api_label)
        layout.addWidget(self.api_input)
        layout.addWidget(test_btn)
        layout.addStretch()
        layout.addWidget(save_btn)

    def test_api_key(self):
        """Test the entered API key by sending a minimal request."""
        api_key = self.api_input.text().strip()
        if not api_key:
            QMessageBox.warning(self, "Test Failed", "API key cannot be empty.")
            return

        try:
            gemini = GeminiAPI(api_key)
            test_prompt = "Say hello."
            response = gemini.generate(test_prompt)
            if response:
                QMessageBox.information(self, "Test Successful", "API key is valid!")
            else:
                QMessageBox.warning(self, "Test Failed", "API key did not return a valid response.")
        except Exception as e:
            QMessageBox.critical(self, "Test Failed", f"API key test failed:\n{e}")

    def save_settings(self):
        """Save settings to config.json and update in-memory Config."""
        api_key = self.api_input.text().strip()

        # Save API key via Config setter
        Config.set_api_key(api_key)

        QMessageBox.information(self, "Settings Saved", "API key and settings saved successfully.")
        self.close()
