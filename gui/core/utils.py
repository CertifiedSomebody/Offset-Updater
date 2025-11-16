from PyQt6.QtWidgets import QMessageBox


def show_error(title: str, message: str):
    """Simple QMessageBox error popup."""
    dlg = QMessageBox()
    dlg.setIcon(QMessageBox.Icon.Critical)
    dlg.setWindowTitle(title)
    dlg.setText(message)
    dlg.exec()


def show_info(title: str, message: str):
    """Simple QMessageBox info popup."""
    dlg = QMessageBox()
    dlg.setIcon(QMessageBox.Icon.Information)
    dlg.setWindowTitle(title)
    dlg.setText(message)
    dlg.exec()
