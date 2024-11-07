import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

import utils.helpers as helpers

class Level(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database = f"{self.bot.env}_database.db"

    def add_xp(self, user_id: int, points: int):
        # Add points to a user or insert if they don't exist
        with sqlite3.connect(self.database) as conn:
            cursor = conn.cursor()

            cursor.execute("SELECT current_xp, total_xp, level FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            
            # If the user is not found, exit without adding XP
            if result is None:
                return None


            cursor.execute('''INSERT OR IGNORE INTO users 
                              (user_id, current_xp, total_xp, level) 
                              VALUES (?, 0, 0, 1)''', (user_id,))
            # Fetch current XP and level before updating
            cursor.execute("SELECT current_xp, total_xp, level FROM users WHERE user_id = ?", (user_id,))
            current_xp, total_xp, level = cursor.fetchone()
            
            # Update the XP and check for level up
            new_total_xp = total_xp + points
            new_current_xp = current_xp + points
            level_up = False

            # Check if the user has leveled up
            if new_current_xp >= 100:
                level += 1
                new_current_xp -= 100  # Reset current XP after level-up
                level_up = True
            
            # Update the database with the new values
            cursor.execute('''UPDATE users 
                              SET current_xp = ?, total_xp = ?, level = ? 
                              WHERE user_id = ?''', 
                           (new_current_xp, new_total_xp, level, user_id))
            conn.commit()

            # Return the new level if leveled up
            if level_up:
                return level

    @commands.Cog.listener()
    async def on_message(self, message):
        # Give points if a user sends a message
        if message.author.bot:
            return  # Ignore bots
        level = self.add_xp(message.author.id, 1)  # Adjust points as needed
        if level:
            await message.channel.send(f"🎉 {message.author.mention} leveled up to level {level}!")



async def setup(bot):
    #name of your log(name of cog, print_info)
    helpers.log("EXAMPLE", "Setting up Example cog...")
    await bot.add_cog(Level(bot))
   