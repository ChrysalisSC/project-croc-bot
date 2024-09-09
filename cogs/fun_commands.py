import discord
import json
import sqlite3
import logging
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timezone, timedelta
import random
import requests


class funcommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    def get_username(self, user_id):
        print("ID", user_id)
        member = self.bot.get_user(user_id)
        print("MEMBER", member)
        if member:
            return member.display_name
        else:
            return "Unknown"

    
    @app_commands.command(
        name="roll",
        description="Roll a number 1-6 or specify a range"
    )
    async def roll_dice(self, interaction: discord.Integration, number: int = None):
        user_id = interaction.user.id
        if number == None:
            number = 6
            roll_result = random.randint(1, 6)
        else:
            roll_result = random.randint(1, number)

        dice_emoji = "🎲"

        # Sending the result to the channel
        await interaction.response.send_message(f"{dice_emoji} {self.get_username(user_id)} rolled a {number} sided dice and got **{roll_result}**!")
    
    @app_commands.command(
        name="flip",
        description="Flip a coin"
    )
    async def flip_coin(self, interaction: discord.Integration):
        user_id = interaction.user.id
        result = random.choice(["Heads", "Tails"])
        await interaction.response.send_message(f"🪙 {self.get_username(user_id)} flipped a coin and landed on: **{result}**")
        
    @app_commands.command(
        name="magicball",
        description="Ask the magic 8-ball a question"
    )
    async def eight_ball(self, interaction: discord.Integration, question:str):
        responses = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes – definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful."
        ]
        response = random.choice(responses)
        await interaction.response.send_message(f"**Question:** {question}\n**Answer:** {response}")

    
    @app_commands.command(
        name="anime",
        description="Anime Commands"
    )
    @app_commands.choices(choices=[
        app_commands.Choice(name="Qoute", value="qoute"),
        app_commands.Choice(name="UWU", value="uwu"),
        ])
    async def anime(self, interaction: discord.Integration, choices: app_commands.Choice[str]):
        print("CHOICE",choices )
        if choices.value == "qoute":
            response = requests.get('https://animechan.xyz/api/random')
            quote = response.json()
            await interaction.response.send_message(f"**Quote**: {quote['quote']} \n \n**Anime:** {quote['anime']}\n**Character:** {quote['character']}")
        if choices.value == 'uwu':
            await interaction.response.send_message("UWU!")

    
    @app_commands.command(
        name="fortunecookie",
        description="Generates and displays a random fortune cookie message"
    )
    async def fortune_cookie(self, interaction: discord.Integration):
        # List of fortune cookie messages
        fortune_messages = [
            "You will soon experience great joy.",
            "Good things are coming your way.",
            "Your hard work will pay off soon.",
            "A surprise awaits you in the near future.",
            "Today is a lucky day for you.",
            "Your kindness will be rewarded.",
            "An exciting opportunity will come your way.",
            "Believe in yourself, and good things will happen.",
            "You will make a new friend today.",
            "Happiness is just around the corner.",
            "Your future looks bright.",
            "Someone special will enter your life soon.",
            "You will find success in your endeavors.",
            "Trust your instincts; they will guide you well.",
            "Adventure awaits you.",
            "You will achieve your goals with determination.",
            "Luck is on your side today.",
            "You will overcome any obstacles in your path.",
            "Stay positive, and good things will come to you.",
            "Your creativity will shine in the days ahead.",
            "The best is yet to come.",
            "You are capable of great things.",
            "Your future is full of promise.",
            "Your dreams will come true with persistence.",
            "You will find love in unexpected places.",
            "Your generosity will be repaid tenfold.",
            "Success is within your reach.",
            "Your positive attitude will lead to success.",
            "Great opportunities are on the horizon.",
            "Your creativity knows no bounds.",
            "A new adventure awaits you.",
            "You are destined for greatness.",
            "Your intuition will guide you wisely.",
            "Good luck will follow you wherever you go.",
            "You have the power to make a difference.",
            "Your hard work will be recognized and rewarded.",
            "You are surrounded by love and happiness.",
            "Every day brings new opportunities for growth.",
            "You will find peace and contentment in the simple things.",
            "Your future is bright with possibilities.",
            "Your determination will lead you to success.",
            "You are stronger than you realize.",
            "Your kindness will inspire others.",
            "A wish you made long ago will soon come true.",
            "Your optimism will lead you to victory.",
            "You will achieve your goals with perseverance.",
            "You are blessed with many talents.",
            "Trust in yourself, and you will achieve great things.",
            "The journey of a thousand miles begins with a single step.",
            "Your life will be filled with joy and fulfillment."
        ]
        
        # Selecting a random fortune message
        fortune = random.choice(fortune_messages)
        
        # Sending the fortune message to the Discord channel
        await interaction.response.send_message(f"🥠 **Fortune Cookie:** *{fortune}*")

    
    @app_commands.command(
        name="randomfact",
        description="Fetches a random useless fact"
    )
    async def random_facte(self, interaction: discord.Integration):
        url = f"https://uselessfacts.jsph.pl/api/v2/facts/random"
        response = requests.get(url)
        if response.status_code == 200:
            fact = response.json()["text"]
            await interaction.response.send_message(f"📜 **Fact:** {fact}")
        else:
            await interaction.response.send_message("Failed to fetch a random fact. Please try again later.")

    @app_commands.command(
        name="insult",
        description="Generates a random insult"
    )
    async def generate_insult(self, interaction: discord.Integration, member: discord.Member = None):
        if member == None:
            response = requests.get("https://insult.mattbas.org/api/insult.txt")
            if response.status_code == 200:
                insult = response.text
                await interaction.response.send_message(f"💥 {insult}")
            else:
                await interaction.response.send_message("Failed to generate an insult. Please try again later.")
        else:
            response = requests.get(f"https://insult.mattbas.org/api/insult.txt?who= ")
            if response.status_code == 200:
                insult = response.text
                await interaction.response.send_message(f"💥 {member.mention}{insult}")
            else:
                await interaction.response.send_message("Failed to generate an insult. Please try again later.")

    @app_commands.command(
        name="gameoftheday",
        description="Fetches the game of the day from Connection Games API"
    )
    async def game_of_the_day(self, interaction: discord.Integration):
        response = requests.get("https://connection.games/api/v1/today")
        if response.status_code == 200:
            game_data = response.json()
            game_name = game_data.get("game_name")
            game_description = game_data.get("game_description")
            await interaction.response.send_message(f"🎮 Game of the Day: {game_name}\nDescription: {game_description}")
        else:
            await interaction.response.send_message("Failed to fetch the game of the day. Please try again later.")

    @app_commands.command(
        name="compliment",
        description="Generates a random compliment"
    )
    async def generate_compliment(self, interaction: discord.Integration, member: discord.Member = None):
        with open ("data/compliments.json", "r") as file:
            COMPLEMENTS = json.load(file)
        compliment = random.choice(COMPLEMENTS)
        if member is None:
             await interaction.response.send_message(f"💖 {compliment}")
        else:
             await interaction.response.send_message(f"💖 {member.mention}, {compliment}")

async def setup(bot):
    await bot.add_cog(funcommands(bot))