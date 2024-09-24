import requests
from bs4 import BeautifulSoup
import pytz



import discord
from discord.ext import commands
from discord import app_commands

import utils.helpers as helpers

class Fantasy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.timezone = pytz.timezone("America/New_York")  
        self.fantasy_update_task.start()  # Start the task when the cog is loaded


    def parse_fantasy_data(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        
        match_results = []
        matches_list = soup.find('ul', class_='ss ss-7')
        # Iterate through each 'li' element within the 'ul'
        for match in matches_list.find_all('li'):
            # Find the teams and their scores
            team1 = match.find('div', class_='first').find('em').text
            score1 = match.find('div', class_='first').find('span', class_='teamTotal').text
            
            team2 = match.find('div', class_='last').find('em').text
            score2 = match.find('div', class_='last').find('span', class_='teamTotal').text
            
            # Store the match result
            match_results.append({
                'team1': team1,
                'score1': score1,
                'team2': team2,
                'score2': score2
            })
        print("MATCH RESULTS", match_results)
        return match_results
        """
        for item in transaction_items:
            transaction = {}
            transaction
            transaction['type'] = item.find('div', class_='mw')['class'][1].split('-')[1]
            transaction['team'] = item.find('a', class_='teamName').text.strip()
            
            players = item.find_all('span', class_='c')
            transaction['players'] = []
            for player in players:
                player_info = {}
                player_info['name'] = player.find('a', class_='playerCard').text.strip()
                player_info['position'] = player.find('em').text.strip().split(' - ')[0]
                player_info['nfl_team'] = player.find('em').text.strip().split(' - ')[1]
                transaction['players'].append(player_info)
            
            date_str = item.find('span', class_='date').text.strip()
            transaction['date'] = datetime.strptime(date_str, '%a, %b %d, %I:%M%p')
            
            transactions.append(transaction)
   
        # Parse scoreboard
        scoreboard = {}
        scoreboard_div = soup.find('div', id='leagueHomeScoreStrip')
        if scoreboard_div:
            scoreboard['week'] = scoreboard_div.find('li', class_='wl').text.strip()
            matchups = scoreboard_div.find_all('li', class_='ss ss-7')
            scoreboard['matchups'] = []
            for matchup in matchups:
                teams = matchup.find_all('div')
                matchup_data = {
                    'team1': {
                        'name': teams[0].find('em').text.strip(),
                        'score': teams[0].find('span', class_='teamTotal').text.strip()
                    },
                    'team2': {
                        'name': teams[1].find('em').text.strip(),
                        'score': teams[1].find('span', class_='teamTotal').text.strip()
                    }
                }
                scoreboard['matchups'].append(matchup_data)
        
        return {'transactions': transactions, 'scoreboard': scoreboard}
        """
    @commands.command()
    async def fantasy_update(self, ctx):
        """Fetch and display the latest fantasy football updates"""
        url = "https://fantasy.nfl.com/league/12293941?standingsTab=standings#leagueHomeStandings=leagueHomeStandings%2C%2Fleague%2F12293941%253FstandingsTab%253Dschedule%2Creplace"
        
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        data = self.parse_fantasy_data(response.text)

         # Create an embed to display the data
        embed = discord.Embed(title="Fantasy Football Updates", color=0x00ff00)
        embed.set_thumbnail(url="https://example.com/logo.png")
        
        # Create an embed to display the data
        for match in data:
            embed.add_field(
                name=f"**{match['team1']}**",
                value=f"Score: {match['score1']}",
                inline=True
            )
         
            embed.add_field(
                name=f"**VS**",
                value=f"",
                inline=True
            )
            embed.add_field(
                name=f"**{match['team2']}**",
                value=f"Score: {match['score2']}",
                inline=True
            )
          
        
        # Add a footer for additional info
        embed.set_footer(text="Week 3 | Fantasy Football")

        
        
        await ctx.send(embed=embed)
    
      

async def setup(bot):
    #name of your log(name of cog, print_info)
    helpers.log("Fantasy", "Setting up Fantasy cog...")
    await bot.add_cog(Fantasy(bot))
   

