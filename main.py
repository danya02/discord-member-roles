import discord
import discord.ext.commands as commands
import os
from cogs.role_manager import RoleManager
from cogs.role_assigner import RoleAssigner

import logging
logging.basicConfig(level=logging.DEBUG)

TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot('!@!#!$!%!^!&', help_command=None, description=None)
bot.add_cog(RoleManager(bot))
bot.add_cog(RoleAssigner(bot))

@bot.event
async def on_ready():
    print("Ready!", bot.user)

bot.run(TOKEN)
