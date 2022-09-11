# MrRazamataz's RazBot
# settings cog

import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from cogs.management.database import mod_log, set_role_permission, check_role_permission, set_log_channel, \
    set_welcome_channel


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
        await ctx.defer()
        if await check_role_permission(ctx.author, "manage_server"):
            await ctx.send(f"Log channel set to {channel.mention}.")
            await set_log_channel(ctx.guild.id, channel.id)
        else:
            await ctx.send(
                f"Sorry, {ctx.author.name}, you don't have permission for that. Required permission: `manage server settings`.")

    @settings_group.command(name="welcomemessages")
    @app_commands.choices(
        state=[
            Choice(name="true", value="true"),
            Choice(name="false", value="false")
        ]
    )
    async def set_welcome_command(self, ctx: commands.Context, state: Choice[str], channel: discord.TextChannel):
        """
        Enable/disable the welcome message and set the channel it should send to.
        """
        await ctx.defer()
        if await check_role_permission(ctx.author, "manage_server"):
            if state.value == "true":
                await ctx.send(f"Welcome channel has been set to {channel.mention} and welcome messages enabled.")
                await set_welcome_channel(ctx.guild.id, channel.id, state.value)
            elif state.value == "false":
                await ctx.send(f"Welcome messages disabled.")
                await set_welcome_channel(ctx.guild.id, channel.id, state.value)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Settings(bot))
