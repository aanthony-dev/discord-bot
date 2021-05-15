import sys
import os
import random
import asyncio
from datetime import datetime
import youtube_dl
import wikipedia
import discord
from discord.ext import commands
from discord.utils import get

from ffmpy import FFmpeg

##############################################################################

#TODO: 
#       set_clip and grab_clip are basically the same thing
#       so make them one.
#       make wiki_search send messages that won't end mid sentence.

##############################################################################

#determines the length in seconds of audio clip outputs
CLIP_LENGTH = 7

##############################################################################

#do you need help? me too
async def help(message):
    await message.channel.send('I\'m a work in progress. Ask my dev... <@!258324838266044418>')
    await message.channel.send('`>clip URL TIMECODE` To set your voice channel intro. Get your best 7 second clip.\n' + 
    '`>play URL TIMECODE` To play a video in your voice channel.\n' +
    '`>stop` To make me leave the voice channel.\n' +
    '`>grab URL TIMECODE` To have me download and serve you up 7 seconds of audio.\n' +
    '`>wiki "SEARCH"` To have me read a wikipedia article directly into your ears.\n' +
    '`>more` To continue hearing me read wikipedia.\n' +
    '`>mock @USER` To have me mock a user\'s last message.\n')

##############################################################################

#function for bot to play local storage audio file in voice channel
def play_audio(audio, voice):
    voice.play(discord.FFmpegPCMAudio(audio))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.value = 0.07

##############################################################################

#set your john cena intro music
def set_clip(message, user_id):
    msg = message.content.split(' ')
    url = str(msg[1])
    time = str(msg[2])

    #download audio from url
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'set_clip.mp3', #name of downloaded file
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print('Downloading Audio\n')
        ydl.download([url])

    output_name = user_id + '.mp3'

    #cut download file down to clip length
    ff = FFmpeg(
        inputs={'set_clip.mp3': '-ss {0}'.format(time)},
        outputs={output_name: '-y -t {0}'.format(CLIP_LENGTH)}
    )
    ff.run()

    #remove downloaded file
    try:
        os.remove('set_clip.mp3')
    except PermissionError:
        print('Failed To Remove Download File')
        
##############################################################################

#upload a hot audio clip straight to discord        
async def grab_clip(message):
    msg = message.content.split(' ')
    url = str(msg[1])
    time = str(msg[2])
    
    #download audio from url
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'grab_clip_raw.mp3', #name of downloaded file
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    } 
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print('Downloading Audio\n')
        ydl.download([url])
        
    #cut download file down to clip length (curse discord upload limits)
    ff = FFmpeg(
        inputs={'grab_clip_raw.mp3': '-ss {0}'.format(time)},
        outputs={'grab_clip.mp3': '-y -t {0}'.format(CLIP_LENGTH)}
    )
    ff.run()
    
    await message.channel.send('Serving up the hottest clips:', file=discord.File('grab_clip.mp3'))
    
    #remove downloaded file
    try:
        os.remove('grab_clip_raw.mp3')
    except PermissionError:
        print('Failed To Remove Download File')
    
##############################################################################

#why not just look it up yourself?    
async def wiki_search(message, want_more):
    global wiki
    global more_count
    
    if want_more:
        more_count += 1
    else:
        msg = message.content.split(' ')
        wiki = wikipedia.summary(str(msg[1]))
        more_count = 0     
    try:   
        wiki_sentences = wiki.split('.')
        await message.channel.send(wiki[150*more_count:150*(more_count+1)], tts=True)
    except:
        await message.channel.send('I couldn\'t find it. Try using quotes, I like those.')  

##############################################################################

#very funny        
async def mock(message):
    msg = message.content.split(' ')
    #requested user to mock
    mock_user = msg[1][3:-1]
    
    mock_msg = ''
    result = ''
    
    #find the message
    async for old_message in message.channel.history(limit=25):
        if str(old_message.author.id) == str(mock_user):
            mock_msg = old_message.content
            break
    
    #generate the mock
    for i in range(len(mock_msg)):
        if i % 2 == 0:
            result += mock_msg[i].upper()
        else:
            result += mock_msg[i].lower()
    
    #add the most important part
    result += ' <:mock:784192319586828379>'
    
    #mock them
    await message.channel.send(result)
    
##############################################################################

#let's jam    
async def play_youtube(message):
    msg = message.content.split(' ')
    url = msg[1]
    timecode = None
    try:
        timecode = msg[2]
    except:
        pass
    
    song_exists = os.path.isfile('download.mp3')
    try:
        if song_exists:
            os.remove('download.mp3')
            print('Previous Audio Removed')
    except PermissionError:
        print('Failed To Remove Audio - Currently Playing')
        return
    
    print('VOICE CHANNEL: ' + str(message.author.voice.channel))

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'download.mp3',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '96',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print('Downloading Audio\n')
        dictMeta = ydl.extract_info(url, download=False)
    
        if dictMeta['duration'] < 600:
            await message.channel.send('Preparing.')
            ydl.download([url])
        else:
            await message.channel.send('No one wants to listen to this for that long.')
            return
        
    #cut download file down to start at given timecode
    if timecode is not None:
        ff = FFmpeg(
            inputs={'download.mp3': '-ss {0}'.format(timecode)},
            outputs={'download_trim.mp3': '-y -t {0}'.format(dictMeta['duration'])}
        )
        ff.run()
        voice = await message.author.voice.channel.connect()
        play_audio('download_trim.mp3', voice)
        try:
            timecode = int(timecode)
        except:
            pass
            
        if type(timecode) is int:
            time = int(timecode)          
        else:
            time = datetime.strptime(timecode, '%M:%S')
            time = time.second + time.minute * 60
            
        await asyncio.sleep(dictMeta['duration'] - time)
        await voice.disconnect()
    else:
        voice = await message.author.voice.channel.connect()
        play_audio('download.mp3', voice)
        await asyncio.sleep(dictMeta['duration'])
        await voice.disconnect()

##############################################################################

#time to go    
async def leave_voice(message):
    voice = message.guild.voice_client
    try:
        await voice.disconnect()
    except:
        await message.channel.send('To disconnect or not disconnect, that is the question.')
