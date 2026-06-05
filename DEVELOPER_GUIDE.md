# Developer Quick Reference

## File Locations

| What | Where | Key Classes/Functions |
|------|-------|---------------------|
| **Config** | `config.py` | All constants |
| **Database** | `core/database.py` | `DatabaseManager` |
| **APIs** | `core/api.py` | `APIManager` |
| **LLM** | `core/llm.py` | `LLMManager` |
| **Commands** | `handlers/commands.py` | `CommandHandler`, `process_commands()` |
| **Events** | `handlers/events.py` | `EventHandler`, `process_events()` |
| **Constants** | `utils/constants.py` | `SAD_WORDS`, `ENCOURAGEMENT_MESSAGES`, etc. |
| **Entry** | `main.py` | `bot`, `main()` |

## Common Tasks

### Access Database
```python
from core.database import db_manager

db_manager.save_user_data(user_id, text)
data = db_manager.get_all_user_data()
```

### Call APIs
```python
from core.api import api_manager

quote = api_manager.get_random_quote()
meme = api_manager.get_random_meme()
```

### Query LLM
```python
from core.llm import llm_manager

answer, reasoning, stats = llm_manager.ask_qwen("Your question")
```

### Get Constants
```python
from utils.constants import SAD_WORDS, ENCOURAGEMENT_MESSAGES

if word in SAD_WORDS:
    response = random.choice(ENCOURAGEMENT_MESSAGES)
```

### Add New Command
```python
# handlers/commands.py
@staticmethod
async def handle_mycommand(message: discord.Message) -> bool:
    if message.content.startswith('!mycommand'):
        await message.channel.send('Response!')
        return True
    return False

# Add to handlers list in process_commands()
handlers = [
    CommandHandler.handle_hello,
    CommandHandler.handle_mycommand,  # ← Add here
    # ...
]
```

### Add New Event Handler
```python
# handlers/events.py
@staticmethod
async def handle_mycondition(message: discord.Message):
    if some_condition:
        await message.channel.send('Triggered!')

# Call in process_events()
async def process_events(message: discord.Message):
    await EventHandler.handle_sad_words(message)
    await EventHandler.handle_mycondition(message)  # ← Add here
```

### Modify Settings
Edit `config.py`:
```python
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")  # Or hardcode for testing
COMMAND_PREFIX = "!"  # Change prefix here
LLM_TEMPERATURE = 0.5  # Adjust LLM creativity
```

### Add New Response
Edit `utils/constants.py`:
```python
SAD_WORDS.append("frustrated")
ENCOURAGEMENT_MESSAGES.append("You've got this!")
CUSTOM_RESPONSES["keyword"] = "Response text"
```

## Import Patterns

### Use These
```python
# ✅ Good - Use managers
from core.database import db_manager
from core.api import api_manager
from core.llm import llm_manager

# ✅ Good - Use handlers
from handlers.commands import process_commands
from handlers.events import process_events

# ✅ Good - Use constants
from utils.constants import SAD_WORDS
```

### Avoid These
```python
# ❌ Bad - Old modules (legacy)
from words import sad_words
from gwen import ask_qwen

# ❌ Bad - Direct class instantiation
from core.database import DatabaseManager
db = DatabaseManager()  # Use singleton instead

# ❌ Bad - Circular imports
# Don't import main from other modules
```

## Debug Helpers

### Check if database works
```python
python -c "from core.database import db_manager; print(db_manager.get_all_user_data())"
```

### Test API
```python
python -c "from core.api import api_manager; print(api_manager.get_random_quote())"
```

### Check config
```python
python -c "import config; print(config.DISCORD_TOKEN)"
```

### Test LLM connection
```python
python -c "from core.llm import llm_manager; print(llm_manager.wait_for_server())"
```

## Common Errors & Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'config'` | Wrong working directory | `cd Data_Collector_Bot` |
| `AttributeError: db_manager is None` | Database not initialized | Restart bot |
| `ConnectionError` to LLM server | Server not running | Start llama.cpp server |
| `Database locked` | Multiple connections | Use singleton manager |
| `No module named 'discord'` | Missing dependencies | `pip install -r requirements.txt` |

## Performance Tips

- API calls run synchronously but have 5s timeout
- LLM queries run in executor to not block bot
- Database uses single connection (thread-safe with locks if needed)
- Discord messages processed sequentially per channel

## Testing Commands Locally

### In Python REPL
```python
import asyncio
import discord
from handlers.commands import CommandHandler

# Create fake message object
class FakeMessage:
    content = "!hello"
    class channel:
        async def send(self, msg):
            print(f"Bot: {msg}")

msg = FakeMessage()
asyncio.run(CommandHandler.handle_hello(msg))
```

## Code Style

- Type hints on all functions (improve IDEs & catch bugs early)
- Docstrings on all classes and public methods
- Snake_case for variables/functions, UPPER_CASE for constants
- Async/await for Discord operations
- Try/except for external APIs

## Version Info

| Component | Version |
|-----------|---------|
| Python | 3.8+ |
| discord.py | 2.3.2 |
| requests | 2.31.0 |
| python-dotenv | 1.0.0 |

---

**Last Updated**: June 2, 2026
**Difficulty**: Easy ← → Hard
