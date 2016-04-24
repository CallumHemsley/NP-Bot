import discord
import asyncio
import sys
import re
from time import strftime

bot = discord.Client()

userdic = {}
def mod_channel():
    id = ""
    modchannel = None
    for server in bot.servers:
        for channel in server.channels:
            if str(channel.name) == "mod-log":
                print(channel.id)
                modchannel = bot.get_channel(channel.id)
                return modchannel

@bot.async_event
def on_message(message):
        
    #if (str(message.channel) != "testing-bacon-and-spam"):
        #return
        
    if str(message.channel) == "cd_newsfeed":
        if str(message.author) == "NP-Bot#2282" or str(message.author) == "obliv1on#8853":
            return
        urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.content)
        
        # checks if there is more than one url
        try: 
            if len(urls) > 1:
                yield from bot.send_message(message.author, "In **" + str(message.channel) + "** you posted two or more articles/links instead of one.")
                yield from bot.delete_message(message)
                yield from bot.send_message(mod_channel(), "In **" + str(message.channel) + "** I deleted a post for having multiple links." + "\n\nFrom: **" + str(message.author) + "**" + "\nDate: **" + strftime("%d-%m-%Y") + " at " + strftime("%H:%M") + "**" + "\n ```"+ str(message.content) + "```")
                return
            
            # checks if description is too long.
            url = urls[0]
            if url:
                description = message.content.split(" ")[1:]
                description = " ".join(description)
                
            
                if (len(description) > 50):
                    yield from bot.delete_message(message)
                    yield from bot.send_message(message.author, "In **" + str(message.channel) + "** your article description was too long.")
                    yield from bot.send_message(mod_channel(), "In **" + str(message.channel) + "** I deleted a post because it had a description longer than 50 words." + "\n\nFrom: **" + str(message.author) + "**" + "\nDate: **" + strftime("%d-%m-%Y") + " at " + strftime("%H:%M") + "**"  + "\n ```"+ str(message.content) + "```")
                    return
                
            name = message.author
    
            # checks if user has already posted in the last x amount of minutes and changes those minutes those minutes
            if name in userdic:
                minutes = convert_seconds(strftime("%Y-%m-%d %H:%M"))
                if ((minutes - userdic[name]) < 30): # AMOUNT OF MINUTES
                    yield from bot.send_message(message.author, "In **" + str(message.channel) + "** you posted two articles too quickly.")
                    yield from bot.delete_message(message)
                    yield from bot.send_message(mod_channel(), "In **" + str(message.channel) + "** I deleted a post because two or more articles were posted within a too short time span." + "\n\nFrom: **" + str(message.author) + "**" + "\nDate: **" + strftime("%d-%m-%Y") + " at " + strftime("%H:%M") + "**" + "\n ```"+ str(message.content) + "```")
                
            userdic[name] = convert_seconds(strftime("%Y-%m-%d %H:%M"))    
            
        # catch errors, so prevents the user from posting plain text.
        except Exception as e:
            print (e)
            yield from bot.delete_message(message)
            yield from bot.send_message(message.author, "In **" + str(message.channel) + "** only articles are allowed.")
            yield from bot.send_message(mod_channel(), "In **" + str(message.channel) + "** I deleted a post as the message didn't contain a link." + "\n\nFrom:** " + str(message.author) + "**\nDate:** " + strftime("%d-%m-%Y") + " at " + strftime("%H:%M") + "**\n ```"+ str(message.content) + "```")
    
    if message.content == (str(bot.user) + " exit"):
        if message.author.id != "98469757308633088" and message.author.id != "124939036325314561":
            yield from bot.send_message(message.channel, 'Exiting..')
            sys.exit()
            
    elif message.content == 'NP-info':
        yield from bot.send_message(message.author, "**Commands:** \n\n**!mention [role] [content]** - Contributors and owner only. \n \n**General bot information:** \n \n__In the channel" + "** cd_newsfeed**" + ", you can only post a link + a small description of 50 words maximum. Once u have posted an article there is a 30 minute cooldown before you can post another article.__ \n\n *Please note that this is a work in progress.* \n\n Made by penguino and Nopply.")
            
    elif message.content.startswith('!mention') or message.content.startswith("!whisper"):
        detected = False
        for role in message.author.roles:
            if str(role) != "Verified Contributors":
                continue
            else:
                detected = True
                break
        if not detected:
            yield from bot.send_message(message.channel,"You can't do that.")
            return
        mentionstring = ''
        userstring = ''
        fromuser = message.author.name
        words = split_line(message.content)
        
        language = words[1]
        content = words[2:]
        
        content = " ".join(content)
        
        for member in message.server.members:
            end = len(member.roles)
            i = 1
            while (i < end):
                role = member.roles[i]
                if (str(role) == language):
                    mentionstring +=  str(member.mention) + " "
                    userstring += str(member.id) + " "
                    break
                else:
                    i += 1
        
        if message.content.startswith('!mention'):
            
            if mentionstring == "" or content == "":
                yield from bot.send_message(message.channel,"format: !mention [role] [content]")
            else:
                yield from bot.send_message(message.channel, "**To:** " + mentionstring + "\n\n**Role: **" + language + "\n\n**Content: **" + content + "\n\n**From:** " + fromuser)
                yield from bot.delete_message(message)
            
        else:
            users = split_line(userstring)
            for username in users:
                user = message.server.get_member(username)
                yield from bot.send_message(user, "**For role: **" + language + "\n\n**Content: **" + content + "\n\n**From:** " + fromuser + "\n")
                yield from bot.delete_message(message)

@bot.async_event
def on_ready():
    yield from bot.change_status(game=discord.Game(name="type NP-info for info"), idle=False)

def split_line(string):
    return string.split(" ")
    
def convert_seconds(string):
    year = int(string.split("-")[0])
    month = int(string.split("-")[1])
    day = int(string.split("-")[2].split(" ")[0])
    hour = int(string.split(" ")[1].split(":")[0])
    minutes = int(string.split(" ")[1].split(":")[1])
    
    total = (year * 365 * 24 * 60) + (month * 30 * 24 * 60) + (day * 24 * 60) + (hour * 60) + minutes
    return total
    
    
    
bot.run('MTczMzY5Mzg3OTgwNTU0MjQy.CfzWUw.U554gZMqtCV0sXUP6VbW4hBldUI')    
