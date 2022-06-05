# MrRazamataz's RazBot
# mod cog
import yaml
import discord
from discord import app_commands
from discord.ext import commands


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


async def setup(bot: commands.Bot) -> None:
  await bot.add_cog(mod(bot))