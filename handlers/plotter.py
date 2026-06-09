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
SURFACE_POINTS = 90
IMPLICIT_POINTS = 36
PLOT_PATTERN = re.compile(r"^[0-9a-zA-ZtTyYzZ+\-*/^().,=\s]+$")
RANGE_PATTERN = re.compile(r"\s+from\s+(.+?)\s+to\s+(.+)$", re.IGNORECASE)
TRANSFORMATIONS = standard_transformations + (
    convert_xor,
    implicit_multiplication_application,
)

X = sp.Symbol("x")
Y = sp.Symbol("y")
Z = sp.Symbol("z")
T = sp.Symbol("t")
ALLOWED_NAMES = {
    "x": X,
    "y": Y,
    "z": Z,
    "t": T,
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
    expression_parts = _split_expression_parts(expression_text)

    if len(expression_parts) == 1:
        expression = _parse_expression(expression_parts[0])
        free_symbols = expression.free_symbols

        if free_symbols <= {X}:
            return _create_2d_function_plot(expression, expression_text, x_min, x_max)
        if free_symbols <= {X, Y}:
            return _create_3d_surface_plot(expression, expression_text, x_min, x_max)
        if free_symbols <= {X, Y, Z}:
            return _create_3d_implicit_plot(expression, expression_text, x_min, x_max)

        raise PlotError("Use only `x`, `y`, `z`, or comma-separated parametric expressions.")

    if len(expression_parts) == 2:
        expressions = [_parse_expression(part) for part in expression_parts]
        return _create_2d_parametric_plot(expressions, expression_text, x_min, x_max)

    if len(expression_parts) == 3:
        expressions = [_parse_expression(part) for part in expression_parts]
        return _create_3d_parametric_plot(expressions, expression_text, x_min, x_max)

    raise PlotError("Use one expression, or 2/3 comma-separated expressions.")


def _create_2d_function_plot(
    expression: sp.Expr,
    expression_text: str,
    x_min: float,
    x_max: float,
) -> tuple[BytesIO, str]:
    x_values = np.linspace(x_min, x_max, MAX_POINTS)
    y_values = _evaluate_expression(expression, (X,), (x_values,))

    real_mask = _real_finite_mask(y_values)
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


def _create_2d_parametric_plot(
    expressions: list[sp.Expr],
    expression_text: str,
    t_min: float,
    t_max: float,
) -> tuple[BytesIO, str]:
    parameter = _get_parametric_symbol(expressions)
    t_values = np.linspace(t_min, t_max, MAX_POINTS)
    x_values = _evaluate_expression(expressions[0], (parameter,), (t_values,))
    y_values = _evaluate_expression(expressions[1], (parameter,), (t_values,))
    real_mask = _real_finite_mask(x_values) & _real_finite_mask(y_values)

    if not np.any(real_mask):
        raise PlotError("The parametric curve has no real values in that range.")

    plot_buffer = BytesIO()
    fig, ax = plt.subplots(figsize=(8, 5), dpi=140)
    ax.plot(x_values.real[real_mask], y_values.real[real_mask], color="#16a34a", linewidth=2)
    ax.axhline(0, color="#222222", linewidth=0.8)
    ax.axvline(0, color="#222222", linewidth=0.8)
    ax.grid(True, linestyle="--", linewidth=0.5, alpha=0.45)
    ax.set_title(expression_text)
    ax.set_xlabel(f"x({parameter})")
    ax.set_ylabel(f"y({parameter})")
    fig.tight_layout()
    fig.savefig(plot_buffer, format="png")
    plt.close(fig)

    plot_buffer.seek(0)
    return plot_buffer, expression_text


def _create_3d_parametric_plot(
    expressions: list[sp.Expr],
    expression_text: str,
    t_min: float,
    t_max: float,
) -> tuple[BytesIO, str]:
    parameter = _get_parametric_symbol(expressions)
    t_values = np.linspace(t_min, t_max, MAX_POINTS)
    x_values = _evaluate_expression(expressions[0], (parameter,), (t_values,))
    y_values = _evaluate_expression(expressions[1], (parameter,), (t_values,))
    z_values = _evaluate_expression(expressions[2], (parameter,), (t_values,))
    real_mask = _real_finite_mask(x_values) & _real_finite_mask(y_values) & _real_finite_mask(z_values)

    if not np.any(real_mask):
        raise PlotError("The 3D parametric curve has no real values in that range.")

    plot_buffer = BytesIO()
    fig = plt.figure(figsize=(8, 5.8), dpi=140)
    ax = fig.add_subplot(111, projection="3d")
    ax.plot(
        x_values.real[real_mask],
        y_values.real[real_mask],
        z_values.real[real_mask],
        color="#7c3aed",
        linewidth=2,
    )
    ax.set_title(expression_text)
    ax.set_xlabel(f"x({parameter})")
    ax.set_ylabel(f"y({parameter})")
    ax.set_zlabel(f"z({parameter})")
    fig.tight_layout()
    fig.savefig(plot_buffer, format="png")
    plt.close(fig)

    plot_buffer.seek(0)
    return plot_buffer, expression_text


def _create_3d_surface_plot(
    expression: sp.Expr,
    expression_text: str,
    axis_min: float,
    axis_max: float,
) -> tuple[BytesIO, str]:
    axis_values = np.linspace(axis_min, axis_max, SURFACE_POINTS)
    x_grid, y_grid = np.meshgrid(axis_values, axis_values)
    z_values = _evaluate_expression(expression, (X, Y), (x_grid, y_grid))
    real_mask = _real_finite_mask(z_values)

    if not np.any(real_mask):
        raise PlotError("The surface has no real values in that range.")

    z_plot = z_values.real.copy()
    z_plot[~real_mask] = np.nan

    plot_buffer = BytesIO()
    fig = plt.figure(figsize=(8, 5.8), dpi=140)
    ax = fig.add_subplot(111, projection="3d")
    ax.plot_surface(x_grid, y_grid, z_plot, cmap="viridis", linewidth=0, antialiased=True)
    ax.set_title(f"z = {expression_text}")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    fig.tight_layout()
    fig.savefig(plot_buffer, format="png")
    plt.close(fig)

    plot_buffer.seek(0)
    return plot_buffer, expression_text


def _create_3d_implicit_plot(
    expression: sp.Expr,
    expression_text: str,
    axis_min: float,
    axis_max: float,
) -> tuple[BytesIO, str]:
    axis_values = np.linspace(axis_min, axis_max, IMPLICIT_POINTS)
    x_grid, y_grid, z_grid = np.meshgrid(axis_values, axis_values, axis_values)
    values = _evaluate_expression(expression, (X, Y, Z), (x_grid, y_grid, z_grid))
    real_mask = _real_finite_mask(values)

    if not np.any(real_mask):
        raise PlotError("The implicit expression has no real values in that range.")

    finite_values = np.abs(values.real[real_mask])
    threshold = max(np.percentile(finite_values, 2), 1e-8)
    near_zero = real_mask & (np.abs(values.real) <= threshold)
    if not np.any(near_zero):
        raise PlotError("Could not find visible points near that implicit surface.")

    plot_buffer = BytesIO()
    fig = plt.figure(figsize=(8, 5.8), dpi=140)
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(
        x_grid[near_zero],
        y_grid[near_zero],
        z_grid[near_zero],
        c=values.real[near_zero],
        cmap="coolwarm",
        s=8,
        alpha=0.8,
    )
    title = expression_text if "=" in expression_text else f"{expression_text} = 0"
    ax.set_title(title)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")
    fig.tight_layout()
    fig.savefig(plot_buffer, format="png")
    plt.close(fig)

    plot_buffer.seek(0)
    return plot_buffer, expression_text


def _parse_plot_request(raw_expression: str) -> tuple[str, float, float]:
    if not PLOT_PATTERN.fullmatch(raw_expression):
        raise PlotError("Use numbers, variables, supported functions, and math operators only.")

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
    if lowered.startswith("z="):
        return expression_text.split("=", 1)[1].strip()
    if lowered.startswith("f(x)="):
        return expression_text.split("=", 1)[1].strip()
    return expression_text


def _parse_expression(expression_text: str) -> sp.Expr:
    try:
        if "=" in expression_text:
            left_text, right_text = expression_text.split("=", 1)
            expression = _parse_sympy_expression(left_text) - _parse_sympy_expression(right_text)
        else:
            expression = _parse_sympy_expression(expression_text)
    except (SyntaxError, TypeError, ValueError, sp.SympifyError) as exc:
        raise PlotError("That function expression is not valid.") from exc

    if expression.free_symbols - {X, Y, Z, T}:
        raise PlotError("Functions can only use `x`, `y`, `z`, or `t`.")

    return expression


def _parse_sympy_expression(expression_text: str) -> sp.Expr:
    return sp.parsing.sympy_parser.parse_expr(
        expression_text.lower(),
        local_dict=ALLOWED_NAMES,
        transformations=TRANSFORMATIONS,
        evaluate=True,
    )


def _split_expression_parts(expression_text: str) -> list[str]:
    parts = []
    depth = 0
    start = 0

    for index, char in enumerate(expression_text):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                raise PlotError("Parentheses are not balanced.")
        elif char == "," and depth == 0:
            parts.append(expression_text[start:index].strip())
            start = index + 1

    if depth != 0:
        raise PlotError("Parentheses are not balanced.")

    parts.append(expression_text[start:].strip())
    if any(not part for part in parts):
        raise PlotError("Comma-separated plot expressions cannot be empty.")

    if len(parts) > 1:
        return [_strip_coordinate_label(part) for part in parts]

    return parts


def _strip_coordinate_label(expression_text: str) -> str:
    lowered = expression_text.lower().replace(" ", "")
    for label in ("x=", "y=", "z="):
        if lowered.startswith(label):
            return expression_text.split("=", 1)[1].strip()
    return expression_text


def _evaluate_expression(
    expression: sp.Expr,
    symbols: tuple[sp.Symbol, ...],
    values: tuple[np.ndarray, ...],
) -> np.ndarray:
    function = sp.lambdify(symbols, expression, modules=["numpy"])
    evaluated = np.asarray(function(*values), dtype=np.complex128)

    if evaluated.shape == ():
        evaluated = np.full_like(values[0], evaluated, dtype=np.complex128)

    return evaluated


def _real_finite_mask(values: np.ndarray) -> np.ndarray:
    return np.isfinite(values.real) & np.isfinite(values.imag) & (np.abs(values.imag) < 1e-8)


def _get_parametric_symbol(expressions: list[sp.Expr]) -> sp.Symbol:
    free_symbols = set().union(*(expression.free_symbols for expression in expressions))
    if not free_symbols:
        return T
    if free_symbols <= {T}:
        return T
    if free_symbols <= {X}:
        return X
    raise PlotError("Comma-separated parametric plots use only one variable: `t` or `x`.")


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
