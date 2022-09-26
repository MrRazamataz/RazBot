# MrRazamataz's RazBot
# remindme cog
import aiohttp
import discord
import aiocron
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
from cogs.management.database import add_reminder, check_for_reminders, delete_reminder
import datetime


class remindme(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot

        @aiocron.crontab('* * * * *')
        async def check_reminders():
            reminders = await check_for_reminders("dm")
            for reminder in reminders:
                user = await self.bot.fetch_user(reminder[0])
                await user.send(f"**Reminder from {reminder[3]}:** \n`{reminder[2]}`")
                await delete_reminder(reminder[2], reminder[0], reminder[3])
            reminders = await check_for_reminders("channel")
            for reminder in reminders:
                channel = await self.bot.fetch_channel(reminder[1])
                user = await self.bot.fetch_user(reminder[0])
                await channel.send(f"**Reminder from {reminder[3]}:** by {user.mention}\n`{reminder[2]}`")
                await delete_reminder(reminder[2], reminder[0], reminder[3])

    @commands.hybrid_command(name="remindme", aliases=["remind"])
    @app_commands.choices(
        timecode=[
            Choice(name="60 seconds", value="60s"),
            Choice(name="5 minutes", value="5m"),
            Choice(name="10 minutes", value="10m"),
            Choice(name="30 minutes", value="30m"),
            Choice(name="1 hour", value="1h"),
            Choice(name="2 hours", value="2h"),
            Choice(name="1 day", value="1d"),
            Choice(name="2 days", value="2d"),
            Choice(name="1 week", value="1w"),
            Choice(name="4 weeks", value="4w"),
            Choice(name="1 month", value="1mo"),
            Choice(name="2 months", value="2mo"),
            Choice(name="3 months", value="3mo"),
            Choice(name="6 months", value="6mo"),
            Choice(name="1 year", value="1y"),
            Choice(name="2 years", value="2y"),
            Choice(name="3 years", value="3y"),
            Choice(name="4 years", value="4y"),
            Choice(name="5 years", value="5y")
        ]
    )
    async def remindme(self, ctx: commands.Context, timecode: Choice[str], *, reminder: str) -> None:
        """Reminds you of something after a specified amount of time in a DM."""
        await ctx.defer(ephemeral=True)
        await ctx.send(f"Reminder set for **{timecode.value}** with the reminder `{reminder}`", ephemeral=True)
        time_convert = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800, "mo": 18144000, "y": 31536000}
        reminder_time_s = int(timecode.value[:-1]) * time_convert[timecode.value[-1]]
        time = datetime.datetime.now() + datetime.timedelta(seconds=reminder_time_s)
        await add_reminder(ctx.author.id, reminder, time, "dm")

    @commands.hybrid_command(name="remindhere")
    @app_commands.choices(
        timecode=[
            Choice(name="60 seconds", value="60s"),
            Choice(name="5 minutes", value="5m"),
            Choice(name="10 minutes", value="10m"),
            Choice(name="30 minutes", value="30m"),
            Choice(name="1 hour", value="1h"),
            Choice(name="2 hours", value="2h"),
            Choice(name="1 day", value="1d"),
            Choice(name="2 days", value="2d"),
            Choice(name="1 week", value="1w"),
            Choice(name="4 weeks", value="4w"),
            Choice(name="1 month", value="1mo"),
            Choice(name="2 months", value="2mo"),
            Choice(name="3 months", value="3mo"),
            Choice(name="6 months", value="6mo"),
            Choice(name="1 year", value="1y"),
            Choice(name="2 years", value="2y"),
            Choice(name="3 years", value="3y"),
            Choice(name="4 years", value="4y"),
            Choice(name="5 years", value="5y")
        ]
    )
    async def remindhere(self, ctx: commands.Context, timecode: Choice[str], *, reminder: str) -> None:
        """Reminds you of something after a specified amount of time in the channel."""
        await ctx.defer()
        await ctx.send(f"Reminder set for **{timecode.value}** with the reminder `{reminder}`")
        time_convert = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800, "mo": 18144000, "y": 31536000}
        reminder_time_s = int(timecode.value[:-1]) * time_convert[timecode.value[-1]]
        time = datetime.datetime.now() + datetime.timedelta(seconds=reminder_time_s)
        await add_reminder(ctx.author.id, reminder, time, "channel", ctx.channel.id)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(remindme(bot))
