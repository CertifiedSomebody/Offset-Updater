"""
Offset Updater Package
----------------------

This package provides tools for parsing IL2CPP dump files,
scanning C++ mod source files, comparing offsets, and generating
update reports or patch snippets.

Modules:
    - dump_parser: Extracts offsets from dump.cs
    - source_scanner: Maps HOOK/LOGD calls from source files
    - offset_analyzer: Detects mismatches between dump + source
    - generators: Builds updated hook/logd code strings
    - reporter: Outputs text/JSON reports
"""

__version__ = "1.0.0"
__author__ = "CertifiedSomebody"
__license__ = "MIT"

# Public imports for easy access
from .dump_parser import DumpParser
from .source_scanner import SourceScanner
from .offset_analyzer import OffsetAnalyzer
from .generators import CodeGenerator
from .reporter import Reporter
