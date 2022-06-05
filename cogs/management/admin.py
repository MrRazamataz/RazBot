# MrRazamataz's RazBot
# mod cog
import yaml
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, Literal
from discord.ext.commands import Greedy

class sync(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx: commands.Context, guilds: Greedy[discord.Object], spec: Optional[Literal["~", "*"]] = None) -> None:
        """
        Admin command to sync all the discord interactions
        """
        if not guilds:
            if spec == "~":
                fmt = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                fmt = await ctx.bot.tree.sync(guild=ctx.guild)
            else:
                fmt = await ctx.bot.tree.sync()

            await ctx.send(
                f"Synced {len(fmt)} commands {'globally' if spec is None else 'to the current guild.'}"
            )
            return

        fmt = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                fmt += 1

        await ctx.send(f"Synced the tree to {fmt}/{len(guilds)} guilds.")


async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(sync(bot))