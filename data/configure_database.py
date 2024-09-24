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
                        xp INTEGER DEFAULT 0,
                        level INTEGER DEFAULT 1,
                        total_xp INTEGER DEFAULT 0,
                        currency INTEGER DEFAULT 0,
                        admin_status BOOLEAN DEFAULT FALSE,
                        time_spent INTEGER DEFAULT 0,
                        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )''')
    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    return True
