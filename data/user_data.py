import sqlite3
import json
import math
import datetime
import time
import os
import discord

from utils.helpers import log, open_config

def check_if_user_exists(user_id, env):
    conn = sqlite3.connect(f'{env}_database.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    
    conn.close()
    return user if user else False

async def add_user_to_user_database(user_id, username, env, bot):

    guild_id = int(open_config(bot.env)['GUILD_ID'])
    guild = bot.get_guild(guild_id)
    if guild is None:
        print(f"Guild with ID {guild_id} not found.")
        return False
    
    # Get the member object from the guild
    member = guild.get_member(user_id)
    if member is None:
        print(f"User with ID {user_id} not found in guild.")
        return False

    # Check if user is server booster
    # Check if user is admin
    admin_status = 0
    booster = 0

    if member.premium_since is not None:
        booster = 1
    if member.guild_permissions.administrator:
        admin_status = 1
    conn = sqlite3.connect(f'{env}_database.db')
    cursor = conn.cursor()

    cursor.execute('''
        INSERT OR REPLACE INTO users 
        (user_id, username, approved, current_xp, level, total_xp, currency, admin_status, time_spent, last_seen, booster)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, username, 1, 0, 1, 0, 0, admin_status, 0, datetime.datetime.now(), booster))
    conn.commit()
    conn.close()

    role_name = "Croc Crew"  # Replace with your desired role name
    role = discord.utils.get(guild.roles, name=role_name)
    if role:
        try:
            await member.add_roles(role)
            print(f"Added {role_name} role to {username}.")
        except discord.Forbidden:
            print("I do not have permission to add roles.")
        except discord.HTTPException:
            print("Failed to add role due to an HTTP exception.")
    else:
        print(f"Role {role_name} not found in the guild.")

    return True

