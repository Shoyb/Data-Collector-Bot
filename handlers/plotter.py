"""
Function plotting command handler for Data Collector Bot.
"""
from io import BytesIO
import re

import discord
import matplotlib
import numpy as np
import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    standard_transformations,
)

from handlers.calculator import CalculatorError, calculate


matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402


COMMAND_PREFIXES = ("data plot ", "data graph ")
DEFAULT_X_MIN = -10.0
DEFAULT_X_MAX = 10.0
MAX_POINTS = 1000
PLOT_PATTERN = re.compile(r"^[0-9a-zA-ZxX+\-*/^().,=\s]+$")
RANGE_PATTERN = re.compile(r"\s+from\s+(.+?)\s+to\s+(.+)$", re.IGNORECASE)
TRANSFORMATIONS = standard_transformations + (
    convert_xor,
    implicit_multiplication_application,
)

X = sp.Symbol("x")
ALLOWED_NAMES = {
    "x": X,
    "pi": sp.pi,
    "e": sp.E,
    "sqrt": sp.sqrt,
    "ln": sp.log,
    "log": lambda value: sp.log(value, 10),
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "arctan": sp.atan,
    "atan": sp.atan,
    "arccos": sp.acos,
    "arcos": sp.acos,
    "acos": sp.acos,
    "arcsin": sp.asin,
    "asin": sp.asin,
}


class PlotError(ValueError):
    """Raised when a function cannot be parsed or plotted."""


def create_function_plot(raw_expression: str) -> tuple[BytesIO, str]:
    """Create a PNG plot for a function expression."""
    expression_text, x_min, x_max = _parse_plot_request(raw_expression)
    expression = _parse_expression(expression_text)

    x_values = np.linspace(x_min, x_max, MAX_POINTS)
    function = sp.lambdify(X, expression, modules=["numpy"])
    y_values = np.asarray(function(x_values), dtype=np.complex128)

    if y_values.shape == ():
        y_values = np.full_like(x_values, y_values, dtype=np.complex128)

    real_mask = np.isfinite(y_values.real) & np.isfinite(y_values.imag)
    real_mask &= np.abs(y_values.imag) < 1e-8
    if not np.any(real_mask):
        raise PlotError("The function has no real values in that range.")

    plot_buffer = BytesIO()
    fig, ax = plt.subplots(figsize=(8, 5), dpi=140)
    ax.plot(x_values[real_mask], y_values.real[real_mask], color="#2563eb", linewidth=2)
    ax.axhline(0, color="#222222", linewidth=0.8)
    ax.axvline(0, color="#222222", linewidth=0.8)
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.45)
    ax.set_title(f"y = {expression_text}")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    fig.tight_layout()
    fig.savefig(plot_buffer, format="png")
    plt.close(fig)

    plot_buffer.seek(0)
    return plot_buffer, expression_text


def _parse_plot_request(raw_expression: str) -> tuple[str, float, float]:
    if not PLOT_PATTERN.fullmatch(raw_expression):
        raise PlotError("Use numbers, x, supported functions, and math operators only.")

    expression_text = raw_expression.strip()
    x_min = DEFAULT_X_MIN
    x_max = DEFAULT_X_MAX

    range_match = RANGE_PATTERN.search(expression_text)
    if range_match:
        start_text, end_text = range_match.groups()
        expression_text = expression_text[:range_match.start()].strip()
        try:
            x_min = float(calculate(start_text))
            x_max = float(calculate(end_text))
        except (CalculatorError, ValueError, ZeroDivisionError, OverflowError) as exc:
            raise PlotError(f"The range is not valid: {exc}") from exc

    expression_text = _strip_function_label(expression_text)

    if not expression_text:
        raise PlotError("Enter a function like `x^2` or `sin(x)`.")

    if x_min >= x_max:
        raise PlotError("The start of the range must be smaller than the end.")

    if abs(x_max - x_min) > 1000000:
        raise PlotError("That range is too large to plot clearly.")

    return expression_text, x_min, x_max


def _strip_function_label(expression_text: str) -> str:
    lowered = expression_text.lower().replace(" ", "")
    if lowered.startswith("y="):
        return expression_text.split("=", 1)[1].strip()
    if lowered.startswith("f(x)="):
        return expression_text.split("=", 1)[1].strip()
    return expression_text


def _parse_expression(expression_text: str) -> sp.Expr:
    try:
        expression = sp.parsing.sympy_parser.parse_expr(
            expression_text.lower(),
            local_dict=ALLOWED_NAMES,
            transformations=TRANSFORMATIONS,
            evaluate=True,
        )
    except (SyntaxError, TypeError, ValueError, sp.SympifyError) as exc:
        raise PlotError("That function expression is not valid.") from exc

    if expression.free_symbols - {X}:
        raise PlotError("Functions can only use the variable `x`.")

    return expression


async def process_plot_commands(message: discord.Message) -> bool:
    """
    Process function plotting commands.

    Args:
        message: Discord message object

    Returns:
        True if a plot command was processed
    """
    msg = message.content.strip()
    lowered = msg.lower()

    prefix = next(
        (candidate for candidate in COMMAND_PREFIXES if lowered.startswith(candidate)),
        None,
    )
    if not prefix:
        return False

    raw_expression = msg[len(prefix):].strip()
    try:
        plot_buffer, expression_text = create_function_plot(raw_expression)
    except PlotError as exc:
        await message.channel.send(f"Could not plot that function: {exc}")
        return True

    await message.channel.send(
        content=f"Plot for `{expression_text}`",
        file=discord.File(plot_buffer, filename="function_plot.png"),
    )
    return True
