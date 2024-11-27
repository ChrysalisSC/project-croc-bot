import discord
from discord.ext import commands, tasks
from discord import app_commands

import utils.helpers as helpers
import random
#import userdata
import data.user_data as user_data
import traceback
from utils.image_create import create_profile_card, create_level_card
import requests
import datetime
import pytz

import sqlite3
responses_agreed = [
    "You have already agreed to the deal.",
    "Looks like you're already on board with the croc crew!",
    "You're as committed as a croc in a swamp—no turning back now!",
    "You've sealed the deal like a croc’s jaws—no second bites!",
    "Once bitten, twice shy? Not for you! You’ve accepted the croc deal.",
    "No need to wade back in, you've already dived into the deal!",
    "You’ve already taken the plunge into this crocodile business!",
    "You’re already swimming with the crocs; no need for another splash!",
    "You've already embraced the swamp life—no take-backs!",
    "The deal’s already set—you're as locked in as a croc in its lair!",
    "You’ve already locked jaws on this deal; it’s a done deal!",
    "You’re already part of the croc gang—no need for a repeat handshake!",
    "You’ve agreed, and the crocs are happy to have you aboard!",
    "No need to paddle back; you’re already in the croc boat!",
    "You're as committed as a croc to a good sunbathing spot!",
    "You've already hopped on this croc express; no stops allowed!",
    "You've made your choice—let’s not get tangled in the reeds again!",
    "You’ve already sunk your teeth into this deal!",
    "You’ve jumped into the swamp with both feet—no going back now!",
    "You’re already on the croc side of the deal; let’s roll with it!",
    "Once a croc deal acceptor, always a croc deal acceptor!"
]

responses_refused = [
    "You can't swim away from this deal that easily!",
    "Are you sure you want to back away from the croc life? It’s pretty chill here!",
    "Refusing a croc deal? Bold move! Hope you like the dry land!",
    "You’re turning tail? Just remember, the swamp has its ways!",
    "You’ve turned your back on the crocs! Are you sure about that?",
    "Swamps can be unforgiving to those who refuse a deal!",
    "The croc is not pleased! You may want to rethink that swim!",
    "Refusal? That’s a slippery slope you’re heading down!",
    "You can’t resist forever! The swamp calls your name!",
    "Are you ready to face the croc consequences of refusal?",
    "Backpedaling, are we? The crocs might not forget this!",
    "You’ve stepped into murky waters with that refusal!",
    "You just passed up a once-in-a-lifetime croc deal!",
    "Are you trying to outsmart the swamp? Good luck with that!",
    "Refusal accepted, but don’t be surprised when the crocs come calling!",
    "You can’t deny the croc charm forever, you know!",
    "Refusing the deal? Just be careful of the hungry eyes watching you!",
    "You might want to keep an eye on your back; crocs have long memories!",
    "You’ve swum upstream, but the croc tide might pull you back!",
    "You might regret this! The croc deals have a way of haunting you!",
    "The crocs might not let you forget this decision—watch your tail!"
]

#get time for midnight pacific
MIDNIGHT = datetime.datetime.now(pytz.timezone('US/Pacific')).replace(hour=0, minute=0, second=0, microsecond=0)

class DealView(discord.ui.View):
    def __init__(self, view_identifier, bot):
        super().__init__(timeout=None)
        self.view_identifier = view_identifier
        self.bot = bot
      
    @discord.ui.button(label="Agree", style=discord.ButtonStyle.success, custom_id="agree_croc_deal")
    async def deal1_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # add user to database or check to see if they aready approved
        random_response = random.choice(responses_agreed)
        user = user_data.check_if_user_exists(interaction.user.id, self.bot.env)
        if user == False:
            await user_data.add_user_to_user_database(interaction.user.id, interaction.user.name, self.bot.env, self.bot)
          
            role_name = "Croc Crew"  # Replace with your desired role name
            role = discord.utils.get(interaction.guild.roles, name=role_name)
            await interaction.response.send_message(f"A Sharp Decision {interaction.user.name.upper()} - Let me show you around...\n Here, Take this role {role} and lets get to it!\n I’m all about that croc-and-roll lifestyle!\n \n *looks at you with a grinning smile*", ephemeral=True)
        else:
            await interaction.response.send_message(random_response, ephemeral=True)
           

    @discord.ui.button(label="Refuse", style=discord.ButtonStyle.danger, custom_id="refuse_croc_deal")
    async def deal2_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        random_response = random.choice(responses_refused)
        await interaction.response.send_message(random_response, ephemeral=True)

class SupplyDropView(discord.ui.View):
    def __init__(self, view_identifier, bot):
        super().__init__(timeout=None)
        self.view_identifier = view_identifier
        self.bot = bot
        #supply_drop_{supply_id}_{ctx.channel.id}"
        self.supply_id = int(view_identifier.split("_")[2])
    
    @discord.ui.button(label="Collect Daily Reward", style=discord.ButtonStyle.primary, custom_id="exchange_buy_{self.supply_id}")
    async def buy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
           
            print("supply_id", self.supply_id)
            #TODO:
            if user_data.check_user_item(interaction.user.id, self.supply_id, self.bot.env):
                await interaction.response.send_message('You have already claimed this reward.', ephemeral=True)
                return
           
            user_data.add_item_to_user(interaction.user.id, self.supply_id, self.bot.env)
            
            await interaction.response.send_message('You have claimed your reward!', ephemeral=True)
        except Exception as e:
            error_message = traceback.format_exc()
            helpers.log("BROADCAST", f"Error starting Shop: {error_message}")
            
        return True

class CurrencyDropView(discord.ui.View):
    def __init__(self, view_identifier, bot):
        super().__init__(timeout=None)
        self.view_identifier = view_identifier
        self.bot = bot

    @discord.ui.button(label="COLLECT YOUR DAILY REWARD", style=discord.ButtonStyle.primary, custom_id="currency_daily_button")
    async def daily_currency_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            #check if user has already claimed
            if user_data.is_user_lockout(interaction.user.id, 1, self.bot.env):
                await interaction.response.send_message('You have already claimed this reward today.', ephemeral=True)
                return

            user_data.add_user_funds(interaction.user.id, 50, self.bot.env)
            #lockout uer
            user_data.lockout_user(interaction.user.id, 1,  self.bot.env)
            await interaction.response.send_message('You have claimed your reward and earned 50 Credits!', ephemeral=True)
        except Exception as e:
            error_message = traceback.format_exc()
            helpers.log("BROADCAST", f"Error with currnecy: {error_message}")
        return True


class Broadcast(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.env = bot.env
        self.persistent_views = bot.get_cog("PersistantViews")
        self.persistent_views.register_view("deal_view", self.create_deal_view)
        self.persistent_views.register_view("profile_view", self.create_profile_view)
        self.persistent_views.register_view("supply_drop_view", self.create_supply_view)
        self.persistent_views.register_view("daily_currency_view", self.create_currency_view)
        self.midnight_reset.start()

    @tasks.loop(time=[datetime.time(hour=18, minute=50, second=0, microsecond=0)])
    async def midnight_reset(self):
        """
        Reset lockouts at midnight.
        """
        print("Midnight Reset")
        user_data.reset_lockouts(self.env)
        return
      
    @commands.command()
    async def send_deal(self, ctx):
        """sends a embed with a deal or no deal buttons"""
        view_identifier = f"a_suspicious_deal_{ctx.channel.id}"
        view = self.create_deal_view(view_identifier)

        deal_offer = (
            "Psst! Hey, you! Yes, YOU! Step right up, I've got something truly special for you!\n"
            "I've noticed you lurking around, fate must have brought you to this very moment! \n"
            "I can't spill all the details just yet, but trust me, my friend...\n"
            "This isn't just any ordinary deal... I'm offering a special invitation!\n"
            "Choose wisely, because I assure you, no one has ever regretted making a deal with a crocodile!"
        )

        embed = discord.Embed(title="A Suspicious Deal?", description=deal_offer, color=0xFFA500)
        embed.set_footer(text="Select 'AGREE' or 'REFUSE'. Agreement will add you to the Croc Crew!")

        # Add the view to the database for persistence
        #set image
        file = discord.File(f"images/server_icons/croc_1.jpg", filename="image.jpg")
        embed.set_image(url="attachment://image.jpg")

        print(view_identifier, "deal_view", ctx.channel.id)
        self.persistent_views.add_view_to_database(view_identifier, "deal_view", ctx.channel.id)
        await ctx.send(embed=embed, view=view, file=file)

      #create a view with a buttons with different games in it.
    def create_deal_view(self, view_identifier):
        return DealView(view_identifier, self.bot)
    
        # Create the view for the Grand Exchange with buttons specific to each store
    def create_profile_view(self, view_identifier):
        return ProfileView(view_identifier, self.bot)
    
    def create_supply_view(self, view_identifier):
        return SupplyDropView(view_identifier, self.bot)
    
    def create_currency_view(self, view_identifier):
        return CurrencyDropView(view_identifier, self.bot)
    
    


   
    
    @commands.command()
    async def currency_drop(self, ctx):
        """sends a embed with a currency button"""
        view_identifier = f"daily_currency_{ctx.channel.id}"
        view = self.create_currency_view(view_identifier)
        embed = discord.Embed(title="Daily Currency!", description="Be rewarded every day!", color=0xFFA500)
        file = discord.File(f"images/customization/daily_drop.png", filename="image.png")
        embed.set_image(url="attachment://image.png")
        self.persistent_views.add_view_to_database(view_identifier, "daily_currency_view", ctx.channel.id)
        await ctx.send(embed=embed, view=view, file=file)
        return

        

    @commands.command()
    async def supply_drop(self, ctx, supply_id: int):
        """sends a embed with a deal or no deal buttons"""
        view_identifier = f"supply_drop_{supply_id}_{ctx.channel.id}"
        view = self.create_supply_view(view_identifier)

        embed = discord.Embed(title="SUPPLY DROP!", description="A new drop has arrived!", color=0xFFA500)
      
        #get item by id
        item = user_data.get_items_by_ids([supply_id], self.env)
   
        embed.add_field(name=f"NAME: {item[0]['item_name']}", value=f"{item[0]['description']}", inline=False)
        if item[0]['item_type'] == "header":
                file = discord.File(f"images/customization/{supply_id}.png", filename="image.png")
                embed.set_image(url="attachment://image.png")
                #add description
                self.persistent_views.add_view_to_database(view_identifier, "supply_drop_view", ctx.channel.id)
                await ctx.send(embed=embed, view=view, file=file)
                return

        print(view_identifier, "supply_drop_view", ctx.channel.id)
        self.persistent_views.add_view_to_database(view_identifier, "supply_drop_view", ctx.channel.id)
        await ctx.send(embed=embed, view=view)

    @commands.command()
    async def send_profile(self, ctx):
        """shows the profile view for a user"""
       
        view_identifier = f"profile_{ctx.channel.id}"
        view = self.create_profile_view(view_identifier)

        embed = discord.Embed(
            title=f"Profile", 
            description="Select an option below:", 
            color=0x00ff00
        )
        embed.set_footer(text="Use the buttons to make your selection.")

        # Add the view to the database for persistence
        self.persistent_views.add_view_to_database(view_identifier, "profile_view", ctx.channel.id)
        await ctx.send(embed=embed, view=view)

    # Create the view for the Grand Exchange with buttons specific to each store
    def create_profile_view(self, view_identifier):
        return ProfileView(view_identifier, self.bot)
  
    @commands.command()
    async def add_funds(self, ctx, member: discord.Member, funds: int):
        user_data.add_user_funds(member.id, funds, self.bot.env)
        await ctx.send(f"Added {funds} to {member.name}'s account")

   
    @app_commands.command(
        name="balance",
        description="Check How much currency you have"
    )
    async def balance(self, interaction: discord.Integration, member: discord.Member = None):
        #get currency by geting users database
        print(f"User {interaction.user.id} requested their balance")
        if member is None:
            member = interaction.user
        else:  
            member = member
        user_id = member.id

        user_data_info = user_data.get_all_profile_data(user_id, self.env)[0]
        print("user_data_info", user_data_info)
        embed = discord.Embed(
            title="Balance",
            description=f"{member.display_name} has {user_data_info[5]} coins",
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=embed)
     
    @app_commands.command(
        name="profile",
        description="Shows User Profile"
    )
    async def profile_commannd(self, interaction: discord.Integration, member: discord.Member = None):
        """shows the profile view for a user"""
        #call create image and send it 
        print(f"User {interaction.user.id} requested their profile")
        if member is None:
            member = interaction.user
        else:  
            member = member
        user_id = member.id
        booster = False
        #check if member is booster
        if member.premium_since is not None:
            booster = True
      
        badge_data = user_data.get_owned_items(user_id, "badge", self.env)
        user_data_info, profile_data = user_data.get_all_profile_data(user_id, self.env)
        title = user_data.get_items_by_ids([profile_data[1]], self.env)

        thumbnail_url = str(member.avatar.url)
        # Download the profile picture from the URL and save it to a temporary file
        profile_picture_path = "temp_profile_picture.png"
        response = requests.get(thumbnail_url)
        if response.status_code == 200:
            with open(profile_picture_path, "wb") as f:
                f.write(response.content)

        title = user_data.get_items_by_ids([profile_data[1]], self.env)

        print("title:", title)  

        interests = user_data.get_items_by_ids([profile_data[5], profile_data[6], profile_data[7], profile_data[8], profile_data[9]],self.env )
        #interests = user_data.get_items_by_ids(interests, self.bot.env)
        create_profile_card(f"images/customization/{profile_data[3]}.png", member.display_name, title[0]['item_name'], user_data_info[4] , badge_data,user_data_info[10], user_data_info[6], user_data_info[3], interests, booster)

        # Create the embed
        embed = discord.Embed(
            title="Profile",
            description="Here's your profile card!",
            color=discord.Color.blurple()
        )

        # file name is profile_card.png
        file = discord.File("profile_card.png", filename="profile_card.png")

        await interaction.response.send_message(file=file)

    @commands.command()
    async def daily_lockout(self, ctx):
        
        embed = discord.Embed(
            title="Bot Info",
            description="This bot is a test bot for testing purposes.",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Leveling", value="This bot has a leveling system that allows users to gain experience points and level up by chatting in the server and in voice.\n You gain 1 xp every minute in voice chat.\n You can check you level progress by using /profile", inline=False)
        embed.add_field(name="Currency", value="This bot has a currency system that allows users to earn currency by chatting in the server and in voice.\n You can check you balance by using /balance", inline=False)
        await ctx.send(embed=embed)
    
    @commands.command()
    async def info_bot(self, ctx):
        #explains how the bot is works
        embed = discord.Embed(
            title="Bot Info",
            description="This bot is a test bot for testing purposes.",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Leveling", value="This bot has a leveling system that allows users to gain experience points and level up by chatting in the server and in voice.\n You gain 1 xp every minute in voice chat.\n You can check you level progress by using /profile", inline=False)
        embed.add_field(name="Currency", value="This bot has a currency system that allows users to earn currency by chatting in the server and in voice.\n You can check you balance by using /balance", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def level_prof(self, ctx):
        """shows the profile view for a user"""
        #call create image and send it 
        user_id = ctx.author.id
        badge_data = user_data.get_owned_items(user_id, "badge", self.env)
        print("badge_data", badge_data)
        level = 2
       

        create_level_card("images/customization/100001.png", "John Doe", "Champion", 1)

        # file name is profile_card.png
        file = discord.File("level_card.png", filename="level_card.png")

        await ctx.send(file=file)


    

class ProfileView(discord.ui.View):
    def __init__(self, view_identifier, bot):
        super().__init__(timeout=None)
        self.view_identifier = view_identifier
        self.bot = bot
       
    
    @discord.ui.button(label="Update Profile", style=discord.ButtonStyle.primary, custom_id="update_profile")
    async def buy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            print(f"Starting Update profile")
            ThreadManager = self.bot.get_cog("ThreadManager")
            print("Got thread manager")
            if ThreadManager is not None:
                thread = await ThreadManager.create_thread(interaction.channel_id, f"USER PROFILE", 1140, 600, interaction.user)
                if thread != False:
                    await interaction.response.send_message(f"Welcome to your profile!", ephemeral=True)
                    profile_cog = self.bot.get_cog("Profile")
                    await profile_cog.start_profile(thread, interaction.user.id) 
                else:
                    await interaction.response.send_message("You already have an open thread", ephemeral=True)
            else:
                await interaction.response.send_message(
                    "Thread manager not found", ephemeral=True
                )
        except Exception as e:
            error_message = traceback.format_exc()
            helpers.log("PROFILE", f"Error starting profile for {interaction.user.id}: {error_message}")
            
        return True


  
     
async def setup(bot):
    #name of your log(name of cog, print_info)
    helpers.log("BROADCAST", "Setting up BROADCAST cog...")
    await bot.add_cog(Broadcast(bot))
