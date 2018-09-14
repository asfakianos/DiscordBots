# firstBot.py
# Alexander Sfakianos
# June 19, 2017
# https://discordapp.com/oauth2/authorize?&client_id=326423843591684108&scope=bot&permissions=0

##############################################################################
#                                   To Do:                                   #
#                                                                            #
#                            Add cool downs per user                         #
#                          Format Date/Time in getInfo                       #
#                                     8 Ball                                 #
##############################################################################

import discord
import asyncio
from discord.ext import commands
import urllib.request
import random
import time
from cricksSmokes import *

# List of commands for each mode
nList = ["c!help", "c!setServerMode [mode]", "c!getServerMode"]

realmList = ["c!help", "c!setServerMode [mode]", "c!getServerMode",
             "c!whoOnline", "c!getInfo [user]",
             "c!giveRandom [upper] [lower] [private/public]",
             "c!changeGame [game]", "c!goodMusic", "c!facts",
             "c!addToList [user]"]

csList = ["c!help", "c!setServerMode [mode]", nList[2], "c!smokes"]

giveList = ["c!help", "c!setServerMode [mode]", "c!start [keyword]", "c!end"]

# List of command descriptions
realmDesc = ["You used this to see this.", "Change the server mode (realm, csgo, giveaway, none)",
             "Gets the active server mode.",
             "Checks when the file of users were last online (Thanks tiffit for the API).",
             "Gives a brief breakdown of the given user's Realmeye (Thanks tiffit).",
             "Produces a random (private or public) number based on bounds.",
             "Changes the game that cricksBot says he is playing.",
             "Dank tunes for dank memers.",
             "Useless facts that are actually opinions",
             "Adds a user to the stalking list. Not case sensitive."
             "\n\n # Thanks tiffit - http://tiffit.net/RealmInfo/"]


csDesc = [realmDesc[0], realmDesc[1], realmDesc[2], "Various smokes for various maps."]

nDesc = [realmDesc[0], realmDesc[1], realmDesc[2]]

giveDesc = [realmDesc[0], realmDesc[1], "Starts a giveaway", "Ends a giveaway started by the user."]


# Used for c!fact
factsList = ['"Girls only buy guitars online so they don{}t feel threatened" -- Andertons music supply in the UK'.format("'"),]

# Used for c!goodMusic
links = ["https://www.youtube.com/watch?v=vTIIMJ9tUc8",
         "https://www.youtube.com/watch?v=l0gewuLwkhQ",]

whiteList = [""]

# Set the cooldown Time for the addToList (seconds)
coolTime = 300
# Used for spam prevention
cooldown = {}
# Mode for the bot. Default = realm. Look to store in a file.
mode = "none"
# For giveaways
start = [0]
original = ""
gaChannel = ""
keyword = ""
black = []
rigged = 0

client = discord.Client()

# Gets the mode of the current server
def getServerMode(message):
    # Check if the server has an intended mode
    if (message.server.id) in open('serverData.txt').read():

        # If it does, find that line
        for line in open('serverData.txt').readlines():
            words = line.split(" ")

            # If the first word of the line is the server id, get the 2nd word (mode)
            if words[0] == message.server.id:
                return words[1].strip("\n")

    # If it doesn't have a mode, return "none"
    else:
        return "none"

# Change or setup a serverMode
async def setServerMode(message):
    # Split the message to find the mode
    newMode = message.content[len("c!setServerMode"):].strip()
    if newMode == "none" or newMode == "csgo" or newMode == "realm" or newMode == "giveaway":
        # Check if the server already exists in directory
        if (message.server.id) in open('serverData.txt').read():

            # If it does, find that line
            serverData = open('serverData.txt', 'r')
            lines = serverData.readlines()
            serverData.close()

            serverData = open('serverData.txt', 'w')
            for line in lines:
                a = line.split(" ")
                if a[0] != message.server.id:
                    serverData.write(line)
                else:
                    serverData.write(a[0] + " "+ newMode + "\n")
            await client.send_message(message.channel, message.author.mention +
                            " Mode successfully set to {}".format(newMode))
            serverData.close()

        # If the server doesn't already exist.
        else:
            await client.send_message(message.channel, message.author.mention +
                                "No stored mode found. Making new entry.")
            serverData = open('serverData.txt', 'a')
            serverData.write(message.server.id + " " + newMode + "\n")
            serverData.close()


    # If the user inputs an invalid mode
    else:
        await client.send_message(message.channel, message.author.mention +
                                "That mode is not recognized. No changes made.")

# Checks if the user is "cooled off", using cool in seconds.
def isCooled(author, message, cool):
    now = int(time.time())
        # Cooled down.
    try:
        if cooldown[author.name] + cool <= int(time.time()):
            # Replace cooldown time with new time
            cooldown.update({author.name : int(time.time())})
            return True, 0
        else:
            print('{} needs to wait {} seconds'.format(author.name, cool -
                                                 (now - cooldown[author.name])))
            return False, (cool - (now - cooldown[author.name]))
    except:
        # Creates a cooldown that is 2 seconds diff. from cooldown to override
        cooldown.update({author.name:int(time.time() - (cool + 2))})

        if cooldown[author.name] + cool <= int(time.time()):
            # Replace cooldown time with new time
            cooldown.update({author.name : int(time.time())})
            return True, 0
        else:
            return False, (cool - (now - cooldown[author.name]))

# Used to get player information from Tiffit's realmeye API
def realmAPI(name):
    try:
        url = "http://tiffit.net/RealmInfo/api/user?u={}&f=".format(name)
        raw = urllib.request.urlopen(url)
        counter = 0

        for line in raw.readlines():
            counter += 1
            if counter == 12:
                seen = line.decode("utf-8")
        when = seen.split('"')
        return when[3]

    except:
        return "Doesn't have enough info to view or is a Private User."

# Checks that a string is "safe" to be Added
def isSafe(string):
    try:
        if len(string) > 19:
            return False

        for char in range(len(string)):
            condition = False

            # If character is within either range, it is set to True
            if ord(string[char]) <= 57 and ord(string[char]) >= 48:
                condition = True

            elif ord(string[char]) <= 122 and ord(string[char]) >= 97:
                condition = True

            # If neither are triggered, condition remains False
            if not condition:
                return False

        return True

    except:
        return False

# Views all of the members listed in onlineCheck.txt
def viewALL():
    allNames = [line.rstrip('\n') for line in open('onlineCheck.txt')]
    BIGSTRING = ""

    for name in allNames:
        BIGSTRING += (name + " @ " + realmAPI(name) + "\n")
    return BIGSTRING

# Brief run down of a single user.
def singleInfo(name):
    url = "http://tiffit.net/RealmInfo/api/user?u={}&f=".format(name)
    raw = urllib.request.urlopen(url)
    seen = []

    for line in raw.readlines():
        seen.append(line.decode("utf-8"))
    return (seen[1] + seen[2] + seen[7] + seen[8] + seen[10] + seen[11])

# Gets whether or not the specified user is online.
async def findAll(author, message):
    await client.send_typing(message.channel)
    await client.send_message(message.channel, message.author.mention +
                                               "```" + viewALL() + "```")

# Adds users to the list of people to stalk on Realmeye
async def addList(author, message):
    msg = message.content[len("c!addToList"):].strip()

    a, c = isCooled(author, message, coolTime)

    if (msg.lower() + "\n") in open('onlineCheck.txt').read():
        await client.send_message(message.channel, message.author.mention +
                                    " OI, THAT'S ALREADY IN.")
    elif not isSafe(msg.lower()):
        await client.send_message(message.channel, message.author.mention +
            " STOP ADDIN' USELESS STUFF.")

    elif a == True:
        addTo = open("onlineCheck.txt", 'a')
        addTo.write(msg.lower() + "\n")

        await client.send_message(message.channel, message.author.mention +
                                                   " Added {}!".format(msg))
    elif a == False:
        await client.send_message(message.channel, message.author.mention +
                                    " CHILL OUT, YOU'RE STILL COOLING DOWN " +
                                    "(**{} sec** remaining)".format(c))

# Gets full info on the specified user.
async def fullInfo(author, message):
    msg = message.content[len("c!getInfo"):].strip()
    await client.send_message(message.channel, "```" + "Listing brief desc.\n"
                                               + singleInfo(msg) + "```")

# Lists all available commands.
async def giveHelp(message, mode):
    if mode[0] == "r":
        paramList = realmList
        paramDesc = realmDesc

    if mode[0] == "c":
        paramList = csList
        paramDesc = csDesc

    if mode[0] == "n":
        paramList = nList
        paramDesc = nDesc

    if mode[0] == "g":
        paramList = giveList
        paramDesc = giveDesc

    # Gets some very cute colors
    helpStr = "```\n **Current mode is: {}\n".format(mode)

    # Adds each of the parameters to the list
    for paramNum in range(len(paramList)):
        helpStr += "[{}] {}\n".format(paramNum + 1, paramList[paramNum])
        helpStr += "\t*{}\n\n".format(paramDesc[paramNum])
    helpStr += "```"

    await client.send_message(message.channel, helpStr)

# Changes the game cricksBot is playing
async def game(author, message):
    g = message.content[len("c!changeGame"):].strip()
    await client.change_presence(game=discord.Game(name=g))
    await client.send_message(message.channel, "```" + message.author.name +
                                               " changed the game to " + g +
                                               "```")

# Produces a random string of digits in range.
async def randStr(author, message):
    given = message.content[len("c!giveRandom"):].strip()
    params = given.split(" ")

    # Catching Errors in no 3rd param.
    try:
        params[2] = params[2].lower()

    except:
        await client.send_message(message.channel,message.author.mention + "```" +
                            "You didn't specify, so we're assuming public.```")
        params.append("public")

    # Catching errors in the random function
    try:
        RAND = str(random.randrange(int(params[0]), int(params[1])))

        if params[2] == "private":
            await client.send_message(message, RAND)

        else:
            await client.send_message(message.channel, RAND)

    except:
        await client.send_message(message.channel, message.author.mention +
                                  "```Invalid keywords. Try c!help, idiot.```")

# Useless terrible meme music
async def giveMusic(message):
    randPick = random.randrange(0, len(links))
    await client.send_message(message.channel, message.author.mention + " " +
                                               links[randPick])

# Random "facts"
async def giveFacts(message):
    randPick = random.randrange(0, len(factsList))
    await client.send_message(message.channel, factsList[randPick])

# Handles smokes for cs go
async def smokePicker(message):
    await client.send_message(message.channel, "```BETA\n[1] Mirage\n\n[2] Cache\n\n" +
                              "[3] Overpass\n\n[4] Train\n\n[5] Cobblestone\n\n" +
                              "[6] Inferno\n\n[7] Nuke\n```")
    msg = await forceNumberInput(message, 7, client)

    if msg == "1":
        await mrgSmokes(message, client)
    elif msg == "2":
        await cacheSmokes(message, client)
    elif msg == "3":
        await ovpSmokes(message, client)
    elif msg == "4":
        await trnSmokes(message, client)
    elif msg == "5":
        await cbbleSmokes(message, client)
    elif msg == "6":
        await infSmokes(message, client)
    elif msg == "7":
        await client.send_message(message.channel, message.author.mention +
                                  "```lol, nuke?\nKid yourself.```" +
                                  "https://media.tenor.com/images/301150b3f84df4d6825e530ea64ce67a/tenor.gif")

async def startGive(author, message):
    item = message.content[len("c!start "):].strip()
    await client.send_message(message.channel,
                              "@everyone - {} has started a giveaway, keyword: **{}**".format(author, item))
    await client.send_message(message.channel, "Simply type (once, you idiots) to join or you will be removed.")
    return item

async def endGive(author, a, message):
    global start
    try:
        await client.send_message(message.channel, "@everyone - {} has ended the giveaway.".format(author))
        win = random.randrange(0, len(a))
        await client.send_message(message.channel, a[win].mention + ", a winner is you!")
    except:
        await client.send_message(message.channel, "Bot error. Ending giveaway.")
        start[0] = 0


# Gets the bot ready for the meme fest
@client.event
async def on_ready():
    await client.change_presence(game=discord.Game(name="Sakura Clicker 9000"))
    print("I'm ready!")

@client.event
async def on_message(message):
    author = message.author
    # Ensures that the bot doesn't respond to its own text
    if author != client.user:

        if message.content.startswith("c!help"):
            await giveHelp(message, str(getServerMode(message)))

        elif message.content.startswith("c!setServerMode"):
            await setServerMode(message)

        elif message.content.startswith("c!getServerMode"):
            await client.send_message(message.channel, author.mention +
                                                       "``` Current mode is " +
                                                       getServerMode(message) + "```")

        elif message.content.startswith("pride"):
            await client.send_message(message.channel,
                                      "https://clips.twitch.tv/IronicAffluentNikudonAsianGlow")

        if getServerMode(message) == "realm":
            if message.content.startswith("c!whoOnline"):
                await findAll(author, message)

            elif message.content.startswith("c!getInfo"):
                await fullInfo(author, message)

            elif message.content.startswith("c!giveRandom"):
                await randStr(author, message)

            elif message.content.startswith("c!changeGame"):
                await game(author, message)

            elif message.content.startswith("c!goodMusic"):
                await giveMusic(message)

            elif message.content.startswith("c!facts"):
                await giveFacts(message)

            elif message.content.startswith("c!addToList"):
                await addList(author, message)

        elif getServerMode(message) == "csgo":
            if message.content.startswith("c!smokes"):
                await smokePicker(message)

        elif getServerMode(message) == "giveaway":
            global ps
            global original
            global gaChannel
            global keyword
            global rigged
            if message.content.startswith("c!start") and start[0] == 0:
                start[0] = 1
                gaChannel = message.channel
                original = author
                ps, original = [], author
                keyword = await startGive(author, message)

            elif message.content.startswith("c!start") and start[0] == 1:
                rigged = 0
                await client.send_message(message.channel, author.mention + " There is already a giveaway going on.")

            elif message.content.startswith("c!end") and start[0] == 1 and author == original:
                if rigged == 0:
                    ps = await endGive(author, ps, message)
                    start[0] = 0

            elif message.content.startswith("c!rig") and start[0] == 1:
                await client.send_message(message.channel, "The giveaway has been rigged for " + author.mention)

            elif start[0] == 1 and message.channel == gaChannel and message.content.startswith(keyword):
                if author not in ps:
                    ps.append(author)
                elif author in ps:
                    await client.send_message(message.channel, author.mention + " You have been removed from this giveaway.")
                    ps.remove(author)
                print(ps)

client.run("MzI2NDIzODQzNTkxNjg0MTA4.DCmmHg.7notmQ370ivNzncWJfAW1MvuH9k")
