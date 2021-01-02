import os
import discord
import GrabFunctions as grab
from dotenv import load_dotenv
from replit import db
from KeepAlive import keep_alive

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

# Set intents.member to true
intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

# Replit Databases
# database for global variables
db["s_level"] = {"794345762275721246": 0,
                "478352853887614986": 0}
db["p_mode_status"] = {"794345762275721246": False,
                      "478352853887614986": False}

# database for forbidden words
db["forbidden_words"] = ["flower", "league"]
db["forbidden_words_pMode"] = [
    "not",
    "non",
    "no",
    "noo",
    "bad",
    "garbage",
    "toxic",
    "terrible",
    "atrocious",
    "awful",
    "crummy",
    "dreadful",
    "lousy",
    "blah",
    "poor",
    "rough",
    "sad",
    "gross",
    "imperfect",
    "inferior",
    "crappy",
    "crap",
    "dissatisfactory",
    "inadequate",
    "incorrect",
    "substandard",
    "never",
    "nay",
    "forget it",
    "opposite",
    "refuse",
    "reject",
    "reverse",
    "negative",
    "sucks"
]

def all_users_voice(list_voice_channel) -> list:
    list_users = []
    for voice_channel in list_voice_channel:
        print(voice_channel)
        print(voice_channel.members)
        list_users.extend(voice_channel.members)
    return list_users
        

async def grab_user(list_users, channel) -> None:
    for user in list_users:
        try:
            await user.move_to(channel)
        except:
            continue

@client.event
async def on_ready():
    print("We are ready")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content
    warning_emoji = "🚩"
    guild_id = str(message.guild.id)

    if msg.startswith("-grab test"):
        await message.channel.send("I am working")

# Grab Bot Security Feature Against Flower ID propaganda
    if msg.startswith("-grab security"):
        if "1" in msg:
            db["s_level"] = grab.update_database(db["s_level"], guild_id, 1)
            await message.channel.send("Security has been set to low")
        
        elif "2" in msg:
            db["s_level"] = grab.update_database(db["s_level"], guild_id, 2)
            await message.channel.send("Security has been set to medium")

        elif "3" in msg:
            db["s_level"] = grab.update_database(db["s_level"], guild_id, 3)
            await message.channel.send("Security has been set to high")
        
        elif "reset" in msg:
            db["s_level"] = grab.update_database(db["s_level"], guild_id, 0)
            await message.channel.send("Security has been turned off")
        # If -grab security is called without a number, it will show the
        # current security level
        else:
            await message.channel.send("Security Level is: {}".format(
                str(db["s_level"][guild_id]) if db["s_level"][guild_id] != 0 else "Not Set"))

    if grab.msg_contains_forbidden(msg, db["forbidden_words"]):
        if db["s_level"][guild_id] == 1:
            print("Low secure", db["s_level"][guild_id])
            await message.channel.send(
                "Warning, content has been flagged as inappropriate :octagonal_sign:"
            )
            await message.add_reaction(warning_emoji)

        if db["s_level"][guild_id] == 2:
            print("M secure", db["s_level"][guild_id])
            await message.delete()
            await message.channel.send(
                "This has been censored by Grab Bot TM (pls sponsor me)")

        if db["s_level"][guild_id] == 3:
            print("H secure", db["s_level"][guild_id])
            await message.delete()
            await message.channel.send(
                "We don't speak of the f word in this server! Muted.")
            try:
                await message.author.edit(mute=True)
            except:
                print("User not connected to voice")

# Grab Positive Mode
    if msg.startswith("-grab pmode on"):
        db["p_mode_status"] = grab.update_database(db["p_mode_status"], guild_id, True)
        await message.channel.send("Grab Bot Positive Mode is activated")
    
    if msg.startswith("-grab pmode off"):
        db["p_mode_status"] = grab.update_database(db["p_mode_status"], guild_id, False)
        await message.channel.send("Grab Bot Positive Mode is now turned off")

    if msg.startswith("-grab pmode status"):
        await message.channel.send("Grab Bot Positive Mode is {}".format(
            "activated" if db["p_mode_status"][guild_id] else "not on"))
    
    if grab.msg_contains_forbidden(msg, db["forbidden_words_pMode"]):
        if db["p_mode_status"][guild_id]:
            await message.delete()
            await message.channel.send("Sorry this is a postive vibe server only")
    
# Grab Bot Grab Feature
    if msg.startswith("-grab user"):
        if "[all]" in msg:
            list_users = all_users_voice(message.guild.voice_channels)
            voice_channel = message.author.voice.channel
            await grab_user(list_users, voice_channel)

        else:
            list_users = message.mentions
            voice_channel = message.author.voice.channel
            await grab_user(list_users, voice_channel)

keep_alive()
client.run(TOKEN)  # Start Bot using: py TheGrabBot.py
