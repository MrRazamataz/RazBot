# MrRazamataz's RazBot
# mod cog
import datetime
import time

import yaml
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
from cogs.management.database import add_ban, add_unban, revoke_ban, add_kick, add_warn, get_user_guild_warncount, \
    get_all_warnings_user_guild, delete_warning


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

    @commands.hybrid_command(name="warn")
    async def warn_command(self, ctx: commands.Context, member: discord.Member, *, reason: str):
        """
        Warn a user in the guild. A reason is required.
        """
        if not reason:  # for message commands
            return await ctx.send("A reason is required.")
        await ctx.defer()
        await add_warn(member.id, ctx.guild.id, ctx.author.id, reason)
        count = await get_user_guild_warncount(member.id, ctx.guild.id)
        embed = discord.Embed(title=f"You have been warned in `{member.guild.name}`", description="",
                              colour=discord.Colour.red())
        embed.description += f"You currently have **{count}** warnings in `{member.guild.name}`.\n Your latest warning had the reason: `{reason}`.\n Please make sure to follow the rules, otherwise you may risk further punishment!"
        await member.send(embed=embed)
        await ctx.send(
            f"`{member.name}` (ID: `{member.id}`) has been warned by `{ctx.author.name}`, with the reason `{reason}`. They have **{count}** warnings in `{member.guild.name}`.")

    @commands.hybrid_command(name="warnings", aliases=["viewwarns, viewwarnings"])
    async def warnings_command(self, ctx: commands.Context, member: discord.Member) -> None:
        """
        View a user's warnings in the guild.
        """
        await ctx.defer()
        warns = await get_all_warnings_user_guild(member.id, ctx.guild.id)
        embed = discord.Embed(title=f"{member.name}'s warnings in `{ctx.guild.name}`:", description="",
                              colour=discord.Colour.orange())
        for row in warns:
            moderator = await self.bot.fetch_user(row[2])
            embed.add_field(name=f"Reason: \n`{row[4]}`",
                            value=f"At: <t:{round(time.mktime(row[3].timetuple()))}:R> \nBy: {moderator.mention} \n**ID: {row[5]}**",
                            inline=True)
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="deletewarn", aliases=["deletewarnings", "unwarn"])
    async def delete_warn_command(self, ctx: commands.Context, warn_id: int) -> None:
        """
        Delete a user's warning in the guild.
        """
        if not warn_id:
            await ctx.send("Please provide an ID. You can grab it from `!warnings <user>`.")
            return
        await ctx.defer()
        if await delete_warning(warn_id, ctx.guild.id):
            await ctx.send(f"Warning with ID `{id}` has been deleted.")
        else:
            await ctx.send(f"Warning with ID `{id}` does not exist in this guild.")

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(mod(bot))
