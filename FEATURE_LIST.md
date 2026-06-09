# Complete Feature List

## Core Commands

### General Interaction

- `!hello` - Simple greeting
- `!quote` or `quote` - Random inspirational quote
- `data meme` or `!meme` - Random meme
- `data waifu` - Random waifu image
- `data curse` - Random curse word

### Games

- `!guess` - Number guessing game from 1 to 100
- `!guess <max_number>` - Number guessing game with a custom upper limit
- `!mental` - Timed 5-round mental math challenge
- `!mental <rounds>` - Timed mental math challenge with a custom number of rounds
- `!mental <difficulty>` - Timed mental math challenge using easy, medium, or hard
- `!mental <rounds> <difficulty>` - Timed mental math challenge with custom rounds and difficulty
- `!connect4` or `!c4` - Play Connect Four against the bot using moves like A, D4, or G6
- `data rock` - Rock paper scissors using rock
- `data paper` - Rock paper scissors using paper
- `data scissor` / `data scissors` - Rock paper scissors using scissors

### Math Tools

- `data <expression>` - Calculator for supported math expressions
  - Examples: `data 5+3`, `data sqrt(25)`, `data 2^8`, `data sin(pi/2)`
  - Supports: addition, subtraction, multiplication, division, powers, sqrt, log, ln, sin, cos, tan, arctan, arccos/arcos, arcsin
- `data poly <polynomial>` - Solve polynomial roots for `x`
- `data polynomial <polynomial>` - Same as `data poly`
- `data roots <polynomial>` - Same as `data poly`
- `data solve <equation>` - Solve a polynomial equation for `x`
- `data plot <function>` - Plot a function and send a PNG image
- `data graph <function>` - Same as `data plot`
- `data plot <function> from <start> to <end>` - Plot with a custom x range

### AI/LLM Integration

- `data llm start` - Start Qwen LLM server
- `data llm stop` - Stop Qwen LLM server
- `!ask [question]` - Ask Qwen LLM a question
  - Optional: `--tokens [num]` to set max tokens
  - Optional: `--temp [float]` to set temperature

### Transformer NLP Features

- `!summarize [text]` - Summarize long text
- `!classify [text] | [label1], [label2], [label3]` - Zero-shot classification
- `!mask [text with [MASK]]` - Predict masked words

### Custom Responses

Automatic responses for configured keywords in `utils/constants.py`.

## Event Handlers

### Encouragement System

- Detects sad words such as sad, lonely, depressed, etc.
- Automatically sends encouragement messages

## Architecture

```text
Data_Collector_Bot/
|-- main.py
|-- config.py
|-- core/
|   |-- api.py
|   |-- llm.py
|   `-- transformers_nlp.py
|-- handlers/
|   |-- calculator.py
|   |-- commands.py
|   |-- events.py
|   |-- games.py
|   |-- plotter.py
|   |-- polynomial.py
|   `-- transformers.py
|-- utils/
|   `-- constants.py
`-- tests/
    `-- test_meme_api.py
```

## Quick Start

```bash
cd Data_Collector_Bot
pip install -r requirements.txt
python main.py
```

## Try Commands

```text
!hello
!quote
!guess 50
!mental 10 hard
!connect4
data rock
data sqrt(81)
data poly x^2 - 5x + 6
data plot sin(x) from -2*pi to 2*pi
!summarize [50+ word text]
!classify [text] | positive, negative, neutral
!mask The capital of France is [MASK]
```

## Dependencies

- discord.py
- requests
- python-dotenv
- sympy
- numpy
- matplotlib

## Documentation

| Document | Purpose |
|----------|---------|
| README.md | Main user guide |
| README_MODULAR.md | Detailed module and command guide |
| ARCHITECTURE.md | System design and patterns |
| DEVELOPER_GUIDE.md | Developer quick reference |
| TRANSFORMER_FEATURES.md | Detailed transformer guide |
| TRANSFORMERS_QUICK_REF.md | Transformer commands reference |
| FEATURE_LIST.md | This file |

## Integration Points

### Add New Manual Command

1. Create a focused handler module in `handlers/` or add to `handlers/commands.py`.
2. Return `True` when the command is handled.
3. Wire the processor into `main.py` before broader handlers that might catch the same message.

### Add New Prefixed Command

1. Register it with `@bot.command` or a setup function like `setup_game_commands(bot)`.
2. Call the setup function from `main.py` after bot creation.

### Add New API

1. Add method to `core/api.py`.
2. Use it from a handler.

### Add New Model

1. Add model logic to `core/transformers_nlp.py` or a focused core module.
2. Create a handler in `handlers/`.
3. Update `requirements.txt` and docs.

## Security

Implemented:

- Environment variable for Discord token
- Timeout on API calls
- Safe AST evaluator for calculator expressions
- Restricted parser inputs for polynomial solving and plotting

Recommended:

- Rate limiting
- Permission system
- Error logging
- Audit trail

## Status

Last updated: June 10, 2026
Version: 2.3 - Connect Four
