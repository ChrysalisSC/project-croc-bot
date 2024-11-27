import sqlite3
import json
import math
import datetime
import time
import os

import utils.helpers as helpers

def start_database(env):
    conn = sqlite3.connect(f'{env}_database.db')
    cursor = conn.cursor()

    # Create a table to store user data
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        approved BOOLEAN DEFAULT FALSE,
                        current_xp INTEGER DEFAULT 0,
                        level INTEGER DEFAULT 1,
                        total_xp INTEGER DEFAULT 0,
                        currency INTEGER DEFAULT 0,
                        admin_status BOOLEAN DEFAULT FALSE,
                        time_spent INTEGER DEFAULT 0,
                        chats Integer DEFAULT 0,
                        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        booster BOOLEAN DEFAULT FALSE
                    )''')
    # create the views table

    cursor.execute('''CREATE TABLE IF NOT EXISTS views (
                        view_id TEXT PRIMARY KEY,
                        view_registration TEXT,
                        channel_id INTEGER,
                        timeout_date TEXT,
                        disabled INTEGER DEFAULT 0      
                    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS wordle (
                    user_id INTEGER,
                    thread_id INTEGER,
                    word TEXT,
                    attempts INTEGER,
                    guess_1 TEXT,
                    guess_2 TEXT,
                    guess_3 TEXT,
                    guess_4 TEXT,
                    guess_5 TEXT,
                    guess_6 TEXT
                )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS items (
                    item_id INTEGER PRIMARY KEY,
                    item_type TEXT NOT NULL,  -- e.g., 'title', 'badge', 'header', 'profile_color'
                    item_name TEXT NOT NULL,
                    item_shop TEXT DEFAULT 'general',  -- e.g., 'general', 'fantasy', 'games'
                    description TEXT,
                    rarity TEXT,              -- e.g., 'common', 'rare', 'legendary'
                    price INTEGER DEFAULT 0   -- in currency, if applicable
                )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS user_items (
                    user_item_id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    item_id INTEGER,
                    equipped BOOLEAN DEFAULT FALSE,  -- indicates if the item is currently equipped
                    aquired_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (item_id) REFERENCES items(item_id)
                )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS user_profile (
                    user_id INTEGER PRIMARY KEY,
                    equipped_title INTEGER,
                    equipped_badge INTEGER,
                    equipped_header INTEGER,
                    equipped_profile_color INTEGER,
                    interest_1 INTEGER,
                    interest_2 INTEGER,
                    interest_3 INTEGER,
                    interest_4 INTEGER,
                    interest_5 INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (equipped_title) REFERENCES items(item_id),
                    FOREIGN KEY (equipped_badge) REFERENCES items(item_id),
                    FOREIGN KEY (equipped_header) REFERENCES items(item_id),
                    FOREIGN KEY (equipped_profile_color) REFERENCES items(item_id)
                )''')

    #headers  100000 - 199999
    #titles   200000 - 299999
    #intrests 300000 - 399999
    #color    400000 - 499999
    #badges   600000 - 699999

    #insert default items
    cursor.execute(
        '''
        INSERT OR IGNORE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (100000, 'header', 'Default Header', 'default', 'The default header for your profile.', 'common', 0)
    )

    cursor.execute(
        '''
        INSERT OR IGNORE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (200000, 'title', 'Newcomer', 'default', 'The default title for your profile.', 'common', 0)
    )

    cursor.execute(
        '''
        INSERT OR REPLACE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (400000, 'profile_color', 'white', 'default', 'white.', 'common', 0)
    )

    cursor.execute(
        '''
        INSERT OR IGNORE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (600000, 'badge', 'Starting Out', 'default', 'The secret of getting ahead is getting started', 'common', 0)
    )


    #intrests
    cursor.execute(
        '''
        INSERT OR IGNORE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (300000, 'interest', 'NONE', 'interest', 'You love gathering rare items and treasures.', 'common', 0)
    )
    
    cursor.execute(
        '''
        INSERT OR IGNORE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (300001, 'interest', 'Collector', 'interest', 'You love gathering rare items and treasures.', 'common', 0)
    )

    cursor.execute(
        '''
        INSERT OR IGNORE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (300002, 'interest', 'Dreamer', 'interest', 'Your imagination knows no bounds.', 'common', 0)
    )

    cursor.execute(
        '''
        INSERT OR IGNORE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (300003, 'interest', 'Innovator', 'interest', 'You thrive on creating and building something new.', 'common', 0)
    )

    cursor.execute(
        '''
        INSERT OR IGNORE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (300004, 'interest', 'Foodie', 'interest', 'Exploring the world through its flavors is your passion.', 'common', 0)
    )

    cursor.execute(
        '''
        INSERT OR IGNORE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (300005, 'interest', 'Storyteller', 'interest', 'Every experience is a tale worth sharing.', 'common', 0)
    )

    cursor.execute(
        '''
        INSERT OR IGNORE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (300006, 'interest', 'Strategist', 'interest', 'You see life as a puzzle waiting to be solved.', 'common', 0)
    )

    cursor.execute(
        '''
        INSERT OR IGNORE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (300007, 'interest', 'Guardian', 'interest', 'You protect what you love with unwavering strength.', 'common', 0)
    )

    cursor.execute(
        '''
        INSERT OR IGNORE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (300008, 'interest', 'Artist', 'interest', 'The world is your canvas, and you create beauty wherever you go.', 'common', 0)
    )

    cursor.execute(
        '''
        INSERT OR IGNORE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (300009, 'interest', 'Leader', 'interest', 'You inspire others to follow their dreams.', 'common', 0)
    )

    cursor.execute(
        '''
        INSERT OR IGNORE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (300010, 'interest', 'Visionary', 'interest', 'You see potential in places others might overlook.', 'common', 0)
    )

    cursor.execute(
        '''
        INSERT OR IGNORE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (300011, 'interest', 'Joker', 'interest', 'You bring laughter wherever you go.', 'common', 0)
    )

    cursor.execute(
        '''
        INSERT OR IGNORE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (300012, 'interest', 'Gamer', 'interest', 'You find joy in conquering virtual worlds.', 'common', 0)
    )

    cursor.execute(
        '''
        INSERT OR IGNORE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (300013, 'interest', 'Music', 'interest', 'Your life has a soundtrack for every moment.', 'common', 0)
    )

    cursor.execute(
        '''
        INSERT OR IGNORE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (300014, 'interest', 'Bookworm', 'interest', 'You find magic between the pages of a good story.', 'common', 0)
    )

    cursor.execute(
        '''
        INSERT OR IGNORE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (300015, 'interest', 'Animal Lover', 'interest', 'You feel happiest when surrounded by animals.', 'common', 0)
    )

    cursor.execute(
        '''
        INSERT OR IGNORE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (300016, 'interest', 'Coffee Enthusiast', 'interest', 'Your day doesn’t start until the first sip of coffee.', 'common', 0)
    )

    cursor.execute(
        '''
        INSERT OR IGNORE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (300017, 'interest', 'Movies', 'interest', 'You’re always ready to recommend a good film.', 'common', 0)
    )

    cursor.execute(
        '''
        INSERT OR IGNORE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (300018, 'interest', 'Sports', 'interest', 'You’re always cheering on your favorite team.', 'common', 0)
    )



    #stores!
  

    #arcane Store
    cursor.execute(
        '''
        INSERT OR IGNORE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (100100, 'header', 'Arcane Survivor Jayce', 'arcane', 'I fight for a brighter tomorrow.', 'common', 200)
    )
    cursor.execute(
        '''
        INSERT OR IGNORE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (100101, 'header', 'Arcane Caitlyn', 'arcane', 'To be the best hunter, you have to be able to think like your prey.', 'common', 200)
    )
    cursor.execute(
        '''
        INSERT OR IGNORE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (100102, 'header', 'Arcane Jinx', 'arcane', 'Volatile explosives are a girls best friend!.', 'common', 200)
    )
    cursor.execute(
        '''
        INSERT OR IGNORE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (100103, 'header', 'Arcane VI', 'arcane', '"Punch first. Ask questions while punching.', 'common', 200)
    )
    cursor.execute(
        '''
        INSERT OR IGNORE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (100104, 'header', 'Arcane Ekko', 'arcane', 'Its not how much time you have, its how you use it.', 'common', 200)
    )

    #destiny collectioon
    cursor.execute(
        '''
        INSERT OR REPLACE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (100200, 'header', 'Cayde-6', 'destiny', 'Hey, Hunter, come back to recharge?', 'common', 200)
    )
    cursor.execute(
        '''
        INSERT OR REPLACE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
         (100201, 'header', 'The Witch Queen', 'destiny', 'I am Sathona, middle daughter of the dead king', 'common', 200)
    )
    cursor.execute(
        '''
        INSERT OR REPLACE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (100202, 'header', 'The Witness', 'destiny', 'I will shape you into perfection yet.', 'common', 200)
    )
    cursor.execute(
        '''
        INSERT OR REPLACE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (100203, 'header', 'The Traveler', 'destiny', 'Yes, Guardian. What do you need?', 'common', 200)
    )
    cursor.execute(
        '''
        INSERT OR REPLACE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (200200, 'title', 'The Traveler', 'destiny', 'Yes, Guardian. What do you need?', 'common', 100)
    )

    cursor.execute(
        '''
        INSERT OR REPLACE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (200201, 'title', 'Hunter', 'destiny', 'Yes, Guardian. What do you need?', 'common', 100)
    )

    cursor.execute(
        '''
        INSERT OR REPLACE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (200202, 'title', 'Warlock', 'destiny', 'Yes, Guardian. What do you need?', 'common', 100)
    )

    cursor.execute(
        '''
        INSERT OR REPLACE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (200203, 'title', 'Almighty', 'destiny', 'Yes, Guardian. What do you need?', 'common', 100)
    )

    cursor.execute(
        '''
        INSERT OR REPLACE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (200204, 'title', 'Titan', 'destiny', 'Yes, Guardian. What do you need?', 'common', 100)
    )

    cursor.execute(
        '''
        INSERT OR REPLACE INTO items (item_id, item_type, item_name, item_shop, description, rarity, price)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''',
        (200205, 'title', 'Forsaken', 'destiny', 'Yes, Guardian. What do you need?', 'common', 100)
    )
  







   
    
    print("DONE!")
    # Commit the changes and close the connection
    print("Database created successfully")
    conn.commit()
    conn.close()
    print("Connection closed")
    return True
