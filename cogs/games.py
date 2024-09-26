import discord
from discord.ext import commands
from discord import app_commands

import utils.helpers as helpers

"""

This class creates the game view with buttons for each game.

"""

class GamesView(discord.ui.View):
    def __init__(self, view_identifier):
        super().__init__(timeout=None)
        self.view_identifier = view_identifier

    @discord.ui.button(label="Game 1", style=discord.ButtonStyle.primary, custom_id="game1")
    async def game1_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Respond to the interaction properly
        await interaction.response.send_message("You selected Game 1!", ephemeral=True)

    @discord.ui.button(label="Game 2", style=discord.ButtonStyle.primary, custom_id="game2")
    async def game2_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You selected Game 2!", ephemeral=True)

    # Add more buttons for more games as needed


class Games(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.persistent_views = bot.get_cog("PersistantViews")
        # Register the games view with the persistent views system
        self.persistent_views.register_view("games_view", self.create_games_view)

    @commands.command()
    async def games(self, ctx):
        """Command to show the games view."""
        view_identifier = f"games_{ctx.channel.id}"
        view = self.create_games_view(view_identifier)

        # Add the view to the database for persistence
        await self.persistent_views.add_view_to_database(view_identifier, "games_view", ctx.channel.id)
        await ctx.send("Choose a game:", view=view)

    #create a view with a buttons with different games in it.
    def create_games_view(self, view_identifier):
        return GamesView(view_identifier)
    

async def setup(bot):
    #name of your log(name of cog, print_info)
    helpers.log("GAMES", "Setting up games cog...")
    await bot.add_cog(Games(bot))
   
