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

def update_last_seen(user_id, time, env):
    conn = sqlite3.connect(f'{env}_database.db')
    cursor = conn.cursor()
    
    cursor.execute('UPDATE users SET last_seen = ? WHERE user_id = ?', (time, user_id))
    conn.commit()
    
    conn.close()
    return True

def update_num_chats(user_id, env):
    conn = sqlite3.connect(f'{env}_database.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT chats FROM users WHERE user_id = ?', (user_id,))
    chats = cursor.fetchone()[0]
    chats += 1
    
    cursor.execute('UPDATE users SET chats = ? WHERE user_id = ?', (chats, user_id))
    conn.commit()
    
    conn.close()
    return True

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
    print("USERNAME: ", username)
    cursor.execute('''
        INSERT OR REPLACE INTO users 
        (user_id, username, approved, current_xp, level, total_xp, currency, admin_status, time_spent, chats, last_seen, booster)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, username, 1, 0, 1, 0, 0, admin_status, 0, 0, datetime.datetime.now(), booster))
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

def add_item_to_user(cursor, user_id, item_id, env):
    conn = sqlite3.connect(f'{env}_database.db')
    cursor = conn.cursor()

    cursor.execute(
        '''
        INSERT INTO user_items (user_id, item_id)
        VALUES (?, ?)
        ''',
        (user_id, item_id)
    )
    conn.commit()
    conn.close()
    return True

def equip_item(cursor, user_id, item_id, item_type, env):
    conn = sqlite3.connect(f'{env}_database.db')
    cursor = conn.cursor()

    slot_mapping = {
        'background': 'equipped_background',
        'title': 'equipped_title',
        'badge': 'equipped_badge',
        'header': 'equipped_header',
        'profile_color': 'equipped_profile_color'
    }
    if item_type in slot_mapping:
        cursor.execute(
            f'''
            UPDATE user_profile
            SET {slot_mapping[item_type]} = ?
            WHERE user_id = ?
            ''',
            (item_id, user_id)
        )
        # Mark item as equipped in user_items
        cursor.execute(
            '''
            UPDATE user_items
            SET equipped = TRUE
            WHERE user_id = ? AND item_id = ?
            ''',
            (user_id, item_id)
        )
    
    conn.commit()
    conn.close()

def user_owns_item(cursor, user_id, item_id, env):
    conn = sqlite3.connect(f'{env}_database.db')
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT 1 FROM user_items
        WHERE user_id = ? AND item_id = ?
        ''',
        (user_id, item_id)
    )
    items = cursor.fetchone() is not None
    conn.commit()
    conn.close()
    return items

def get_user_items(cursor, user_id, env):
    conn = sqlite3.connect(f'{env}_database.db')
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT ui.user_item_id, ui.item_id, ui.equipped, ui.aquired_date, 
               i.item_type, i.item_name, i.item_shop, i.description, i.rarity, i.price
        FROM user_items ui
        JOIN items i ON ui.item_id = i.item_id
        WHERE ui.user_id = ?
        ''',
        (user_id,)
    )
    items =  cursor.fetchall()
    conn.commit()
    conn.close()
    return items
  