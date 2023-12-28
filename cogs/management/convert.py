# MrRazamataz's RazBot
# converter cog
import datetime
import discord
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice
from typing import Optional, Union
from datetime import timedelta
import aiofiles
import os
from cogs.management.database import add_warn, add_reaction_role


class convert(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    @commands.hybrid_group(name="convert")
    async def convert(self, ctx: commands.Context) -> None:
        """
        Aid you in transitioning from bots to RazBot.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send(f"{ctx.prefix}help recommend")

    @convert.command(name="warnings")
    @commands.has_permissions(administrator=True)
    async def convert_warnings(self, ctx: commands.Context) -> None:
        """
        Convert warnings from old RazBot to new.
        """
        await ctx.defer()
        server = ctx.guild.id
        if os.path.exists(f"old-warnings/{server}.txt"):
            async with aiofiles.open(f"old-warnings/{server}.txt", mode="r") as file:
                lines = await file.readlines()
                count = len(lines)
                message = await ctx.send(f"<a:Loading:740263015483441172> Converting **{count}** warnings...")
                for line in lines:
                    data = line.split(" ")
                    member_id = int(data[0])
                    admin_id = int(data[1])
                    reason = " ".join(data[2:]).strip("\n")
                    await add_warn(member_id, server, admin_id, reason)
                await message.edit(content=f"✅ Converted **{count}** warnings.")
            os.remove(f"old-warnings/{server}.txt")
        else:
            await ctx.send("No old warnings found for this server.")

    @convert.command(name="reactionroles")
    @commands.has_permissions(administrator=True)
    async def convert_reactionroles(self, ctx: commands.Context) -> None:
        """
        Convert reaction roles from old RazBot to new.
        """
        await ctx.defer()
        if os.path.exists(f"old-reactionroles.txt"):
            #reaction_roles = []
            async with aiofiles.open("old-reactionroles.txt", mode="r") as file:
                lines = await file.readlines()
                print(lines)
                await ctx.send(f"Converting **{len(lines)}** reaction roles...")
                for line in lines:
                    data = line.split(" ")
                    #reaction_roles.append((int(data[0]), int(data[1]), data[2].strip("\n")))
                    message_id = data[1]
                    role_id = data[0]
                    emoji = data[2].strip("\n")
                    print(emoji)
                    emoji = bytes.decode(emoji[2:-1])
                    print(emoji)
                    #await add_reaction_role(message_id, role_id, emoji.decode("utf-8"))


        else:
            await ctx.send("No old reaction roles found.")



'''
    @convert_warnings.error()
    async def convert_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You do not have the required permissions to use this command.")
        else:
            await ctx.send("An error occurred while running this command. Please try again later.")
            print(error)
            traceback.print_exc()
'''


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(convert(bot))
