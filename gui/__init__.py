"""
GUI Package for Offset Updater
------------------------------

This package contains the full graphical interface built using PyQt6.
It is completely modular, with clear separation between:

- core:     shared logic, config, controller, global state
- components: reusable widgets (buttons, file selectors, views)
- windows:     full application windows/screens
- services:    file operations, background threads, APIs
- assets:      images, fonts, stylesheets

The main entry point to launch the GUI is `gui_main.py`.
"""

__version__ = "1.0.0"
__author__ = "Certified Somebody"

# Optional: expose GUI launcher for easy imports
from .gui_main import launch_gui
