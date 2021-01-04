import os
import discord
import GrabFunctions as grab
import requests
# import json
from typing import List
from dotenv import load_dotenv
from replit import db
from KeepAlive import keep_alive
from better_profanity import profanity

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')

HELP_MSG = """```Commands for Grab Bot include:
              -grab need admin on  (turn on admin mode, only admins can turn this on)
              -grab need admin off (turn off admin mode, admin mode is default to off)
              -grab test           (to check if the bot is running)
              -grab security       (to check the security level)
              -grab security [int] (set security to: 1-low, 2-med, 3-high 0-reset)
              -grab pmode on       (turn postive mode on)
              -grab pmode off      (turn postive mode off)
              -grab pmode status   (check the state of the pmode)
              -grab user @user     (grab user into your voice channel)
              -grab user [all]     (grab all users in call into your voice channel)
              Github: (https://github.com/Simoidne/GrabBot)
            ```"""


# Set intents.member to true
intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

# Replit Databases
# database for global variables
db["s_level"] = {}
db["p_mode_status"] = {}
db["need_admin"] = {}
db["user_mute_list"] = {} #users muted by bot (used to unmute once security is reset)

# database for forbidden words
def get_forbidden_words_pMode_database():
    forbidden_words_pMode = []
    with open("forbidden_words_pMode.txt") as file:
        forbidden_words_pMode = [word.strip().lower() for word in file.readlines()]
        
    return forbidden_words_pMode
  
def get_forbidden_words_database():
    forbidden_words = []
    with open("forbidden_words.txt") as file:
        forbidden_words = [word.strip().lower() for word in file.readlines()]
      
    return forbidden_words

db["forbidden_words_pMode"] = get_forbidden_words_pMode_database()
db["forbidden_words"] = get_forbidden_words_database()


# Helper Functions
def create_random_words() -> List[str]:
    """Creates a list of random words from a random word API"""

    random_words = requests.get("https://random-word-api.herokuapp.com/home?/word?number=10")
    print("This is random_words: ", random_words.json())
    return ['']


def all_users_voice(list_voice_channel: list) -> list:
    """Returns a list of users connected to any of the voice channels in
    list_voice_channel
    """
    
    list_users = []
    for voice_channel in list_voice_channel:
        list_users.extend(voice_channel.members)
    return list_users


def add_new_guild(guild_id: str) -> None:
    """Initializes a guild into the database"""
    
    db["s_level"] = grab.update_database(db["s_level"], guild_id, 0)
    db["p_mode_status"] = grab.update_database(db["p_mode_status"], guild_id, False)
    db["user_mute_list"] = grab.update_database(db["user_mute_list"], guild_id, [])
    db["need_admin"] = grab.update_database(db["need_admin"],guild_id, False)


async def grab_user(list_users: list, channel) -> None:
    """Moves a user connected to voice to a specified channel"""
    
    for user in list_users:
        try:
            await user.move_to(channel)
        except:
            continue


async def unmute_users(dictionary: dict, guild_id, guild) -> None:
    """Takes in dictionary from db["user_mute_list"] and finds the 
    corresponding list of users through the guild_id. Unmutes all users 
    in the list if they are connected to voice, otherwise will storage
    user back into the muted user list for the guild.
    """
    
    list_users = dictionary[guild_id]
    new_list = []
    for user_id in list_users:
        user = guild.get_member(user_id)
        try:
            if user.voice.mute:
                await user.edit(mute=False)
        except:
            new_list.append(user_id)
    db["user_mute_list"] = grab.update_database(db["user_mute_list"], guild_id, new_list)



# The Bot
@client.event
async def on_ready():
    print("We are ready")
    game = discord.Game("use '-grab help'")
    await client.change_presence(status=discord.Status.online, activity=game)


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    is_admin = message.author.guild_permissions.administrator
    msg = message.content
    warning_emoji = "🚩"
    guild_id = str(message.guild.id)

    if guild_id not in db["s_level"]:
        add_new_guild(guild_id)

    if msg.startswith("-grab help"):
        await message.channel.send(HELP_MSG)

    if db["need_admin"][guild_id] and not is_admin:
        if msg.startswith("-grab "):
            await message.channel.send("Admin perms are required to use Grab Bot. Ask your server admin to give access to Grab Bot.")
        return

    if msg.startswith("-grab test"):
        create_random_words()
        await message.channel.send("I am working")

    if msg.startswith("-grab need admin"):
        if "off" in msg:
            db["need_admin"] = grab.update_database(db["need_admin"], guild_id, False)
            await message.channel.send("Everyone is now able to use Grab Bot")
        elif is_admin:
            db["need_admin"] = grab.update_database(db["need_admin"], guild_id, True)
            await message.channel.send("Admin perms are now required to use Grab Bot")
        else:
            await message.channel.send("Admin perms are needed to turn on 'need admin'")
    

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
        
        elif "0" in msg:
            db["s_level"] = grab.update_database(db["s_level"], guild_id, 0)
            await message.channel.send("Security has been turned off")
            await unmute_users(db["user_mute_list"], guild_id, message.guild)


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
                "This has been censored by Grab Bot TM")

        if db["s_level"][guild_id] == 3:
            print("H secure", db["s_level"][guild_id])
            await message.delete()
            await message.channel.send(
                "The content has been deemed dangerous. Muted.")
            try:
                await message.author.edit(mute=True)
                new_user_list = db["user_mute_list"][guild_id]
                new_user_list.append(message.author.id)
                db["user_mute_list"] = grab.update_database(db["user_mute_list"], guild_id, new_user_list)
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
    
    if profanity.contains_profanity(msg):
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
