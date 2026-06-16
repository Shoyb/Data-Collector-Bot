﻿# Developer Quick Reference

## File Locations

| What | Where | Key Classes/Functions |
|------|-------|-----------------------|
| Config | `config.py` | All constants |
| APIs | `core/api.py` | `APIManager`, `api_manager` |
| LLM | `core/llm.py` | `LLMManager`, `llm_manager` |
| General commands | `handlers/commands.py` | `CommandHandler`, `process_commands()` |
| Events | `handlers/events.py` | `EventHandler`, `process_events()` |
| Games | `handlers/games.py` | `setup_game_commands()`, `process_game_commands()` |
| Calculator | `handlers/calculator.py` | `calculate()`, `process_calculator_commands()` |
| Polynomial solver | `handlers/polynomial.py` | `solve_polynomial()`, `process_polynomial_commands()` |
| Plotter | `handlers/plotter.py` | `create_function_plot()`, `process_plot_commands()` |
| Words | `handlers/words.py` | `setup_word_commands()`, `_load_five_letter_words()` |
| Transformers | `handlers/transformers.py` | `process_transformer_commands()` |
| Constants | `utils/constants.py` | `SAD_WORDS`, `ENCOURAGEMENT_MESSAGES`, etc. |
| Entry | `main.py` | `bot`, `main()` |

## Common Tasks

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

### Calculate Math

```python
from handlers.calculator import calculate

print(calculate("sqrt(25) + 2^3"))
```

### Solve Polynomial Roots

```python
from handlers.polynomial import solve_polynomial

print(solve_polynomial("x^2 - 5x + 6"))
```

### Generate Plot Image

```python
from handlers.plotter import create_function_plot

buffer, expression = create_function_plot("sin(x) from -3.14 to 3.14")
```

### Add New Manual Command

Create or update a focused handler module:

```python
async def process_my_commands(message: discord.Message) -> bool:
    if not message.content.lower().startswith("data mycommand"):
        return False

    await message.channel.send("Response!")
    return True
```

Wire it into `main.py`:

```python
if not handled:
    handled = await process_my_commands(message)
```

Place specific handlers before broad handlers. For example, `data plot ...` runs before the calculator because calculator messages also start with `data `.

### Add New Prefixed Command

For `!command` style features, register with `@bot.command` directly or use a setup function:

```python
def setup_my_commands(bot: commands.Bot) -> None:
    @bot.command(name="mycommand")
    async def mycommand(ctx: commands.Context):
        await ctx.send("Response!")
```

Call setup after bot creation in `main.py`.

### Add New Event Handler

```python
# handlers/events.py
@staticmethod
async def handle_mycondition(message: discord.Message):
    if some_condition:
        await message.channel.send("Triggered!")

# Call in process_events()
async def process_events(message: discord.Message):
    await EventHandler.handle_sad_words(message)
    await EventHandler.handle_mycondition(message)
```

### Modify Settings

Edit `config.py`:

```python
COMMAND_PREFIX = "!"
LLM_TEMPERATURE = 0.5
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
from core.api import api_manager
from core.llm import llm_manager
from handlers.calculator import process_calculator_commands
from handlers.games import setup_game_commands
from utils.constants import SAD_WORDS
```

### Avoid These

```python
from words import sad_words  # legacy
from gwen import ask_qwen    # legacy
import main                  # avoid circular imports
```

## Debug Helpers

### Test API

```bash
python -c "from core.api import api_manager; print(api_manager.get_random_quote())"
```

### Test Calculator

```bash
python -c "from handlers.calculator import calculate; print(calculate('sqrt(25)+2^3'))"
```

### Test Polynomial Solver

```bash
python -c "from handlers.polynomial import solve_polynomial; print(solve_polynomial('x^2 - 5x + 6'))"
```

### Test Plotter

```bash
python -c "from handlers.plotter import create_function_plot; b,e=create_function_plot('x^2'); print(e, len(b.getvalue()))"
```

### Check Config

```bash
python -c "import config; print(config.COMMAND_PREFIX)"
```

### Test LLM Connection

```bash
python -c "from core.llm import llm_manager; print(llm_manager.wait_for_server())"
```

## Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `ModuleNotFoundError: No module named 'config'` | Wrong working directory | `cd Data_Collector_Bot` |
| `No module named 'discord'` | Missing dependencies | `pip install -r requirements.txt` |
| `No module named 'sympy'` | Math dependencies not installed | `pip install -r requirements.txt` |
| Plot command sends an error | Invalid function or range | Use `x`, supported functions, and a valid range |
| LLM connection error | Server not running | Start llama.cpp server |

## Performance Tips

- API calls run synchronously with timeouts.
- LLM queries run in an executor to avoid blocking the event loop.
- Plotting and polynomial solving can be heavier than simple commands; add rate limiting if this bot is used on busy servers.
- Keep broad command matchers late in the dispatcher chain.

## Testing Commands Locally

Current test module:

```bash
python -m tests.test_meme_api
```

Syntax check:

```bash
python -m py_compile main.py handlers/calculator.py handlers/games.py handlers/plotter.py handlers/polynomial.py
```

## Code Style

- Type hints on public functions
- Docstrings on modules and public handlers
- Snake_case for variables/functions, UPPER_CASE for constants
- Async/await for Discord operations
- Focused handler modules for larger features
- Avoid raw `eval`; use allowlisted parsers for user math input

## Version Info

| Component | Version |
|-----------|---------|
| Python | 3.8+ |
| discord.py | 2.3.2 |
| requests | 2.31.0 |
| python-dotenv | 1.0.0 |
| sympy | 1.14.0 |
| matplotlib | 3.10.1 |
| numpy | 2.2.5 |

---

Last updated: June 10, 2026
