"""


"""

import logging
import random 
import discord
from discord.ext import commands
from datetime import datetime, timezone
import pytz
import os
import json
import sqlite3

from utils.helpers import log, get_time

def add_user_to_user_table(env,user_id, username):
    #get current time
    last_seen = get_time()
    conn = sqlite3.connect(f"{env}_database.db")
    c = conn.cursor()
    c.execute('''INSERT OR IGNORE INTO users (user_id, username, xp, level, total_xp, arcanum, admin_status, time_spent, last_seen) VALUES (?, ?, 0, 1, 0, 0, 0, 0, ?)''', (user_id, username, last_seen))
    conn.commit()
    conn.close()

