import discord
from discord.ext import commands
from discord import app_commands

import utils.helpers as helpers

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def start_profile(self,thread, user_id):
        #create and send the profile embed
        embed = discord.Embed(
            title="Profile",
            description=f"Welcome to your profile!",
            color=discord.Color.blurple()
        )
        embed.set_footer(text="Use the buttons to update your profile.")

        #send the embed
        thread.send(embed=embed)

        


async def setup(bot):
    #name of your log(name of cog, print_info)
    helpers.log("EXAMPLE", "Setting up Example cog...")
    await bot.add_cog(Profile(bot))
   

