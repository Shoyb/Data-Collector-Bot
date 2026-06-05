"""
Event handlers for Data Collector Bot.
Processes Discord events like message reactions and user interactions.
"""
import random
import discord
from utils.constants import SAD_WORDS, ENCOURAGEMENT_MESSAGES


class EventHandler:
    """Handles bot events."""
    
    @staticmethod
    async def handle_sad_words(message: discord.Message):
        """
        Detect sad words in message and send encouragement.
        
        Args:
            message: Discord message object
        """
        if any(word in message.content.lower() for word in SAD_WORDS):
            encouragement = random.choice(ENCOURAGEMENT_MESSAGES)
            await message.channel.send(encouragement)


async def process_events(message: discord.Message):
    """
    Process all events in message.
    
    Args:
        message: Discord message object
    """
    await EventHandler.handle_sad_words(message)
