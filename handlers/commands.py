"""
Command handlers for Data Collector Bot.
Processes user commands from Discord messages.
"""
import random
import requests
import discord
from core.api import api_manager
from core.llm import llm_manager
from handlers.help import process_help_commands
from handlers.message import process_message_commands
from utils.constants import CUSTOM_RESPONSES
from words import swear_words


class CommandHandler:
    """Handles bot commands."""
    
    @staticmethod
    async def handle_hello(message: discord.Message) -> bool:
        """Handle !hello command."""
        if message.content.startswith('!hello'):
            await message.channel.send('Hello!')
            return True
        return False
    
    @staticmethod
    async def handle_quote(message: discord.Message) -> bool:
        """Handle quote commands."""
        msg = message.content.lower().strip()
        if msg.startswith('quote') or msg.startswith('!quote') or msg.startswith('data quote'):
            quote = api_manager.get_random_quote()
            if quote:
                await message.channel.send(quote)
            else:
                await message.channel.send("Could not fetch quote at this time.")
            return True
        return False

    @staticmethod
    async def handle_data_meme(message: discord.Message) -> bool:
        """Handle data meme command."""
        msg = message.content.lower().strip()
        if msg.startswith('data meme') or msg.startswith('!meme'):
            meme = api_manager.get_random_meme()
            if not meme:
                await message.channel.send("Could not fetch a meme at this time.")
                return True

            image_url = meme.get('url') or meme.get('image') or meme.get('preview')
            title = meme.get('title') or meme.get('postLink') or "Random meme"
            if image_url:
                embed = discord.Embed(title=title, color=discord.Color.random())
                embed.set_image(url=image_url)
                await message.channel.send(embed=embed)
            else:
                await message.channel.send(f"Meme: {title}")
            return True
        return False

    @staticmethod
    async def handle_data_waifu(message: discord.Message) -> bool:
        """Handle data waifu command."""
        msg = message.content.lower().strip()
        if msg.startswith('data waifu'):
            try:
                response = requests.get("https://api.waifu.im/images", timeout=10)
                response.raise_for_status()
                data = response.json()
                items = data.get('items') or data.get('images')
                if not items or not isinstance(items, list):
                    await message.channel.send("Could not fetch a waifu image at this time.")
                    return True

                image_url = items[0].get('url')
                if not image_url:
                    await message.channel.send("Could not fetch a waifu image at this time.")
                    return True

                embed = discord.Embed(
                    title="Here is your waifu image!",
                    color=discord.Color.random()
                )
                embed.set_image(url=image_url)
                await message.channel.send(embed=embed)
            except Exception as e:
                await message.channel.send(f"Could not fetch a waifu image: {str(e)}")
            return True
        return False
    
    @staticmethod
    async def handle_data_curse(message: discord.Message) -> bool:
        """Handle data curse command."""
        msg = message.content.lower()
        if msg.startswith('data curse'):
            curse = random.choice(swear_words) if swear_words else "No curses available!"
            await message.channel.send(curse)
            return True
        return False
    
    @staticmethod
    async def handle_custom_response(message: discord.Message) -> bool:
        """Handle custom predefined responses."""
        msg = message.content.lower()
        for trigger, response in CUSTOM_RESPONSES.items():
            if msg.startswith(trigger):
                await message.channel.send(response)
                return True
        return False
    
    @staticmethod
    async def handle_llm_start(message: discord.Message) -> bool:
        """Handle data llm start command."""
        msg = message.content.lower()
        if msg.startswith('data llm start'):
            await message.channel.send("🚀 Starting LLM server...")
            success = llm_manager.start_server()
            if success:
                await message.channel.send("✅ LLM server started! You can now use `!ask` command.")
            else:
                await message.channel.send("❌ Failed to start LLM server. Check if llama.cpp is installed.")
            return True
        return False
    
    @staticmethod
    async def handle_llm_stop(message: discord.Message) -> bool:
        """Handle data llm stop command."""
        msg = message.content.lower()
        if msg.startswith('data llm stop'):
            await message.channel.send("🛑 Stopping LLM server...")
            llm_manager.stop_server()
            await message.channel.send("✅ LLM server stopped.")
            return True
        return False


async def process_commands(message: discord.Message) -> bool:
    """
    Process all commands in message.
    
    Args:
        message: Discord message object
        
    Returns:
        True if a command was processed
    """
    handlers = [
        CommandHandler.handle_hello,
        CommandHandler.handle_quote,
        process_help_commands,
        process_message_commands,
        CommandHandler.handle_data_curse,
        CommandHandler.handle_data_meme,
        CommandHandler.handle_data_waifu,
        CommandHandler.handle_llm_start,
        CommandHandler.handle_llm_stop,
        CommandHandler.handle_custom_response,
    ]
    
    for handler in handlers:
        if await handler(message):
            return True
    
    return False
