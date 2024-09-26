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
                        current_xp INTEGER DEFAULT 0,
                        level INTEGER DEFAULT 1,
                        total_xp INTEGER DEFAULT 0,
                        currency INTEGER DEFAULT 0,
                        admin_status BOOLEAN DEFAULT FALSE,
                        time_spent INTEGER DEFAULT 0,
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
    # Commit the changes and close the connection
    #print("Database created successfully")
    conn.commit()
    conn.close()
    return True
