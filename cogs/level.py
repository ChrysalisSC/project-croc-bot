import discord
from discord.ext import commands, tasks
from discord import app_commands
import sqlite3

import utils.helpers as helpers
import requests
import data.user_data as user_data
from utils.image_create import create_level_card

class Level(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.database = f"{self.bot.env}_database.db"
        self.env = bot.env
        self.chronicles =self.set_croc(bot.env)
        self.check_voice_channels.start()  # Start the background task
        self.level_speed = 50
    
    def set_croc(self, env):
        config = helpers.open_config(env)
        print("config:",config)
        return config['CROCCHRONICLES']
    
    @tasks.loop(minutes=3)
    async def check_voice_channels(self):
        time = helpers.get_time()
        print(f"Checking voice channels at {time}")
        for guild in self.bot.guilds:
            for member in guild.members:
                if member.voice and member.voice.channel:
                    user_id = member.id
                    print("Found user in voice channel:", member.display_name)
                    level = self.add_xp(user_id, self.level_speed)  # Grant 1 XP per minute
                    if level:
                        #send_level up image
                        channel = self.bot.get_channel(int(self.chronicles))
                        user_data_info, profile_data = user_data.get_all_profile_data(user_id, self.env)
                        title = user_data.get_items_by_ids([profile_data[1]], self.env)

                        thumbnail_url = str(member.avatar.url)
                        profile_picture_path = "temp_profile_picture.png"
                        response = requests.get(thumbnail_url)
                        if response.status_code == 200:
                            with open(profile_picture_path, "wb") as f:
                                f.write(response.content)

                        create_level_card(f"images/customization/{profile_data[3]}.png", member.display_name, title[0]['item_name'], level, int(user_data_info[3]))
                        file = discord.File("level_card.png", filename="level_card.png")
                        print(user_data_info)
                        if user_data_info[12] == 1:
                            await channel.send(f"🎉 {member.mention} leveled up to level {level}!", file = file)
                        else:
                            await channel.send(f"🎉 {member.display_name} leveled up to level {level} 2", file = file)


    def cog_unload(self):
        """Stops tasks when the cog is unloaded."""
        self.check_voice_channels.cancel()
    

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
            print(f"User {user_id} gained {points} XP. Total XP: {new_total_xp}, Level: {level}")
            # Return the new level if leveled up
            if level_up:
                user_data.add_user_funds(user_id, 100, self.env)
                return level

    @commands.Cog.listener()
    async def on_message(self, message):
        channel = self.bot.get_channel(int(self.chronicles))
        if message.author.bot:
            return  # Ignore bots
        user_id = message.author.id
        member = message.author
        level = self.add_xp(message.author.id, self.level_speed)  # Adjust points as needed
        if level:
            #send_level up image
            user_data_info, profile_data = user_data.get_all_profile_data(user_id, self.env)
            title = user_data.get_items_by_ids([profile_data[1]], self.env)

            thumbnail_url = str(member.avatar.url)
            profile_picture_path = "temp_profile_picture.png"
            response = requests.get(thumbnail_url)
            if response.status_code == 200:
                with open(profile_picture_path, "wb") as f:
                    f.write(response.content)

            create_level_card(f"images/customization/{profile_data[3]}.png", member.display_name, title[0]['item_name'], level, int(user_data_info[3]))
            file = discord.File("level_card.png", filename="level_card.png")
            if user_data_info[12] == 1:
                await channel.send(f"🎉 {member.mention} leveled up to level {level}!", file = file)
            else:
                await channel.send(f"🎉 {member.display_name} leveled up to level {level}!", file = file)

async def setup(bot):
    #name of your log(name of cog, print_info)
    helpers.log("LEVEL", "Setting up LEVEL cog...")
    await bot.add_cog(Level(bot))
   