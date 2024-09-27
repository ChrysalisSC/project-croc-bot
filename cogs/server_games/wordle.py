import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import utils.helpers as helpers
import random
from PIL import Image, ImageDraw, ImageFont





class Wordle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.wordle_answers = [
            "apple", "baker", "chair", "dance", "eagle", 
            "flint", "grape", "house", "jumpy", "knack", 
            "lemon", "mouse", "noble", "plumb", "quilt", 
            "river", "shine", "table", "umber", "vivid", 
            "waltz", "yacht", "zesty", "brick", "cloud", 
            "dough", "flame", "globe", "hasty", "ivory", 
            "jewel", "kiosk"
        ]
        self.database = f"{self.bot.env}_database.db"

    async def start_wordle(self, thread, user_id):
        # Check if the user already has a game of Wordle in progress
        data = self.get_wordle_data(user_id)

        if data:
            word = data[2]
            attempts = data[3]
            previous_guesses = data[4:]  # Assign the remaining elements of data to previous_guesses

            if word == "" or attempts == 0:
                # Start a new game if the current word is empty
                word = self.generate_word()
                attempts = 6
                previous_guesses = [""] * 6
                self.update_wordle_data(user_id, thread.id, word, attempts, previous_guesses)
               
                message = "Let's play Wordle! You have 6 attempts to guess a 5-letter word. Use the command `/guess <word>` to make a guess."
            else:
                # Inform the user that they are already playing
                message = f"You are already playing Wordle. You have {attempts} attempts left."
        else:
            # If no data exists, start a new game
            word = self.generate_word()
            attempts = 6
            previous_guesses = [""] * 6
            self.insert_wordle_data(user_id, thread.id, word, attempts, previous_guesses)
            message = "Let's play Wordle! You have 6 attempts to guess a 5-letter word. Use the command `/guess <word>` to make a guess."

        # Create the game instructions embed
        embed = discord.Embed(
            title="🟩 Welcome to Wordle! 🟩",
            description="Guess the 5-letter word in 6 tries!\n"
                        "Each guess must be a valid 5-letter word. \n\n"
                        "🟩 means the letter is correct and in the correct position. \n"
                        "🟨 means the letter is correct but in the wrong position. \n"
                        "⬜ means the letter is not in the word.\n\n"
                        "Have fun!",
            color=0x00FF00
        )
        embed.add_field(
            name="How to Play",
            value="1. Type your guess in the thread.\n"
                "2. You will receive feedback with colored boxes.\n"
                "3. Keep guessing until you find the word or run out of attempts!",
            inline=False
        )
        embed.add_field(name=message, value="Good luck!", inline=False)

        await thread.send(embed=embed)

    # Function to insert user data into the Wordle table
    def insert_wordle_data(self, user_id, thread_id, word, attempts, guesses):
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        c.execute("INSERT INTO wordle (user_id, thread_id, word, attempts, guess_1, guess_2, guess_3, guess_4, guess_5, guess_6) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (user_id, thread_id, word, attempts, *guesses))
        conn.commit()
        conn.close()

    # Function to retrieve user data from the Wordle table
    def get_wordle_data(self, user_id):
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        c.execute("SELECT * FROM wordle WHERE user_id=?", (user_id,))
        data = c.fetchone()
        conn.close()
        return data

    # Function to update user data in the Wordle table
    def update_wordle_data(self, user_id,thread_id, word, attempts, guesses):
        conn = sqlite3.connect(self.database)
        c = conn.cursor()
        c.execute("UPDATE wordle SET word=?, thread_id=?, attempts=?, guess_1=?, guess_2=?, guess_3=?, guess_4=?, guess_5=?, guess_6=? WHERE user_id=?",
                (word, thread_id, attempts, *guesses, user_id))
        conn.commit()
        conn.close()

    # Function to generate a random word for Wordle
    def generate_word(self):
        word_list = self.wordle_answers
        return random.choice(word_list)

    # Function to check if the guess is valid
    def is_valid_guess(self, guess):
        return len(guess) == 5 and guess.isalpha()
    
    async def process_guess(self, user, guess_word: str, interaction: discord.Interaction):
        user_id = user.id
        thread = interaction.channel
        data = self.get_wordle_data(user_id)
        print(data)
        if not data:
            await interaction.response.send_message("You haven't started playing Wordle. Use the command `!wordle` to start a new game.")
            return

        word = data[2]
        thread_id = data[1] 
        attempts = data[3]
        previous_guesses = list(data[4:])
        if attempts <= 0:
            await interaction.response.send_message("You have no attempts left. The word was: " + word)
            return

        if not self.is_valid_guess(guess_word):
            await interaction.response.send_message("Invalid guess. Guess must be a 5-letter word with no spaces or special characters.")
            return

        if guess_word in previous_guesses:
            await interaction.response.send_message("You have already guessed this word. Please guess a different word.")
            return
        print(previous_guesses)
        previous_guesses[6 - attempts] = guess_word

        bulls, cows = 0, 0
        for i in range(5):
            if guess_word[i] == word[i]:
                bulls += 1
            elif guess_word[i] in word:
                cows += 1
        
        
        await self.create_wordle_grid(word, previous_guesses)

        
        
        self.update_wordle_data(user_id,thread_id, word, attempts - 1, previous_guesses)
        embed = discord.Embed(
            
            title=f"Wordle Game",
            description=f"",
            color=0xFFFFFF
            
        )
        file = discord.File(f'images/games/wordle/wordle_grid.png')
        embed.set_image(url=f"attachment://{file.filename}")
        embed.add_field(name=f"Guess: {guess_word}", value=f"Bulls: {bulls}, Cows: {cows}, Attempts left: {attempts - 1}", inline=False)
       
        if guess_word == word:
            # User has guessed the word correctly
            embed.add_field(name=f"Congratulations!", value=f"You guessed the word '{word}' in {6 - attempts} attempts.")
            
            # Reset the user's Wordle data to start a new game
            new_word = self.generate_word()  # Get a new word for the next game
            attempts = 6  # Reset attempts
            previous_guesses = [""] * 6  # Clear previous guesses

            # Update the Wordle data for the user with the new game
            self.update_wordle_data(user_id, '', new_word, attempts, previous_guesses)
            
            # Optionally inform the user about starting a new game
            embed.add_field(name="New Game", value="A new game of Wordle has started! You have 6 attempts to guess the new 5-letter word. Use the command `/guess <word>` to make a guess.", inline=False)
            await interaction.response.send_message(embed=embed, file=file)
            
           

        elif attempts - 1 == 0:
            # User has run out of attempts
            embed.set_footer(text=f"Out of attempts! The word was '{word}'.")
            
            # Reset the user's Wordle data to start a new game
            new_word = self.generate_word()  # Get a new word for the next game
            attempts = 6  # Reset attempts
            previous_guesses = [""] * 6  # Clear previous guesses

            # Update the Wordle data for the user with the new game
            self.update_wordle_data(user_id, '', new_word, attempts, previous_guesses)
            
            embed.add_field(name="New Game", value="A new game of Wordle has started! You have 6 attempts to guess the new 5-letter word. Use the command `/guess <word>` to make a guess.", inline=False)
            await interaction.response.send_message(embed=embed, file=file)
            
 
           
        else:
            await interaction.response.send_message(embed=embed, file =file)

  

    async def create_wordle_grid(self, correct_word, words):
            BOX_SIZE = 40  # Size of each box in pixels
        
            MARGIN = 20  # Margin around the grid
            BG_COLOR = "white"  # Background color
            BOX_COLOR = "black"  # Box color
            LINE_WIDTH = 2  # Width of grid lines
            TEXT_COLOR = "white"  # Text color
            TEXT_FONT = ImageFont.truetype("fonts/Nunito/Nunito-Light.ttf", 30)  # Font for the text

            # Calculate image size
            image_width = 248
            image_height = 300

            # Create a new image
            image = Image.new("RGB", (image_width, image_height), color=BG_COLOR)
            draw = ImageDraw.Draw(image)

            # Draw grid lines 5 by 6
            for row in range(6):
                for col in range(5):
                    x1 = MARGIN + ((BOX_SIZE + LINE_WIDTH) * col)
                    y1 = MARGIN + ((BOX_SIZE + LINE_WIDTH) * row)
                    x2 = x1 + BOX_SIZE 
                    y2 = y1 + BOX_SIZE
                    draw.rectangle([(x1, y1 + 20), (x2, y2+ 20)], fill="white", outline="black")
            
            # Manually place the text "WORDLE" at the top
            text = "WORDLE"
            WORDLE_FONT = ImageFont.truetype("fonts/Nunito/Nunito-Light.ttf", 36)  # Font for the text
            text_x = 45  # Manually adjust the x-coordinate
            text_y = 0  # Manually adjust the y-coordinate
            draw.text((text_x, text_y), text, fill="black", font=WORDLE_FONT)

            
            words = [word.upper() for word in words if word != ""]
            length = len(words)
            correct_word = correct_word.upper()
        
            if length == 0:
                image.save("images/games/wordle/wordle_grid.png")
                return None
            
            
            for row in range(0,length):
                for col in range(5):
                    x1 = MARGIN + ((BOX_SIZE + LINE_WIDTH) * col)
                    y1 = MARGIN + ((BOX_SIZE + LINE_WIDTH) * row)
                    x2 = x1 + BOX_SIZE 
                    y2 = y1 + BOX_SIZE
                

                    # Check if the letter is in the correct word\
                    #print(words[row][col], correct_word[col])
                    if words[row][col] in str(correct_word):
                        # Check if it's in the correct position
                        
                        if correct_word[col] == words[row][col]:
                            box_color =	(108,169,101)
                        else:
                            box_color = (200,182,83)
                    else:
                        box_color = (120,124,127)

                    draw.rectangle([(x1, y1 + 20), (x2, y2+ 20)], fill=box_color, outline=BOX_COLOR)
                    text = f"{words[row][col]}"
                    text_width = draw.textlength(text, font=WORDLE_FONT)
                    text_x = x1 + (BOX_SIZE - text_width) / 2
                    text_y = y1  - 2 +  (BOX_SIZE) / 2

                    draw.text((text_x, text_y), text, fill=TEXT_COLOR, font=WORDLE_FONT)
                
            # Save the image with border
            image.save("images/games/wordle/wordle_grid.png")
        
            return None


# Setup function to add the cog to the bot

async def setup(bot):
    #name of your log(name of cog, print_info)
    helpers.log("EXAMPLE", "Setting up Example cog...")
    await bot.add_cog(Wordle(bot))
   