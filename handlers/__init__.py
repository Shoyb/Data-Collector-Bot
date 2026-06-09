"""Event and command handlers for Data Collector Bot."""
from .calculator import process_calculator_commands
from .commands import process_commands
from .events import process_events
from .games import process_game_commands, setup_game_commands
from .plotter import process_plot_commands
from .polynomial import process_polynomial_commands
from .transformers import process_transformer_commands

__all__ = [
    "process_calculator_commands",
    "process_commands",
    "process_events",
    "process_game_commands",
    "process_plot_commands",
    "process_polynomial_commands",
    "process_transformer_commands",
    "setup_game_commands",
]
