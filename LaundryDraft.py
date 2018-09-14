# LaundryDraft.py
# Alexander Sfakianos
# September 19
# Attempt to see if solely discord notifs would work when integrated
# permanently into discord.

# Permissions link:https://discordapp.com/oauth2/authorize?&client_id=359362881529315329&scope=bot&permissions=0
#

import discord
from discord.ext import commands
import asyncio
import urllib.request
import time
import threading


# Defining globals that help @ startup
washNum, dryNum = 3, 3

client = discord.Client()

# Actual execution of getting necc. data from LaundryView.
@asyncio.coroutine
def parseLaundryView(raw):
    LView = []
    # Parsing using urllib to request html from laundryView.
    i = 0
    for line in raw.readlines():
        if "of 3 available" in line.decode("utf-8"):
            nL = line.decode("utf-8")
            nL = nL[32:-12]
            info = nL.split("</span> ")
            # Appends the x of 3 available text as an int.
            LView.append(int(info[1][0]))
            i += 1
        if i >= 2:
            break

    # LView is a list with index 0 = washers, 1 = dryers
    return LView


# Handles the refresh of data from LaundryView.
@asyncio.coroutine
def refresh(washers, dryers):
    # LaundryView Site
    url = "http://classic.laundryview.com/laundry_room.php?lr=70080783"
    # Get the raw text from the site
    raw = urllib.request.urlopen(url)
    # Send raw data to parse function to get the number of each available.
    data = parseLaundryView(raw)


# Main loop, calls all other functions necc. for checking statuses, etc. + Notifications
@asyncio.coroutine
def LaundryLoop(author, message):
    try:
        global washNum, dryNum
        # Run setup, get lights

        # Provides an alternate method for quitting.
        while washNum != -1 and dryNum != -1:

            # Get the statuses of the laundry machines
            status = refresh()

            # Applying notifications to the washer/dryer change in numbers.
            if washers > washNum:
                yield from client.send_message(channel, author.mention + "Washer(s) have opened up.")
            if dryers > dryNum:
                yield from client.send_message(channel, author.mention + "Dryer(s) have opened up.")

            # Delay to prevent insane iteration amounts
            time.sleep(45)

        yield from client.send_message(channel, author.mention + "Loop has ended.")

    # Just so that it doesn't flood pi with error messages.
    except:
        yield from client.send_message(channel, author.mention + "Loop has ended due to an error.")

@asyncio.coroutine
def setup_1(message):
    # Define author, channel based on the message passed through given
    author = message.author
    channel = message.channel

    # Begin LaundryLoop threading, pass message data
    LThread = threading.Thread(target="LaundryLoop", args=(author, channel))
    yield from LThread.start()
    print('Started loop.')

@client.event
@asyncio.coroutine
def on_ready():
    yield from client.change_presence(game=discord.Game(name="LaundryView!"))
    print("I'm Ready!")

@client.event
@asyncio.coroutine
def on_message(message):
    if message.content.startswith("&start"):
        yield from setup_1(message)

    elif message.content.startswith("&end"):
        global washNum, dryNum
        washNum, dryNum = -1, -1


client.run("MzU5MzYyODgxNTI5MzE1MzI5.DKGIBw.KMXO_fzME3abaKBnqJUcJBNgoDU")
