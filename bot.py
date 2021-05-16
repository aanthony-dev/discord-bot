import time
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
       
    #Rhythm, your days are numbered
    if message.content.startswith('!p'):
        await message.channel.send('Support local. Use: `>play URL TIMECODE`')
            
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

        #if bot in voice channel already, don't do anything
        if voice:
            print('Bot already in channel')
        #connect to channel
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
            
            await asyncio.sleep(8)
            await voice.disconnect()
            
##############################################################################

#let's get to work
bot.run(TOKEN)
