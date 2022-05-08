import time as realtime
from datetime import datetime, time, timedelta
import asyncio
import discord
from discord.ext import commands
from discord.utils import get

from bot_functions import *

##############################################################################

#TODO:
#       make a function for on_voice_state_update.

##############################################################################

with open('token.txt') as f:
    TOKEN = f.readline()

BOT_PREFIX = '>'
INTRO_DIRECTORY = './intros/'

bot = commands.Bot(command_prefix = BOT_PREFIX)

##############################################################################

#print when bot is ready
@bot.event
async def on_ready():
    print(realtime.ctime(realtime.time()), '\t', 'Logged in as: ' + bot.user.name)

##############################################################################

#do the things
@bot.event
async def on_message(message):
    #ignore yourself
    if message.author.id == bot.user.id:
        return  
    
    #first things first, what does this do?
    if message.content.startswith('>help'):
        await help(message)
    
    #search the wikipedias
    if message.content.startswith('>wiki'):
        await wiki_search(message, False)
            
    #annoy dave more
    if message.content.startswith('>more'):
        await wiki_search(message, True)
    
    #old command for setting intro
    if message.content.startswith('>clip'):
        await message.channel.send('Command has changed. Use: `>intro URL TIMECODE`')
        
    #set user voice channel intro
    if message.content.startswith('>intro'):
        set_clip(message, str(message.author.id))
        
    #mock the last message of a user
    if message.content.startswith('>mock'):
        await mock(message)
         
    #play youtube audio in voice channel
    if message.content.startswith('>play'):
        await play_youtube(message)
     
    #make bot leave voice channel
    if message.content.startswith('>stop'):
        await leave_voice(message)
         
    #serving up hot audio clips
    if message.content.startswith('>grab'):
        await grab_clip(message)
     
    if message.content.startswith('>meme'):
       await make_meme(message)
        
    if message.content.startswith('>test'):
        await roomba()
            
##############################################################################

#whenever a user enters a voice channel, greet them
@bot.event
async def on_voice_state_update(member, before, after):
    #stop joining yourself stop joining yourself
    if member.id != bot.user.id:
        print(realtime.ctime(realtime.time()), '\t', member.display_name, 'connected to:', after.channel)

        channel = after.channel
        voice = get(bot.voice_clients)
    #make sure bot not trying to join itself and user has joined a new channel
    if member.id != bot.user.id and after.channel != None and after.channel != before.channel:

        #if bot in voice channel already, don't do anything
        if voice:
            print('Bot already in channel')
        #don't join the csgo channel
        elif channel.id == 672273919583191073:
            print('Cannot join CS:GO channel')
        #connect to channel
        else:

            voice = await channel.connect()
            print(realtime.ctime(realtime.time()), '\t', f'Bot connected to: {channel}')

            #determine which audio file to play
            audio = str(member.id) + '.mp3'
            found_audio = False      
            for file in os.listdir(INTRO_DIRECTORY):
                if audio == file:
                    found_audio = True
                    break

            #play personal greeting
            if found_audio:
                play_audio(INTRO_DIRECTORY + audio, voice)
            #play default greeting
            else:
                play_audio(INTRO_DIRECTORY + 'audio_default.mp3', voice)
            
            await asyncio.sleep(8)
            await voice.disconnect()
            
##############################################################################

WHEN = time(15, 30, 0)

async def called_once_a_day():  # Fired every day
    await bot.wait_until_ready()  # Make sure your guild cache is ready so the channel can be found via get_channel
    guild_id = 401858796516933653 #testing guild
    channel_id = 401858796516933655 #testing text channel
    channel = bot.get_guild(guild_id).get_channel(channel_id)
    await channel.send("once a day test!")

async def background_task():
    now = datetime.utcnow()
    print(realtime.ctime(realtime.time()), '\t', "Background task started.")
    WHEN = datetime.time(datetime.combine(now.date() + timedelta(seconds=10), time(0)))
    if now.time() > WHEN:  # Make sure loop doesn't start after {WHEN} as then it will send immediately the first time as negative seconds will make the sleep yield instantly
        tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))
        seconds = (tomorrow - now).total_seconds()  # Seconds until tomorrow (midnight)
        await asyncio.sleep(seconds)   # Sleep until tomorrow and then the loop will start 
    while True:
        now = datetime.utcnow() # You can do now() or a specific timezone if that matters, but I'll leave it with utcnow
        target_time = datetime.combine(now.date(), WHEN)  # 6:00 PM today (In UTC)
        seconds_until_target = (target_time - now).total_seconds()
        await asyncio.sleep(seconds_until_target)  # Sleep until we hit the target time
        await called_once_a_day()  # Call the helper function that sends the message
        tomorrow = datetime.combine(now.date() + timedelta(days=1), time(0))
        seconds = (tomorrow - now).total_seconds()  # Seconds until tomorrow (midnight)
        await asyncio.sleep(seconds)

##############################################################################

#let's get to work
bot.loop.create_task(background_task())
bot.run(TOKEN)
