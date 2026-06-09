"""
Data Collector Bot - Main Entry Point
A modular Discord bot for data collection, quotes, and LLM integration.
"""
import discord
from discord.ext import commands
from config import DISCORD_TOKEN, COMMAND_PREFIX
from handlers.calculator import process_calculator_commands
from handlers.commands import process_commands
from handlers.events import process_events
from handlers.games import process_game_commands, setup_game_commands
from handlers.plotter import process_plot_commands
from handlers.polynomial import process_polynomial_commands
from handlers.transformers import process_transformer_commands
from core.llm import llm_manager


# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)
setup_game_commands(bot)


@bot.event
async def on_ready():
    """Called when bot successfully connects to Discord."""
    print(f'Bot ready as {bot.user}')


@bot.event
async def on_message(message: discord.Message):
    """
    Handle incoming messages.

    Args:
        message: Discord message object
    """
    # Ignore bot's own messages
    if message.author == bot.user:
        return

    # Run manual command/event handlers first.
    # If one of them handled the message, skip bot.process_commands to avoid
    # CommandNotFound errors for commands like !summarize, !classify, !mask
    # that are handled manually rather than registered as @bot.command.
    handled = await process_commands(message)
    if not handled:
        handled = await process_transformer_commands(message)
    if not handled:
        handled = await process_plot_commands(message)
    if not handled:
        handled = await process_polynomial_commands(message)
    if not handled:
        handled = await process_calculator_commands(message)
    if not handled:
        handled = await process_game_commands(message)

    await process_events(message)

    # Only pass to discord.py's command system if not already handled.
    # This lets @bot.command decorators (e.g. !ask) still work.
    if not handled:
        await bot.process_commands(message)


@bot.command(name="ask")
async def ask(ctx: commands.Context, *, raw: str):
    """
    Ask Qwen LLM a question.

    Usage:
        !ask What is the capital of France?
        !ask --tokens 512 --temp 0.9 Explain quantum computing

    Note: Start the LLM server first with: !data llm start
    """
    # Check if LLM server is running
    if llm_manager.llama_process is None:
        await ctx.send(
            "❌ LLM server is not running!\n\n"
            "Start it with: `!data llm start`"
        )
        return

    try:
        question, max_tokens, temperature = llm_manager.parse_args(raw)

        tok_display = max_tokens if max_tokens is not None else 4096
        temp_display = temperature if temperature is not None else 0.7

        msg = await ctx.send(
            f"⏳ **Generating...** `0.0s`\n"
            f"-# Using `Qwen3.5-0.8B` · max_tokens=`{tok_display}` · temp=`{temp_display}`"
        )

        try:
            # Run LLM query in executor to avoid blocking
            answer, reasoning, stats = await bot.loop.run_in_executor(
                None, llm_manager.ask_qwen, question, max_tokens, temperature
            )

            response = f"**Answer:** {answer}\n\n**Stats:** {stats['elapsed']:.2f}s"
            if reasoning:
                response += f"\n**Reasoning:** {reasoning}"

            await msg.edit(content=response)
        except Exception as e:
            await msg.edit(content=f"❌ Error: {str(e)}")
    except Exception as e:
        await ctx.send(f"❌ Command error: {str(e)}")


def main():
    """Start the bot."""
    if not DISCORD_TOKEN:
        raise ValueError("DISCORD_TOKEN not found in environment variables!")

    print("Starting Data Collector Bot...")
    bot.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
