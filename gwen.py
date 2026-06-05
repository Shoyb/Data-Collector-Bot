import discord
from discord.ext import commands
import requests
import asyncio
import time
import subprocess
import sys
import re
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# --- Config ---
SERVER_URL = "http://127.0.0.1:8080/v1/chat/completions"
MAX_TOKENS = 4096
TEMPERATURE = 0.7
TIMEOUT = 300
MAX_THINKING_TOKENS = 500
REPEAT_PENALTY = 1.1

SYSTEM_PROMPT = """You are a fast, concise assistant. Follow these rules strictly:
- Answer directly without long preambles
- Be brief and to the point
- Do not over-explain unless asked
- /no_think"""

llama_process = None

# --- Server management ---

def start_llama_server():
    global llama_process
    print("🚀 Starting llama.cpp server...")
    llama_process = subprocess.Popen(
        [
            r"C:\llama\llama-server.exe",
            "--model", r"C:\llama\models\Qwen3.5-0.8B-Q4_K_M.gguf",
            "--port", "8080",
            "--threads", "6",
            "--temp", "0.3"
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    print(f"   Server PID: {llama_process.pid}")

def wait_for_server(retries=20, delay=2):
    print("Waiting for server to be ready", end="", flush=True)
    for _ in range(retries):
        try:
            r = requests.get("http://127.0.0.1:8080/health", timeout=2)
            if r.status_code == 200:
                print(" ready")
                return True
        except Exception:
            pass
        print(".", end="", flush=True)
        time.sleep(delay)
    print(" failed")
    return False

def stop_llama_server():
    global llama_process
    if llama_process:
        print("Stopping llama.cpp server...")
        llama_process.terminate()
        llama_process.wait()
        print("   Server stopped.")

# --- Qwen inference ---

def ask_qwen(prompt: str, max_tokens: int = None, temperature: float = None):
    data = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature if temperature is not None else TEMPERATURE,
        "max_tokens": max_tokens if max_tokens is not None else MAX_TOKENS,
        "repeat_penalty": REPEAT_PENALTY,
        "stream": False,
    }

    if MAX_THINKING_TOKENS > 0:
        data["thinking"] = {"type": "enabled", "budget_tokens": MAX_THINKING_TOKENS}

    start = time.time()
    r = requests.post(SERVER_URL, json=data, timeout=TIMEOUT)
    r.raise_for_status()
    elapsed = time.time() - start

    result = r.json()
    message = result["choices"][0]["message"]
    timings = result.get("timings", {})
    usage = result.get("usage", {})

    content = message.get("content", "").strip()
    reasoning = message.get("reasoning_content", "").strip()
    answer = content if content else reasoning

    stats = {
        "elapsed": elapsed,
        "prompt_tokens": usage.get("prompt_tokens", "?"),
        "completion_tokens": usage.get("completion_tokens", "?"),
        "total_tokens": usage.get("total_tokens", "?"),
        "tok_per_sec": round(timings.get("predicted_per_second", 0), 2),
        "finish_reason": result["choices"][0].get("finish_reason", "?"),
        "max_tokens_used": max_tokens if max_tokens is not None else MAX_TOKENS,
        "temp_used": temperature if temperature is not None else TEMPERATURE,
    }

    return answer, reasoning, stats

# --- Argument parser ---

def parse_args(raw: str):
    """
    Parses optional --tokens and --temp flags.
    Example: !ask --tokens 512 --temp 0.9 what is gravity
    """
    max_tokens = None
    temperature = None

    token_match = re.search(r"--tokens\s+(\d+)", raw)
    temp_match = re.search(r"--temp\s+([0-9.]+)", raw)

    if token_match:
        max_tokens = int(token_match.group(1))
        raw = raw.replace(token_match.group(0), "")
    if temp_match:
        temperature = float(temp_match.group(1))
        raw = raw.replace(temp_match.group(0), "")

    return raw.strip(), max_tokens, temperature

# --- Discord helpers ---

async def live_timer(msg, start_time: float, stop_event: asyncio.Event, tok_display, temp_display):
    while not stop_event.is_set():
        elapsed = time.time() - start_time
        try:
            await msg.edit(content=(
                f"⏳ **Generating...** `{elapsed:.1f}s`\n"
                f"-# Using `Qwen3.5-0.8B` · max_tokens=`{tok_display}` · temp=`{temp_display}`"
            ))
        except discord.errors.HTTPException:
            pass
        await asyncio.sleep(1)

async def stream_edit(msg, text: str, chunk_size: int = 30):
    displayed = ""
    for i in range(0, len(text), chunk_size):
        displayed += text[i:i + chunk_size]
        try:
            await msg.edit(content=displayed)
        except discord.errors.HTTPException:
            pass
        await asyncio.sleep(0.05)

# --- Bot setup ---

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command(name="ask")
async def ask(ctx, *, raw: str):
    """
    Ask Qwen. Usage:
      !ask <question>
      !ask --tokens 512 --temp 0.9 <question>
    """
    question, max_tokens, temperature = parse_args(raw)

    tok_display = max_tokens if max_tokens is not None else MAX_TOKENS
    temp_display = temperature if temperature is not None else TEMPERATURE

    msg = await ctx.send(
        f"⏳ **Generating...** `0.0s`\n"
        f"-# Using `Qwen3.5-0.8B` · max_tokens=`{tok_display}` · temp=`{temp_display}`"
    )
    start_time = time.time()
    stop_event = asyncio.Event()
    timer_task = asyncio.create_task(live_timer(msg, start_time, stop_event, tok_display, temp_display))

    try:
        answer, reasoning, stats = await asyncio.get_event_loop().run_in_executor(
            None, ask_qwen, question, max_tokens, temperature
        )
    except requests.exceptions.ConnectionError:
        stop_event.set()
        await timer_task
        await msg.edit(content="❌ Cannot connect to llama.cpp server.")
        return
    except requests.exceptions.Timeout:
        stop_event.set()
        await timer_task
        await msg.edit(content=f"❌ Request timed out after {TIMEOUT}s.")
        return
    except Exception as e:
        stop_event.set()
        await timer_task
        await msg.edit(content=f"❌ Error: {e}")
        return
    finally:
        stop_event.set()
        await timer_task

    # Handle Discord's 2000 char limit
    if len(answer) > 1900:
        chunks = [answer[i:i+1900] for i in range(0, len(answer), 1900)]
        await msg.edit(content=chunks[0])
        for chunk in chunks[1:]:
            await ctx.send(chunk)
        last_msg = await ctx.send("_ _")
    else:
        await stream_edit(msg, answer)
        last_msg = msg

    # --- Buttons ---
    view = discord.ui.View(timeout=180)

    if reasoning:
        class ReasoningButton(discord.ui.Button):
            def __init__(self):
                super().__init__(label="🧠 Show Reasoning", style=discord.ButtonStyle.secondary)

            async def callback(self, interaction: discord.Interaction):
                await interaction.response.defer()
                self.disabled = True
                chunks = [reasoning[i:i+4000] for i in range(0, len(reasoning), 4000)]
                for i, chunk in enumerate(chunks):
                    embed = discord.Embed(
                        title=f"🧠 Reasoning {'(continued)' if i > 0 else ''}",
                        description=chunk,
                        color=discord.Color.blurple()
                    )
                    await ctx.send(embed=embed)
                await interaction.message.edit(view=view)

        view.add_item(ReasoningButton())

    class StatsButton(discord.ui.Button):
        def __init__(self):
            super().__init__(label="📊 Stats", style=discord.ButtonStyle.gray)

        async def callback(self, interaction: discord.Interaction):
            finish = stats["finish_reason"]
            warning = " ⚠️ hit token limit!" if finish == "length" else ""
            await interaction.response.send_message(
                content=(
                    f"```\n"
                    f"⏱  Time         : {stats['elapsed']:.2f}s\n"
                    f"⚡  Speed        : {stats['tok_per_sec']} tok/s\n"
                    f"📥  Prompt tokens: {stats['prompt_tokens']}\n"
                    f"📤  Output tokens: {stats['completion_tokens']}\n"
                    f"🔢  Total tokens : {stats['total_tokens']}\n"
                    f"🎛  Max tokens   : {stats['max_tokens_used']}\n"
                    f"🌡  Temperature  : {stats['temp_used']}\n"
                    f"🔁  Repeat pen.  : {REPEAT_PENALTY}\n"
                    f"🧠  Think budget : {MAX_THINKING_TOKENS} tokens\n"
                    f"```{warning}"
                ),
                ephemeral=True
            )

    view.add_item(StatsButton())
    await last_msg.edit(view=view)

@bot.command(name="help_ask")
async def help_ask(ctx):
    """Shows usage instructions."""
    embed = discord.Embed(
        title="🤖 Qwen Bot Usage",
        color=discord.Color.blurple()
    )
    embed.add_field(
        name="Basic",
        value="`!ask <question>`",
        inline=False
    )
    embed.add_field(
        name="With options",
        value=(
            "`!ask --tokens 512 <question>`\n"
            "`!ask --temp 0.9 <question>`\n"
            "`!ask --tokens 1024 --temp 0.4 <question>`"
        ),
        inline=False
    )
    embed.add_field(
        name="Defaults",
        value=(
            f"max_tokens = `{MAX_TOKENS}`\n"
            f"temperature = `{TEMPERATURE}`\n"
            f"repeat penalty = `{REPEAT_PENALTY}`\n"
            f"thinking budget = `{MAX_THINKING_TOKENS}` tokens"
        ),
        inline=False
    )
    embed.add_field(
        name="Tips",
        value=(
            "• Lower temp (e.g. `0.1`) = more focused\n"
            "• Higher temp (e.g. `1.0`) = more creative\n"
            "• Lower tokens = faster response\n"
            "• Click 📊 Stats to see generation details\n"
            "• Click 🧠 Show Reasoning to see thinking"
        ),
        inline=False
    )
    await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f"Bot online as {bot.user}")
    print(f"   Server       : {SERVER_URL}")
    print(f"   Timeout      : {TIMEOUT}s")
    print(f"   Max tokens   : {MAX_TOKENS}")
    print(f"   Temperature  : {TEMPERATURE}")
    print(f"   Repeat pen.  : {REPEAT_PENALTY}")
    print(f"   Think budget : {MAX_THINKING_TOKENS} tokens")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Provide a question. Usage: `!ask <question>` or `!help_ask` for options.")
    else:
        await ctx.send(f"❌ {error}")

# --- Entry point ---

if __name__ == "__main__":
    start_llama_server()

    if not wait_for_server():
        print("Server failed to start. Exiting.")
        stop_llama_server()
        sys.exit(1)

    try:
        bot.run(TOKEN)
    finally:
        stop_llama_server()