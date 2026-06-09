"""
Calculator command handler for Data Collector Bot.
"""
import ast
import math
import operator

import discord


ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
}

ALLOWED_FUNCTIONS = {
    "sqrt": math.sqrt,
    "log": math.log10,
    "ln": math.log,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "arctan": math.atan,
    "atan": math.atan,
    "arccos": math.acos,
    "arcos": math.acos,
    "acos": math.acos,
    "arcsin": math.asin,
    "asin": math.asin,
}

ALLOWED_CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
}


class CalculatorError(ValueError):
    """Raised when an expression cannot be safely calculated."""


def calculate(expression: str) -> float:
    """Safely calculate a supported math expression."""
    normalized_expression = expression.replace("^", "**")

    try:
        tree = ast.parse(normalized_expression, mode="eval")
    except SyntaxError as exc:
        raise CalculatorError("That math expression is not valid.") from exc

    return _evaluate_node(tree.body)


def _evaluate_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value

    if isinstance(node, ast.Name):
        try:
            return ALLOWED_CONSTANTS[node.id]
        except KeyError as exc:
            raise CalculatorError(f"`{node.id}` is not a supported constant.") from exc

    if isinstance(node, ast.BinOp):
        operator_function = ALLOWED_OPERATORS.get(type(node.op))
        if not operator_function:
            raise CalculatorError("That operator is not supported.")

        left = _evaluate_node(node.left)
        right = _evaluate_node(node.right)
        return operator_function(left, right)

    if isinstance(node, ast.UnaryOp):
        operand = _evaluate_node(node.operand)
        if isinstance(node.op, ast.UAdd):
            return operand
        if isinstance(node.op, ast.USub):
            return -operand
        raise CalculatorError("That unary operator is not supported.")

    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise CalculatorError("Only simple math functions are supported.")

        function = ALLOWED_FUNCTIONS.get(node.func.id.lower())
        if not function:
            raise CalculatorError(f"`{node.func.id}` is not a supported function.")

        if len(node.args) != 1 or node.keywords:
            raise CalculatorError("Math functions need exactly one value.")

        return function(_evaluate_node(node.args[0]))

    raise CalculatorError("That expression is not supported.")


async def process_calculator_commands(message: discord.Message) -> bool:
    """
    Process calculator commands.

    Args:
        message: Discord message object

    Returns:
        True if a calculator command was processed
    """
    msg = message.content.strip()
    if not msg.lower().startswith("data "):
        return False

    expression = msg[5:].strip()
    if not _looks_like_math(expression):
        return False

    try:
        answer = calculate(expression)
    except (CalculatorError, ValueError, ZeroDivisionError, OverflowError) as exc:
        await message.channel.send(f"Could not calculate that: {exc}")
        return True

    await message.channel.send(f"`{expression}` = **{_format_answer(answer)}**")
    return True


def _looks_like_math(expression: str) -> bool:
    if any(character.isdigit() for character in expression):
        return True

    lowered = expression.lower()
    return lowered in ALLOWED_CONSTANTS or any(
        lowered.startswith(f"{function_name}(")
        for function_name in ALLOWED_FUNCTIONS
    )


def _format_answer(answer: float) -> str:
    if isinstance(answer, float) and answer.is_integer():
        return str(int(answer))
    return f"{answer:.12g}"
