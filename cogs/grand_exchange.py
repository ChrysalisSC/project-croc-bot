import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import utils.helpers as helpers
import random
from PIL import Image, ImageDraw, ImageFont
import traceback

class GrandExchangeView(discord.ui.View):
    def __init__(self, view_identifier, bot, store_name):
        super().__init__(timeout=None)
        self.view_identifier = view_identifier
        self.bot = bot
        self.store_name = store_name
    
    @discord.ui.button(label="Browse Collection", style=discord.ButtonStyle.primary, custom_id="exchange_buy_{self.store_name}")
    async def buy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            print(f"starting shop for {self.store_name}")
            ThreadManager = self.bot.get_cog("ThreadManager")
            if ThreadManager is not None:
                thread = await ThreadManager.create_thread(interaction.channel_id, f"{self.store_name}", 1140, 600, interaction.user)
                if thread != False:
                    await interaction.response.send_message(f"Welcome to the Grand Exchange", ephemeral=True)
                    shop_cog = self.bot.get_cog("Shop")
                    await shop_cog.shop_start(thread, self.store_name, interaction.user.id) 
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
       

class GrandExchange(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.persistent_views = bot.get_cog("PersistantViews")
        # Register the games view with the persistent views system
        self.persistent_views.register_view("exchange_view", self.create_exchange_view)
    
    @commands.command()
    async def grandexchange(self, ctx, store_name: str):
        """Command to show the Grand Exchange view for a specific store."""
        view_identifier = f"grand_exchange_{store_name}_{ctx.channel.id}"
        view = self.create_exchange_view(view_identifier)

        embed = discord.Embed(
            title=f"{store_name.upper()} EXCHANGE", 
            description=f"Enter the store for the {store_name} collection.", 
            color=0xFFFFFF
        )
        embed.set_footer(text="Powered by the Grand Exchange")

        #set image as the store name
        image_path = f"images/stores/{store_name}.png"
        file = discord.File(image_path, filename="store.png")

        #add image to embed
        embed.set_image(url="attachment://store.png")
        # Add the view to the database for persistence
        self.persistent_views.add_view_to_database(view_identifier, "exchange_view", ctx.channel.id)
        await ctx.send(embed=embed, view=view, file=file)

    # Create the view for the Grand Exchange with buttons specific to each store
    def create_exchange_view(self, view_identifier):
        store_name = view_identifier.split("_")[2]
        return GrandExchangeView(view_identifier, self.bot, store_name)

async def setup(bot):
    helpers.log("GRAND EXCHANGE", "Setting up Grand Exchange cog...")
    await bot.add_cog(GrandExchange(bot))