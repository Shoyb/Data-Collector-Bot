"""
Game commands for Data Collector Bot.
"""
import random

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
