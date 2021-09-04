import discord
import discord.ext.commands as commands
from .database import *

class InvalidMessage(Exception):
    pass

class RoleManager(commands.Cog):
    """ Cog that manages the creation and deletion of roles. """
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user: return None
        chan = await self.get_channel_entry(message)
        if not chan: return

        await self.ensure_plain_message(message)

        color = None  # TODO: set this based on the message

        guild = message.guild
        role_name = chan.role_prefix + message.content + chan.role_suffix
        for role in guild.roles:
            if role.name == role_name:
                await message.channel.send(message.author.mention + " Error: the role already exists.", delete_after=10)
                await message.delete()
                return
        
        role = await guild.create_role(name=role_name, color=color or chan.default_color, reason='Manual reaction roles: message sent')
        await message.add_reaction(chan.vote_emoji)
        ReactionRole.create(channel=chan, message_id=message.id, role_id=role.id)
    
    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        role_entry = ReactionRole.get_or_none(ReactionRole.message_id == payload.message_id)
        if role_entry:
            guild = self.bot.get_guild(role_entry.channel.guild) or await self.bot.fetch_guild(role_entry.channel.guild)
            if not guild:
                print("Received deletion for a message that has a role entry, but we could not find the guild??")
                return
            role = guild.get_role(role_entry.role_id)
            if not role: return
            await role.delete(reason="Manual reaction roles: message that created this role was deleted.")
        


    async def get_channel_entry(self, message):
        if not message.guild: return None
        try:
            return RoleChannel.select().where(RoleChannel.guild == message.guild.id).where(RoleChannel.channel == message.channel.id).get()
        except RoleChannel.DoesNotExist:
            return None

    async def ensure_plain_message(self, message):
        if message.raw_channel_mentions or message.raw_role_mentions or message.raw_mentions or message.embeds or message.type != discord.MessageType.default or message.reference or not message.content:
            await message.channel.send(message.author.mention + " Error: message must be a plain text message.", delete_after=10)
            await message.delete()
            raise InvalidMessage
