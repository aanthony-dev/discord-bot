import asyncio

import discord
from discord.ext import commands, tasks
from discord.utils import get

from bot_functions import *

##############################################################################

# TODO:
#       - Polls for users to vote on things. Message where users vote with reactions.
#       - Dice rolling. i.e >roll 4d20
#       - Team generator. Users react to message and randomly make teams from them.

##############################################################################

TEST_GUILD = 401858796516933653     # Testing guild.
TEST_CHANNEL = 401858796516933655   # Testing text channel.

with open('token.txt') as f:
    TOKEN = f.readline()
BOT_PREFIX = '>'

bot = commands.Bot(command_prefix = BOT_PREFIX)

##############################################################################

@bot.event
async def on_ready():
    """
    Prints when the bot is logged into Discord and starts background tasks.
    """
    
    print(realtime.ctime(realtime.time()), '\t', 'Logged in as: ' + bot.user.name)
    #bot.loop.create_task(start_background_task())   
    
    background_task.start(bot) # Start looping background task.
    print(realtime.ctime(realtime.time()), '\t', "Background task started.")

##############################################################################

@bot.event
async def on_message(message):
    """
    Monitors all user messages, checking for any specific bot function requests.
    
    :param message:  The message that was sent by a user.
    """
    
    # Ignore yourself.
    if message.author.id == bot.user.id:
        return  
    
    # First things first, what does this do?.
    elif message.content.startswith('>help'):
        await get_help(message)
    
    # Search the wikipedias.
    elif message.content.startswith('>wiki'):
        await wiki_search(message, False)
            
    # Annoy Dave more.
    elif message.content.startswith('>more'):
        await wiki_search(message, True)
    
    # Old command for setting intro.
    elif message.content.startswith('>clip'):
        await message.channel.send('Command has changed. Use: `>intro URL TIMECODE`')
        
    # Set user voice channel intro.
    elif message.content.startswith('>intro'):
        set_intro(message)
        
    # Mock the last message of a user.
    elif message.content.startswith('>mock'):
        await mock(message)
         
    # Play youtube audio in voice channel.
    elif message.content.startswith('>play'):
        await play_youtube(message)
     
    # Make bot leave voice channel.
    elif message.content.startswith('>stop'):
        await leave_voice(message)
         
    # Serving up hot audio clips.
    elif message.content.startswith('>grab'):
        await grab_clip(message)
    
    # Have bot generate your meme for you.
    elif message.content.startswith('>meme'):
       await make_meme(message)
    
    # Secret dev testing.
    elif message.content.startswith('>test'):
        await roomba()
            
##############################################################################

@bot.event
async def on_voice_state_update(member, before, after):
    """
    Monitors all user voice channel changes, and introduces them 
    when applicable.
    
    :param member:  The member that joined a voice channel.
    :param before:  The voice channel the member was in previously.
    :param after:   The voice channel the member is currently in.
    """
    
    await play_intro(bot, member, before, after)
            
##############################################################################

# Let's get to work.
bot.run(TOKEN)
