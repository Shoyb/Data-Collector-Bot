# Data Collector Bot

A modular Discord bot for data collection, quotes, encouragement messages, and LLM integration.

## Project Structure

```
Data_Collector_Bot/
├── main.py                 # Entry point - runs the bot
├── config.py              # Centralized configuration
├── core/                   # Core functionality modules
│   ├── __init__.py
│   ├── database.py        # Database operations (SQLite)
│   ├── api.py            # External API integrations
│   └── llm.py            # LLM server management & Qwen inference
├── handlers/               # Message and event handlers
│   ├── __init__.py
│   ├── commands.py       # Command processing
│   └── events.py         # Event processing
├── utils/                  # Utility modules
│   ├── __init__.py
│   └── constants.py      # Constants and word lists
├── tests/                  # Test modules
│   ├── __init__.py
│   └── test_meme_api.py  # Meme API tests
├── words.py              # (Legacy) Word lists
├── gwen.py               # (Legacy) LLM module
└── README.md
```

## Features

### Commands
- **`!hello`** - Simple greeting
- **`!quote`** - Get a random inspirational quote
- **`!ask <question>`** - Ask Qwen LLM (requires llama.cpp server)
  - Optional flags: `--tokens <num>` and `--temp <float>`
- **`data save <text>`** - Save text to database
- **`data get list`** - Retrieve all saved data
- **`data curse`** - Get a random curse word

### Custom Responses
Predefined responses for specific mentions:
- Pulak, awsaf, toppers, ray, mimu, shuckle, etc.

### Event Handlers
- Detects sad words and responds with encouragement messages

## Installation

### 1. Clone/Setup Repository
```bash
cd Data_Collector_Bot
```

### 2. Create Virtual Environment (Optional but Recommended)
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
Create a `.env` file in the project root:
```env
DISCORD_TOKEN=your_discord_bot_token_here
```

## Configuration

Edit `config.py` to customize:
- **Discord settings**: Token, prefix, etc.
- **Database**: Database filename
- **LLM settings**: Server URL, model path, temperature, tokens, etc.
- **API endpoints**: Quote API, meme API URLs

## Usage

### Starting the Bot
```bash
python main.py
```

### Using Commands in Discord
```
!hello                          # Greeting
!quote                          # Random quote
!ask What is Python?            # Ask LLM
!ask --tokens 256 --temp 0.5 Explain AI
data save My important note     # Save data
data get list                   # View saved data
data curse                      # Get curse word
```

## Module Documentation

### `core.database`
Handles all database operations with `DatabaseManager` class:
- `save_user_data(user_id, text)`
- `get_user_data(user_id)`
- `get_all_user_data()`

### `core.api`
Manages external APIs with `APIManager` class:
- `get_random_quote()` - Fetches from ZenQuotes
- `get_random_meme()` - Fetches from meme API

### `core.llm`
LLM integration with `LLMManager` class:
- `start_server()` - Start llama.cpp server
- `ask_qwen(prompt, max_tokens, temperature)` - Query Qwen model
- `parse_args(raw)` - Parse command arguments

### `handlers.commands`
Command processing:
- `process_commands(message)` - Routes to appropriate handler

### `handlers.events`
Event processing:
- `process_events(message)` - Handles message events

## Adding New Commands

1. Create handler in `handlers/commands.py`:
```python
@staticmethod
async def handle_new_command(message: discord.Message) -> bool:
    if message.content.startswith('!new'):
        await message.channel.send('Response!')
        return True
    return False
```

2. Add to handlers list in `process_commands()`:
```python
handlers = [
    CommandHandler.handle_new_command,
    # ... other handlers
]
```

## Adding New Responses

Edit `utils/constants.py`:
- Add words to `SAD_WORDS` list
- Add responses to `ENCOURAGEMENT_MESSAGES`
- Add triggers to `CUSTOM_RESPONSES` dict

## Testing

Run tests:
```bash
python -m tests.test_meme_api
```

## Dependencies

See `requirements.txt` for all dependencies:
- discord.py
- requests
- python-dotenv

## Legacy Files

- `words.py` - Kept for backward compatibility (use `utils/constants.py` instead)
- `gwen.py` - Kept for reference (use `core/llm.py` instead)
- `db_main.py` - Redundant, not needed (database setup in `core/database.py`)

## Troubleshooting

### Bot doesn't respond
- Check DISCORD_TOKEN in `.env`
- Verify bot has message content intent enabled
- Check if prefix is correct (`!` by default)

### Database errors
- Ensure write permissions in project directory
- Check `database.db` isn't corrupted

### LLM commands not working
- Ensure llama.cpp server is running
- Check `LLM_SERVER_URL` in config.py
- Verify model file path exists

## License

Proprietary - All rights reserved

## Contact

For issues or questions, check the README or review individual module docstrings.
