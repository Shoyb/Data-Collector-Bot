"""
Central configuration file for the Data Collector Bot.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Discord Configuration
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
COMMAND_PREFIX = "!"

# Database Configuration
DATABASE_NAME = "database.db"

# LLM Configuration
LLM_SERVER_URL = "http://127.0.0.1:8080/v1/chat/completions"
LLM_MAX_TOKENS = 4096
LLM_TEMPERATURE = 0.7
LLM_TIMEOUT = 300
LLM_MAX_THINKING_TOKENS = 500
LLM_REPEAT_PENALTY = 1.1
LLM_MODEL_PATH = r"C:\llama\models\Qwen3.5-0.8B-Q4_K_M.gguf"
LLM_SERVER_PATH = r"C:\llama\llama-server.exe"

# Hugging Face API Configuration
# api-inference.huggingface.co is deprecated — now using router.huggingface.co (handled in transformers_nlp.py)
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
HF_SUMMARIZATION_MODEL = "sshleifer/distilbart-cnn-12-6"   # fast ~300MB, replaces bart-large-cnn (1.6GB, times out)
HF_CLASSIFICATION_MODEL = "facebook/bart-large-mnli"        # zero-shot classification
HF_MASKING_MODEL = "google-bert/bert-base-uncased"          # correct model ID (bert-base-uncased is rejected)

# External APIs Configuration
ZENQUOTES_API_URL = "https://zenquotes.io/api/random"
MEME_API_URL = "https://meme-api.com/gimme"
