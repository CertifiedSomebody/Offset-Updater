"""
Core logic for the Offset Updater GUI.

Contains:
- config:   global paths, constants
- state:    global application state model
- controller: communication layer between UI and backend logic
- utils:    helper tools for paths, threads, error dialogs
"""

from .config import Config
from .state import AppState
from .controller import AppController
