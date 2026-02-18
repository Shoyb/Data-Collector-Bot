from email.mime import message
import discord
import requests
import json
from words import sad_words
from words import starter_encouragement
import random
import sqlite3
from dotenv import load_dotenv
import os

conn = sqlite3.connect("database.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS user_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    saved_text TEXT
)
""")
conn.commit()


load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]['q'] + " -" + json_data[0]['a']
    return quote
def get_saved_data(user_id):
        cursor.execute("SELECT saved_text FROM user_data WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            return None
def get_data_list():
    cursor.execute("SELECT user_id, saved_text FROM user_data")
    return cursor.fetchall()
        
    
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
@client.event
async def on_ready():
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    msg = message.content.lower()
    if message.content.startswith('!hello'):
        await message.channel.send('Hello!')
    elif message.content.startswith('Pulak'):
        await message.channel.send('Diddy Pulak is GAY')
    elif message.content.startswith('awsaf'):
        await message.channel.send('awsaf is Pedo')
    elif message.content.startswith('toppers'):
        await message.channel.send('Pulak and Asfia are toppers')
    elif message.content.startswith('ray'):
        await message.channel.send('HIPPO')
    elif message.content.startswith('mimu'):
        await message.channel.send('Mimu is my waifu, We are so similar.')
    elif message.content.startswith('shuckle'):
        await message.channel.send('shuckle shuckle shuckle')
    elif message.content.startswith('I love Shoyb'):
        await message.channel.send('I love you too')
    elif message.content == 'A topper spotted':
        await message.channel.send('Pulak, The topper has been spotted, RUN!')
    elif message.content.startswith('quote'):
        quote = get_quote()
        await message.channel.send(quote)
    if any(word in message.content for word in sad_words):
        await message.channel.send(random.choice(starter_encouragement))
    if msg.startswith('data save '):
        text_to_save = message.content[len('data save '):]
        cursor.execute("""
        INSERT INTO user_data (user_id, saved_text)
        VALUES (?, ?)
        """, (message.author.id, text_to_save))
        conn.commit()
        await message.channel.send('Your data has been saved!')
    elif msg.startswith('data get list'):
            cursor.execute("SELECT user_id, saved_text FROM user_data")
            results = cursor.fetchall()
            if results:
                formatted = "\n".join(
                    [f"User {user_id}: {text}" for user_id, text in results]
                )
                await message.channel.send(f"All saved data:\n{formatted}")
            else:
                await message.channel.send("No data saved yet.")
    elif msg.startswith('data get'):
        cursor.execute(
        "SELECT saved_text FROM user_data WHERE user_id = ?",
        (message.author.id,))
        results = cursor.fetchall()
        if results:
            user_texts = "\n".join([row[0] for row in results])
            await message.channel.send(f"Your saved data:\n{user_texts}")
        else:
            await message.channel.send("You have no saved data.")
    elif msg.startswith("data meaning"):
        parts = msg.split(" ", 2)

        if len(parts) < 3:
            await message.channel.send("Please provide a word.")
            return

        word = parts[2].strip().lower()

        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(url)

        if response.status_code != 200:
            await message.channel.send("No meaning found.")
            return

        data = response.json()

        if not isinstance(data, list):
            await message.channel.send("No meaning found.")
            return

        embed = discord.Embed(
            title=word.capitalize(),
            color=discord.Color.blue()
        )

        meanings = data[0].get("meanings", [])

        for item in meanings:
            part_of_speech = item.get("partOfSpeech", "Unknown")
            definitions = item.get("definitions", [])

            formatted = ""
            for i, definition_obj in enumerate(definitions[:5], 1):
                definition = definition_obj.get("definition", "")
                formatted += f"{i}. {definition}\n"

            if formatted:
                embed.add_field(
                    name=part_of_speech,
                    value=formatted,
                    inline=False
                )

        if embed.fields:
            await message.channel.send(embed=embed)
        else:
            await message.channel.send("No meaning found.")
    if msg == 'data waifu':
            waifu_response = requests.get("https://api.waifu.im/images")
            img_url = waifu_response.json()["items"][0]["url"]
            
            embed = discord.Embed(
                title= "Here's your waifu!",
                color = discord.Color.random()
            )
            embed.set_image(url= img_url)
            await message.channel.send(embed = embed)

client.run(DISCORD_TOKEN)