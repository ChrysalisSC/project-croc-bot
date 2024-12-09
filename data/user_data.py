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
    try:
        cursor.execute('SELECT chats FROM users WHERE user_id = ?', (user_id,))
        chats = cursor.fetchone()[0]
        chats += 1
    except:
        chats = 1
    
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

    # Determine admin and booster status
    admin_status = 1 if member.guild_permissions.administrator else 0
    booster = 1 if member.premium_since is not None else 0

    conn = sqlite3.connect(f'{env}_database.db')
    cursor = conn.cursor()
    print("ADDED USERNAME: ", username)
    cursor.execute('''
        INSERT OR REPLACE INTO users 
        (user_id, username, approved, current_xp, level, total_xp, currency, admin_status, time_spent, chats, last_seen, booster)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, username, 1, 0, 1, 0, 0, admin_status, 0, 0, datetime.datetime.now(), booster))

    #user_id INTEGER PRIMARY KEY,
    #                equipped_title INTEGER,
     #               equipped_badge INTEGER,
     #               equipped_header INTEGER,
      #              equipped_profile_color INTEGER,
      #              intrest_1 TEXT,
     #               intrest_2 TEXT,
    #                intrest_3 TEXT,
     #               intrest_4 TEXT,
     #               intrest_5 TEXT,

    # Insert default entries in `user_profile` if they don't already exist
    cursor.execute('''
        INSERT OR IGNORE INTO user_profile 
        (user_id, equipped_title, equipped_badge, equipped_header, equipped_profile_color, interest_1, interest_2, interest_3, interest_4, interest_5) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, 200000, 600000, 100000, 400000, 300000, 300000, 300000, 300000, 300000))
    
    #add default items to user_items
    cursor.execute('''
        INSERT OR IGNORE INTO user_items 
        (user_id, item_id, equipped, aquired_date) 
        VALUES (?, ?, ?, ?)
    ''', (user_id, 200000, 1, datetime.datetime.now()))
    cursor.execute('''
        INSERT OR IGNORE INTO user_items 
        (user_id, item_id, equipped, aquired_date) 
        VALUES (?, ?, ?, ?)
    ''', (user_id, 600000, 1, datetime.datetime.now()))
    cursor.execute('''
        INSERT OR IGNORE INTO user_items 
        (user_id, item_id, equipped, aquired_date) 
        VALUES (?, ?, ?, ?)
    ''', (user_id, 100000, 1, datetime.datetime.now()))
    cursor.execute('''
        INSERT OR IGNORE INTO user_items 
        (user_id, item_id, equipped, aquired_date) 
        VALUES (?, ?, ?, ?)
    ''', (user_id, 400000, 1, datetime.datetime.now()))


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

def add_item_to_user(user_id, item_id, env):
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

def equip_item(user_id, item_id, item_type, env):
    conn = sqlite3.connect(f'{env}_database.db')
    cursor = conn.cursor()

    slot_mapping = {
        'title': 'equipped_title',
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

def user_owns_item(user_id, item_id, env):
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

def get_user_items(user_id, env):
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
  
def check_user_funds(user_id, env):
    conn = sqlite3.connect(f'{env}_database.db')
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT currency FROM users
        WHERE user_id = ?
        ''',
        (user_id,)
    )
    currency = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return currency

def add_user_funds(user_id, amount, env):
    conn = sqlite3.connect(f'{env}_database.db')
    cursor = conn.cursor()
    cursor.execute(
        '''
        UPDATE users
        SET currency = currency + ?
        WHERE user_id = ?
        ''',
        (amount, user_id)
    )
    conn.commit()
    conn.close()

def remove_user_funds(user_id, amount, env):
    conn = sqlite3.connect(f'{env}_database.db')
    cursor = conn.cursor()
    cursor.execute(
        '''
        UPDATE users
        SET currency = currency - ?
        WHERE user_id = ?
        ''',
        (amount, user_id)
    )
    conn.commit()
    conn.close()

def get_user_profile(user_id, env):
    connection = sqlite3.connect(f'{env}_database.db')
    cursor = connection.cursor()
    query = '''SELECT equipped_title, equipped_badge, equipped_header, equipped_profile_color, interest_1, interest_2, interest_3, interest_4, interest_5 
                FROM user_profile WHERE user_id = ?'''
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    connection.close()
    
    if result:
        keys = ['equipped_title', 'equipped_badge', 'equipped_header', 'equipped_profile_color', 'interest_1', 'interest_2', 'interest_3', 'interest_4', 'interest_5']
        return dict(zip(keys, result))
    return None

def get_owned_items(user_id, item_type, env):
    connection = sqlite3.connect(f'{env}_database.db')
    cursor = connection.cursor()
    query = '''SELECT items.item_id, items.item_name, items.price FROM items 
                JOIN user_items ON items.item_id = user_items.item_id
                WHERE user_items.user_id = ? AND items.item_type = ?'''
    cursor.execute(query, (user_id, item_type))
    items = cursor.fetchall()
    connection.close()
    return items


def get_all_owned_items(user_id, item_type, env):
    connection = sqlite3.connect(f'{env}_database.db')
    cursor = connection.cursor()
    # Get all items that are owned by the user, match item type, and include description from items table
    query = '''SELECT items.item_id, items.item_name, items.price, items.description 
                FROM items 
                JOIN user_items ON items.item_id = user_items.item_id 
                WHERE user_items.user_id = ? AND items.item_type = ?'''

    cursor.execute(query, (user_id, item_type))
    items = cursor.fetchall()
    connection.close()
    
    # Format the result to include equipped status and description
    formatted_items = [
        {
            "item_id": item[0], 
            "item_name": item[1], 
            "price": item[2], 
            "description": item[3]  # Include description from the items table
        } 
        for item in items
    ]
   
    return formatted_items

async def change_equipped_item( user_id, item_type, item_id, env):
  
    connection = sqlite3.connect(f'{env}_database.db')
    cursor = connection.cursor()
    column_name = f"equipped_{item_type}"
    query = f"UPDATE user_profile SET {column_name} = ? WHERE user_id = ?"
    cursor.execute(query, (item_id, user_id))
    connection.commit()

    #before changing see which one is equpped == 1 and is the 
    item_id_str = str(item_id)

    # Step 1: Query all equipped items for the user
    cursor.execute("SELECT item_id FROM user_items WHERE user_id = ? AND equipped = 1", (user_id,))
    equipped_items = cursor.fetchall()

    # Step 2: Iterate over the equipped items and update the one that matches the first digit of item_id
    for equipped_item in equipped_items:
        equipped_item_id = equipped_item[0]
        
        # Check if the first digit matches
        if str(equipped_item_id)[0] == item_id_str[0]:
            # Step 3: Update the matched item to "not equipped" (equipped = 0)
            cursor.execute("UPDATE user_items SET equipped = 0 WHERE user_id = ? AND item_id = ?", (user_id, equipped_item_id))
            connection.commit()
            
            # Break after updating the matched item
            break

    # Step 4: Update the selected item to "equipped" (equipped = 1)
    cursor.execute("UPDATE user_items SET equipped = 1 WHERE user_id = ? AND item_id = ?", (user_id, item_id))
    connection.commit()
    connection.close()


def get_items_by_ids(item_ids, env):
    connection = sqlite3.connect(f'{env}_database.db')
    cursor = connection.cursor()
    if not item_ids:
        print("No item IDs provided.")
        return []

    # Prepare query with placeholders for the IDs
    placeholders = ', '.join('?' for _ in item_ids)
    query = f"SELECT * FROM items WHERE item_id IN ({placeholders})"
    
    try:
        # Execute the query
        cursor.execute(query, item_ids)
        rows = cursor.fetchall()
        
        # Fetch column names for creating dictionaries
        column_names = [description[0] for description in cursor.description]
        
        # Transform rows into a list of dictionaries
        items = [dict(zip(column_names, row)) for row in rows]
        return items
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return []
    finally:
        # Always close the connection
        connection.close()


async def update_user_interests(user_id, interest_ids, env):
    connection = sqlite3.connect(f'{env}_database.db')
    cursor = connection.cursor()
   
    # Pad with `None` if fewer than 5 interests are selected
    interests = interest_ids + [None] * (5 - len(interest_ids))

    try:
        cursor.execute(
            '''
            UPDATE user_profile
            SET interest_1 = ?,  interest_2 = ?,  interest_3 = ?,  interest_4 = ?,  interest_5 = ?
            WHERE user_id = ?
            ''',
            (*interests, user_id)
        )
        connection.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        connection.close()

def get_all_profile_data(user_id, env):
    #get data from the user table and user_profile table
    connection = sqlite3.connect(f'{env}_database.db')
    cursor = connection.cursor()
    query = '''SELECT * FROM users WHERE user_id = ?'''
    cursor.execute(query, (user_id,))
    user_data = cursor.fetchone()
    query = '''SELECT * FROM user_profile WHERE user_id = ?'''
    cursor.execute(query, (user_id,))
    profile_data = cursor.fetchone()
    connection.close()
    return user_data, profile_data

def check_user_item(user_id, item_id, env):
    connection = sqlite3.connect(f'{env}_database.db')
    cursor = connection.cursor()
    query = '''SELECT * FROM user_items WHERE user_id = ? AND item_id = ?'''
    cursor.execute(query, (user_id, item_id))
    result = cursor.fetchone()
    connection.close()
    return result


def lockout_user(user_id, lockout, env):
    add_user_to_lockouts(user_id, env)
    if not (1 <= lockout <= 10):
        raise ValueError("Invalid lockout number. It must be between 1 and 10.")

    connection = sqlite3.connect(f'{env}_database.db')
    cursor = connection.cursor()
    
    # Dynamically build the query for the specified lockout column
    query = f'UPDATE lockouts SET lockout_{lockout} = 1 WHERE user_id = ?'
    
    cursor.execute(query, (user_id,))
    connection.commit()
    connection.close()

def is_user_lockout(user_id, lockout, env):
    add_user_to_lockouts(user_id, env)
    if not (1 <= lockout <= 10):
        raise ValueError("Invalid lockout number. It must be between 1 and 10.")

    connection = sqlite3.connect(f'{env}_database.db')
    cursor = connection.cursor()
    
    # Dynamically build the query for the specified lockout column
    query = f'SELECT lockout_{lockout} FROM lockouts WHERE user_id = ?'
    
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    connection.close()
    
    return result[0] == 1 if result else False

def add_user_to_lockouts(user_id, env):
    connection = sqlite3.connect(f'{env}_database.db')
    cursor = connection.cursor()
    
    cursor.execute('''
        INSERT OR IGNORE INTO lockouts (user_id)
        VALUES (?)
    ''', (user_id,))
    
    connection.commit()
    connection.close()

def reset_lockouts(env):
    connection = sqlite3.connect(f'{env}_database.db')
    cursor = connection.cursor()
    
    cursor.execute('''
        UPDATE lockouts
        SET lockout_1 = 0, lockout_2 = 0, lockout_3 = 0, lockout_4 = 0, lockout_5 = 0,
            lockout_6 = 0, lockout_7 = 0, lockout_8 = 0, lockout_9 = 0, lockout_10 = 0
    ''')
    
    connection.commit()
    connection.close()


def get_leaderboard(env, limit=10):
        print("GETTING LEADERBOARD")
        print("ENV: ", env)
        """Fetch the top users by total XP from the database."""
        connection = sqlite3.connect(f'{env}_database.db')
        cursor = connection.cursor()
        cursor.execute(
            '''
            SELECT user_id, username, total_xp, level 
            FROM users 
            ORDER BY total_xp DESC 
            LIMIT ?
            ''', (limit,)
        )
        leaderboard = cursor.fetchall()
        connection.close()
        return leaderboard


def fetch_leaderboard_data(env, limit=10):
    """Fetch the top users by total XP from the database."""
    connection = sqlite3.connect(f'{env}_database.db')
    cursor = connection.cursor()
    cursor.execute(
        '''
        SELECT username, total_xp, level, "default_header.jpg" AS header_image_path, "default_profile.jpg" AS profile_picture_path 
        FROM users 
        ORDER BY total_xp DESC 
        LIMIT ?
        ''', (limit,)
    )
    leaderboard = cursor.fetchall()
    connection.close()
    return [
        {
            "header_image_path": row[3],
            "name": row[0],
            "title": f"Level {row[2]} Player",
            "level": row[2],
            "xp": row[1],
            "profile_picture_path": row[4]
        }
        for row in leaderboard
    ]


def get_broadcasts_status(user_id, env):
    #select tthe broadcast col from users
    connection = sqlite3.connect(f'{env}_database.db')
    cursor = connection.cursor()
    query = '''SELECT broadcast FROM users WHERE user_id = ?'''
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    connection.close()
    return result[0] if result else False

def set_broadcasts_status(user_id, status, env):
    connection = sqlite3.connect(f'{env}_database.db')
    cursor = connection.cursor()
    query = '''UPDATE users SET broadcast = ? WHERE user_id = ?'''
    cursor.execute(query, (status, user_id))
    connection.commit()
    connection.close()