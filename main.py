# RazBot new boy edition
import asyncio
import traceback

import aiomysql
import discord
from discord import app_commands
from discord.ext import commands
import yaml
from discord import app_commands
import logging, logging.handlers

cogs = ['cogs.management.database', 'cogs.moderation.mod', 'cogs.management.admin', 'cogs.fun.fun',
        'cogs.management.permissions', 'cogs.management.settings', 'cogs.tools.yt2mp4']
print("Imported libs. RazBot is starting...")

with open("config.yml", 'r') as yaml_read:
    config = yaml.safe_load(yaml_read)
with open("token.yml", 'r') as yaml_read:
    tokens = yaml.safe_load(yaml_read)

description = '''This is the RazBot rewrite.'''
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', description=description, intents=intents)

logger = logging.getLogger('discord')
logger.setLevel(logging.ERROR)
handler = logging.handlers.RotatingFileHandler(
    filename='razbot.log',
    encoding='utf-8',
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)


async def main():
    async with bot:
        for cog in cogs:  # Looks for the cogs,
            await bot.load_extension(cog)  # Loads the cogs.
            print(f"Loaded cog: {cog}")
        try:
            pool = await aiomysql.create_pool(host=tokens["database_info"]["host"], port=3306,
                                              user=tokens["database_info"]["username"],
                                              password=tokens["database_info"]["password"],
                                              db='razbotxy_botDB')
            bot.pool = pool
            await bot.start(tokens["secret_stuff"]["token"])
        except KeyboardInterrupt:
            print("Bye!")
            pool.close()
            await pool.wait_closed()
            await bot.close()


@bot.event
async def on_command_error(ctx, error):
    traceback.print_exc()
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(f"Unknown command, sorry. Use `{ctx.prefix}help` to view a list of commands.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("Hey! Sorry but you don't have perms for that command. Duh-Doy!")
    else:
        raise error


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')


asyncio.run(main())
