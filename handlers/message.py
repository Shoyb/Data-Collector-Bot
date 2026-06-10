"""
Message handler for Data Collector Bot.
Allows users to send a message through the bot, including mentions.
"""

import discord

MESSAGE_PREFIXES = (
    "data message ",
    "data msg ",
    "!message ",
    "!msg ",
)


def _usage_text() -> str:
    return "Usage: `data message <text>` or `data msg <text>` - the bot will resend the text."


async def process_message_commands(message: discord.Message) -> bool:
    """
    Process message delivery commands.

    Args:
        message: Discord message object

    Returns:
        True if a message command was processed
    """
    content = message.content
    lowered = content.lower()

    prefix = next(
        (candidate for candidate in MESSAGE_PREFIXES if lowered.startswith(candidate)),
        None,
    )
    if not prefix:
        return False

    text = content[len(prefix):].strip()
    if not text:
        await message.channel.send(
            "❌ No message provided. " + _usage_text()
        )
        return True

    allowed_mentions = discord.AllowedMentions(users=True, roles=True, everyone=False)
    await message.channel.send(text, allowed_mentions=allowed_mentions)
    return True
