"""
Help command module for Data Collector Bot.
"""

import discord

COMMANDS = {
    "hello": {
        "display": "!hello",
        "description": "Say hello to the bot.",
        "usage": "`!hello`",
    },
    "quote": {
        "display": "quote / !quote / data quote",
        "description": "Get a random quote.",
        "usage": "`quote`, `!quote`, or `data quote`",
    },
    "meme": {
        "display": "data meme",
        "description": "Fetch a random meme image.",
        "usage": "`data meme`",
    },
    "waifu": {
        "display": "data waifu",
        "description": "Fetch a random waifu image.",
        "usage": "`data waifu`",
    },
    "curse": {
        "display": "data curse",
        "description": "Send a random data curse.",
        "usage": "`data curse`",
    },
    "rps": {
        "display": "data rock / data paper / data scissors",
        "description": "Play rock-paper-scissors with the bot.",
        "usage": "`data rock`, `data paper`, or `data scissors`",
    },
    "llm": {
        "display": "data llm start / data llm stop",
        "description": "Start or stop the local LLM server used by `!ask`.",
        "usage": (
            "`data llm start` - Start the LLM server.\n"
            "`data llm stop` - Stop the LLM server.\n"
            "`!ask <question>` - Ask the LLM once the server is running."
        ),
    },
    "ask": {
        "display": "!ask <question>",
        "description": "Ask the Qwen LLM a question.",
        "usage": "`!ask What is the capital of France?`",
    },
    "summarize": {
        "display": "!summarize [text]",
        "description": "Summarize long text using transformer NLP.",
        "usage": "`!summarize [your text here]`",
    },
    "classify": {
        "display": "!classify [text] | [label1], [label2], [label3]",
        "description": "Classify text into labels.",
        "usage": "`!classify This is awesome! | positive, negative, neutral`",
    },
    "mask": {
        "display": "!mask [text with MASK token]",
        "description": "Fill in a masked token in a sentence.",
        "usage": "`!mask The capital of France is [MASK]`",
    },
    "plot": {
        "display": "data plot <expression> [from a to b]",
        "description": "Plot a mathematical function or parametric curve.",
        "usage": "`data plot x^2 from -10 to 10`",
    },
    "polynomial": {
        "display": "data polynomial / data poly / data roots / data solve <expression>",
        "description": "Solve polynomial roots or equations in x.",
        "usage": "`data polynomial x^2 - 5x + 6`",
    },
    "message": {
        "display": "data message <text>",
        "description": "Send a message through the bot, preserving mentions.",
        "usage": "`data message Hello <@123456789012345678>`",
    },
    "guess": {
        "display": "!guess [max_number]",
        "description": "Play a number guessing game.",
        "usage": "`!guess` or `!guess 50`",
    },
    "mental": {
        "display": "!mental [rounds] [difficulty]",
        "description": "Play a timed mental math challenge.",
        "usage": "`!mental`, `!mental 10`, `!mental hard`, or `!mental 10 hard`",
    },
    "words": {
        "display": "!words [include=abc] [pos2=a] [pos5=c]",
        "description": "Find 5-letter words filtered by required letters and positions.",
        "usage": (
            "`!words`\n"
            "`!words abc`\n"
            "`!words include=abc pos2=a pos5=c`"
        ),
    },
    "connect4": {
        "display": "!connect4",
        "description": "Play Connect Four against the bot.",
        "usage": (
            "`!connect4`\n"
            "Moves: A-G or coordinates like `A1`, `D4`, `G6`"
        ),
    },
}

ALIASES = {
    "hello": "hello",
    "quote": "quote",
    "meme": "meme",
    "waifu": "waifu",
    "curse": "curse",
    "rock": "rps",
    "paper": "rps",
    "scissors": "rps",
    "scissor": "rps",
    "llm": "llm",
    "ask": "ask",
    "summarize": "summarize",
    "classify": "classify",
    "mask": "mask",
    "plot": "plot",
    "graph": "plot",
    "polynomial": "polynomial",
    "poly": "polynomial",
    "roots": "polynomial",
    "solve": "polynomial",
    "guess": "guess",
    "mental": "mental",
    "mentalmath": "mental",
    "quickmath": "mental",
    "words": "words",
    "connect4": "connect4",
    "c4": "connect4",
}


def _build_summary() -> str:
    lines = [
        "📘 **Data Collector Bot Commands**",
        "Use `data help <command>` for detailed usage.",
        "",
    ]
    for key in (
        "hello",
        "quote",
        "meme",
        "waifu",
        "curse",
        "rps",
        "llm",
        "ask",
        "summarize",
        "classify",
        "mask",
        "plot",
        "polynomial",
        "message",
        "guess",
        "mental",
        "words",
        "connect4",
    ):
        info = COMMANDS[key]
        lines.append(f"• `{info['display']}` — {info['description']}")
    return "\n".join(lines)


def _build_detail(command_key: str) -> str:
    info = COMMANDS[command_key]
    lines = [
        f"📘 **Help: {info['display']}**",
        info["description"],
        "",
        "**Usage:**",
        info["usage"],
    ]
    if command_key == "llm":
        lines.append("\nNote: Start the LLM server first with `data llm start` before using `!ask`.")
    return "\n".join(lines)


def _normalize_command_name(raw: str) -> str | None:
    raw = raw.strip().lower()
    if not raw:
        return None
    # Accept multi-word queries like "llm start" or "data plot".
    if raw.startswith("data "):
        raw = raw[len("data "):].strip()
    if raw.startswith("!"):
        raw = raw[1:]
    if raw.startswith("llm"):
        return "llm"
    if raw.startswith("connect4") or raw.startswith("c4"):
        return "connect4"
    if raw.startswith("mental") or raw.startswith("mentalmath") or raw.startswith("quickmath"):
        return "mental"
    parts = raw.split()
    if not parts:
        return None
    return ALIASES.get(parts[0])


async def process_help_commands(message: discord.Message) -> bool:
    """
    Process help commands triggered by `data help`.
    """
    text = message.content.strip()
    if not text.lower().startswith("data help"):
        return False

    remainder = text[len("data help"):].strip()
    if not remainder:
        await message.channel.send(_build_summary())
        return True

    command_key = _normalize_command_name(remainder)
    if not command_key or command_key not in COMMANDS:
        await message.channel.send(
            "❌ Unknown command. Use `data help` to see all available commands."
        )
        return True

    await message.channel.send(_build_detail(command_key))
    return True
