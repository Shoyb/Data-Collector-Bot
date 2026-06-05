# Architecture Overview

## Module Dependency Graph

```
main.py
├── config.py                    (configuration constants)
├── discord                      (external library)
├── handlers/
│   ├── commands.py
│   │   ├── core/database.py
│   │   ├── core/api.py
│   │   └── utils/constants.py
│   └── events.py
│       └── utils/constants.py
└── core/
    ├── database.py              (sqlite3)
    ├── api.py                   (requests)
    └── llm.py                   (requests, subprocess)
```

## Module Descriptions

### **config.py** (Central Configuration)
- Single source of truth for all settings
- Discord token, database name, API URLs
- LLM parameters, server paths
- Easy to switch between dev/prod configs

### **core/database.py** (Data Persistence)
- `DatabaseManager` class for SQLite operations
- Methods: save, retrieve, list user data
- Handles connection lifecycle
- Future-proof: Can add migrations, backups

### **core/api.py** (External Integrations)
- `APIManager` class for HTTP API calls
- Methods: get quotes, get memes
- Error handling and timeouts
- Easy to add new APIs (weather, etc.)

### **core/llm.py** (AI Integration)
- `LLMManager` class for llama.cpp server
- Server lifecycle: start, wait, stop
- Qwen model inference with streaming
- Parameter parsing for commands

### **handlers/commands.py** (Message Commands)
- `CommandHandler` class with static methods
- Each command = separate method
- `process_commands()` dispatcher
- Returns bool: command handled or not

### **handlers/events.py** (Message Events)
- `EventHandler` class for non-command events
- Sad word detection → encouragement response
- `process_events()` dispatcher
- Easy to add more reactive behaviors

### **utils/constants.py** (Reusable Data)
- `SAD_WORDS` list
- `ENCOURAGEMENT_MESSAGES` list
- `CUSTOM_RESPONSES` dict
- `SWEAR_WORDS` list (extensible)

### **main.py** (Orchestration)
- Discord bot setup with intents
- `on_ready()` event handler
- `on_message()` dispatcher to handlers
- `@ask` command for LLM
- Clean 95-line entry point

## Design Patterns Used

### 1. **Manager Pattern**
Each core responsibility has a manager class:
- DatabaseManager
- APIManager  
- LLMManager

Benefits:
- Centralized state management
- Easy to test (mock managers)
- Can add caching, logging later

### 2. **Handler Pattern**
Command and event handlers are static methods:
- `CommandHandler.handle_hello()`
- `EventHandler.handle_sad_words()`

Benefits:
- Stateless and testable
- Easy to add/remove handlers
- Clear handler chain

### 3. **Dispatcher Pattern**
`process_commands()` and `process_events()` dispatch to handlers:
- Iterate through handlers list
- Stop on first match (commands)
- Process all (events)

Benefits:
- Extensible without touching main.py
- Order-independent (mostly)
- Clear flow control

### 4. **Configuration Pattern**
`config.py` centralizes all magic numbers:
- No hardcoded values in handlers
- Easy feature flags
- Environment override support

Benefits:
- Single change point for settings
- Easy A/B testing
- Development vs production

## Data Flow

### Command Processing
```
Discord User sends message
        ↓
Discord Library routes to on_message()
        ↓
main.py extracts message content
        ↓
process_commands() iterates handlers
        ↓
handlers/commands.py executes handler
        ↓
Handler calls core module (db, api, llm)
        ↓
core module returns result
        ↓
Handler sends Discord message back
```

### Event Processing
```
Discord User sends message
        ↓
Discord Library routes to on_message()
        ↓
process_events() iterates handlers
        ↓
handlers/events.py executes handler
        ↓
Handler calls utils/constants for data
        ↓
Handler sends Discord message back
```

## Extensibility Points

### Add New Command
1. Create handler in `handlers/commands.py`
2. Add to `handlers` list in `process_commands()`

### Add New Event
1. Create handler in `handlers/events.py`
2. Call in `process_events()`

### Add New API
1. Add method to `core/api.py`
2. Use in handlers

### Add New Database Table
1. Add CREATE TABLE to `_initialize_tables()` in `core/database.py`
2. Add methods to `DatabaseManager`

### Add New Configuration
1. Add to `config.py`
2. Import and use where needed

## Error Handling

Current approach:
- API failures: Return None, graceful error messages
- Database errors: Print to console, return empty results
- LLM errors: Send error message to user

Future improvements:
- Add logging module
- Add error recovery
- Add retry logic
- Add monitoring/alerts

## Testing Strategy

Current structure allows:
- **Unit tests**: Test managers in isolation (no Discord)
- **Integration tests**: Test handlers with mock Discord
- **End-to-end tests**: Run actual bot in test server

Example test:
```python
def test_get_quote():
    quote = api_manager.get_random_quote()
    assert quote is not None
    assert "-" in quote  # Format check
```

## Performance Considerations

Current optimizations:
- Async/await for non-blocking I/O
- Executor pool for blocking LLM queries
- Timeout handling on API calls

Future optimizations:
- Cache quotes/memes
- Connection pooling for database
- Rate limiting on commands
- Message batching

## Security Considerations

Current status:
- ✅ No SQL injection (parameterized queries)
- ✅ Environment variables for secrets
- ✅ Timeout on API calls
- ⚠️ No user input validation
- ⚠️ No rate limiting
- ⚠️ No permission system

Recommendations:
- Add input validation in handlers
- Add rate limiting (per user)
- Add permission checks
- Audit logs for data access

## Documentation

- `README_MODULAR.md` - User guide
- `MIGRATION_GUIDE.md` - What changed
- `ARCHITECTURE.md` - This file
- Inline docstrings in each module

## Maintenance Checklist

Regular tasks:
- [ ] Update dependencies quarterly
- [ ] Review error logs monthly
- [ ] Test LLM functionality weekly
- [ ] Backup database periodically
- [ ] Monitor Discord API changes

---

**Last Updated**: June 2, 2026
**Status**: ✅ Modular Architecture Implemented
**Next Phase**: Add logging, monitoring, advanced features
