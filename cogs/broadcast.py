import discord
from discord.ext import commands
from discord import app_commands

import utils.helpers as helpers
import random
#import userdata
import data.user_data as user_data
import traceback

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
            await interaction.response.send_message(f"A Sharp Decision {interaction.user.name.upper()} - Let me show you around...\n Here, Take this role *[role name/id here]* and lets get to it!\n I’m all about that croc-and-roll lifestyle!\n \n *looks at you with a grinning smile*", ephemeral=True)
        else:
            await interaction.response.send_message(random_response, ephemeral=True)
           

    @discord.ui.button(label="Refuse", style=discord.ButtonStyle.danger, custom_id="refuse_croc_deal")
    async def deal2_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        random_response = random.choice(responses_refused)
        await interaction.response.send_message(random_response, ephemeral=True)


class Broadcast(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.env = bot.env
        self.persistent_views = bot.get_cog("PersistantViews")
        # Register the games view with the persistent views system
        self.persistent_views.register_view("deal_view", self.create_deal_view)
        self.persistent_views.register_view("profile_view", self.create_profile_view)
      

    @commands.command()
    async def send_deal(self, ctx):
        """sends a embed with a deal or no deal buttons"""
        view_identifier = f"a_suspicious_deal_{ctx.channel.id}"
        view = self.create_deal_view(view_identifier)

        deal_offer = (
            "**Psst! You there! Yes, you! Come closer for a very special offer!**\n"
            "I’ve seen you popping up here and there—must be fate leading you to this deal!\n"
            "I cant say just what it is yet, but I can promise **YOU** my dear friend! \n"
            "This isn't just any deal... it's a *suspiciously delightful* one!\n"
            "Choose wisely, because I guarantee that no one has *ever* regretted a deal with a crocodile!\n"
        )

        embed = discord.Embed(title="A Suspicious Deal?", description=deal_offer, color=0xFFA500)
        embed.set_footer(text="Use the buttons to make your selection.")

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
                    await profile_cog.shop_start(thread, interaction.user.id) 
                else:
                    await interaction.response.send_message("You already have an open thread", ephemeral=True)
            else:
                await interaction.response.send_message(
                    "Thread manager not found", ephemeral=True
                )
        except Exception as e:
            error_message = traceback.format_exc()
            helpers.log("SHOP", f"Error starting Shop: {error_message}")
            
        return True
   
  
async def setup(bot):
    #name of your log(name of cog, print_info)
    helpers.log("EXAMPLE", "Setting up Example cog...")
    await bot.add_cog(Broadcast(bot))
