import discord
import discord.ext.commands as commands
import os

TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot('!@!#!$!%!^!&', help_command=None, description=None)

@bot.event
async def on_ready():
    print("Ready!", bot.user)

bot.run(TOKEN)
