import discord
import discord.ext.commands as commands
import os
from cogs.role_manager import RoleManager

TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot('!@!#!$!%!^!&', help_command=None, description=None)
bot.add_cog(RoleManager(bot))

@bot.event
async def on_ready():
    print("Ready!", bot.user)

bot.run(TOKEN)
