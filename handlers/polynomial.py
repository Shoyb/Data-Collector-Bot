"""
Polynomial solver command handler for Data Collector Bot.
"""
import re

import discord
import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    standard_transformations,
)


COMMAND_PREFIXES = ("data polynomial ", "data poly ", "data roots ", "data solve ")
POLYNOMIAL_PATTERN = re.compile(r"^[0-9xX+\-*/^().=\s]+$")
TRANSFORMATIONS = standard_transformations + (
    convert_xor,
    implicit_multiplication_application,
)


class PolynomialError(ValueError):
    """Raised when a polynomial cannot be parsed or solved."""


def solve_polynomial(raw_polynomial: str) -> list[complex]:
    """Solve a polynomial expression or equation for x using SymPy."""
    if not POLYNOMIAL_PATTERN.fullmatch(raw_polynomial):
        raise PolynomialError("Use only numbers, x, operators, parentheses, and `=`.")

    x = sp.Symbol("x")
    expression_text = raw_polynomial.lower().replace(" ", "")

    if expression_text.count("=") > 1:
        raise PolynomialError("Use only one equals sign.")

    if "=" in expression_text:
        left_text, right_text = expression_text.split("=", 1)
        expression = _parse_expression(left_text, x) - _parse_expression(right_text, x)
    else:
        expression = _parse_expression(expression_text, x)

    try:
        polynomial = sp.Poly(sp.expand(expression), x)
    except sp.PolynomialError as exc:
        raise PolynomialError("That is not a polynomial in x.") from exc

    if polynomial.degree() < 1:
        raise PolynomialError("Enter a polynomial with x, like `x^2 - 5x + 6`.")

    return [complex(root) for root in sp.nroots(polynomial.as_expr())]


def _parse_expression(expression_text: str, x: sp.Symbol) -> sp.Expr:
    if not expression_text:
        raise PolynomialError("The polynomial expression is empty.")

    try:
        return sp.parsing.sympy_parser.parse_expr(
            expression_text,
            local_dict={"x": x},
            transformations=TRANSFORMATIONS,
            evaluate=True,
        )
    except (SyntaxError, TypeError, ValueError, sp.SympifyError) as exc:
        raise PolynomialError("That polynomial expression is not valid.") from exc


async def process_polynomial_commands(message: discord.Message) -> bool:
    """
    Process polynomial solver commands.

    Args:
        message: Discord message object

    Returns:
        True if a polynomial command was processed
    """
    msg = message.content.strip()
    lowered = msg.lower()

    prefix = next(
        (candidate for candidate in COMMAND_PREFIXES if lowered.startswith(candidate)),
        None,
    )
    if not prefix:
        return False

    raw_polynomial = msg[len(prefix):].strip()
    try:
        roots = solve_polynomial(raw_polynomial)
    except PolynomialError as exc:
        await message.channel.send(f"Could not solve that polynomial: {exc}")
        return True

    formatted_roots = ", ".join(_format_root(root) for root in roots)
    await message.channel.send(
        f"Roots for `{raw_polynomial}`:\n**x = {formatted_roots}**"
    )
    return True


def _format_root(root: complex) -> str:
    real = 0.0 if abs(root.real) < 1e-12 else root.real
    imaginary = 0.0 if abs(root.imag) < 1e-12 else root.imag

    if imaginary == 0.0:
        return _format_number(real)

    sign = "+" if imaginary > 0 else "-"
    return f"{_format_number(real)} {sign} {_format_number(abs(imaginary))}i"


def _format_number(value: float) -> str:
    if float(value).is_integer():
        return str(int(value))
    return f"{value:.12g}"
