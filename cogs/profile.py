import discord
from discord.ext import commands
from discord import app_commands

import utils.helpers as helpers
import sqlite3
import data.user_data as user_data

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database = f"{self.bot.env}_database.db"

    async def start_profile(self, thread, user_id):
        profile_data_dict = user_data.get_user_profile(user_id, self.bot.env)
        
        embed = discord.Embed(
            title="Profile",
            description="Welcome to your profile! Select an item to equip from your owned items below.\n Use /profile to view your profile.",
            color=discord.Color.blurple()
        )
       
      
        # {'equipped_title': 200000, 'equipped_badge': 600000, 'equipped_header': 100000, 'equipped_profile_color': 400000}
        #convert data to a list of ids
        profile_data_ids = [profile_data_dict.get("equipped_title"), profile_data_dict.get("equipped_header"), profile_data_dict.get("equipped_profile_color"), profile_data_dict.get("interest_1"), profile_data_dict.get("interest_2"), profile_data_dict.get("interest_3"), profile_data_dict.get("interest_4"), profile_data_dict.get("interest_5")]
      
        #print("profile DATA IDS:",profile_data_ids)
        profile_data = user_data.get_items_by_ids(profile_data_ids, self.bot.env)
        #print("profile DATA:",profile_data)
        #[{'item_id': 100000, 'item_type': 'header', 'item_name': 'Default Header', 'item_shop': 'default', 'description': 'The default header for your profile.', 'rarity': 'common', 'price': 0}, {'item_id': 200000, 'item_type': 'title', 'item_name': 'Newcomer', 'item_shop': 'default', 'description': 'The default title for your profile.', 'rarity': 'common', 'price': 0}, {'item_id': 400000, 'item_type': 'color', 'item_name': 'white', 'item_shop': 'default', 'description': 'white.', 'rarity': 'common', 'price': 0}]  
        #fix below:
        ints = 0
        if profile_data:
           
            equipped_items = ""
            for item in profile_data:
                print("ITEM:",item)
                if item["item_type"] == "title":
                    equipped_items += f"Title: {item['item_name']}\n"
                elif item["item_type"] == "header":
                    equipped_items += f"Header: {item['item_name']}\n"
                elif item["item_type"] == "profile_color":
                    equipped_items += f"Profile Color: {item['item_name']}\n"
                elif item["item_type"] == "interest":
                    ints += 1
                    equipped_items += f"Interest {ints}: {item['item_name']}\n"
               
        else:
            equipped_items = "No items equipped."
                
        embed.add_field(name="Equipped Items", value=equipped_items, inline=False)
        embed.set_footer(text="Use the select menus to change your equipped items.")
        
        # Create the view with selects for different item types
        view = discord.ui.View(timeout=None)
        for item_type in ["title", "header", "profile_color"]:
            items = user_data.get_all_owned_items(user_id, item_type, self.bot.env)
            if items:
                view.add_item(ProfileSelect(item_type, items, user_id, self.bot.env))

        # Fetch interest items (assuming item_type = 'interest' for the database)
        interest_items = user_data.get_items_by_ids([300000, 300001, 300002, 300003, 300004, 300005, 300006, 300007, 300008, 300009, 300010, 300011, 300012, 300013, 300014, 300015, 300016, 300017, 300018], self.bot.env)
        #print("interest_items:",interest_items)
        if interest_items:
            view.add_item(InterestSelect(interest_items, user_id, self.bot.env))

        await thread.send(embed=embed, view=view)

class ProfileSelect(discord.ui.Select):
    def __init__(self, item_type, items, user_id, env):
        for item in items:
            print(f"item_id: {item['item_id']}, item_name: {item['item_name']}, description: {item['description']}")

        options = [
            discord.SelectOption(label=item['item_name'], description=item['description'], value=str(item['item_id']))
            for item in items  # iterate over the items
        ]
        super().__init__(placeholder=f"Choose a {item_type}", min_values=1, max_values=1, options=options)
        self.item_type = item_type
        self.user_id = user_id
        self.env =env

    async def callback(self, interaction: discord.Interaction):
        selected_item_id = int(self.values[0])

        # Update the user's equipped item in the database
        print(f"user {self.user_id} equipped item {selected_item_id}")
        await user_data.change_equipped_item(self.user_id, self.item_type, selected_item_id, self.env)
        
        # Send confirmation message
        await interaction.response.send_message(f"You equipped a new {self.item_type}!", ephemeral=True)

class InterestSelect(discord.ui.Select):
    def __init__(self, items, user_id, env):
        options = [
            discord.SelectOption(
                label=item['item_name'],  # Extract from the dictionary
                description=f"{item['price']} currency",  # Extract from the dictionary
                value=str(item['item_id'])  # Extract from the dictionary
            )
            for item in items
        ]
        super().__init__(
            placeholder="Choose up to 5 interests", 
            min_values=1, 
            max_values=5, 
            options=options
        )
        self.user_id = user_id
        self.env = env

    async def callback(self, interaction: discord.Interaction):
        selected_item_ids = [int(value) for value in self.values]

        # Update the user's interests in the database
        print(f"user {self.user_id} selected interests {selected_item_ids}")
        await user_data.update_user_interests(self.user_id, selected_item_ids, self.env)
        
        # Send confirmation message
        await interaction.response.send_message("Your interests have been updated!", ephemeral=True)

async def setup(bot):
    #name of your log(name of cog, print_info)
    helpers.log("PROFILE", "Setting up PROFILE cog...")
    await bot.add_cog(Profile(bot))
   

