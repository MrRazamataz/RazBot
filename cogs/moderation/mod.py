# MrRazamataz's RazBot
# mod cog
import yaml
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional
from cogs.management.database import add_ban, add_unban, revoke_ban, add_kick


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


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(mod(bot))
