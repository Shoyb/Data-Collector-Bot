"""
Word-related command module for Data Collector Bot.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import discord
from discord.ext import commands

WORD_FILE = Path(__file__).resolve().parents[1] / "valid-wordle-words.txt"
WORDS_PER_PAGE = 20


def _load_five_letter_words() -> list[str]:
    try:
        text = WORD_FILE.read_text(encoding="utf-8")
    except FileNotFoundError:
        return []

    words = [line.strip().lower() for line in text.splitlines()]
    return [word for word in words if len(word) == 5 and word.isalpha()]


FIVE_LETTER_WORDS = _load_five_letter_words()


def _parse_word_options(raw: str) -> tuple[set[str], dict[int, str], list[str]]:
    include_letters: set[str] = set()
    positions: dict[int, str] = {}
    unknown_tokens: list[str] = []

    for token in raw.split():
        token = token.strip().lower()
        if not token:
            continue

        if "=" in token:
            key, value = token.split("=", 1)
            value = ''.join(ch for ch in value if ch.isalpha())
            if not value:
                continue

            if key in {"include", "letters", "contain", "contains", "has"}:
                include_letters.update(value)
                continue

            position_match = re.match(r'^(?:pos|p)?([1-5])$', key)
            if position_match:
                position = int(position_match.group(1))
                positions[position] = value[0]
                continue

        if token.isalpha():
            include_letters.update(token)
        else:
            unknown_tokens.append(token)

    return include_letters, positions, unknown_tokens


def _filter_words(words: list[str], include_letters: set[str], positions: dict[int, str]) -> list[str]:
    if not words:
        return []

    filtered = []
    required_letters = set(include_letters)

    for word in words:
        if required_letters and not required_letters.issubset(set(word)):
            continue

        matches_positions = True
        for position, letter in positions.items():
            if word[position - 1] != letter:
                matches_positions = False
                break

        if matches_positions:
            filtered.append(word)

    return filtered


def _build_words_embed(
    words: list[str],
    page: int,
    include_letters: set[str],
    positions: dict[int, str],
    raw_query: str,
) -> discord.Embed:
    total = len(words)
    page_count = max(1, (total + WORDS_PER_PAGE - 1) // WORDS_PER_PAGE)
    start_index = (page - 1) * WORDS_PER_PAGE
    page_words = words[start_index : start_index + WORDS_PER_PAGE]

    description = "\n".join(page_words) if page_words else "No matching words found."
    embed = discord.Embed(
        title="5-Letter Word Finder",
        description=description,
        color=discord.Color.blue(),
    )
    embed.set_footer(text=f"Page {page}/{page_count} • {total} words matched")

    if include_letters:
        embed.add_field(
            name="Required letters",
            value=", ".join(sorted(include_letters)),
            inline=True,
        )

    if positions:
        embed.add_field(
            name="Position constraints",
            value=", ".join(
                f"{position}={letter}" for position, letter in sorted(positions.items())
            ),
            inline=True,
        )

    if raw_query:
        embed.add_field(name="Query", value=raw_query, inline=False)

    return embed


class WordListView(discord.ui.View):
    def __init__(self, author: discord.User, words: list[str], include_letters: set[str], positions: dict[int, str], raw_query: str):
        super().__init__(timeout=180)
        self.author = author
        self.words = words
        self.include_letters = include_letters
        self.positions = positions
        self.raw_query = raw_query
        self.current_page = 1
        self.total_pages = max(1, (len(words) + WORDS_PER_PAGE - 1) // WORDS_PER_PAGE)
        self._update_buttons()

    def _update_buttons(self) -> None:
        self.previous_button.disabled = self.current_page <= 1
        self.next_button.disabled = self.current_page >= self.total_pages

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message(
                "Only the command author can use these controls.",
                ephemeral=True,
            )
            return False
        return True

    @discord.ui.button(label="⬅️ Previous", style=discord.ButtonStyle.secondary)
    async def previous_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.current_page = max(1, self.current_page - 1)
        self._update_buttons()
        await interaction.response.edit_message(
            embed=_build_words_embed(self.words, self.current_page, self.include_letters, self.positions, self.raw_query),
            view=self,
        )

    @discord.ui.button(label="Close", style=discord.ButtonStyle.danger)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        for item in self.children:
            item.disabled = True
        self.stop()
        await interaction.response.edit_message(
            content="Word finder session closed.",
            view=self,
        )

    @discord.ui.button(label="Next ➡️", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.current_page = min(self.total_pages, self.current_page + 1)
        self._update_buttons()
        await interaction.response.edit_message(
            embed=_build_words_embed(self.words, self.current_page, self.include_letters, self.positions, self.raw_query),
            view=self,
        )


def setup_word_commands(bot: commands.Bot) -> None:
    """Register word-related commands on the bot."""

    @bot.command(name="words")
    async def words(ctx: commands.Context, *, options: str = ""):
        """
        Find 5-letter words from the word list.

        Usage:
            !words
            !words abc
            !words include=abc
            !words pos2=a pos5=c
            !words include=abc pos2=a pos5=c
        """
        if not FIVE_LETTER_WORDS:
            await ctx.send("Could not load the word list. Make sure valid-wordle-words.txt is present.")
            return

        include_letters, positions, unknown_tokens = _parse_word_options(options)
        filtered_words = _filter_words(FIVE_LETTER_WORDS, include_letters, positions)

        if not filtered_words:
            await ctx.send(
                "No words matched your query. "
                "Use `!words` to see all 5-letter words, or add filters like `include=abc` and `pos2=a`."
            )
            return

        view = WordListView(ctx.author, filtered_words, include_letters, positions, options)
        embed = _build_words_embed(filtered_words, view.current_page, include_letters, positions, options)
        await ctx.send(embed=embed, view=view)


__all__ = ["setup_word_commands"]
