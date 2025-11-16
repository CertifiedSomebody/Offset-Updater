from PyQt6.QtWidgets import (
    QWidget, QMainWindow, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QMessageBox, QTabWidget, QFileDialog
)
from PyQt6.QtCore import Qt

from ..components.file_selector import FileSelector
from ..components.buttons import PrimaryButton, SecondaryButton
from ..components.results_viewer import ResultsViewer
from ..components.progress_window import ProgressWindow
from ..core.config import Config
from .settings_window import SettingsWindow
from .about_window import AboutWindow

# AI updater
from ..services.ai_maincpp_updater import AIMainCppUpdater


class MainWindow(QMainWindow):
    """Main UI window of the Offset Updater."""

    def __init__(self, controller):
        super().__init__()

        self.controller = controller
        self.setWindowTitle(f"{Config.APP_NAME} - v{Config.VERSION}")
        self.setMinimumSize(Config.DEFAULT_WIDTH, Config.DEFAULT_HEIGHT)

        # --- LAYOUT ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        root = QVBoxLayout()
        central_widget.setLayout(root)

        # Title
        title = QLabel(Config.APP_NAME)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; margin-bottom: 12px;")
        root.addWidget(title)

        # File selectors (Dump file + main.cpp)
        self.dump_selector = FileSelector("Dump File:", Config.FILTER_DUMP)
        # Use a standard filter label for main.cpp
        self.cpp_selector = FileSelector("main.cpp File:", "C++ Source (*.cpp)")

        root.addWidget(self.dump_selector)
        root.addWidget(self.cpp_selector)

        # Buttons row
        btn_row = QHBoxLayout()

        load_btn = PrimaryButton("Load Files")
        load_btn.clicked.connect(self.load_files)

        analyze_btn = PrimaryButton("Run Analysis")
        analyze_btn.clicked.connect(self.run_analysis)

        generate_btn = SecondaryButton("Generate Code & Report")
        generate_btn.clicked.connect(self.generate_outputs)

        ai_update_btn = PrimaryButton("AI Update main.cpp")
        ai_update_btn.clicked.connect(self.ai_update_maincpp)

        btn_row.addWidget(load_btn)
        btn_row.addWidget(analyze_btn)
        btn_row.addWidget(generate_btn)
        btn_row.addWidget(ai_update_btn)

        root.addLayout(btn_row)

        # Tabs: Results, Code/Report, AI-updated main.cpp
        self.tabs = QTabWidget()
        self.results_viewer = ResultsViewer()
        self.tabs.addTab(self.results_viewer, "Results")

        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        self.tabs.addTab(self.output_box, "Generated Code / Report")

        self.ai_output = QTextEdit()
        self.ai_output.setReadOnly(True)
        self.tabs.addTab(self.ai_output, "AI Updated main.cpp")

        root.addWidget(self.tabs)

        # Bottom row: settings + about
        bottom_row = QHBoxLayout()
        settings_btn = SecondaryButton("Settings")
        settings_btn.clicked.connect(self.open_settings)

        about_btn = SecondaryButton("About")
        about_btn.clicked.connect(self.open_about)

        bottom_row.addWidget(settings_btn)
        bottom_row.addWidget(about_btn)
        root.addLayout(bottom_row)

    # ------------------------------
    # FILE LOAD
    # ------------------------------
    def load_files(self):
        dump_path = self.dump_selector.get_path()
        cpp_path = self.cpp_selector.get_path()

        if not dump_path or not cpp_path:
            QMessageBox.warning(self, "Missing Files", "Please select both a dump file and main.cpp.")
            return

        progress = ProgressWindow("Loading Files...", self)
        progress.show()

        try:
            loaded_dump = self.controller.load_dump_file(dump_path)
            loaded_cpp = self.controller.load_source_file(cpp_path)
        finally:
            progress.close()

        if loaded_dump and loaded_cpp:
            QMessageBox.information(self, "Success", "Dump and main.cpp loaded successfully.")
        else:
            QMessageBox.warning(self, "Load Error", "Failed to load dump or main.cpp. Check logs for details.")

    # ------------------------------
    # ANALYSIS
    # ------------------------------
    def run_analysis(self):
        results = self.controller.run_analysis()

        if not results:
            QMessageBox.warning(self, "No Results", "No analysis results found. Ensure files are loaded.")
            return

        self.results_viewer.load_results(results)
        QMessageBox.information(self, "Analysis Complete", "Offsets analyzed successfully.")

    # ------------------------------
    # GENERATE SNIPPETS & REPORT
    # ------------------------------
    def generate_outputs(self):
        code = self.controller.generate_fix_code()
        report = self.controller.generate_report()

        if not code and not report:
            QMessageBox.warning(self, "Nothing Generated", "No code or report could be generated.")
            return

        self.output_box.clear()
        self.output_box.append("=== PATCH SNIPPETS ===\n")
        self.output_box.append(code or "[No patch code generated]")
        self.output_box.append("\n\n=== REPORT ===\n")
        self.output_box.append(report or "[No report generated]")

        # Switch to the Generated Code / Report tab so user sees output
        self.tabs.setCurrentWidget(self.output_box)

    # ------------------------------
    # AI: UPDATE main.cpp
    # ------------------------------
    def ai_update_maincpp(self):
        cpp_path = self.cpp_selector.get_path()
        dump_data = self.controller.state.parsed_dump

        if not cpp_path:
            QMessageBox.warning(self, "Missing File", "Please select main.cpp to update.")
            return

        if not dump_data:
            QMessageBox.warning(self, "Missing Dump", "Load a dump file before using the AI updater.")
            return

        try:
            with open(cpp_path, "r", encoding="utf-8") as f:
                cpp_text = f.read()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to read main.cpp:\n{e}")
            return

        progress = ProgressWindow("AI Updating main.cpp...", self)
        progress.show()

        try:
            ai_updater = AIMainCppUpdater()
            updated_cpp = ai_updater.generate_updated_cpp(dump_data, cpp_text)

            self.ai_output.clear()
            self.ai_output.setPlainText(updated_cpp or "[AI returned empty response]")
            self.tabs.setCurrentWidget(self.ai_output)

            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save Updated main.cpp",
                "updated_main.cpp",
                "C++ Files (*.cpp)"
            )

            if save_path:
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(updated_cpp)
                QMessageBox.information(self, "Saved", "Updated main.cpp saved successfully.")

        except Exception as e:
            QMessageBox.critical(self, "AI Error", str(e))
        finally:
            progress.close()

    # ------------------------------
    # SETTINGS / ABOUT
    # ------------------------------
    def open_settings(self):
        SettingsWindow(self).exec()

    def open_about(self):
        AboutWindow(self).exec()
