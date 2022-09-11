# MrRazamataz's RazBot
# fun cog
import aiohttp, aiofiles
import yaml
import discord
from discord import app_commands
from discord.ext import commands
from cogs.management.database import apod_on, apod_off, apod_run
from datetime import date
from cogs.management.database import check_role_permission
import aiocron
import os


class fun(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

        # apod cron job
        @aiocron.crontab('0 8 * * *')
        async def apod_task():
            print("[APOD] Running task...")
            for attempt in range(5):
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                                f"https://api.nasa.gov/planetary/apod?api_key={tokens['api_keys']['nasa']}") as resp:
                            resp = await resp.json()
                            await session.close()

                except:
                    print("[APOD] Retrying apod...")
                else:
                    success = True
                    break
            else:
                success = False

            output = await apod_run()
            output = list(output)
            for i in output:
                i = str(i)
                i = i.strip("(,)")
                if "None" not in i:
                    channel = self.bot.get_channel(int(i))
                    if success is True:
                        embed = discord.Embed(title=f"<:nasa:935260377871159296> APOD `{date.today()}`",
                                              description=resp["explanation"],
                                              color=0xfffa86)
                        embed.set_image(url=resp["hdurl"])
                        embed.set_author(name="RazBot", url="https://razbot.xyz",
                                         icon_url="https://mrrazamataz.ga/archive/RazBot.png")
                        await channel.send(embed=embed)
                    else:
                        await channel.send(
                            "The automated apod failed, we think it was an API error (NASA's API must run in space, because its slow to connect).")
            print("[APOD] Task ran.")

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
        if await check_role_permission(ctx.author, "manage_server"):
            await apod_on(ctx.guild.id, ctx.channel.id)
            await ctx.send(f"Daily APOD will send to {ctx.channel.mention}.")
        else:
            await ctx.send(
                f"Sorry, {ctx.author.name}, you don't have permission for that. Required permission: `manage server settings`.")

    @apod.command(name="off")
    async def apod_off(self, ctx: commands.Context) -> None:
        """
        Turn off APOD for a channel
        """
        if await check_role_permission(ctx.author, "manage_server"):
            await apod_off(ctx.guild.id)
            await ctx.send(f"Daily APOD will no longer send in {ctx.guild.name}")
        else:
            await ctx.send(
                f"Sorry, {ctx.author.name}, you don't have permission for that. Required permission: `manage server settings`.")

    @apod.command(name="run")
    async def apod_run(self, ctx: commands.Context) -> None:
        """
        Run APOD
        """
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

    @commands.hybrid_group(name="memegen")
    async def memegen(self, ctx: commands.Context) -> None:
        """
        Generate funny haha memes with your images and witty humour.
        """
        if ctx.invoked_subcommand is None:
            await ctx.send(f"{ctx.prefix}help memegen")

    @memegen.command(name="impact")
    async def memegen_impact(self, ctx: commands.Context, image: discord.Attachment, top_text: str,
                             bottom_text: str) -> None:
        """
        Add top and bottom text to an image.
        """
        await ctx.defer()
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    f"https://api.razbot.xyz/memegen/impact?top_text={top_text}&bottom_text={bottom_text}&image_url={image.url}") as resp:
                resp = await resp.json()

            async with session.get(resp['url']) as resp:
                if resp.status == 200:
                    f = await aiofiles.open("IMPACT-image.jpg", mode='wb')
                    await f.write(await resp.read())
                    await f.close()
                    await ctx.send(file=discord.File('IMPACT-image.jpg'))
                    os.remove('IMPACT-image.jpg')
                    await session.close()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(fun(bot))
