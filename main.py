# RazBot new boy edition

import discord
from discord import app_commands
from discord.ext import commands
import yaml
from discord import app_commands

with open("config.yml", 'r') as yaml_read:
    config = yaml.safe_load(yaml_read)
with open("token.yml", 'r') as yaml_read:
    token = yaml.safe_load(yaml_read)
description = '''This is the RazBot rewrite.'''
intents = discord.Intents.all()
client = commands.Bot(command_prefix='!', description=description, intents=intents)

@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')


client.run(token["secret_stuff"]["token"])
