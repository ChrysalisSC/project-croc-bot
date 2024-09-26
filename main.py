"""
Python Bot V2

Date: 
- 04/08/2024
Description:
- This Python script serves as a template for creating a bot application. It can be used as a foundation for building various types of bots, such as chatbots, automation bots, or social media bots.

Authors:
- Colton Trebbien, Max Hopkins

Dependencies:
- [List of Python modules/libraries required]

Usage:
- python main.py <env>

Notes:

"""

# IMPORTS
import os
import json
import sys
import pytz
import datetime
import time


import utils.helpers as helpers
from data.configure_database import start_database

from cogs.fun_commands import FunCommands
from cogs.fun_commands import setup as setup_fun_commands
from cogs.fantasy import Fantasy
from cogs.fantasy import setup as setup_fantasy
from cogs.repository import Repository
from cogs.repository import setup as setup_repository
from cogs.games import Games
from cogs.games import setup as setup_games
from cogs.persistant_views import PersistantViews
from cogs.persistant_views import setup as setup_persistant_views

import discord
from discord.ext import commands, tasks
from discord.ui import Button, View
from discord import app_commands




class discord_bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.env = kwargs.pop('env', None)
       


bot = discord_bot(command_prefix="!", intents=discord.Intents.all())
script_dir = os.path.dirname(os.path.abspath(__file__)) #this is main
parent_dir = os.path.dirname(script_dir) 

    
@bot.command()
async def sync(ctx):
    CONFIG = helpers.open_config(bot.env)
    try:
        G = bot.get_guild(int(CONFIG['GUILD_ID']))
        bot.tree.copy_global_to(guild=G)
        synced = await bot.tree.sync(guild=G)
      
        await ctx.send(f"Synced {len(synced)} command(s).")
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        await ctx.send(f"Error syncing commands: {e}")
        print(f"Error syncing commands: {e}")

'''
async def delete_all_threads():
    # Iterate over each guild the bot is connected to
    for guild in bot.guilds:
        # Iterate over each channel in the guild
        for channel in guild.text_channels:
            # Fetch the threads in the channel
            threads = channel.threads
            # Delete each thread
            for thread in threads:
                await thread.delete()
'''

@bot.event
async def on_message(message):
   
    #time = str(helpers.get_pacific_time())
    if message.author == bot.user:
        return
    if message.author.bot:
        return
    try:
        helpers.log("MAIN", f"{message.author} - {message.content}")
    except:
        helpers.log("MAIN", f"{message.author} - ERROR MESSAGE")

    # await add_xp(bot, message.author.id, 50, 'XP')
    # print("added xp")
    # update_last_seen( message.author.id, time)
    # print("updated last seen")
    # await add_renown_to_user(bot, message.author.id, 50,  await get_selected_track(message.author.id))
    # print("added renown")
       
    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    # Define the welcome embed
    print()

    embed = discord.Embed(
        title=f"Welcome to the server, {member.name}!",
        description="We are excited to have you here.",
        color=discord.Color.green()
    )
    embed.set_thumbnail(url=member.display_avatar)
    embed.add_field(name="Rules", value="Be respectful and follow the server rules.")
    embed.set_footer(text=f"Joined at {member.joined_at}")
    
    # Send the embed to a specific channel (replace 'welcome_channel_id' with your channel ID)
    welcome_channel = bot.get_channel(1253800012630986854)
    if welcome_channel:
        await welcome_channel.send(embed=embed)
    
@bot.event
async def on_ready():


    # Setup Database if in prod or dev. (automatically skips if already created)
    if bot.env == 'prod' or bot.env == 'dev':
        start_database(bot.env)
    helpers.log("main", f"Logged in as {bot.user.name}")

    #setup views first so that other cogs can add their view registration to list
    await setup_persistant_views(bot)
    

    # Setup the cogs
    await setup_fun_commands(bot)
    await setup_fantasy(bot)
    await setup_games(bot)

    #if its the main bot running - not used for testing
    if bot.env == 'prod':
        await setup_repository(bot)
    if bot.env == 'test':
        await setup_repository(bot)

    #load all registered views
    persistent_views = bot.get_cog("PersistantViews") 
    persistent_views.load_views()  # Load views when setting up

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <env>")
        sys.exit(1)
    # Get the environment from the command-line argument
    env = sys.argv[1]
    helpers.log("main", f"Starting bot in {env} environment")
    # Load the configuration based on the provided environment
    config = helpers.open_config(env)
    if config:
        print("Configuration loaded successfully")
        bot.env = env


        bot.run(str(config['DISCORD_API']))
    else:
        print("Failed to load configuration. Please check that you have added the /config/settings/{env}.json file.")

if __name__ == "__main__":
    # Check if the environment is provided as a command-line argument
    main()
    
  
