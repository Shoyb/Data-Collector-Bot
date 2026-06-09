"""
Game commands for Data Collector Bot.
"""
import random
import time

import discord
from discord.ext import commands


RPS_CHOICES = ("rock", "paper", "scissors")
RPS_WINNERS = {
    "rock": "scissors",
    "paper": "rock",
    "scissors": "paper",
}
RPS_ALIASES = {
    "rock": "rock",
    "paper": "paper",
    "scissor": "scissors",
    "scissors": "scissors",
}
MENTAL_DIFFICULTIES = {"easy", "medium", "hard"}
MENTAL_TIMEOUT_SECONDS = 45
MAX_MENTAL_ROUNDS = 20
CONNECT4_ROWS = 6
CONNECT4_COLUMNS = 7
CONNECT4_COLUMN_NAMES = tuple(chr(ord("A") + index) for index in range(CONNECT4_COLUMNS))
CONNECT4_PLAYER = "X"
CONNECT4_BOT = "O"
CONNECT4_EMPTY = "."
CONNECT4_TIMEOUT_SECONDS = 90


async def process_game_commands(message: discord.Message) -> bool:
    """
    Process manual game commands.

    Args:
        message: Discord message object

    Returns:
        True if a game command was processed
    """
    msg = message.content.lower().strip()

    if not msg.startswith("data "):
        return False

    player_choice = RPS_ALIASES.get(msg.removeprefix("data ").strip())
    if not player_choice:
        return False

    bot_choice = random.choice(RPS_CHOICES)

    if player_choice == bot_choice:
        result = "It's a tie!"
    elif RPS_WINNERS[player_choice] == bot_choice:
        result = "You won!"
    else:
        result = "I won!"

    await message.channel.send(
        f"You chose **{player_choice}**. I chose **{bot_choice}**. {result}"
    )
    return True


def setup_game_commands(bot: commands.Bot) -> None:
    """Register game commands on the bot."""

    @bot.command(name="guess")
    async def guess(ctx: commands.Context, max_number: int = 100):
        """
        Play a number guessing game.

        Usage:
            !guess
            !guess 50
        """
        if max_number < 2:
            await ctx.send("Please choose a maximum number greater than 1.")
            return

        secret_number = random.randint(1, max_number)
        attempts = 0

        await ctx.send(
            f"I picked a number between 1 and {max_number}. "
            "Send your guesses here. Type `cancel` to stop."
        )

        def is_player_guess(message: discord.Message) -> bool:
            return message.author == ctx.author and message.channel == ctx.channel

        while True:
            try:
                message = await bot.wait_for(
                    "message",
                    check=is_player_guess,
                    timeout=60,
                )
            except TimeoutError:
                await ctx.send(
                    f"Game ended because there were no guesses for 60 seconds. "
                    f"The number was {secret_number}."
                )
                return

            guess_text = message.content.strip().lower()
            if guess_text in {"cancel", "stop", "quit"}:
                await ctx.send(
                    f"Game cancelled after {attempts} valid guesses. "
                    f"The number was {secret_number}."
                )
                return

            try:
                player_guess = int(guess_text)
            except ValueError:
                await ctx.send("Please send a whole number, or type `cancel` to stop.")
                continue

            attempts += 1

            if player_guess == secret_number:
                await ctx.send(
                    f"Correct! The number was {secret_number}. "
                    f"You guessed it in {attempts} steps."
                )
                return

            if player_guess > secret_number:
                await ctx.send("Too big. Try a smaller number.")
            else:
                await ctx.send("Too small. Try a bigger number.")

    @bot.command(name="mental", aliases=["mentalmath", "quickmath"])
    async def mental(ctx: commands.Context, *, options: str = ""):
        """
        Play a timed mental math challenge.

        Usage:
            !mental
            !mental 10
            !mental hard
            !mental 10 hard
        """
        try:
            rounds, difficulty = _parse_mental_options(options)
        except ValueError as exc:
            await ctx.send(str(exc))
            return

        correct = 0
        total_time = 0.0
        answered_rounds = 0

        await ctx.send(
            f"Mental math started: **{rounds}** rounds on **{difficulty}**. "
            f"You have {MENTAL_TIMEOUT_SECONDS} seconds per round. "
            "Type `cancel` to stop."
        )

        def is_player_answer(message: discord.Message) -> bool:
            return message.author == ctx.author and message.channel == ctx.channel

        for round_number in range(1, rounds + 1):
            expression, answer = _generate_mental_expression(difficulty)
            await ctx.send(f"Round {round_number}/{rounds}: `{expression}` = ?")
            start_time = time.perf_counter()

            try:
                message = await bot.wait_for(
                    "message",
                    check=is_player_answer,
                    timeout=MENTAL_TIMEOUT_SECONDS,
                )
            except TimeoutError:
                await ctx.send(
                    f"Time's up. The answer was **{answer}**.\n"
                    f"{_format_mental_summary(correct, answered_rounds, total_time)}"
                )
                return

            elapsed = time.perf_counter() - start_time
            answer_text = message.content.strip().lower()
            if answer_text in {"cancel", "stop", "quit"}:
                await ctx.send(
                    f"Challenge cancelled.\n"
                    f"{_format_mental_summary(correct, answered_rounds, total_time)}"
                )
                return

            try:
                player_answer = int(answer_text.replace(",", ""))
            except ValueError:
                await ctx.send(
                    f"That was not a whole number. The answer was **{answer}** "
                    f"({elapsed:.2f}s)."
                )
                answered_rounds += 1
                total_time += elapsed
                continue

            answered_rounds += 1
            total_time += elapsed

            if player_answer == answer:
                correct += 1
                await ctx.send(f"Correct in **{elapsed:.2f}s**.")
            else:
                await ctx.send(
                    f"Not quite. The answer was **{answer}** "
                    f"({elapsed:.2f}s)."
                )

        await ctx.send(_format_mental_summary(correct, answered_rounds, total_time))

    @bot.command(name="connect4", aliases=["c4"])
    async def connect4(ctx: commands.Context):
        """
        Play Connect Four against the bot.

        Usage:
            !connect4

        Moves:
            A-G or coordinate-style moves like A1, D4, G6
        """
        board = _create_connect4_board()
        await ctx.send(
            "Connect Four started. You are **X**, I am **O**.\n"
            "Send a move like `A`, `D`, `A1`, or `D4`. "
            "The piece drops into that column. Type `cancel` to stop.\n"
            f"{_format_connect4_board(board)}"
        )

        def is_player_move(message: discord.Message) -> bool:
            return message.author == ctx.author and message.channel == ctx.channel

        while True:
            try:
                message = await bot.wait_for(
                    "message",
                    check=is_player_move,
                    timeout=CONNECT4_TIMEOUT_SECONDS,
                )
            except TimeoutError:
                await ctx.send(
                    "Connect Four ended because there was no move for "
                    f"{CONNECT4_TIMEOUT_SECONDS} seconds."
                )
                return

            move_text = message.content.strip()
            if move_text.lower() in {"cancel", "stop", "quit"}:
                await ctx.send("Connect Four cancelled.")
                return

            try:
                player_column = _parse_connect4_move(move_text)
                player_row = _drop_connect4_piece(board, player_column, CONNECT4_PLAYER)
            except ValueError as exc:
                await ctx.send(f"{exc} Try `A` through `G`, or coordinates like `D4`.")
                continue

            if _has_connect4_winner(board, player_row, player_column, CONNECT4_PLAYER):
                await ctx.send(
                    f"You win!\n{_format_connect4_board(board)}"
                )
                return

            if _is_connect4_full(board):
                await ctx.send(f"It's a draw.\n{_format_connect4_board(board)}")
                return

            bot_column = _choose_connect4_bot_move(board)
            bot_row = _drop_connect4_piece(board, bot_column, CONNECT4_BOT)

            if _has_connect4_winner(board, bot_row, bot_column, CONNECT4_BOT):
                await ctx.send(
                    f"I played **{CONNECT4_COLUMN_NAMES[bot_column]}** and won.\n"
                    f"{_format_connect4_board(board)}"
                )
                return

            await ctx.send(
                f"I played **{CONNECT4_COLUMN_NAMES[bot_column]}**.\n"
                f"{_format_connect4_board(board)}"
            )

            if _is_connect4_full(board):
                await ctx.send("It's a draw.")
                return


def _parse_mental_options(options: str) -> tuple[int, str]:
    rounds = 5
    difficulty = "medium"

    for option in options.lower().split():
        if option.isdigit():
            rounds = int(option)
        elif option in MENTAL_DIFFICULTIES:
            difficulty = option
        else:
            raise ValueError(
                "Usage: `!mental`, `!mental 10`, `!mental hard`, or `!mental 10 hard`."
            )

    if rounds < 1 or rounds > MAX_MENTAL_ROUNDS:
        raise ValueError(f"Choose between 1 and {MAX_MENTAL_ROUNDS} rounds.")

    return rounds, difficulty


def _generate_mental_expression(difficulty: str) -> tuple[str, int]:
    if difficulty == "easy":
        return _generate_easy_mental_expression()
    if difficulty == "hard":
        return _generate_hard_mental_expression()
    return _generate_medium_mental_expression()


def _generate_easy_mental_expression() -> tuple[str, int]:
    operation = random.choice(("add", "subtract", "multiply"))
    if operation == "add":
        left = random.randint(2, 50)
        right = random.randint(2, 50)
        return f"{left} + {right}", left + right
    if operation == "subtract":
        answer = random.randint(2, 50)
        right = random.randint(2, 50)
        left = answer + right
        return f"{left} - {right}", answer

    left = random.randint(2, 12)
    right = random.randint(2, 12)
    return f"{left} * {right}", left * right


def _generate_medium_mental_expression() -> tuple[str, int]:
    operation = random.choice(("multiply_add", "multiply_subtract", "parentheses"))
    if operation == "multiply_add":
        left = random.randint(3, 15)
        middle = random.randint(3, 15)
        right = random.randint(5, 40)
        return f"{left} * {middle} + {right}", left * middle + right
    if operation == "multiply_subtract":
        left = random.randint(5, 18)
        middle = random.randint(3, 15)
        right = random.randint(5, 40)
        return f"{left} * {middle} - {right}", left * middle - right

    left = random.randint(5, 25)
    middle = random.randint(5, 25)
    right = random.randint(2, 9)
    return f"({left} + {middle}) * {right}", (left + middle) * right


def _generate_hard_mental_expression() -> tuple[str, int]:
    operation = random.choice(("two_products", "square_offset", "exact_division"))
    if operation == "two_products":
        left = random.randint(8, 24)
        middle = random.randint(6, 19)
        right = random.randint(8, 24)
        last = random.randint(6, 19)
        return f"{left} * {middle} + {right} * {last}", left * middle + right * last
    if operation == "square_offset":
        base = random.randint(11, 30)
        offset = random.randint(10, 90)
        return f"{base}^2 - {offset}", base * base - offset

    divisor = random.randint(3, 12)
    answer = random.randint(12, 60)
    dividend = divisor * answer
    addend = random.randint(10, 75)
    return f"{dividend} / {divisor} + {addend}", answer + addend


def _format_mental_summary(correct: int, answered_rounds: int, total_time: float) -> str:
    if answered_rounds == 0:
        return "No answered rounds yet."

    average_time = total_time / answered_rounds
    return (
        f"Final score: **{correct}/{answered_rounds}** correct. "
        f"Total answer time: **{total_time:.2f}s**. "
        f"Average: **{average_time:.2f}s**."
    )


def _create_connect4_board() -> list[list[str]]:
    return [[CONNECT4_EMPTY for _ in range(CONNECT4_COLUMNS)] for _ in range(CONNECT4_ROWS)]


def _format_connect4_board(board: list[list[str]]) -> str:
    rendered_rows = []
    for display_row, board_row in enumerate(board):
        row_number = CONNECT4_ROWS - display_row
        cells = " ".join(_connect4_cell_symbol(cell) for cell in board_row)
        rendered_rows.append(f"{row_number} | {cells}")

    header = "    " + " ".join(CONNECT4_COLUMN_NAMES)
    return "```text\n" + header + "\n" + "\n".join(rendered_rows) + "\n```"


def _connect4_cell_symbol(cell: str) -> str:
    if cell == CONNECT4_PLAYER:
        return "X"
    if cell == CONNECT4_BOT:
        return "O"
    return "."


def _parse_connect4_move(move_text: str) -> int:
    compact = move_text.strip().upper().replace(" ", "")
    if not compact:
        raise ValueError("Enter a move.")

    column_name = compact[0]
    if column_name not in CONNECT4_COLUMN_NAMES:
        raise ValueError("That column does not exist.")

    suffix = compact[1:]
    if suffix:
        if not suffix.isdigit():
            raise ValueError("Use chess-style coordinates like `A1` or `D4`.")
        row_number = int(suffix)
        if row_number < 1 or row_number > CONNECT4_ROWS:
            raise ValueError(f"Rows are 1 through {CONNECT4_ROWS}.")

    return CONNECT4_COLUMN_NAMES.index(column_name)


def _drop_connect4_piece(board: list[list[str]], column: int, piece: str) -> int:
    for row in range(CONNECT4_ROWS - 1, -1, -1):
        if board[row][column] == CONNECT4_EMPTY:
            board[row][column] = piece
            return row

    raise ValueError(f"Column {CONNECT4_COLUMN_NAMES[column]} is full.")


def _has_connect4_winner(board: list[list[str]], row: int, column: int, piece: str) -> bool:
    return any(
        _count_connect4_direction(board, row, column, piece, row_step, column_step)
        + _count_connect4_direction(board, row, column, piece, -row_step, -column_step)
        - 1
        >= 4
        for row_step, column_step in ((0, 1), (1, 0), (1, 1), (1, -1))
    )


def _count_connect4_direction(
    board: list[list[str]],
    row: int,
    column: int,
    piece: str,
    row_step: int,
    column_step: int,
) -> int:
    count = 0
    current_row = row
    current_column = column

    while (
        0 <= current_row < CONNECT4_ROWS
        and 0 <= current_column < CONNECT4_COLUMNS
        and board[current_row][current_column] == piece
    ):
        count += 1
        current_row += row_step
        current_column += column_step

    return count


def _is_connect4_full(board: list[list[str]]) -> bool:
    return all(board[0][column] != CONNECT4_EMPTY for column in range(CONNECT4_COLUMNS))


def _choose_connect4_bot_move(board: list[list[str]]) -> int:
    valid_columns = _get_connect4_valid_columns(board)

    winning_column = _find_connect4_winning_column(board, valid_columns, CONNECT4_BOT)
    if winning_column is not None:
        return winning_column

    blocking_column = _find_connect4_winning_column(board, valid_columns, CONNECT4_PLAYER)
    if blocking_column is not None:
        return blocking_column

    center_order = sorted(valid_columns, key=lambda column: abs(column - CONNECT4_COLUMNS // 2))
    best_columns = center_order[:3] if len(center_order) >= 3 else center_order
    return random.choice(best_columns)


def _get_connect4_valid_columns(board: list[list[str]]) -> list[int]:
    return [
        column
        for column in range(CONNECT4_COLUMNS)
        if board[0][column] == CONNECT4_EMPTY
    ]


def _find_connect4_winning_column(
    board: list[list[str]],
    valid_columns: list[int],
    piece: str,
) -> int | None:
    for column in valid_columns:
        row = _get_connect4_open_row(board, column)
        if row is None:
            continue

        board[row][column] = piece
        is_winner = _has_connect4_winner(board, row, column, piece)
        board[row][column] = CONNECT4_EMPTY

        if is_winner:
            return column

    return None


def _get_connect4_open_row(board: list[list[str]], column: int) -> int | None:
    for row in range(CONNECT4_ROWS - 1, -1, -1):
        if board[row][column] == CONNECT4_EMPTY:
            return row

    return None
