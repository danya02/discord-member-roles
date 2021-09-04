import discord
import discord.ext.commands as commands
from .database import *
import logging

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
                logging.info(f"Found role {role} that has the same name as the new role.")
                await message.channel.send(message.author.mention + " Error: the role already exists.", delete_after=10)
                await message.delete()
                return
        
        logging.info(f"Creating role {role_name} and marking it with channel emoji now.")
        role = await guild.create_role(name=role_name, color=color or chan.default_color, reason='Manual reaction roles: message sent')
        await message.add_reaction(chan.vote_emoji)
        ReactionRole.create(channel=chan, message_id=message.id, role_id=role.id)
    
    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        
        role_entry = ReactionRole.get_or_none(ReactionRole.message_id == payload.message_id)
        if not role_entry: return
        logging.info(f"Received deletion payload about reaction role message: {payload}")
        guild = self.bot.get_guild(role_entry.channel.guild) or await self.bot.fetch_guild(role_entry.channel.guild)
        if not guild:
            logging.error("Received deletion for a message that has a role entry, but we could not find the guild -- were we kicked from the guild?!")
            return
        role = guild.get_role(role_entry.role_id)
        if not role:
            logging.error("Could not find the role corresponding to the deleted reaction message. Has the role already been deleted?")
            return
        logging.info(f"Deleting role {role} because message that created it is gone.")
        await role.delete(reason="Manual reaction roles: message that created this role was deleted.")
        role_entry.delete_instance()

    async def get_channel_entry(self, message):
        if not message.guild:
            logging.debug("Received message not in guild context, ignoring.")
            return None
        try:
            return RoleChannel.select().where(RoleChannel.guild == message.guild.id).where(RoleChannel.channel == message.channel.id).get()
        except RoleChannel.DoesNotExist:
            logging.debug("Received message in channel not for reaction roles.")
            return None

    async def ensure_plain_message(self, message):
        if message.raw_channel_mentions or message.raw_role_mentions or message.raw_mentions or message.embeds or message.type != discord.MessageType.default or message.reference or not message.content:
            logging.info(f"Received message {message} that isn't a simple text message.")
            await message.channel.send(message.author.mention + " Error: message must be a plain text message.", delete_after=10)
            await message.delete()
            raise InvalidMessage
