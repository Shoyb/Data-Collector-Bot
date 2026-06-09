# Architecture Overview

## Module Dependency Graph

```text
main.py
|-- config.py
|-- discord
|-- handlers/
|   |-- calculator.py
|   |   `-- math / ast
|   |-- commands.py
|   |   |-- core/api.py
|   |   |-- core/llm.py
|   |   `-- utils/constants.py
|   |-- events.py
|   |   `-- utils/constants.py
|   |-- games.py
|   |-- plotter.py
|   |   |-- handlers/calculator.py
|   |   |-- sympy
|   |   |-- numpy
|   |   `-- matplotlib
|   |-- polynomial.py
|   |   `-- sympy
|   `-- transformers.py
|       `-- core/transformers_nlp.py
`-- core/
    |-- api.py
    `-- llm.py
```

## Module Descriptions

### `config.py`

Single source of truth for configuration such as Discord token, command prefix, API URLs, and LLM settings.

### `core/api.py`

External API integrations through `APIManager`:

- Quotes
- Memes

### `core/llm.py`

LLM integration through `LLMManager`:

- Server lifecycle management
- Qwen inference
- Argument parsing for `!ask`

### `handlers.commands`

General manual command handlers such as greetings, quotes, memes, waifu images, curse words, custom responses, and LLM start/stop commands.

### `handlers.events`

Reactive non-command behavior, including sad word detection and encouragement responses.

### `handlers.games`

Game features:

- `setup_game_commands(bot)` registers `!guess`
- `process_game_commands(message)` handles `data rock`, `data paper`, and `data scissors`

### `handlers.calculator`

Safe calculator for messages like `data 5+3` and `data sqrt(25)`. It uses Python AST parsing with an allowlist of operators and math functions instead of raw `eval`.

### `handlers.polynomial`

Polynomial root solving for `x` using SymPy. Supports expressions and equations, such as `data poly x^2 - 5x + 6` and `data solve 2x^2 - 8 = 0`.

### `handlers.plotter`

Function plotting using SymPy parsing, NumPy sampling, and Matplotlib PNG rendering. Supports commands such as `data plot sin(x) from -2*pi to 2*pi`.

### `handlers.transformers`

Manual transformer NLP command routing for summarization, classification, and mask filling.

### `utils/constants.py`

Reusable word lists and custom response data.

### `main.py`

Orchestration layer:

- Discord bot setup
- `on_ready()` event
- `on_message()` dispatcher chain
- `!ask` command
- Game command registration

## Dispatcher Order

Manual handlers run in this order:

1. `process_commands(message)`
2. `process_transformer_commands(message)`
3. `process_plot_commands(message)`
4. `process_polynomial_commands(message)`
5. `process_calculator_commands(message)`
6. `process_game_commands(message)`
7. `process_events(message)`
8. `bot.process_commands(message)` if no manual handler matched

The order matters. More specific `data plot` and `data poly` commands run before the calculator because they also contain math-looking text.

## Design Patterns Used

### Manager Pattern

Core services such as API and LLM behavior are managed through singleton-style managers.

### Handler Pattern

Each feature area owns its message processing. Handlers return `True` when they handled a message so the dispatcher can stop cleanly.

### Focused Module Pattern

Larger features are split into focused files:

- `games.py` for games
- `calculator.py` for arithmetic evaluation
- `polynomial.py` for roots
- `plotter.py` for function images

## Data Flow

```text
Discord user sends message
        |
Discord library routes to on_message()
        |
main.py runs handlers in order
        |
First matching handler performs work
        |
Handler sends Discord response
```

## Extensibility Points

### Add New Manual Command

1. Add a handler function returning `bool`.
2. Wire it into `main.py` in the correct order.
3. Keep broad matchers later than specific matchers.

### Add New Prefixed Command

1. Register with `@bot.command` directly or through a setup function.
2. Call the setup function after bot creation in `main.py`.

### Add New API

1. Add a method to `core/api.py`.
2. Use the API manager from a handler.

## Error Handling

Current approach:

- API failures return graceful messages
- LLM failures are sent back to the user
- Calculator uses a safe allowlist parser
- Polynomial and plot inputs are restricted before SymPy parsing
- Plotting uses Matplotlib's non-GUI `Agg` backend

Future improvements:

- Add structured logging
- Add per-user rate limiting
- Add monitoring/alerts
- Add more unit tests for math handlers

## Security Considerations

Implemented:

- Environment variables for secrets
- Timeout on API calls
- No raw `eval` for calculator input
- Restricted parser inputs for polynomial solving and plotting

Recommended:

- Rate limiting
- Permission checks
- Audit logs for sensitive commands

## Documentation

- `README.md` - Main user guide
- `README_MODULAR.md` - Detailed user and module guide
- `FEATURE_LIST.md` - Complete feature list
- `DEVELOPER_GUIDE.md` - Developer quick reference
- `ARCHITECTURE.md` - This file

## Maintenance Checklist

- [ ] Update dependencies quarterly
- [ ] Test Discord command flow after handler order changes
- [ ] Add tests for calculator, polynomial, and plotter modules
- [ ] Monitor Discord API changes

---

Last updated: June 10, 2026
Status: Modular architecture with games and math tools
