__version__ = "0.1.0"

from .cli import app

from .types import HistoryEntry

from .parser import parse_history_file

from .analyzer import analyze_history

from .suggester import suggest_optimizations

from .visualizer import print_analysis
