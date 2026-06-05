"""
Transformer NLP command handlers for Data Collector Bot.
Provides Discord commands for AI NLP tasks.
"""
import asyncio
import discord
from core.transformers_nlp import transformer_models


class TransformerHandler:
    """Handles transformer-based NLP commands."""
    
    @staticmethod
    async def handle_summarize(message: discord.Message) -> bool:
        """Handle !summarize command."""
        msg = message.content.lower()
        if msg.startswith('!summarize '):
            text = message.content[len('!summarize '):]
            
            if not text or len(text.split()) < 50:
                await message.channel.send(
                    "❌ Text too short! Please provide at least 50 words.\n\n"
                    "Usage: `!summarize [your text here]`"
                )
                return True
            
            if not transformer_models.enabled:
                await message.channel.send(
                    "❌ Transformer commands are disabled. Set HF_API_TOKEN in your environment or .env file to enable summarization."
                )
                return True

            await message.channel.send("⏳ Summarizing text...")
            
            try:
                loop = asyncio.get_running_loop()
                summary = await loop.run_in_executor(
                    None, transformer_models.summarize, text
                )
                
                if summary:
                    await message.channel.send(f"**Summary:**\n{summary}")
                else:
                    await message.channel.send("❌ Failed to summarize text.")
            except Exception as e:
                await message.channel.send(f"❌ Error: {str(e)}")
            
            return True
        return False
    
    @staticmethod
    async def handle_classify(message: discord.Message) -> bool:
        """Handle !classify command."""
        msg = message.content.lower()
        if msg.startswith('!classify '):
            content = message.content[len('!classify '):]
            
            # Parse: !classify text | label1, label2, label3
            if '|' not in content:
                await message.channel.send(
                    "❌ Invalid format!\n\n"
                    "Usage: `!classify [text] | [label1], [label2], [label3]`\n"
                    "Example: `!classify This is awesome! | positive, negative, neutral`"
                )
                return True
            
            text, labels_str = content.split('|', 1)
            text = text.strip()
            labels = [l.strip() for l in labels_str.split(',')]
            
            if not text or not labels or len(labels) < 2:
                await message.channel.send(
                    "❌ Need at least text and 2+ labels!\n\n"
                    "Usage: `!classify [text] | [label1], [label2], [label3]`"
                )
                return True
            
            if not transformer_models.enabled:
                await message.channel.send(
                    "❌ Transformer commands are disabled. Set HF_API_TOKEN in your environment or .env file to enable classification."
                )
                return True

            await message.channel.send("⏳ Classifying text...")
            
            try:
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(
                    None, transformer_models.zero_shot_classify, text, labels
                )
                
                if result:
                    response = f"**Classification Result:**\n"
                    response += f"Text: `{result['text']}`\n"
                    response += f"Top Match: **{result['top']}**\n\n"
                    response += "**All Scores:**\n"
                    for label, score in zip(result['labels'], result['scores']):
                        response += f"  • {label}: {score:.2%}\n"
                    await message.channel.send(response)
                else:
                    await message.channel.send("❌ Failed to classify text.")
            except Exception as e:
                await message.channel.send(f"❌ Error: {str(e)}")
            
            return True
        return False
    
    @staticmethod
    async def handle_mask(message: discord.Message) -> bool:
        """Handle !mask command."""
        msg = message.content.lower()
        if msg.startswith('!mask '):
            text = message.content[len('!mask '):]
            
            if '[mask]' not in text.lower():
                await message.channel.send(
                    "❌ Text must contain `[MASK]` token!\n\n"
                    "Usage: `!mask [text with MASK token]`\n"
                    "Example: `!mask The capital of France is [MASK]`"
                )
                return True
            
            # Convert to uppercase for BERT
            text = text.replace('[mask]', '[MASK]').replace('[Mask]', '[MASK]')
            
            if not transformer_models.enabled:
                await message.channel.send(
                    "❌ Transformer commands are disabled. Set HF_API_TOKEN in your environment or .env file to enable mask filling."
                )
                return True

            await message.channel.send("⏳ Filling mask...")
            
            try:
                loop = asyncio.get_running_loop()
                results = await loop.run_in_executor(
                    None, transformer_models.fill_mask, text
                )
                
                if results:
                    response = f"**Mask Predictions for:** `{text}`\n\n"
                    for i, result in enumerate(results, 1):
                        response += f"{i}. `{result['token']}` ({result['score']:.2%})\n"
                        response += f"   → {result['sequence']}\n\n"
                    await message.channel.send(response)
                else:
                    await message.channel.send("❌ No [MASK] token found.")
            except Exception as e:
                await message.channel.send(f"❌ Error: {str(e)}")
            
            return True
        return False


async def process_transformer_commands(message: discord.Message) -> bool:
    """
    Process transformer-based NLP commands.
    
    Args:
        message: Discord message object
        
    Returns:
        True if a command was processed
    """
    handlers = [
        TransformerHandler.handle_summarize,
        TransformerHandler.handle_classify,
        TransformerHandler.handle_mask,
    ]
    
    for handler in handlers:
        if await handler(message):
            return True
    
    return False
