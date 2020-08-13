import discord
from discord.ext import commands, tasks
import pymongo
from pymongo import MongoClient
from datetime import datetime, time
import asyncio
import requests

with open('slime_token.txt', 'r') as f:
    TOKEN = f.readline()

with open('mongo_url.txt', 'r') as f:
    MONGO = f.readline()

cluster = MongoClient(MONGO)
db = cluster['Discord']
collection = db['Spotify']

slime = commands.Bot(command_prefix = '-')
slime.remove_command('help')

channel = None
snitchMode = False
daily = False
weekly = False
track = False
guild = None
users = {}

#---- EVENTS ----#
@slime.event
async def on_ready():
    await slime.change_presence(activity = discord.Game('Grinding Mesos'))
    embed = discord.Embed(colour = discord.Colour.green())
    embed.set_author(name = 'Hello, I am SlimeTime! Type -help for a list of commands!')

    guilds = slime.guilds
    for guild in guilds:
        channel = guild.text_channels[0]
        await channel.send(embed = embed)

    await slime.change_presence(activity = discord.Game('Grinding Mesos'))
    print('Bot is online!')

@slime.event
async def on_message(message):
    guild = message.guild
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
        if(snitchMode == True):
            await message.channel.send(f'{message.author} said: {message.content}')

#---- COMMANDS ----#

# MAPLESTORY COMMANDS
@slime.command()
async def daily(ctx):
    global channel
    global daily 
    daily = True
    channel = ctx.message.channel
    embed = discord.Embed(colour = discord.Colour.green())
    embed.set_author(name = 'Notifications for dailies turned on!', icon_url = 'https://www.freeiconspng.com/thumbs/checkmark-png/checkmark-png-5.png')
    await ctx.send(embed = embed)
    waitTime = startCount()
    await waitForHour(waitTime)
    daily_reset_message.start()

@slime.command()
async def weekly(ctx):
    global weekly
    weekly = True
    embed = discord.Embed(colour = discord.Colour.green())
    currentDate = datetime.now()
    displayDay = 2 - int(currentDate.strftime("%w"))
    if displayDay < 0:  # Calulate days until next wednesday
        displayDay += 6

    currentTime = datetime.now().time()
    displayHour = 16 - int(currentTime.strftime("%H"))
    displayMin = 60 - int(currentTime.strftime("%M"))
    currentSeconds = currentTime.strftime("%S")
    displaySec = 59 - int(currentSeconds)

    if(displayHour < 0):
        displayHour += 24
    if(displayMin == 60):
        displayMin = 0
        displayHour += 1
    
    waitTime = (displayDay * 86400) + (displayHour * 3600) + (displayMin * 60) + displaySec
    embed.set_author(name = 'Notifications for weeklys turned on!', icon_url = 'https://www.freeiconspng.com/thumbs/checkmark-png/checkmark-png-5.png')
    await ctx.send(embed = embed)
    await waitForHour(waitTime)
    weekly_reset_message.start()

async def waitForHour(secondsTilHour):
    print('Waiting for ' + str(secondsTilHour) + ' seconds.')
    await asyncio.sleep(secondsTilHour)

def startCount():
    currentTime = datetime.now()
    currentTime = currentTime.time()

    currentMinute = currentTime.strftime("%M")
    remainingMinutes = 60 - int(currentMinute)
    currentSeconds = currentTime.strftime("%S")
    remainingSeconds = 59 - int(currentSeconds)
    print(remainingMinutes, remainingSeconds)
    remainingSeconds = (int(remainingMinutes) * 60) + int(currentSeconds)
    return remainingSeconds

@slime.command()
async def stop(ctx, choice = 'None'):
    if choice == 'daily':
        global daily 
        daily = False
        embed = discord.Embed(colour = discord.Colour.green())
        embed.set_author(name = 'Dailies notifcations stopped.', icon_url = 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Dark_Red_x.svg/600px-Dark_Red_x.svg.png')
        await ctx.send(embed = embed)
        daily_reset_message.stop()
    elif choice == 'weekly':
        global weekly 
        weekly = False
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
    currentDate = datetime.now()
    currentTime = datetime.now().time()
    displayDay = 3 - int(currentDate.strftime("%w"))
    if displayDay <= 0:  # Calulate days until next wednesday
        displayDay += 6
    displayHour = 16 - int(currentTime.strftime("%H"))
    displayMin = 60 - int(currentTime.strftime("%M"))

    if(displayHour < 0):
        displayHour += 24
    if(displayMin == 60):
        displayMin = 0
        displayHour += 1

    if(displayHour == 0):
        displayTime = f'Reset is in {displayMin} minutes.\n'
    else:
        displayTime = f'Reset is in {displayHour} hours and {displayMin} minutes.\n'
    
    if displayDay != 0:
        displayTime += f'Weeklys reset in {displayDay} days and {displayHour} hours.'
    else:
        displayTime += f'Weeklys reset in {displayHour} hours and {displayMin} minutes.'

    embed.set_author(name = displayTime)
    await ctx.send(embed = embed)

@slime.command()
async def links(ctx):
    embed = discord.Embed(colour = discord.Colour.green())
    embed.set_author(name = 'Helpful Links', icon_url = 'https://www.freeiconspng.com/thumbs/checkmark-png/checkmark-png-5.png')
    embed.add_field(name = 'Familiars', value = 'https://docs.google.com/spreadsheets/d/1HShIqsK0zghH6BnrFgJJnrxOXcauHbGpgX8gL310NNQ/edit#gid=0', inline = False)
    await ctx.send(embed = embed)

# CHAT COMMANDS
@slime.command()
async def snitch(ctx):
    global snitchMode
    embed = discord.Embed(colour = discord.Colour.green())
    if(snitchMode == False):
        snitchMode = True
        embed.set_author(name = 'Snitch Mode On', icon_url = 'https://www.freeiconspng.com/thumbs/checkmark-png/checkmark-png-5.png')
    elif(snitchMode == True):
        snitchMode = False
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
        embed.set_footer(text = 'Page 4/5')
    elif choice == 'general':
        embed.set_author(name = 'General Commands', icon_url = 'https://icons.iconarchive.com/icons/paomedia/small-n-flat/1024/cog-icon.png')
        embed.add_field(name = '-state', value = 'Check the state of toggles', inline = False)
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

@slime.command()
async def track(ctx):
    global track
    track = True
    global guild
    guild = ctx.guild
    embed = discord.Embed(colour = discord.Colour.green())
    embed.set_author(name = 'Spotify tracker is now on.')
    await ctx.send(embed = embed)
    initSongs()
    spotify_tracker.start()

def initSongs():
    # Initialize current songs list
    for member in guild.members:
            if member.activities:
                for activity in member.activities:
                    if activity.name == 'Spotify':  #Find someone listening to music
                        # Update current song dictionary
                        currentSong = users.get(member.name, 0)
                        if currentSong == 0:    # User not in currently listening dictionary yet
                            users[f'{member.name}'] = f'{activity.title}'
                        elif currentSong != activity.title:     # User is listening to a new song
                            users[f'{member.name}'] = f'{activity.title}' 

@slime.command()
async def top(ctx, choice = 'None'):
    first = True
    person = collection.find_one({'_id':f'{ctx.author.name}'})
    songList = person['song']
    songList.sort(key = lambda x: x[2], reverse = True)
    embed = discord.Embed(colour = discord.Colour.green())
    length = len(songList)
    if length < 6 and choice != 'None':     # Only show first page
        choice = 'None'
    
    if choice == 'None':
        if length > 5:
            length = 5
            embed.set_footer(text = 'Page 1/2: Type -top 2 to see page 2')
        topFiveSongs = songList[0:length]
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
        topTenSongs = songList[5:length]
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

# GENERAL COMMANDS
@slime.command()
async def state(ctx):
    global snitchMode
    global daily
    global weekly
    embed = discord.Embed(colour = discord.Colour.green())
    embed.set_author(name = 'Current Toggle States')

    if daily == True:
        embed.add_field(name = 'Daily', value = 'On', inline = False)
    else:
        embed.add_field(name = 'Daily', value = 'Off', inline = False)
    if weekly == True:
        embed.add_field(name = 'Weekly', value = 'On', inline = False)
    else:
        embed.add_field(name = 'Weekly', value = 'Off', inline = False)
    if track == True:
        embed.add_field(name = 'Track', value = 'On', inline = False)
    else:
        embed.add_field(name = 'Track', value = 'Off', inline = False)
    if snitchMode == True:
        embed.add_field(name = 'Snitch Mode', value = 'On', inline = False)
    else:
        embed.add_field(name = 'Snitch Mode', value = 'Off', inline = False)
    await ctx.send(embed = embed)



#---- TASKS ----#
@tasks.loop(hours = 1)
async def daily_reset_message():
    # Use this to put daily reset notifcation in first channel messaged in
    embed = discord.Embed(colour = discord.Colour.green())
    global channel

    currentDateTime = datetime.now()
    currentTime = currentDateTime.time()
    currentHour = currentTime.strftime("%H")
    resetHour = 17 - int(currentHour)   #5PM
    if resetHour == 0:
        embed.set_author(name = 'Dailies Reset!')
        await channel.send(embed = embed)
    elif resetHour > 0 and resetHour < 5:
        embed.set_author(name = f'Reset is in {resetHour} hours')
        await channel.send(embed = embed)

@tasks.loop(hours = 168)
async def weekly_reset_message():
    # Use this to put daily reset notifcation in first channel messaged in
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
                        if member.name in users:    # If listener is in currently listening list                         
                            found = False
                            # Database changes
                            if collection.find_one({'_id':f'{member.name}'}) == None:   # If its a new person
                                print(f"New Member - {member.name}")
                                collection.insert_one({'_id': f'{member.name}', 'song': [ (f'{activity.title}', f'{activity.artist}', 1) ]})      # List of tuples with song name and play count
                            else:
                                # Check their list of songs
                                person = collection.find_one({'_id':f'{member.name}'})
                                songList = person['song']
                                for songs in songList:
                                    if songs[0] == activity.title:   # Found song in users list
                                        found = True
                                        count = songs[2] + 1
                                        if activity.title != users[member.name]:    # If the song was not their previous current song
                                            empty = []
                                            for x in songList:
                                                if x[0] == activity.title:  # When we find the song in the db, update count by 1
                                                    empty.append((f'{activity.title}', f'{activity.artist}', count))
                                                else:
                                                    empty.append((x[0], x[1], x[2]))
                                            collection.update_one({'_id': f'{member.name}'}, {'$set':{'song':empty}})
                                if found == False:  # If the song is not in their list, add it
                                    print(f'New song for {member.name}')
                                    song = person['song']
                                    song.append((f'{activity.title}', f'{activity.artist}', 1))
                                    collection.update_one({'_id': f'{member.name}'}, {'$set':{'song':song}})
                                # Check dictionary for current song
                                
                            # Update current song dictionary
                            users[f'{member.name}'] = f'{activity.title}' 

                        else:   # If not in listnening list, add them
                            users[f'{member.name}'] = f'{activity.title}' 

                       
slime.run(TOKEN)