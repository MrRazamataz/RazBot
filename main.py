# RazBot new boy edition
import asyncio

import discord
from discord import app_commands
from discord.ext import commands
import yaml
from discord import app_commands
cogs = ['cogs.management.database']
print("Imported libs. RazBot is starting...")

with open("config.yml", 'r') as yaml_read:
    config = yaml.safe_load(yaml_read)
with open("token.yml", 'r') as yaml_read:
    token = yaml.safe_load(yaml_read)

description = '''This is the RazBot rewrite.'''
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', description=description, intents=intents)


async def main():
    async with bot:
        for cog in cogs:  # Looks for the cogs,
            await bot.load_extension(cog)  # Loads the cogs.
        try:
            await bot.start(token["secret_stuff"]["token"])
        except KeyboardInterrupt:
            print("Bye!")
            await bot.close()
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')




asyncio.run(main())
