import traceback
from typing import Optional

from offset_updater.dump_parser import DumpParser
from offset_updater.source_scanner import SourceScanner
from offset_updater.offset_analyzer import OffsetAnalyzer
from offset_updater.generators import CodeGenerator
from offset_updater.reporter import Reporter

from ..services.ai_maincpp_updater import AIMainCppUpdater
from .utils import show_error


class AppController:
    """Main controller for GUI <-> Backend communication."""

    def __init__(self, state):
        self.state = state
        self.ai_updater = AIMainCppUpdater()

    # ------------------------------------------------------
    # FILE LOADING
    # ------------------------------------------------------
    def load_dump_file(self, path: str) -> bool:
        """Parse dump file and store results in state."""
        try:
            parser = DumpParser()
            self.state.parsed_dump = parser.parse(path)
            self.state.dump_path = path
            return True

        except Exception as e:
            show_error("Dump Parse Error", str(e))
            traceback.print_exc()
            self.state.parsed_dump = None
            self.state.dump_path = None
            return False

    def load_source_file(self, path: str) -> bool:
        """Load and parse source file (main.cpp)."""
        try:
            scanner = SourceScanner(path)
            self.state.parsed_source = scanner.scan()
            self.state.source_path = path
            return True

        except Exception as e:
            show_error("Source Scan Error", str(e))
            traceback.print_exc()
            self.state.parsed_source = None
            self.state.source_path = None
            return False

    # ------------------------------------------------------
    # ANALYSIS
    # ------------------------------------------------------
    def run_analysis(self) -> dict:
        """Compare dump offsets with source offsets."""
        if not self.state.parsed_dump or not self.state.parsed_source:
            show_error("Analysis Error", "Dump or source files not loaded.")
            return {}

        try:
            analyzer = OffsetAnalyzer(
                dump_data=self.state.parsed_dump,
                source_data=self.state.parsed_source
            )

            results = analyzer.analyze()
            self.state.analysis_results = results
            return results

        except Exception as e:
            show_error("Analysis Error", str(e))
            traceback.print_exc()
            self.state.analysis_results = {}
            return {}

    # ------------------------------------------------------
    # AI UPDATE OF main.cpp
    # ------------------------------------------------------
    def run_ai_maincpp_update(self) -> Optional[str]:
        """Send dump + main.cpp to AI and save updated output."""
        if not self.state.source_path:
            show_error("AI Error", "main.cpp file not loaded.")
            return None

        if not self.state.parsed_dump:
            show_error("AI Error", "Dump file not loaded.")
            return None

        try:
            # read real main.cpp text
            with open(self.state.source_path, "r", encoding="utf-8") as f:
                cpp_text = f.read()

            dump_data = self.state.parsed_dump

            updated_cpp = self.ai_updater.generate_updated_cpp(
                dump_data=dump_data,
                cpp_text=cpp_text
            )

            self.state.ai_generated_cpp = updated_cpp
            return updated_cpp

        except Exception as e:
            show_error("AI Update Error", str(e))
            traceback.print_exc()
            self.state.ai_generated_cpp = None
            return None

    # ------------------------------------------------------
    # CODE GENERATION
    # ------------------------------------------------------
    def generate_fix_code(self) -> str:
        """Generate hook + LOGD patch code based on results."""
        if not self.state.analysis_results:
            show_error("Code Generation Error", "No analysis results available.")
            return ""

        try:
            generator = CodeGenerator()
            updated_entries = self.state.analysis_results.get("updated", [])

            return (
                generator.generate_hook_snippets(updated_entries)
                + "\n\n"
                + generator.generate_logd_snippets(updated_entries)
            )

        except Exception as e:
            show_error("Code Generation Error", str(e))
            traceback.print_exc()
            return ""

    # ------------------------------------------------------
    # REPORTING
    # ------------------------------------------------------
    def generate_report(self) -> str:
        """Generate readable analysis report."""
        if not self.state.analysis_results:
            show_error("Report Error", "No analysis results available.")
            return ""

        try:
            reporter = Reporter()
            return reporter.build_text_report(self.state.analysis_results)

        except Exception as e:
            show_error("Report Error", str(e))
            traceback.print_exc()
            return ""
