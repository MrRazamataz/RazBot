# MrRazamataz's RazBot
# fun cog
import aiohttp
import yaml
import discord
from discord import app_commands
from discord.ext import commands
from cogs.management.database import apod_on, apod_off, apod_run
from datetime import date


class fun(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        global tokens
        with open("token.yml", mode="r") as file:
            tokens = yaml.safe_load(file)

    @commands.hybrid_group(name="apod")
    async def apod(self, ctx: commands.Context) -> None:
        """
        Get the daily APOD from NASA!
        """
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(title="<:nasa:935260377871159296> APOD",
                                  description="<a:Loading:982974699183177798> Contacting...", color=0xbb00ff)
            embed.set_author(name="RazBot", url="https://razbot.xyz",
                             icon_url="https://mrrazamataz.ga/archive/RazBot.png")
            m = await ctx.send(embed=embed)
            async with ctx.channel.typing():
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                            f"https://api.nasa.gov/planetary/apod?api_key={tokens['api_keys']['nasa']}") as resp:
                        resp = await resp.json()
                        await session.close()
                        embed = discord.Embed(title=f"<:nasa:935260377871159296> APOD `{date.today()}`",
                                              description=resp["explanation"],
                                              color=0xfffa86)
                        embed.set_image(url=resp["hdurl"])
                        embed.set_author(name="RazBot", url="https://razbot.xyz",
                                         icon_url="https://mrrazamataz.ga/archive/RazBot.png")
                        await m.edit(embed=embed)

    @apod.command(name="on")
    async def apod_on(self, ctx: commands.Context) -> None:
        """
        Turn on daily APOD for a channel
        """
        await apod_on(ctx.guild.id, ctx.channel.id)
        await ctx.send(f"Daily APOD will send to {ctx.channel.mention}.")

    @apod.command(name="off")
    async def apod_off(self, ctx: commands.Context) -> None:
        """
        Turn off APOD for a channel
        """
        await apod_off(ctx.guild.id)
        await ctx.send(f"Daily APOD will no longer send in {ctx.guild.name}")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(fun(bot))
