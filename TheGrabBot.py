import os
import discord
import GrabFunctions as grab
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

forbidden_words = ["flower", "flower", "flow3r", "fl0wer", "fl0w3r"]

@client.event
async def on_ready():
    print("We are ready")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    msg = message.content
    warning_emoji = "🚩"
    global s_level

    if msg.startswith("-grab test"):
        await message.channel.send("I am working")
    

# Grab Bot Security Feature Against Flower ID propaganda
    if msg.startswith("-grab security"):
        if "1" in msg:
            s_level = 1
            await message.channel.send("Security has been set to low")
        elif "2" in msg:
            s_level = 2
            await message.channel.send("Security has been set to medium")
        elif "3" in msg:
            s_level = 3
            await message.channel.send("Security has been set to high")
        # If grab security is called without a number, it will show the current security level
        else:
            try:
                s_level
            except NameError:
                s_level_set = False
            else:
                s_level_set = True
            await message.channel.send("Security Level is: {}".format(str(s_level) if s_level_set else "Not Set"))

    if any(word in msg for word in forbidden_words):
        if s_level == 1:
            print("Low secure", s_level)
            await message.channel.send("Warning, content has been flag as inappropriate :octagonal_sign:")
            await message.add_reaction(warning_emoji)
        
        if s_level == 2:
            print("M secure", s_level)
            await message.delete()
            await message.channel.send("This has been censored by Grab Bot TM (pls sponsor me)")

        if s_level == 3:
            print("H secure", s_level)
            await message.author.edit(mute=True)
            await message.delete()
            await message.channel.send("We don't speak of the f word in this server! Muted.")

client.run(TOKEN) # Start Bot using: py TheGrabBot.py