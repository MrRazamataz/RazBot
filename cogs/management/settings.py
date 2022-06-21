# MrRazamataz's RazBot
# settings cog

import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from cogs.management.database import mod_log, set_role_permission


class Settings(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    @commands.hybrid_group(name="settings")
    async def settings_group(self, ctx: commands.Context) -> None:
        """
        Manage the bot's settings.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send(f"{ctx.prefix}help settings")

    @settings_group.command(name="setlogchannel")
    async def setlogchannel_command(self, ctx: commands.Context, channel: discord.TextChannel) -> None:
        """
        Set the channel for the bot's logs.
        """


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Settings(bot))
