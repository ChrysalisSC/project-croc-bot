import discord
from discord.ext import commands
from discord import app_commands

import utils.helpers as helpers



"""

This class creates the game view with buttons for each game.

"""






class GamesView(discord.ui.View):
    def __init__(self, view_identifier, bot):
        super().__init__(timeout=None)
        self.view_identifier = view_identifier
        self.bot = bot

    @discord.ui.button(label="Wordle", style=discord.ButtonStyle.primary, custom_id="game1_wordle")
    async def game1_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            print("starting wordle")
            ThreadManager = self.bot.get_cog("ThreadManager")
            print("Got thread manager")
            if ThreadManager is not None:
                thread = await ThreadManager.create_thread(interaction.channel_id, "Wordle", 1140, 600, interaction.user)
                if thread != False:
                    await interaction.response.send_message(f"Welcome to Wordle", ephemeral=True)
                    wordle_cog = self.bot.get_cog("Wordle")
                    await wordle_cog.start_wordle(thread, interaction.user.id) 
                else:
                    await interaction.response.send_message("You already have an open thread", ephemeral=True)
            else:
                await interaction.response.send_message(
                    "Thread manager not found", ephemeral=True
                )
        except Exception as e:
            helpers.log("Wordle", f"Error starting wordle: {e}")
        return True
       

    @discord.ui.button(label="Game 2", style=discord.ButtonStyle.primary, custom_id="game2")
    async def game2_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("You selected Game 2!", ephemeral=True)

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

        embed = discord.Embed(title="GAMES:", description="Select one of the games below:", color=0x00ff00)
        embed.set_footer(text="Use the buttons to make your selection.")

        # Add the view to the database for persistence
        self.persistent_views.add_view_to_database(view_identifier, "games_view", ctx.channel.id)
        await ctx.send(embed=embed, view=view)

    #create a view with a buttons with different games in it.
    def create_games_view(self, view_identifier):
        return GamesView(view_identifier, self.bot)
    
    
    @app_commands.command(
        name="guess",
        description="Submit your guess for the current game"
    )
    async def guess(self, interaction: discord.Interaction, guess: str):
        user_id = interaction.user.id
        thread = interaction.channel  # Assuming each game runs in its own thread

        if thread.name == "Wordle":  # Check if the user is in a Wordle thread
            wordle_cog = self.bot.get_cog("Wordle")
            if wordle_cog:
                await wordle_cog.process_guess(interaction.user, guess, interaction)
            else:
                await interaction.response.send_message("Wordle game is not available", ephemeral=True)
        else:
            await interaction.response.send_message(f"Guess command is not available in this channel or thread.", ephemeral=True)
    
   
async def setup(bot):
    #name of your log(name of cog, print_info)
    helpers.log("GAMES", "Setting up games cog...")
    await bot.add_cog(Games(bot))
   
