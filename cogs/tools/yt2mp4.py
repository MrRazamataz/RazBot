# MrRazamataz's RazBot
# tools cog
import aiohttp
from discord.ext import commands


class tools(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

    @commands.hybrid_command(name="yt2mp4")
    async def yt2mp4(self, ctx: commands.Context, url: str) -> None:
        """
        Convert a YouTube video to a mp4 file.
        """
        await ctx.defer(ephemeral=True)
        msg = await ctx.send("<a:Loading:740263015483441172> Downloading that video for you...")
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.razbot.xyz/yt2mp4?link={url}") as resp:
                if resp.status == 200:
                    resp = await resp.json()
                    url = resp["url"]
                    await msg.edit(content=f"Conversion complete! Please download the file ASAP. \n{url}")
                else:
                    await msg.edit(content="Invalid URL.")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(tools(bot))
