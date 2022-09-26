# MrRazamataz's RazBot
# music cog
import aiohttp
import discord
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
import datetime
import wavelink


class music(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(music(bot))
