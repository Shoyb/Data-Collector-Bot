# Data Collector Bot - Modular Guide

A modular Discord bot for entertainment commands, math tools, quotes, encouragement messages, transformer NLP, and LLM integration.

## Project Structure

```text
Data_Collector_Bot/
|-- main.py                  # Entry point and dispatcher wiring
|-- config.py                # Centralized configuration
|-- core/
|   |-- api.py               # External API integrations
|   |-- llm.py               # LLM server management and Qwen inference
|   `-- transformers_nlp.py  # Transformer NLP models
|-- handlers/
|   |-- calculator.py        # Safe calculator commands
|   |-- commands.py          # General command processing
|   |-- events.py            # Reactive event processing
|   |-- games.py             # Guessing game and rock paper scissors
|   |-- plotter.py           # Function plotting
|   |-- polynomial.py        # Polynomial solving
|   `-- transformers.py      # Transformer command processing
|-- utils/
|   `-- constants.py         # Constants and word lists
|-- tests/
|   `-- test_meme_api.py     # Meme API tests
|-- words.py                 # Legacy word lists
|-- gwen.py                  # Legacy LLM module
`-- README.md
```

## Commands

### General

- `!hello` - Simple greeting
- `!quote` or `quote` - Random inspirational quote
- `data meme` or `!meme` - Random meme
- `data waifu` - Random waifu image
- `data curse` - Random curse word
- `!ask <question>` - Ask Qwen LLM after the LLM server is running

### Games

- `!guess` - Guess a number from 1 to 100
- `!guess 50` - Guess a number from 1 to 50
- `data rock`, `data paper`, `data scissor`, `data scissors` - Play rock paper scissors

### Math

- `data 5+3` - Calculator expression
- `data sqrt(25)` - Square root
- `data 2^8` or `data 2**8` - Power
- `data sin(pi/2)` - Trigonometry in radians
- `data poly x^2 - 5x + 6` - Polynomial roots
- `data roots x^2 + 1` - Polynomial roots with complex output
- `data solve 2x^2 - 8 = 0` - Polynomial equation solving
- `data plot x^2` - Plot a function
- `data plot sin(x) from -2*pi to 2*pi` - Plot with a custom x range

### Transformer NLP

- `!summarize <text>` - Summarize long text
- `!classify <text> | <label1>, <label2>` - Zero-shot classification
- `!mask <text with [MASK]>` - Mask filling

## Installation

```bash
cd Data_Collector_Bot
pip install -r requirements.txt
```

Create `.env`:

```env
DISCORD_TOKEN=your_discord_bot_token_here
```

Run:

```bash
python main.py
```

## Dependencies

- discord.py - Discord bot framework
- requests - External API calls
- python-dotenv - Environment variable loading
- sympy - Symbolic parsing and polynomial roots
- numpy - Plot sampling
- matplotlib - Plot image generation

## Module Notes

### `handlers.calculator`
Uses a safe AST evaluator for calculator expressions. It supports arithmetic, powers, square root, logs, trig, inverse trig, `pi`, and `e`.

### `handlers.polynomial`
Uses SymPy to parse and solve polynomial expressions or equations for `x`. It supports implicit multiplication such as `5x`.

### `handlers.plotter`
Uses SymPy, NumPy, and Matplotlib to render functions as PNG files for Discord.

### `handlers.games`
Contains `!guess` registration plus manual game commands like rock paper scissors.

## Testing

Run the current test module:

```bash
python -m tests.test_meme_api
```

Quick syntax check:

```bash
python -m py_compile main.py handlers/calculator.py handlers/games.py handlers/plotter.py handlers/polynomial.py
```

## Legacy Files

- `words.py` - Kept for backward compatibility
- `gwen.py` - Kept for reference; use `core/llm.py` for current LLM code

## Troubleshooting

### Bot does not respond

- Check `DISCORD_TOKEN` in `.env`
- Verify the bot has message content intent enabled
- Check the command prefix in `config.py`

### Plot or polynomial command fails

- Run `pip install -r requirements.txt`
- Confirm `sympy`, `numpy`, and `matplotlib` are installed
- Use `x` as the function or polynomial variable

### LLM commands do not work

- Start the llama.cpp server with `data llm start`
- Check `LLM_SERVER_URL` and model paths in `config.py`

## License

Proprietary - All rights reserved
