# Data Collector Bot

A modular Discord bot for entertainment, math utilities, quotes, encouragement messages, and LLM integration.

## Features

### Entertainment

- **Greetings**: Responds to `!hello`.
- **Custom Responses**: Has specific responses for configured keywords.
- **Quotes**: Fetches random inspirational quotes with `!quote` or `quote`.
- **Memes**: Sends a random meme with `data meme` or `!meme`.
- **Waifu Images**: Sends a random waifu image with `data waifu`.
- **Swear Word Generator**: Sends a random curse word with `data curse`.
- **Number Guessing Game**: Start with `!guess` or `!guess 50`; the bot gives high/low hints and reports the number of steps.
- **Mental Math Challenge**: Start with `!mental`, `!mental 10`, or `!mental hard`; the bot times each answer.
- **Connect Four**: Play with `!connect4`; moves use columns or chess-style coordinates like `D` or `D4`.
- **Rock Paper Scissors**: Play with `data rock`, `data paper`, `data scissor`, or `data scissors`.

### Math Tools

- **Calculator**: Evaluate expressions like `data 5+3`, `data sqrt(25)`, `data 2^8`, `data sin(pi/2)`.
- **Polynomial Solver**: Solve roots with commands like `data poly x^2 - 5x + 6` or `data roots x^2 + 1`.
- **Function Plotter**: Generate PNG plots with commands like `data plot x^2`, `data plot x, x^2`, or `data plot x^2 + y^2 from -3 to 3`.

### AI and NLP

- **LLM Questions**: Ask Qwen with `!ask <question>` after starting the LLM server.
- **Transformer Commands**: Supports summarization, classification, and mask filling through the transformer handlers.

### Emotional Support

- **Encouragement**: Detects sad words in messages and responds with encouragement.

## Setup and Installation

1. Clone the repository or download the files.
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory and add your Discord bot token:
   ```env
   DISCORD_TOKEN=your_discord_bot_token_here
   ```
4. Run the bot:
   ```bash
   python main.py
   ```

## Command Examples

```text
!hello
!quote
!guess
!guess 50
!mental
!mental 10 hard
!connect4
data rock
data paper
data 12+45
data sqrt(81)
data log(1000)
data poly x^2 - 5x + 6
data roots x^2 + 1
data plot x^2
data plot sin(x) from -2*pi to 2*pi
data plot x, x^2
data plot sin(t), cos(t), t from -2*pi to 2*pi
data plot x^2 + y^2 from -3 to 3
data plot x^2 + y^2 + z^2 = 4 from -3 to 3
```

## Math Notes

- Calculator and plot trig functions use radians.
- Calculator supports `+`, `-`, `*`, `/`, `^` or `**`, `sqrt`, `log`, `ln`, `sin`, `cos`, `tan`, `arctan`, `arccos`/`arcos`, and `arcsin`.
- Mental math supports `easy`, `medium`, and `hard` difficulties, up to 20 rounds.
- Polynomial solving uses SymPy and solves for `x`.
- Function plotting supports 2D functions, 2D parametric curves, 3D parametric curves, 3D surfaces, and simple implicit 3D plots.

## Dependencies

- discord.py: Discord bot functionality
- requests: External API calls
- python-dotenv: Environment variable management
- sympy: Polynomial solving and function parsing
- numpy: Plot data generation
- matplotlib: Plot image rendering

## Note

This bot is for entertainment and personal use. Ensure compliance with Discord's Terms of Service and API usage guidelines for external APIs used by the bot.
