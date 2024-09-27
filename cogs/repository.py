import discord
from discord.ext import commands, tasks
from discord import app_commands
import os
import json
import utils.helpers as helpers
import requests
from datetime import datetime
import time
import pytz

class Repository(commands.Cog):

    def __init__(self, bot, config):
        self.bot = bot
        self.channel_id = config['pipeline']  # Replace with your channel ID
        self.github_token = config['github_token']  # Your GitHub token
        self.owner = 'ChrysalisSC'  # Repository owner
        self.repo = 'project-croc-bot'  # Repository name
        self.last_push_time = None  # Track last push time
        self.last_event_id_file = os.path.join('config','last_event_id.json')
        self.last_event_id = self.load_last_event_id()  # Track last event ID
        self.last_pull_requests = []  # Track last pull requests
        self.check_repo.start()  # Start the task


    async def send_message(self, message):
        channel = self.bot.get_channel(self.channel_id)
        if channel:
            await channel.send(message)

    def load_last_event_id(self):
        """Load the last event ID from a JSON file."""
        if os.path.exists(self.last_event_id_file):
            with open(self.last_event_id_file, 'r') as f:
                data = json.load(f)
                return data.get('last_event_id')
        return None

    def save_last_event_id(self, event_id):
        """Save the last event ID to a JSON file."""
        with open(self.last_event_id_file, 'w') as f:
            json.dump({'last_event_id': event_id}, f)

    @tasks.loop(minutes=20)  # Check every minute
    async def check_repo(self):
        print("checking repo for updates")
        await self.check_push_events()
        await self.check_pull_requests()

    async def check_push_events(self):
        url = f'https://api.github.com/repos/{self.owner}/{self.repo}/events'
        headers = {'Authorization': f'token {self.github_token}',  'Cache-Control': 'no-cache' }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            events = response.json()
           
            # Filter for PushEvents
            push_events = [event for event in events if event['type'] == 'PushEvent']

            if push_events:
                # Sort events by the created_at timestamp to find the latest one
                latest_event = max(push_events, key=lambda x: x['created_at'])
                event_id = latest_event['id']
                
                # Check if this event ID has already been sent
                if self.last_event_id is None or event_id != self.last_event_id:
                    pusher = latest_event['actor']['login']
                    commit_count = len(latest_event['payload']['commits'])

                    # Get the commit details
                    commits_info = []
                    for commit in latest_event['payload']['commits']:
                        commit_message = commit['message']
                        branch = latest_event['payload']['ref'].split('/')[-1]  # Extract the branch name
                        commits_info.append(f"- {commit_message} (Branch: {branch})")

                    # Get the push time
                    push_time = latest_event['created_at']
                    # Convert to datetime object in UTC
                    push_datetime = datetime.fromisoformat(push_time[:-1]).replace(tzinfo=pytz.utc)

                    # Convert to your local timezone (replace 'America/YourTimezone' with your actual timezone)
                    local_timezone = pytz.timezone('America/Los_Angeles')  # e.g., 'America/New_York'
                    local_datetime = push_datetime.astimezone(local_timezone)

                    # Convert to Unix time (in seconds) for Discord
                    discord_unix_time = int(local_datetime.timestamp())

                    commits_info_str = "\n".join(commits_info)
                    message = (f"User {pusher} pushed {commit_count} commits:\n{commits_info_str}\n"
                            f"Time of push: <t:{discord_unix_time}:f> (<t:{discord_unix_time}:R>)")  # f = short format, R = relative time
                    await self.send_message(message)

                    # Update the last event ID
                    self.last_event_id = event_id
                    self.save_last_event_id(event_id)

        else:
            print(f"Failed to fetch events: {response.status_code}")

    async def check_pull_requests(self):
        url = f'https://api.github.com/repos/{self.owner}/{self.repo}/pulls'
        headers = {'Authorization': f'token {self.github_token}'}

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            pull_requests = response.json()
            new_pull_requests = [pr for pr in pull_requests if pr['id'] not in self.last_pull_requests]

            for pr in new_pull_requests:
                title = pr['title']
                author = pr['user']['login']
                message = f"New pull request '{title}' opened by {author}."
                await self.send_message(message)

            # Update the list of last pull request IDs
            self.last_pull_requests = [pr['id'] for pr in pull_requests]

        else:
            print(f"Failed to fetch pull requests: {response.status_code}")

  

async def setup(bot):
    #name of your log(name of cog, print_info)
    helpers.log("Repository", "Setting up Example cog...")
    config = helpers.open_config(bot.env)
    await bot.add_cog(Repository(bot, config))
   

