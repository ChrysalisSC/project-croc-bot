type	name	tbl_name	rootpage	sql
table	users	users	2	CREATE TABLE users (
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
                    )
table	views	views	3	CREATE TABLE views (
                        view_id TEXT PRIMARY KEY,
                        view_registration TEXT,
                        channel_id INTEGER,
                        timeout_date TEXT,
                        disabled INTEGER DEFAULT 0      
                    )
index	sqlite_autoindex_views_1	views	4	NULL
table	wordle	wordle	5	CREATE TABLE wordle (
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
                )
table	items	items	6	CREATE TABLE items (
                    item_id INTEGER PRIMARY KEY,
                    item_type TEXT NOT NULL,  -- e.g., 'background', 'title', 'badge', 'header', 'profile_color'
                    item_name TEXT NOT NULL,
                    item_shop TEXT DEFAULT 'general',  -- e.g., 'general', 'fantasy', 'games'
                    description TEXT,
                    rarity TEXT,              -- e.g., 'common', 'rare', 'legendary'
                    price INTEGER DEFAULT 0   -- in currency, if applicable
                )
table	user_items	user_items	7	CREATE TABLE user_items (
                    user_item_id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    item_id INTEGER,
                    equipped BOOLEAN DEFAULT FALSE,  -- indicates if the item is currently equipped
                    aquired_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (item_id) REFERENCES items(item_id)
                )
table	user_profile	user_profile	8	CREATE TABLE user_profile (
                    user_id INTEGER PRIMARY KEY,
                    equipped_background INTEGER,
                    equipped_title INTEGER,
                    equipped_badge INTEGER,
                    equipped_header INTEGER,
                    equipped_profile_color INTEGER,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (equipped_background) REFERENCES items(item_id),
                    FOREIGN KEY (equipped_title) REFERENCES items(item_id),
                    FOREIGN KEY (equipped_badge) REFERENCES items(item_id),
                    FOREIGN KEY (equipped_header) REFERENCES items(item_id),
                    FOREIGN KEY (equipped_profile_color) REFERENCES items(item_id)
                )