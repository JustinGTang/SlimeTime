''' SlimeTime Dicord Bot'''
import discord
from discord.ext import commands, tasks
import pymongo
from pymongo import MongoClient
from datetime import datetime, date, time
import asyncio
import random
import requests
from bs4 import BeautifulSoup
import re

with open('slime_token.txt', 'r') as f:
    TOKEN = f.readline()

with open('mongo_url.txt', 'r') as f:
    MONGO = f.readline()

cluster = MongoClient(MONGO)
db = cluster['Discord']
musicDB = db['Spotify']
mapleDB = db['Maplestory']

slime = commands.Bot(command_prefix = '-')
slime.remove_command('help')

channel = None
sntich_mode = False
daily_state = False
weekly_state = False
track = False
guild = None
maintenance = False
users = {}
daily_tasks = ['Ursus', 'Gollux', 'Maple Tour', 'Arcane River Quests', 'Arcane River Jobs', 'Arkarium/Ranmaru', 'Commerci', 'Monster Park']
weekly_tasks = ['Scrapyard', 'Dark World Tree', 'Lotus', 'Damien', 'Lucid', 'CRA']

#---- EVENTS ----#
@slime.event
async def on_ready():
    embed = discord.Embed(colour = discord.Colour.green())
    embed.set_author(name = 'Hello, I am SlimeTime! Type -help for a list of commands and toggles! Type -toggle to start all the toggles.')

    guilds = slime.guilds
    for guild in guilds:
        channel = guild.text_channels[0]
        await channel.send(embed = embed)

    await slime.change_presence(activity = discord.Game('Grinding Mesos'))
    maintenance_check.start()
    print('Bot is online!')

@slime.event
async def on_message(message):
    global maintenance
    global track
    global guild
    guild = message.guild
    if track == False:
        init_songs()
        spotify_tracker.start()
        track = True
        print('Now tracking songs.')
    if(message.author.name != 'SlimeTime'):
        if(message.content == 'lucid?' or message.content == 'lomien?'):
            index = 0
            for x in message.guild.roles:
                if str(x) == 'Maple':
                    mention = message.guild.roles[index].mention
                    await message.channel.send(mention)
                else:
                    index += 1
        elif(message.content == 'slatt'):
            await message.channel.send('https://i1.wp.com/www.passionweiss.com/wp-content/uploads/2019/10/DgENgW3WAAAbLdY.jpeg?resize=749%2C749&ssl=1')
        elif(message.content == 'LOL'):
            await message.channel.send('https://external-preview.redd.it/Rp6OukRwEmSaoQwZCyYiWcapeTWSw82UEclX9-4Wcvk.png?auto=webp&s=85e04ca7752e482c613066bf6a725ab58243dba7')  
        else:
            await slime.process_commands(message)

@slime.event
async def on_message_delete(message):
    if(message.author.name != 'SlimeTime'):
        if(sntich_mode == True):
            await message.channel.send(f'{message.author} said: {message.content}')

#---- COMMANDS ----#

# MAPLESTORY COMMANDS
@slime.command()
async def daily(ctx):
    global channel
    global daily_state 
    daily_state = True
    channel = ctx.message.channel
    embed = discord.Embed(colour = discord.Colour.green())
    embed.set_author(name = 'Notifications for dailies turned on!', icon_url = 'https://www.freeiconspng.com/thumbs/checkmark-png/checkmark-png-5.png')
    await ctx.send(embed = embed)
    await wait_for_hour(start_count())
    daily_reset_message.start()

@slime.command()
async def weekly(ctx):
    global channel
    global weekly_state
    weekly_state = True
    channel = ctx.message.channel
    embed = discord.Embed(colour = discord.Colour.green())
    embed.set_author(name = 'Notifications for weeklys turned on!', icon_url = 'https://www.freeiconspng.com/thumbs/checkmark-png/checkmark-png-5.png')
    await ctx.send(embed = embed)
    await wait_for_hour(get_weekly_wait_time())
    weekly_reset_message.start()

async def wait_for_hour(secondsTilHour):
    print('Waiting for ' + str(secondsTilHour) + ' seconds.')
    await asyncio.sleep(secondsTilHour)

def get_weekly_wait_time():
    current_date = datetime.now()
    display_day = 2 - int(current_date.strftime("%w"))
    # Calulate days until next wednesday
    if display_day < 0:
        display_day += 6

    current_time = datetime.now().time()
    display_hour = 16 - int(current_time.strftime("%H"))
    display_min = 60 - int(current_time.strftime("%M"))
    current_seconds = current_time.strftime("%S")
    display_sec = 59 - int(current_seconds)

    if(display_hour < 0):
        display_hour += 24
    if(display_min == 60):
        display_min = 0
        display_hour += 1
    
    wait_time = (display_day * 86400) + (display_hour * 3600) + (display_min * 60) + display_sec
    return wait_time

def start_count():
    current_time = datetime.now()
    current_time = current_time.time()

    currentMinute = current_time.strftime("%M")
    remaining_Minutes = 60 - int(currentMinute)
    current_seconds = current_time.strftime("%S")
    remaining_seconds = 59 - int(current_seconds)
    print(remaining_Minutes, remaining_seconds)
    remaining_seconds = (int(remaining_Minutes) * 60) + int(current_seconds)
    return remaining_seconds

@slime.command()
async def stop(ctx, choice = 'None'):
    if choice == 'daily':
        global daily_state 
        daily_state = False
        embed = discord.Embed(colour = discord.Colour.green())
        embed.set_author(name = 'Dailies notifcations stopped.', icon_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Dark_Red_x.svg/600px-Dark_Red_x.svg.png')
        await ctx.send(embed = embed)
        daily_reset_message.stop()
    elif choice == 'weekly':
        global weekly_state 
        weekly_state = False
        embed = discord.Embed(colour = discord.Colour.green())
        embed.set_author(name = 'Weekly notifcations stopped.', icon_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Dark_Red_x.svg/600px-Dark_Red_x.svg.png')
        await ctx.send(embed = embed)
        weekly_reset_message.stop()
    elif choice == 'track':
        global track
        track = False
        embed = discord.Embed(colour = discord.Colour.green())
        embed.set_author(name = 'Spotify tracking stopped.', icon_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Dark_Red_x.svg/600px-Dark_Red_x.svg.png')
        await ctx.send(embed = embed)
        spotify_tracker.stop()
    else:
        embed = discord.Embed(colour = discord.Colour.green())
        embed.set_author(name = 'Please use one of the following valid commands:\n -stop daily\n -stop weekly\n -stop track')
        await ctx.send(embed = embed)

@slime.command()
async def reset(ctx):
    embed = discord.Embed(colour = discord.Colour.green())
    current_date = datetime.now()
    current_time = datetime.now().time()
    display_day = 3 - int(current_date.strftime("%w"))
    # Calulate days until next wednesday
    if display_day <= 0:
        display_day += 6
    display_hour = 16 - int(current_time.strftime("%H"))
    display_min = 60 - int(current_time.strftime("%M"))

    if(display_hour < 0):
        display_hour += 24
    if(display_min == 60):
        display_min = 0
        display_hour += 1

    if(display_hour == 0):
        display_time = f'Reset is in {display_min} minutes.\n'
    else:
        display_time = f'Reset is in {display_hour} hours and {display_min} minutes.\n'
    
    if display_day != 0:
        display_time += f'Weeklys reset in {display_day} days and {display_hour} hours.'
    else:
        display_time += f'Weeklys reset in {display_hour} hours and {display_min} minutes.'

    embed.set_author(name = display_time)
    await ctx.send(embed = embed)

@slime.command()
async def links(ctx):
    embed = discord.Embed(colour = discord.Colour.green())
    embed.set_author(name = 'Helpful Links', icon_url = 'https://www.freeiconspng.com/thumbs/checkmark-png/checkmark-png-5.png')
    embed.add_field(name = 'Familiars', value = 'https://docs.google.com/spreadsheets/d/1HShIqsK0zghH6BnrFgJJnrxOXcauHbGpgX8gL310NNQ/edit#gid=0', inline = False)
    embed.add_field(name = 'Legion', value = 'https://ayumilove.net/maplestory-maple-union-guide/', inline = False)
    await ctx.send(embed = embed)

# CHAT COMMANDS
@slime.command()
async def snitch(ctx):
    global sntich_mode
    embed = discord.Embed(colour = discord.Colour.green())
    if(sntich_mode == False):
        sntich_mode = True
        embed.set_author(name = 'Snitch Mode On', icon_url = 'https://www.freeiconspng.com/thumbs/checkmark-png/checkmark-png-5.png')
    elif(sntich_mode == True):
        sntich_mode = False
        embed.set_author(name = 'Snitch Mode Off', icon_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Dark_Red_x.svg/600px-Dark_Red_x.svg.png')
    await ctx.send(embed = embed)

@slime.command()
async def delete(ctx, num = 2):
    await ctx.channel.purge(limit = num + 1)
    message = f'Deleted {num} messages'
    embed = discord.Embed(
        colour = discord.Colour.green()
    )
    embed.set_author(name = message)
    await ctx.send(embed = embed)

@slime.command()
async def help(ctx, choice = 'None'):
    embed = discord.Embed(colour = discord.Colour.green())
    choice = choice.lower()
    if choice == 'maplestory':
        embed.set_author(name = 'Maplestory Commands', icon_url = 'https://img.pngio.com/introduce-yourself-forums-official-maplestory-2-website-maplestory-png-240_240.png')
        embed.add_field(name = '-daily', value = 'Turn on daily reset notifications.', inline = False)
        embed.add_field(name = '-weekly', value = 'Turn on weekly reset notifications.', inline = False)
        embed.add_field(name = '-stop', value = 'Specify daily or weekly to turn off reset notifications.', inline = False)
        embed.add_field(name = '-reset', value = 'Tells you when dailies and weeklys reset.', inline = False)
        embed.add_field(name = '-links', value = 'Helpful links for Maplestory.', inline = False)
        embed.set_footer(text = 'Page 2/5')
    elif choice == 'chat':
        embed.set_author(name = 'Chat Commands', icon_url = 'https://www.pinclipart.com/picdir/big/51-510498_clipart-info-white-outline-speech-bubble-transparent-png.png')
        embed.add_field(name = '-delete x', value = 'Deletes x amount of messages.', inline = False)
        embed.add_field(name = '-snitch', value = 'Turns on/off snitch mode.', inline = False)
        embed.set_footer(text = 'Page 3/5')
    elif choice == 'music':
        embed.set_author(name = 'Music Commands', icon_url = 'https://www.freepnglogos.com/uploads/spotify-logo-png/spotify-icon-marilyn-scott-0.png')
        embed.add_field(name = '-spotify', value = 'Lists the users currently listening to Spotify, as well as the song they are listening to.', inline = False)
        embed.add_field(name = '-song [x]', value = 'Get info on the number [x] song in the currently listening list.', inline = False)
        embed.add_field(name = '-top', value = 'Get your top 10 most listened to songs. Use -top 2 to see page 2.', inline = False)
        embed.add_field(name = '-artists [x]', value = 'View your top 5 artists, or @someone and see their top 5 artists.', inline = False)
        embed.add_field(name = '-playcount [x]', value = 'View your total playcount, or @someone and see total playcount.', inline = False)
        embed.add_field(name = '-leaderboard', value = 'View the top 5 listeners on the server.', inline = False)
        embed.set_footer(text = 'Page 4/5')
    elif choice == 'general':
        embed.set_author(name = 'General Commands', icon_url = 'https://icons.iconarchive.com/icons/paomedia/small-n-flat/1024/cog-icon.png')
        embed.add_field(name = '-flip', value = 'A coinflip.', inline = False)
        embed.add_field(name = '-state', value = 'Check the state of toggles', inline = False)
        embed.add_field(name = '-toggle', value = 'Turns all toggles on.', inline = False)
        embed.set_footer(text = 'Page 5/5')
    else: 
        embed.set_author(name = 'Command List', icon_url = 'https://banner2.cleanpng.com/20190118/fzg/kisspng-computer-icons-shopping-list-clip-art-portable-net-shopping-list-sketch-icon-royalty-free-vector-imag-5c426370b23315.6744144015478547047299.jpg')
        embed.add_field(name = 'Use -help [list] for further details. (Example: -help general)', value = '\u200B', inline = False)
        embed.add_field(name = 'Maplestory', value = 'Commands for Maplestory daily reset', inline = False)
        embed.add_field(name = 'Chat', value = 'Commands to edit chat', inline = False)
        embed.add_field(name = 'Music', value = 'Commands to check music stats', inline = False)
        embed.add_field(name = 'General', value = 'A variety of commands', inline = False)
        embed.set_footer(text = 'Page 1/5')
    await ctx.send(embed = embed)



# MUSIC COMMANDS
@slime.command()
async def spotify(ctx):
    guild = ctx.guild
    listeners = 0
    listernerList = ''
    embed = discord.Embed(colour = discord.Colour.green())
    embed.set_author(name = 'Currently Listening', icon_url = 'https://www.freepnglogos.com/uploads/spotify-logo-png/spotify-icon-marilyn-scott-0.png')
    for member in guild.members:
            if member.activities:
                for activity in member.activities:
                    if activity.name == 'Spotify':
                        listeners = 1
                        embed.add_field(name = member.display_name, value = f'{activity.title} - {activity.artist}', inline = False)
    if listeners == 0:
        embed.set_author(name = 'No one is currently listening to Spotify.')
    await ctx.send(embed = embed)

@slime.command()
async def song(ctx, num):
    guild = ctx.guild
    song = 0
    embed = discord.Embed(colour = discord.Colour.green())
    for member in guild.members:
            if member.activities:
                for activity in member.activities:
                    if activity.name == 'Spotify':
                        song += 1
                        if song == int(num):
                            embed.set_author(name = activity.title, icon_url = 'https://www.freepnglogos.com/uploads/spotify-logo-png/spotify-icon-marilyn-scott-0.png')
                            embed.add_field(name = activity.artist, value = activity.album, inline = True)
                            embed.set_image(url = activity.album_cover_url)
    if song == 0:
        embed.set_author(name = 'No one is currently listening to Spotify.')
    await ctx.send(embed = embed)

def init_songs():
    global users
    # Initialize current songs list
    for member in guild.members:
            if member.activities:
                for activity in member.activities:
                    #Find someone listening to music
                    if activity.name == 'Spotify':
                        # Update current song dictionary
                        currentSong = users.get(member.name, 0)
                        # User not in currently listening dictionary yet or user is listening to a new song
                        if currentSong == 0 or currentSong != activity.title:
                            users[member.id] = f'{activity.title}'

@slime.command()
async def top(ctx, choice = 'None'):
    first = True
    person = musicDB.find_one({'_id':ctx.author.id})
    song_list = person['song']
    song_list.sort(key = lambda x: x[2], reverse = True)
    embed = discord.Embed(colour = discord.Colour.green())
    length = len(song_list)
    if length < 6 and choice != 'None':     # Only show first page
        choice = 'None'
    
    if choice == 'None':
        if length > 5:
            length = 5
            embed.set_footer(text = 'Page 1/2: Type -top 2 to see page 2')
        topFiveSongs = song_list[0:length]
        embed.set_author(name = f'Your top {length} tracks are: ', icon_url = 'https://www.freepnglogos.com/uploads/spotify-logo-png/spotify-icon-marilyn-scott-0.png')
        for songs in topFiveSongs:
            embed.add_field(name = songs[0], value = songs[1], inline = True)
            embed.add_field(name = '\u200B', value = '\u200B', inline = True)
            if first == True:
                embed.add_field(name = 'Play Count', value = songs[2], inline = True)
                first = False
            else:
                embed.add_field(name = '\u200B', value = songs[2], inline = True)
    else:
        if length > 10:
            length = 10
        topTenSongs = song_list[5:length]
        embed.set_author(name = f'Your top 6 through {length} tracks are:', icon_url = 'https://www.freepnglogos.com/uploads/spotify-logo-png/spotify-icon-marilyn-scott-0.png')
        for songs in topTenSongs:
            embed.add_field(name = songs[0], value = songs[1], inline = True)
            embed.add_field(name = '\u200B', value = '\u200B', inline = True)
            if first == True:
                embed.add_field(name = 'Play Count', value = songs[2], inline = True)
                first = False
            else:
                embed.add_field(name = '\u200B', value = songs[2], inline = True)
        embed.set_footer(text = 'Page 2/2')
    
    await ctx.send(embed = embed)

@slime.command()
async def artists(ctx, person = 'None'):
    embed = discord.Embed(colour = discord.Colour.green())
    artists = {}
    if person == 'None':
        member = ctx.author.id
    else:
        member = int(person.strip('<!@>'))
    person = musicDB.find_one({'_id': member})
    song_list = person['song']
    for songs in song_list:
        artistName = songs[1].split(';')
        play_count = songs[2]
        # If artist is not in temp dictionary yet
        if artistName[0] in artists:
            plays = artists[artistName[0]]
            artists[artistName[0]] = plays + play_count
        else:
            artists[artistName[0]] = play_count

    artists = sorted(artists.items(), key = lambda x: x[1], reverse = True)
    if len(artists) <= 5:
        top5 = len(artists) - 1
    else:
        top5 = 4

    embed.set_author(name = f'Your top 5 Artists are: ', icon_url = 'https://www.freepnglogos.com/uploads/spotify-logo-png/spotify-icon-marilyn-scott-0.png')
    embed.add_field(name = 'Artists', value = artists[0][0], inline = True)
    embed.add_field(name = '\u200B', value = '\u200B', inline = True)
    embed.add_field(name = 'Play Count', value = artists[0][1], inline = True)
    for x in range(top5):
        embed.add_field(name = '\u200B', value = artists[x + 1][0], inline = True)
        embed.add_field(name = '\u200B', value = '\u200B', inline = True)
        embed.add_field(name = '\u200B', value = artists[x + 1][1], inline = True)

    await ctx.send(embed = embed)

@slime.command()
async def playcount(ctx, person = 'None'):
    embed = discord.Embed(colour = discord.Colour.green())
    if person == 'None':
        member = ctx.author.id
    else:
        member = int(person.strip('<!@>'))

    play_count = find_count(member)

    embed.set_author(name = f'You have a total play count of {play_count}.', icon_url = 'https://www.freepnglogos.com/uploads/spotify-logo-png/spotify-icon-marilyn-scott-0.png')
    await ctx.send(embed = embed)

@slime.command()
async def leaderboard(ctx, person = 'None'):
    global guild
    embed = discord.Embed(colour = discord.Colour.green())
    member_count = {}

    for member in guild.members:
        count = find_count(member.id)
        member_count[member.name] = count

    leaders = sorted(member_count.items(), key = lambda x: x[1], reverse = True)
    if len(leaders) <= 5:
        top5 = len(leaders) - 1
    else:
        top5 = 4

    embed.set_author(name = f'The top 5 listeners are: ', icon_url = 'https://www.freepnglogos.com/uploads/spotify-logo-png/spotify-icon-marilyn-scott-0.png')
    embed.add_field(name = 'Listener', value = leaders[0][0], inline = True)
    embed.add_field(name = '\u200B', value = '\u200B', inline = True)
    embed.add_field(name = 'Play Count', value = leaders[0][1], inline = True)
    for x in range(top5):
        embed.add_field(name = '\u200B', value = leaders[x + 1][0], inline = True)
        embed.add_field(name = '\u200B', value = '\u200B', inline = True)
        embed.add_field(name = '\u200B', value = leaders[x + 1][1], inline = True)

    await ctx.send(embed = embed)

def find_count(personID):
    global guild
    embed = discord.Embed(colour = discord.Colour.green())
    play_count = 0

    for member in guild.members:
        if personID == member.id:
                person = musicDB.find_one({'_id': member.id})
                # If they have no songs in database
                if person == None:
                    return play_count

                song_list = person['song']
                for songs in song_list:
                    play_count += songs[2]
    return play_count



# GENERAL COMMANDS
@slime.command()
async def state(ctx):
    global sntich_mode
    global daily_state
    global weekly_state
    embed = discord.Embed(colour = discord.Colour.green())
    embed.set_author(name = 'Current Toggle States')

    if daily_state == True:
        embed.add_field(name = 'Daily', value = 'On', inline = False)
    else:
        embed.add_field(name = 'Daily', value = 'Off', inline = False)
    if weekly_state == True:
        embed.add_field(name = 'Weekly', value = 'On', inline = False)
    else:
        embed.add_field(name = 'Weekly', value = 'Off', inline = False)
    if sntich_mode == True:
        embed.add_field(name = 'Snitch Mode', value = 'On', inline = False)
    else:
        embed.add_field(name = 'Snitch Mode', value = 'Off', inline = False)
    await ctx.send(embed = embed)

@slime.command()
async def flip(ctx):
    embed = discord.Embed(colour = discord.Colour.green())
    choice = random.randint(0,1)
    if choice == 0:
        embed.set_author(name = 'Yes')
    else:
        embed.set_author(name = 'No')
    await ctx.send(embed = embed)

#---- TASKS ----#
@tasks.loop(hours = 1)
async def daily_reset_message():
    # Use this to put daily reset notifcation in first channel messaged in
    embed = discord.Embed(colour = discord.Colour.green())
    global channel

    current_datetime = datetime.now()
    current_time = current_datetime.time()
    current_hour = current_time.strftime("%H")
    reset_hour = 17 - int(current_hour)   #5PM
    if reset_hour == 0:
        embed.set_author(name = 'Dailies Reset!')
        await channel.send(embed = embed)
    elif reset_hour > 0 and reset_hour < 5:
        embed.set_author(name = f'Reset is in {reset_hour} hours')
        await channel.send(embed = embed)

@tasks.loop(hours = 168)
async def weekly_reset_message():
    # Use this to put daily reset notifcation in first channel messaged in
    global channel
    embed = discord.Embed(colour = discord.Colour.green())
    embed.set_author(name = 'Weeklys Reset!')
    await channel.send(embed = embed)

@tasks.loop(seconds = 5)
async def spotify_tracker():
    global guild
    global users
                      
    for member in guild.members:
            if member.activities:
                for activity in member.activities:
                    if activity.name == 'Spotify':  #Find someone listening to music
                        # If listener is in currently listening list
                        if member.id in users:                        
                            found = False
                            # Database changes
                            if musicDB.find_one({'_id': member.id}) == None:   # If its a new person
                                print(f"New Member - {member.name}")
                                musicDB.insert_one({
                                    '_id': member.id, 
                                    'name': f'{member.name}', 
                                    # List of tuples with song name and play count
                                    'song': [ (f'{activity.title}', f'{activity.artist}', 1) ]
                                })      
                            else:
                                # Check their list of songs
                                person = musicDB.find_one({'_id': member.id})
                                song_list = person['song']
                                for songs in song_list:
                                    if songs[0] == activity.title:   # Found song in users list
                                        found = True
                                        count = songs[2] + 1
                                        if activity.title != users[member.id]:    # If the song was not their previous current song
                                            empty = []
                                            for x in song_list:
                                                if x[0] == activity.title:  # When we find the song in the db, update count by 1
                                                    empty.append((f'{activity.title}', f'{activity.artist}', count))
                                                else:
                                                    empty.append((x[0], x[1], x[2]))
                                            musicDB.update_one({'_id': member.id}, {'$set':{'song':empty}})
                                # If the song is not in their list, add it
                                if found == False:  
                                    print(f'New song {activity.title} for {member.name}')
                                    song = person['song']
                                    song.append((f'{activity.title}', f'{activity.artist}', 1))
                                    musicDB.update_one({'_id': member.id}, {'$set':{'name': f'{member.name}', 'song':song}})
                                
                            # Update current song dictionary
                            users[member.id] = f'{activity.title}' 

                        # If not in listnening list, add them
                        else:
                            users[member.id] = f'{activity.title}' 

@tasks.loop(hours = 1)
async def maintenance_check():
    global channel
    embed = discord.Embed(colour = discord.Colour.green())

    # Get the current date
    current_date = datetime.now()
    current_date = int(current_date.strftime("%d"))

    # Get the date of the last maintenance post
    maintenance = requests.get('https://maplestory.nexon.net/news/maintenance#news-filter').text
    soup = BeautifulSoup(maintenance, 'html.parser')
    post = soup.find('li', "news-item news-item--maintenance")
    date = (post.find('p', "timestamp")).string
    main_date = date[4:6]
    title = post.find_all('a')
    word = title[1].string.split(' ', 1)

    # Go into the maintance post page for more details
    next_page = 'https://maplestory.nexon.net'
    next_page += title[0]['href']
    detail_page = requests.get(next_page).text
    soup2 = BeautifulSoup(detail_page, 'html.parser')
    mainTimes = soup2.find('div', 'article-content')
    PDT = mainTimes.find_all('strong')

    # If current date and maintenance post date are the same and post is not marked complete
    if current_date == main_date and word[0] == 'Scheduled':
        embed.set_author(name = f'There is scheduled maintenance on {PDT[1].string}')
        await channel.send(embed = embed)
    else:
        print('No server maintenance detected')


slime.run(TOKEN)