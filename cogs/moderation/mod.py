# MrRazamataz's RazBot
# mod cog
import datetime
import time
import traceback

import yaml
import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from typing import Optional, Union
from cogs.management.database import add_ban, add_unban, revoke_ban, add_kick, add_warn, get_user_guild_warncount, \
    get_all_warnings_user_guild, delete_warning, mod_log, clear_all_users_warnings, clear_all_guild_warnings, \
    check_role_permission
from datetime import timedelta


class mod(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    @commands.hybrid_command(name="ping")
    async def ping_command(self, ctx: commands.Context) -> None:
        """
        This command is actually used as an app command AND a message command.
        This means it is invoked with `raz!ping` and `/ping` (once synced, of course).
        """

        await ctx.send("Hello!")

    @commands.hybrid_command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban_command(self, ctx: commands.Context, member: discord.Member, *,
                          reason: str = "No reason set") -> None:
        """
        Ban a user from the guild.
        """
        if member.top_role >= ctx.author.top_role:
            await ctx.send(
                "This command failed due to role hierarchy! You are below or equal to the target user in this ~~pyramid scheme~~ discord server.")
            return
        else:
            try:
                await member.send(f"You have been banned from `{member.guild.name}`. \nBan reason: `{reason}`")
            except:
                pass
            try:
                await member.ban(reason=reason)
            except Exception as e:
                await ctx.send(f"Error whilst banning, do I have permission? \n`{e}`")
                return
            await ctx.send(
                f"`{member.name}` (ID: `{member.id}`) has been banned by `{ctx.author.name}`, with the reason `{reason}`.")
            await add_ban(member.id, member.guild.id, ctx.author.id, reason)
            await mod_log(ctx.author.id, ctx.guild.id, f"Banned {member.name} (ID: {member.id})")

    @commands.hybrid_command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban_command(self, ctx, user: discord.User, *, reason: str = "No reason set") -> None:
        """
        Unban a user from the guild.
        """
        guild = ctx.guild
        try:
            await guild.unban(user, reason=reason)
        except Exception as e:
            await ctx.send(f"Error whilst unbanning, do I have permission? \n`{e}`")
            return
        await ctx.send(
            f"`{user.name}` (ID: `{user.id}`) has been unbanned by `{ctx.author.name}`, with the reason `{reason}`.")
        await add_unban(user.id, guild.id, ctx.author.id, reason)
        await revoke_ban(user.id, guild.id)
        await mod_log(ctx.author.id, ctx.guild.id, f"Unbanned {user.name} (ID: {user.id})")

    @commands.hybrid_command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick_command(self, ctx: commands.Context, member: discord.Member, *,
                           reason: str = "No reason set") -> None:
        """
        Kick a member from the guild
        """
        if member.top_role >= ctx.author.top_role:
            await ctx.send(
                "This command failed due to role hierarchy! You are below or equal to the target user in this ~~pyramid scheme~~ discord server.")
            return
        else:
            try:
                await member.send(f"You have been kicked from `{ctx.guild.name}`. \bKick reason: `{reason}`")
            except Exception as e:
                pass
            await member.kick(reason=reason)
            await ctx.send(
                f"`{member.name}` (ID: `{member.id}`) has been kicked by `{ctx.author.name}`, with the reason `{reason}`.")
            await add_kick(member.id, ctx.guild.id, ctx.author.id, reason)
            await mod_log(ctx.author.id, ctx.guild.id, f"Kicked {member.name} (ID: {member.id})")

    @commands.hybrid_command(name="warn")
    async def warn_command(self, ctx: commands.Context, member: discord.Member, *, reason: str) -> None:
        """
        Warn a user in the guild. A reason is required.
        """
        if not reason:  # for message commands
            await ctx.send("A reason is required.")
            return
        await ctx.defer()
        if await check_role_permission(ctx.author, "warn"):
            await add_warn(member.id, ctx.guild.id, ctx.author.id, reason)
            count = await get_user_guild_warncount(member.id, ctx.guild.id)
            embed = discord.Embed(title=f"You have been warned in `{member.guild.name}`", description="",
                                  colour=discord.Colour.red())
            embed.description += f"You currently have **{count}** warnings in `{member.guild.name}`.\n Your latest warning had the reason: `{reason}`.\n Please make sure to follow the rules, otherwise you may risk further punishment!"
            try:
                await member.send(embed=embed)
            except:
                pass
            await ctx.send(
                f"`{member.name}` (ID: `{member.id}`) has been warned by `{ctx.author.name}`, with the reason `{reason}`. They have **{count}** warnings in `{member.guild.name}`.")
            await mod_log(ctx.author.id, ctx.guild.id, f"Warned {member.name} (ID: {member.id}). Reason: {reason}")
        else:
            await ctx.send(
                f"Sorry, {ctx.author.name}, you don't have permission for that. Required permission: `give warn`.")

    @commands.hybrid_command(name="warnings", aliases=["viewwarns, viewwarnings", "warns"])
    async def warnings_command(self, ctx: commands.Context, member: discord.Member) -> None:
        """
        View a user's warnings in the guild.
        """
        await ctx.defer()
        if await check_role_permission(ctx.author, "warnings"):
            warns = await get_all_warnings_user_guild(member.id, ctx.guild.id)
            embed = discord.Embed(title=f"{member.name}'s warnings in `{ctx.guild.name}`:", description="",
                                  colour=discord.Colour.orange())
            for row in warns:
                moderator = await self.bot.fetch_user(row[2])
                embed.add_field(name=f"Reason: \n`{row[4]}`",
                                value=f"At: <t:{round(time.mktime(row[3].timetuple()))}:R> \nBy: {moderator.mention} \n**ID: {row[5]}**",
                                inline=True)
            await ctx.send(embed=embed)
            await mod_log(ctx.author.id, ctx.guild.id, f"Viewed {member.name}'s warnings in {ctx.guild.name}")
        else:
            await ctx.send(
                f"Sorry, {ctx.author.name}, you don't have permission for that. Required permission: `view user warnings`.")

    @commands.hybrid_command(name="deletewarn", aliases=["deletewarnings", "unwarn"])
    async def delete_warn_command(self, ctx: commands.Context, warn_id: int) -> None:
        """
        Delete a user's warning in the guild.
        """
        if await check_role_permission(ctx.author, "manage_warnings"):
            if not warn_id:
                await ctx.send("Please provide an ID. You can grab it from `!warnings <user>`.")
                return
            await ctx.defer()
            if await delete_warning(warn_id, ctx.guild.id):
                await ctx.send(f"Warning with ID `{warn_id}` has been deleted.")
                await mod_log(ctx.author.id, ctx.guild.id, f"Deleted warning with ID `{warn_id}`")
            else:
                await ctx.send(f"Warning with ID `{warn_id}` does not exist in this guild.")
        else:
            await ctx.send(
                f"Sorry, {ctx.author.name}, you don't have permission for that. Required permission: `manage warnings`.")

    @commands.hybrid_command(name="clearwarns", aliases=["clearwarn"])
    @app_commands.choices(
        mode=[
            Choice(name="from user", value="user"),
            Choice(name="from guild", value="guild")
        ]
    )
    async def clear_warns_command(self, ctx: commands.Context, mode: Choice[str],
                                  member: discord.Member = None) -> None:
        """
        Clear a user's or guild's warnings.
        """
        await ctx.defer()
        if await check_role_permission(ctx.author, "manage_warnings"):
            if mode.value == "user":
                if not member:
                    await ctx.send("Please provide a user.")
                    return
                await clear_all_users_warnings(member.id, ctx.guild.id)
                await ctx.send(
                    f"All warnings for `{member.name}` (ID: {member.id}) in {ctx.guild.name} have been cleared.")
                await mod_log(ctx.author.id, ctx.guild.id, f"Cleared all warnings for {member.name} (ID: {member.id})")
            if mode.value == "guild":
                if ctx.author.guild_permissions.administrator:
                    await clear_all_guild_warnings(ctx.guild.id)
                    await ctx.send(f"All warnings in `{ctx.guild.name}` have been cleared.")
                    await mod_log(ctx.author.id, ctx.guild.id, f"Cleared all warnings in `{ctx.guild.name}`")
                else:
                    await ctx.send(
                        f"Sorry, {ctx.author.name}, you don't have permission for that. Required permission: `administrator`.")
        else:
            await ctx.send(
                f"Sorry, {ctx.author.name}, you don't have permission for that. Required permission: `manage warnings`.")

    @commands.hybrid_command(name="mute", aliases=["tempmute"])
    @app_commands.choices(
        timecode=[
            Choice(name="60 seconds", value="60s"),
            Choice(name="5 minutes", value="5m"),
            Choice(name="10 minutes", value="10m"),
            Choice(name="1 hour", value="1h"),
            Choice(name="2 hours", value="2h"),
            Choice(name="1 day", value="1d"),
            Choice(name="2 days", value="2d"),
            Choice(name="1 week", value="1w"),
            Choice(name="4 weeks", value="4w")
        ]
    )
    async def mute_command(self, ctx: commands.Context, member: discord.Member, timecode: Choice[str], *, reason: str = "No reason set") -> None:
        """
        Timeout a user for a certain amount of time with an optional reason.
        """
        if member.top_role >= ctx.author.top_role:
            await ctx.send(
                "This command failed due to role hierarchy! You are below the target user in this ~~pyramid scheme~~ discord server.")
            return
        if ctx.author.guild_permissions.moderate_members:
            try:
                await ctx.defer()
                delta = timedelta(
                    seconds=60 if timecode.value == "60s" else 300 if timecode.value == "5m" else 600 if timecode.value == "10m" else 3600 if timecode.value == "1h" else 7200 if timecode.value == "2h" else 86400 if timecode.value == "1d" else 172800 if timecode.value == "2d" else 604800 if timecode.value == "1w" else 2419200 if timecode.value == "4w" else 0
                )
                await member.timeout(delta, reason=reason)
                await ctx.send(
                    f"`{member.name}` (ID: `{member.id}`) has been muted by `{ctx.author.name}`, with the reason `{reason}` for `{timecode.value}`.")
                await mod_log(ctx.author.id, ctx.guild.id, f"Muted {member.name} (ID: {member.id}). Reason: {reason}. Duration: {timecode.value}")
            except Exception as e:
                print(e)
                print(traceback.format_exc())


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(mod(bot))
