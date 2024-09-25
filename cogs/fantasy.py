import requests
from bs4 import BeautifulSoup
import pytz
import random
import asyncio
import datetime

import discord
from discord.ext import commands, tasks
from discord import app_commands

import utils.helpers as helpers

THESPORTSDB_API_KEY = '3' 

class Fantasy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.timezone = pytz.timezone("America/New_York")  
        

    def get_random_nfl_team_image(self):
        """Fetch a random NFL team logo or image using TheSportsDB API."""
        url = f"https://www.thesportsdb.com/api/v1/json/{THESPORTSDB_API_KEY}/search_all_teams.php"
        
        # Fetching NFL teams (NFL league id in TheSportsDB is 4391)
        params = {'l': 'NFL'}
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            # Parse the response and get a list of teams
            data = response.json()
          
            teams = data['teams']
            
            # Choose a random team
            random_team = random.choice(teams)
            
            # Return the team badge/logo image URL
            print("RANDOM TEAM", random_team)
            return random_team['strFanart3']  # Badge URL for the team logo
        else:
            print(f"Error fetching data: {response.status_code}")
            return None  # Handle errors gracefully
        
    def parse_standings(self):
        """Parse the weekly fantasy football data from the NFL website."""
        url = "https://fantasy.nfl.com/league/12293941?standingsTab=standings#leagueHomeStandings=leagueHomeStandings%2C%2Fleague%2F12293941%253FstandingsTab%253Dstandings%2Creplace"
        
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        print(soup)
        # Find the week number
        # Find the standings table
        standings_table = soup.find('table', class_='tableType-team hasGroups')
        
        # Create a list to store standings data
        standings = []

        # Parse the table rows (teams) from the tbody
        rows = standings_table.find('tbody').find_all('tr')

        for row in rows:
            rank = row.find('td', class_='teamRank').text.strip()  # Rank
            team_name = row.find('a', class_='teamName').text.strip()  # Team Name
            record = row.find('td', class_='teamRecord').text.strip()  # Win-Loss-Tie Record
            win_pct = row.find('td', class_='teamWinPct').text.strip()  # Win Percentage
            streak = row.find('td', class_='teamStreak').text.strip()  # Streak
            waiver_priority = row.find('td', class_='teamWaiverPriority').text.strip()  # Waiver Priority
            points_for = row.find_all('td', class_='teamPts')[0].text.strip()  # Points For
            points_against = row.find_all('td', class_='teamPts')[1].text.strip()  # Points Against
            
            # Append the parsed data into the standings list
            standings.append({
                'rank': rank,
                'team_name': team_name,
                'record': record,
                'win_pct': win_pct,
                'streak': streak,
                'waiver_priority': waiver_priority,
                'points_for': points_for,
                'points_against': points_against
            })

        # Optionally return or print the parsed standings data
   

       
        week = soup.find('ul', class_='weekNav weekNav-mini').find('li', class_='wl').text
        return standings, week


    def parse_fantasy_data(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        #print(soup)
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
        #print("MATCH RESULTS", match_results)
        #<ul class="weekNav weekNav-mini"><li class="wl wl-3 first">Week 3
        week = soup.find('ul', class_='weekNav weekNav-mini').find('li', class_='wl').text


        return match_results, week
 
    @app_commands.command(
        name="fantasy_update",
        description="Check the latest fantasy football updates"
    )
    async def fantasy_update(self, interaction):
        """Fetch and display the latest fantasy football updates"""
        url = "https://fantasy.nfl.com/league/12293941?standingsTab=standings#leagueHomeStandings=leagueHomeStandings%2C%2Fleague%2F12293941%253FstandingsTab%253Dschedule%2Creplace"
        await interaction.response.defer()
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        data, week= self.parse_fantasy_data(response.text)

         # Create an embed to display the data
        nfl_team_logo_url = self.get_random_nfl_team_image()
        embed = discord.Embed(title="Fantasy Football Updates", color=0xFFFF00)
        if nfl_team_logo_url:
            embed.set_image(url=nfl_team_logo_url)
        
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
        embed.set_footer(text=f"{week} | Fantasy Football")
        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="standings",
        description="Check the latest fantasy football standings"
    )
    async def standings(self, interaction):
        """Fetch and display the latest fantasy football updates"""
        url = "https://fantasy.nfl.com/league/12293941?standingsTab=standings#leagueHomeStandings=leagueHomeStandings%2C%2Fleague%2F12293941%253FstandingsTab%253Dschedule%2Creplace"
        await interaction.response.defer()
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        data, week = self.parse_standings()
        print(data , week)
        # Create an embed to display the data

        fire_emoji = "🔥"
        ice_emoji = "❄️"
        up_arrow = "⬆️"
   
        up = "🢁"
        down = "🢃"
        nfl_team_logo_url = self.get_random_nfl_team_image()
        embed = discord.Embed(title=f"Fantasy Football Standings | {week}", color=0xFFFF00)
        if nfl_team_logo_url:
            embed.set_image(url=nfl_team_logo_url)
            

        for team in data:
            # Left column (Rank and Team Name)
            team_position = team['rank'].split(' ')[0]
            movement = team['rank'].split(' ')[1]

            if 'W' in team['streak']:
                 streak_with_emoji = f"{fire_emoji} {team['streak']}"
            elif 'L' in team['streak']:
                streak_with_emoji = f"{ice_emoji} {team['streak']}"
            else:
                streak_with_emoji = team['streak']

            if "+" in movement:
                movement_with_arrow = f"{up} {movement}"
            elif "-" in movement:
                movement_with_arrow = f"{down} {movement}"
            else:
                movement_with_arrow = movement
            
            # Formatted string with padded spacing for better alignment
            standings_info = (
                f"*Streak:* {streak_with_emoji:<5}\n"
                f"*Win Pct:* {team['win_pct']:<5}\n"
              
                f"*Points For:* {team['points_for']:<10} *Points Against:* {team['points_against']:<10}"
            )
            
            # Add a field for each team with aligned information
            embed.add_field(
                name=f"**{team_position}. {movement_with_arrow} | ({team['record']}) - {team['team_name']}**",
                value=standings_info,
                inline=False
            )

        # Add a footer with additional info
        embed.set_footer(text=f"Fantasy Football Standings | {week}")
        
        # Send the embed to the channel
        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="winnersandlosersthisweek",
        description="Custom output of fantasy rankings"
    )
    async def winnersandlosersthisweek(self, interaction):
        """Fetch and display the latest fantasy football updates"""
        url = "https://fantasy.nfl.com/league/12293941?standingsTab=standings#leagueHomeStandings=leagueHomeStandings%2C%2Fleague%2F12293941%253FstandingsTab%253Dschedule%2Creplace"
        await interaction.response.defer()
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        data, week = self.parse_standings()
        print(data , week)
        # Create an embed to display the data

        fire_emoji = "🔥"
        ice_emoji = "❄️"   
            
        winners = []
        losers = []

        for team in data:
            # Left column (Rank and Team Name)
            if 'W' in team['streak']:
                 winners.append(team)
            elif 'L' in team['streak']:
                losers.append(team)
            else:
                losers.append(team)
        

        embedWinners = discord.Embed(title=f"WINNERS | {week}", color=0x00FF00)
        sorted_winners = sorted(winners, key=lambda x: int(x['streak'].split('W')[1]), reverse=True)
        i = 0
        for team in sorted_winners:
            i+=1
            embedWinners.add_field(
                name=f"**{i}: {team['team_name']} - {fire_emoji}{team['streak']} | Overall: ({team['record']})**",
                value="",
                inline=False
            )

        embedLosers = discord.Embed(title=f"LOSERS | {week}", color=0xFF0000)
        sorted_losers = sorted(losers, key=lambda x: int(x['streak'].split('L')[1]), reverse=True)
        i = 0
        for team in sorted_losers:
            i+=1
            embedLosers.add_field(
                name=f"** {i}: {team['team_name']} - {ice_emoji}{team['streak']} | Overall: ({team['record']})**",
                value="",
                inline=False
            )

        # Send the embed to the channel
        await interaction.followup.send(embeds=[embedWinners, embedLosers])

    
      

async def setup(bot):
    #name of your log(name of cog, print_info)
    helpers.log("Fantasy", "Setting up Fantasy cog...")
    await bot.add_cog(Fantasy(bot))
   

