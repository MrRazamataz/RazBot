# MrRazamataz's RazBot
# permissions cog
import datetime
import time

import yaml
import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from cogs.management.database import mod_log, set_role_permission, set_panel_user


class PermissionHandler(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    @commands.hybrid_group(name="permission", aliases=["perms"])
    async def permission_group(self, ctx: commands.Context) -> None:
        """
        This is the permission group for managing the bot's permission settings for roles and users.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send(f"{ctx.prefix}help permission")

    @permission_group.command(name="grantrole")
    @app_commands.choices(
        permission=[
            Choice(name="give warn", value="warn"),
            Choice(name="view user warnings", value="warnings"),
            Choice(name="manage warnings", value="manage_warnings"),
            Choice(name="manage server settings", value="manage_server")
        ],
        state=[
            Choice(name="true", value="true"),
            Choice(name="false", value="false")
        ]
    )
    async def grantrole_command(self, ctx: commands.Context, role: discord.Role, permission: Choice[str],
                                state: Choice[str]) -> None:
        """
        Grant a role a certain permission.
        """
        if ctx.author.guild_permissions.administrator:
            await ctx.send(f"Role `{role.name}` (ID: `{role.id}`) has had `{permission.name}` set to `{state.value}`.")
            await set_role_permission(role.id, permission.value, state.value)
            await mod_log(ctx.author.id, ctx.guild.id,
                          f"Updated {role.name} (ID: {role.id}) permission `{permission.name}` to `{state.value}`")
        else:
            await ctx.send(
                f"Sorry, `{ctx.author.name}`, but you do not have permission to use this command, this needs the discord administrator permission!")

    @permission_group.command(name="panelaccess")
    @app_commands.choices(
        state=[
            Choice(name="true", value="true"),
            Choice(name="false", value="false")
        ]
    )
    async def panelaccess_command(self, ctx: commands.Context, user: discord.Member, state: Choice[str]) -> None:
        """
        Grant or revoke the ability to use the RazBot webpanel for this guild.
        """
        if ctx.author.guild_permissions.administrator:
            await ctx.send(f"Member `{user.name}` (ID: `{user.id}`) has had panel access set to `{state.value}`.")
            await set_panel_user(user.id, ctx.guild.id, state.value)
            await mod_log(ctx.author.id, ctx.guild.id,
                          f"Member `{user.name}` (ID: `{user.id}`) has had panel access set to `{state.value}`.")
        else:
            await ctx.send(
                f"Sorry, `{ctx.author.name}`, but you do not have permission to use this command, this needs the discord administrator permission!")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PermissionHandler(bot))
