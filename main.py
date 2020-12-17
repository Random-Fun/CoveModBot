import discord
import time
import asyncio
from discord.ext import commands
import datetime
import random
import setup
import os
import json

bot = commands.Bot(command_prefix=[setup.prefix()])


@bot.event
async def on_ready():
    startup = time.ctime()
    print('Signed in as:')
    print(bot.user.name)
    print(bot.user.id)
    print('Startup at: ' + startup)
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")




bot.run(setup.token())
