import time
import discord
from discord.ext import commands
from discord.utils import get

from bot_functions import *

##############################################################################

#TODO:
#       make a function for on_voice_state_update.

##############################################################################

TOKEN = ''
BOT_PREFIX = '>'

bot = commands.Bot(command_prefix = BOT_PREFIX)

##############################################################################

#print when bot is ready
@bot.event
async def on_ready():
    print('Logged in as: ' + bot.user.name)

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
    
    #set user voice channel intro
    if message.content.startswith('>clip'):
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
            
##############################################################################

#whenever a user enters a voice channel, greet them
@bot.event
async def on_voice_state_update(member, before, after):
    #stop joining yourself stop joining yourself
    if member.id != bot.user.id:
        print(member.display_name, 'connected to:', after.channel)

        channel = after.channel
        voice = get(bot.voice_clients)

    #make sure bot not trying to join itself and user has joined a new channel
    if member.id != bot.user.id and after.channel != None and after.channel != before.channel:

        #if bot in voice channel already, move to new channel
        #DOES NOT ACTUALLY DO ANYTHING HAS TO DO WITH THE SLEEP FUNCTION
        if voice:
            await voice.move_to(channel)

        #connect to channel
        #THROWS ERROR IF USER JOINS ANOTHER CHANNEL BEFORE BOT LEAVES CURRENT
        else:
            voice = await channel.connect()
            print(f'Bot connected to: {channel}\n')

        #determine which audio file to play
        audio = str(member.id) + '.mp3'
        found_audio = False      
        for file in os.listdir('./'):
            if audio == file:
                found_audio = True
                break

        #play personal greeting
        if found_audio:
            play_audio(audio, voice)
        #play default greeting
        else:
            play_audio('audio_default.mp3', voice)
        
        time.sleep(10) #CHANGE THIS TO FIX
        await voice.disconnect()
            
##############################################################################

#let's get to work
bot.run(TOKEN)
