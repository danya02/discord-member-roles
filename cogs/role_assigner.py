import discord
import discord.ext.commands as commands
from .database import *
import logging

class RoleAssigner(commands.Cog):
    """ Cog responsible for monitoring reactions and assigning/de-assigning roles. """
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.bot.user.id: return  # ignore own reactions
        logging.debug(f"Received add-reaction {payload}")
        reaction_role = ReactionRole.get_or_none(message_id=payload.message_id)
        if not reaction_role:
            logging.debug(f"Reaction role for message {payload.message_id} does not exist.")
            return
        if payload.emoji.name != reaction_role.channel.vote_emoji:
            logging.debug("Wrong reaction used.")
            return
        member = payload.member
        logging.info(f"Adding role {reaction_role.role_id} to {member}")
        await member.add_roles(discord.Object(reaction_role.role_id), reason="Manual reaction roles: member reacted to corresponding message.")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        if payload.user_id == self.bot.user.id: return  # ignore own reactions
        logging.debug(f"Received remove-reaction {payload}")
        reaction_role = ReactionRole.get_or_none(message_id=payload.message_id)
        if not reaction_role:
            logging.debug(f"Reaction role for message {payload.message_id} does not exist.")
            return
        if payload.emoji.name != reaction_role.channel.vote_emoji:
            logging.debug("Wrong reaction used.")
            return
        guild = self.bot.get_guild(reaction_role.channel.guild) or await self.bot.fetch_guild(reaction_role.channel.guild)
        member = guild.get_member(payload.user_id) or await guild.fetch_member(payload.user_id)
        logging.info(f"Removing role {reaction_role.role_id} from {member}")
        await member.remove_roles(discord.Object(reaction_role.role_id), reason="Manual reaction roles: member removed reaction to corresponding message.")
