import sys
import os
import random
import asyncio
import requests
import time as realtime
from datetime import datetime, time, timedelta

import youtube_dl
import wikipedia
import discord
from discord.ext import commands, tasks
from discord.utils import get
from ffmpy import FFmpeg

from memes import *

##############################################################################

# TODO: 
#       - set_intro and grab_clip are basically the same thing, merge them.
#       - Make wiki_search send messages that won't end mid sentence.
#       - Edit progress messages during audio downloads to keep users informed.

##############################################################################

TEST_GUILD = 401858796516933653     # Testing guild.
TEST_CHANNEL = 401858796516933655   # Testing text channel.

CLIP_LENGTH = 7                     # Length in seconds of audio clip outputs.
INTRO_DIRECTORY = './intros/'       # Directory that contains user intro audio clips.

##############################################################################

async def get_help(message):
    """
    Sends a help message to the channel where the help commands was requested.
    
    :param message:  The message that was sent to request help.
    """
    
    await message.channel.send('I\'m a work in progress. Ask my dev... <@!258324838266044418>')
    await message.channel.send('`>intro URL TIMECODE`\nTo set your voice channel intro. Get your best 7 second Youtube clip.\n' + 
    '`>play URL TIMECODE`\nTo play a video in your voice channel.\n' +
    '`>stop`\nTo make me leave the voice channel.\n' +
    '`>meme URL TEXT`\nHave me make the meme because you\'re too lazy to do it yourself.\n'
    '`>grab URL TIMECODE`\nTo have me download and serve you up 7 seconds of audio.\n' +
    '`>wiki "SEARCH"`\nTo have me read a wikipedia article directly into your ears.\n' +
    '`>more`\nTo continue hearing me read wikipedia.\n' +
    '`>mock @USER`\nTo have me mock a user\'s last message.\n')
    
##############################################################################

@tasks.loop(hours = 12.0) #seconds, minutes, hours are all acceptable params
async def background_task(bot):
    channel = bot.get_guild(TEST_GUILD).get_channel(TEST_CHANNEL)
    await channel.send('Background Task: ' + realtime.ctime(realtime.time()))

##############################################################################

async def play_intro(bot, member, before, after):
    """
    Plays a user's intro audio clip when they join a voice channel before leaving. 
    If the user does not have a specific intro, plays the default intro.
    
    :param bot:     The bot.  
    :param member:  The member that joined a voice channel.
    :param before:  The voice channel the member was in previously.
    :param after:   The voice channel the member is currently in.
    """
    
    # Stop joining yourself.
    if member.id != bot.user.id:
        print(realtime.ctime(realtime.time()), '\t', member.display_name, 'connected to:', after.channel)

        channel = after.channel
        voice = get(bot.voice_clients)
        
    # Make sure bot not trying to join itself and user has joined a new channel.
    if member.id != bot.user.id and after.channel != None and after.channel != before.channel:

        # If bot in voice channel already, don't do anything.
        if voice:
            print('Bot already in channel')
            
        # Don't join the CSGO channel.
        # TODO: File containing off limits channels that can be changed through bot commands.
        elif channel.id == 672273919583191073:
            print('Cannot join CS:GO channel')
            
        # Connect to channel.
        else:

            voice = await channel.connect()
            print(realtime.ctime(realtime.time()), '\t', f'Bot connected to: {channel}')

            # Determine which audio file to play.
            audio = str(member.id) + '.mp3'
            found_audio = False      
            for file in os.listdir(INTRO_DIRECTORY):
                if audio == file:
                    found_audio = True
                    break

            # Play personal greeting.
            if found_audio:
                play_audio(INTRO_DIRECTORY + audio, voice)
                
            # Play default greeting.
            else:
                play_audio(INTRO_DIRECTORY + 'audio_default.mp3', voice)
            
            await asyncio.sleep(8)
            await voice.disconnect()

##############################################################################

def play_audio(audio, voice):
    """
    Plays a given local storage audio file in a given voice channel.
    
    :param audio:   The audio file to be played.
    :param voice:   The voice channel to play the audio in.
    """
    
    voice.play(discord.FFmpegPCMAudio(audio))
    voice.source = discord.PCMVolumeTransformer(voice.source)
    voice.source.value = 0.07

##############################################################################

async def set_intro(message): 
    """
    Downloads and sets a user's custom intro audio. The user's message 
    must supply a Youtube URL and the time code they want their intro to 
    start at.
    
    :param message: The message that was sent to request an intro change.
    """
    
    user_id = str(message.author.id)
    msg = message.content.split(' ')
    url = str(msg[1])
    time = str(msg[2])

    # Download audio from URL.
    ydl_opts = {
        'verbose': False,
        'format': 'bestaudio/best',
        'outtmpl': 'set_clip.mp3',          # Name of downloaded file.
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    await message.channel.send('Download Percentage: ' + str(0) + '%') # TODO: edit this to show progress.
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print(realtime.ctime(realtime.time()), '\t', 'Downloading Audio')
        ydl.download([url])

    output_name = user_id + '.mp3'

    # Cut download file down to clip length.
    ff = FFmpeg(
        inputs={'set_clip.mp3': '-ss {0}'.format(time)},
        outputs={output_name: '-y -t {0}'.format(CLIP_LENGTH)}
    )
    ff.run()

    # Remove downloaded file.
    try:
        os.remove('set_clip.mp3')
    except PermissionError:
        print(realtime.ctime(realtime.time()), '\t', 'Failed To Remove Download File')
        
##############################################################################

def callable_hook(response):
    """
    Hook used during a YoutubeDL download process to monitor
    and keep users notified of download progress.
    
    :param response:    Response from YoutubeDL during download.
    """
    
    if response['status'] == 'downloading':
        speed = response['speed']
        downloaded_percent = round((response['downloaded_bytes'] * 100) / response['total_bytes'], 1)
        print('TEST:', str(downloaded_percent))
     
async def grab_clip(message):
    """
    Downloads an audio clip from Youtube URL and uploads it to
    the Discord channel a user requested it in. The user's message 
    must supply a Youtube URL and the time code they want their clip to 
    start at.
    
    :param message: The message that was sent to request an audio clip.
    """
    
    msg = message.content.split(' ')
    url = str(msg[1])
    time = str(msg[2])
    
    # Download audio from URL.
    ydl_opts = {
        'verbose': False,
        'format': 'bestaudio/best',
        'progress_hooks': [callable_hook],
        'outtmpl': 'grab_clip_raw.mp3',     # Name of downloaded file.
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    } 
    await message.channel.send('Download Percentage: ' + str(0) + '%') # TODO: edit this to show progress.
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print(realtime.ctime(realtime.time()), '\t', 'Downloading Audio')
        ydl.download([url])
        
    # Cut download file down to clip length (curse discord upload limits).
    ff = FFmpeg(
        inputs={'grab_clip_raw.mp3': '-ss {0} -hide_banner -loglevel error'.format(time)},
        outputs={'grab_clip.mp3': '-y -t {0}'.format(CLIP_LENGTH)}
    )
    ff.run()

    await message.channel.send('Serving up the hottest clips:', file=discord.File('grab_clip.mp3'))
    
    # Remove downloaded file.
    try:
        os.remove('grab_clip_raw.mp3')
    except PermissionError:
        print(realtime.ctime(realtime.time()), '\t', 'Failed To Remove Download File')
    
##############################################################################
  
async def wiki_search(message, want_more):
    """
    Performs a wikipedia search for the user requested search term and
    sends the result into the requested text channel using text-to-speech
    for maximum knowledge effect.
    
    :param message:     The message that was sent to request wiki search.
    :param want_more:   Does user wants to know more about last wiki search.
    """
    
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
     
async def mock(message):
    """
    Sends a mocking version of the last message from a specified user in the
    mock request. The user's requesting message must @ the user they want to have
    mocked.
    
    :param message:     The message that was sent to request a mock.
    """
    
    msg = message.content.split(' ')
    mock_user = msg[1][3:-1] # Requested user to mock.
    
    mock_msg = ''
    result = ''
    
    # Find the mocked user's last message.
    async for old_message in message.channel.history(limit=25):
        if str(old_message.author.id) == str(mock_user):
            mock_msg = old_message.content
            break
    
    # Generate the mock.
    for i in range(len(mock_msg)):
        if i % 2 == 0:
            result += mock_msg[i].upper()
        else:
            result += mock_msg[i].lower()
    
    # Add the most important part.
    result += ' <:mock:784192319586828379>'
    
    # Mock them.
    await message.channel.send(result)
    
##############################################################################
 
async def play_youtube(message):
    """
    Downloads and plays the audio from a Youtube URL in the voice channel 
    the requesting user is currently in.
    
    :param message:     The message that was sent to request playing of Youtube.
    """
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
            print(realtime.ctime(realtime.time()), '\t', 'Previous Audio Removed')
    except PermissionError:
        print(realtime.ctime(realtime.time()), '\t', 'Failed To Remove Audio - Currently Playing')
        return
    
    print(realtime.ctime(realtime.time()), '\t', 'VOICE CHANNEL: ' + str(message.author.voice.channel))

    ydl_opts = {
        'verbose': False,
        'format': 'bestaudio/best',
        'outtmpl': 'download.mp3',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '96',
        }],
    }
    await message.channel.send('Download Percentage: ' + str(0) + '%') # TODO: edit this to show progress.
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        print(realtime.ctime(realtime.time()), '\t', 'Downloading Audio\n')
        dictMeta = ydl.extract_info(url, download=False)
    
        if dictMeta['duration'] < 600:
            ydl.download([url])
        else:
            await message.channel.send('No one wants to listen to this for that long.')
            return
        
    # Cut download file down to start at given timecode.
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
  
async def leave_voice(message):
    """
    Leaves any voice channel in the guild that the requesting message is from.
    
    :param message:     The message that was sent to request leaving.
    """
    
    voice = message.guild.voice_client
    try:
        await voice.disconnect()
    except:
        await message.channel.send('To disconnect or not disconnect, that is the question.')

##############################################################################

async def make_meme(message):
    """
    Generates and uploads a meme based on the requesting message's contents. 
    The message must contains a link to an image folllowed by text to be placed
    over the image. The meme is uploaded to the text channel it was requested in.
    
    :param message:     The message that was sent to request a meme.
    """
    
    msg = message.content.split(' ')
    url = msg[1]
    text = msg[2:]
    text_split = int(len(text) / 2)
    print(text)
    print(int(len(text) / 2))
    top_text = ' '.join(text[0:text_split])
    bottom_text = ' '.join(text[text_split:])
    print(top_text)
    print(bottom_text)
    
    create_image(url, top_text, bottom_text)
    await message.channel.send('Mmmmm fresh memes:', file=discord.File('meme.png'))

############################### WIP #########################################

async def roomba():
    print(realtime.ctime(realtime.time()), '\t', Client.guilds)

async def check_stock(message):
    with requests.get("https://finance.yahoo.com/quote/" + ticker, stream=True) as r:
        source = r.text
        source = source.split("<span")

        for line in source:
            if 'class="Trsdu(0.3s) Fw(b) Fz(36px) Mb(-4px) D(ib)"' in line:
                line = line.split(">")[1]
                num = line.split("<")[0]
                print(num)
            if 'class="Trsdu(0.3s) Fw(500) Pstart(10px) Fz(24px)' in line:
                line = line.split(">")[1]
                num = line.split("<")[0]
                print(num)


    
