import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import utils.helpers as helpers
import data.user_data as user_data

class ShopSelect(discord.ui.Select):
    def __init__(self, item_type, items, database):
        options = [
            discord.SelectOption(label=item_name, description=f"{price} currency", value=item_id)
            for item_id, item_name, price in items
        ]
        super().__init__(placeholder=f"Choose a {item_type}", min_values=1, max_values=1, options=options)
        self.item_type = item_type
        self.database = database
        self.preview_message = None
        self.env = database.split('_')[0]

    async def callback(self, interaction: discord.Interaction):
        # If there's an existing preview message, delete it
        if self.preview_message:
            await self.preview_message.delete()

        selected_item_id = self.values[0]  # Now this is the item_id
        selected_item_details = await self.get_item_details(selected_item_id)

        embed = discord.Embed(
            title=f"Preview: **{selected_item_details['item_name']}**",
            description=selected_item_details['description'],
            color=discord.Color.green()
        )
        
        # Check if an image is associated with the item_id
        is_image = False
        if selected_item_id.startswith('1'):  # Assuming IDs that start with "1" are images
            is_image = True
            file = discord.File(f"images/customization/{selected_item_id}.png", filename=f"{selected_item_id}.png")
            embed.set_image(url=f"attachment://{selected_item_id}.png")

        # Create buttons for buying or canceling
        buy_button = discord.ui.Button(label="Buy", style=discord.ButtonStyle.primary)
        cancel_button = discord.ui.Button(label="Cancel", style=discord.ButtonStyle.secondary)

        async def buy_callback(button_interaction: discord.Interaction):
            # Logic to handle item purchase
            currency_amount = user_data.check_user_funds(button_interaction.user.id, self.env)
            if currency_amount < selected_item_details['price']:
                await button_interaction.response.send_message("You don't have enough currency to buy this item.", ephemeral=True)
                return
            #check if user already has this item
            if user_data.check_user_item(button_interaction.user.id, selected_item_details['item_id'], self.env):
                await button_interaction.response.send_message("You already own this item.", ephemeral=True)
                return
            user_data.remove_user_funds(button_interaction.user.id, selected_item_details['price'], self.env)
            user_data.add_item_to_user(button_interaction.user.id, selected_item_details['item_id'], self.env)

            await button_interaction.response.send_message(f"You bought **{selected_item_details['item_name']}**!", ephemeral=True)

        buy_button.callback = buy_callback
      
        # Create a new view for the buttons
        button_view = discord.ui.View()
        button_view.add_item(buy_button)
       
        if is_image:
            self.preview_message = await interaction.response.send_message(embed=embed, file=file, view=button_view, ephemeral=True)
        else:
            self.preview_message = await interaction.response.send_message(embed=embed, view=button_view, ephemeral=True)

        # Store the preview message reference
        self.preview_message = await interaction.original_response()

    async def get_item_details(self, item_id):
        # Fetch details from the database based on item_id
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()
        
        print("Item ID:", item_id)
        query = '''SELECT * FROM items WHERE item_id = ?'''
        cursor.execute(query, (item_id,))
        columns = [column[0] for column in cursor.description]  # Get column names
        result = cursor.fetchone()
        connection.close()
        if result:
            result = dict(zip(columns, result))
        print(result)
        return result
            
            
         


class ShopView(discord.ui.View):
    def __init__(self, shop_items, database):
        super().__init__()
        self.database = database
        # Create a separate dropdown for each item_type
        for item_type, items in shop_items.items():
            self.add_item(ShopSelect(item_type, items, self.database))


class Shop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database = f"{self.bot.env}_database.db"



    async def shop_start(self, thread, shop_name, user_id):
        # Step 1: Connect to the database
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()
        
        # Step 2: Query to retrieve items by shop name and group by item_type
        query = '''SELECT item_type, item_id, item_name, price 
               FROM items 
               WHERE item_shop = ? 
               ORDER BY item_type'''
        cursor.execute(query, (shop_name,))
        items = cursor.fetchall()

        # Step 3: Organize items by type
          # Step 3: Organize items by type
        shop_items = {}
        for item_type, item_id, item_name, price in items:
            if item_type not in shop_items:
                shop_items[item_type] = []
            shop_items[item_type].append((item_id, item_name, price))

        # Step 4: Create an embed
        embed = discord.Embed(
            title=f"{shop_name.capitalize()} Shop Offerings",
            description=f"Here are the items available in the {shop_name} shop.",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Use the dropdowns to view item details and make a purchase.")

        #add store image
        file = discord.File(f"images/stores/{shop_name}_1.png", filename=f"store.png")
        embed.set_image(url=f"attachment://store.png")

        # Add fields to the embed for each item type
        for item_type, item_list in shop_items.items():
            item_details = "\n".join([f"**{item_name}** - {price} currency" for item_id, item_name, price in item_list])
            embed.add_field(name=item_type.capitalize(), value=item_details, inline=False)

        # Step 5: Close the database connection
        connection.close()

        # Step 6: Send the embed and view with categorized dropdowns
        view = ShopView(shop_items, self.database)
        await thread.send(embed=embed, view=view, file=file)

async def setup(bot):
    helpers.log("SHOP", "Setting up Shop cog...")
    await bot.add_cog(Shop(bot))