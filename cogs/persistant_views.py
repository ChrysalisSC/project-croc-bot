# Define a simple View that persists between bot restarts
# In order for a view to persist between restarts it needs to meet the following conditions:
# 1) The timeout of the View has to be set to None
# 2) Every item in the View has to have a custom_id set
# It is recommended that the custom_id be sufficiently unique to
# prevent conflicts with other buttons the bot sends.
# Note that custom_ids can only be up to 100 characters long.

import json
import os
import sqlite3
import discord
from discord.ext import commands
from discord import app_commands

from typing import Callable, Dict
from utils.helpers import log

class PersistantViews(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
       
        self.view_creators = {}
        self.database_name = f"{self.bot.env}_database.db"
        self.table_name = "views"
        

    def register_view(self, view_identifier, create_function):
        '''
        regitsters a view into the create_function
        '''
        self.view_creators[view_identifier] = create_function
        print(f"Registered view creator for: {view_identifier}")
        return

    def add_view_to_database(self, view_identifier, view_registration, channel_id, timeout_date="", disabled=0):
        #Add the view Id to the database
        print("ADDING VIEW TO DATABASE", view_identifier, view_registration, channel_id, timeout_date, disabled)
        conn = sqlite3.connect(self.database_name)
        c = conn.cursor()
    
        c.execute('''
            INSERT OR REPLACE INTO views 
            (view_id, view_registration, channel_id, timeout_date, disabled)
            VALUES (?, ?, ?, ?, ?)
        ''', (view_identifier, view_registration, channel_id, timeout_date,disabled ))
        conn.commit()
         
      
        conn.close()
        return True
    

    def load_views(self):
        conn = sqlite3.connect(self.database_name)
        c = conn.cursor()
        c.execute('SELECT view_id, view_registration FROM views')
        rows = c.fetchall()
        print("FOUND VIEWS", rows)
        for row in rows:
            view_identifier = row[0]
            view_registration = row[1]
            
            if view_registration in self.view_creators:
                view = self.view_creators[view_registration](view_identifier)
                self.bot.add_view(view)
            else:
                print(f"No creator function found for view: {view_identifier} - {view_registration}")
                print(self.view_creators)
        conn.close()


async def setup(bot):
    log("VIEWS", "Setting up Persistant views...")
    await bot.add_cog(PersistantViews(bot))
   