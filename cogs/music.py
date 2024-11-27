import discord
from discord.ext import commands, tasks
from discord import app_commands
import requests
import time
import base64
import os
import json
from html.parser import HTMLParser

import utils.helpers as helpers
from datetime import datetime, timezone, timedelta
import pytz

RAINBOW_COLORS = [0xFF0000, 0xFF7F00, 0xFFFF00, 0x00FF00, 0x0000FF, 0x4B0082, 0x9400D3]

#r&b and lofi

def data():
    list = {
    "2Mq9TtE1Hv3c20UvuX3UwB_LAST_UPDATED": "2024-09-28T21:59:02Z",
    "2Mq9TtE1Hv3c20UvuX3UwB_LAST_UPDATED_SONG": "Just Better",
    "37i9dQZF1DWUa8ZRTfalHk_LAST_UPDATED": "2024-09-27T04:00:00Z",
    "37i9dQZF1DWUa8ZRTfalHk_LAST_UPDATED_SONG": "Burning Down"
    }

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs = True
        self.text = []

    def handle_data(self, d):
        self.text.append(d)

    def get_data(self):
        return ''.join(self.text)
    
def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.SPOT_SECRET_ID = None
        self.SPOT_CLIENT_ID = None
        self.token =  None
        self.token_expiry = 0
        self.current_color_index = 0
        self.base_url = "https://en.wikipedia.org/w/api.php"
        self.music_channel = None
        self.set_Ids(bot.env)
        self.check_playlist_updates.start()

    def set_Ids(self, env):
        config = helpers.open_config(env)
        print(config)
        self.SPOT_SECRET_ID = config['SPOT_SECRET_ID']
        self.SPOT_CLIENT_ID = config['SPOT_CLIENT_ID']
        self.music_channel = config['MUSIC_CHANNEL']

    def cog_unload(self):
        self.check_playlist_updates.cancel()

    
   
    async def get_token(self):
        if not self.token or time.time() >= self.token_expiry:
            auth_string = self.SPOT_CLIENT_ID + ":" + self.SPOT_SECRET_ID
            auth_bytes = auth_string.encode("utf-8")
            auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    
            url = "https://accounts.spotify.com/api/token"
    
            headers = {
                'Authorization': 'Basic ' + auth_base64,
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            data = {"grant_type": "client_credentials"}
            response = requests.post(url, headers=headers, data=data)
            json_result = response.json()
            
            # Cache the token and its expiration time
            self.token = json_result['access_token']
            self.token_expiry = time.time() + json_result['expires_in']
        return self.token
    

    async def get_wikipedia_extract(self, artist_name):
        # Step 1: Search for the artist
        search_params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": artist_name,
            "srlimit": 1
        }

        try:
            search_response = requests.get(self.base_url, params=search_params)
            search_response.raise_for_status()
            search_data = search_response.json()
            #print("SEARCH DATA: ", search_data)

            # Step 2: If a search result is found, get the page ID of the first result
            if search_data['query']['search']:
                page_id = search_data['query']['search'][0]['pageid']

                # Step 3: Query for the extract using the page ID
                extract_params = {
                    "action": "query",
                    "format": "json",
                    "prop": "extracts",
                    "exintro": True,
                    "pageids": page_id
                }

                extract_response = requests.get(self.base_url, params=extract_params)
                extract_response.raise_for_status()
                extract_data = extract_response.json()
                #print("EXTRACT DATA: ", extract_data)

                # Extract the page content
                extract = extract_data['query']['pages'][str(page_id)]['extract']
                extract = strip_tags(extract)
                #print("EXTRACT: ", extract)

                max_length = 800
                if len(extract) > max_length:
                    extract = extract[:max_length] + "..."
                return extract.strip()

        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from Wikipedia: {e}")

        return f"Biography not found for {artist_name}."
    
    def get_time(self):
        utc_now = datetime.now(timezone.utc)
        pacific_now = utc_now.astimezone(pytz.timezone('America/Los_Angeles'))
        return pacific_now
   
    
    async def create_music_embed(self, channel, radio_name, track_title, artist, spotify_link, image_url, artist_id):   
        print("creating emebed")     
        channel = self.bot.get_channel(int(channel))
        unix_timestamp = int(helpers.get_time().timestamp())
        radio_name = radio_name.upper()
       # role_mention = f'<@&{self.config['MUSIC_ROLE']}>'  # Mention the role
        role_mention = f'<@&MUSICROLE>'  # Mention the role
        music_embed = discord.Embed(
            title=f":loudspeaker: *NEW SONG DROP <t:{unix_timestamp}:R>*",
            description=f"A new song has been added to the {radio_name} playlist! Check it out below - {role_mention} ",
            color=RAINBOW_COLORS[self.current_color_index]
        )
        self.current_color_index = (self.current_color_index + 1) % len(RAINBOW_COLORS)
        artists = artist.split(",")  # Split by comma if multiple artists
        first_artist = artists[0].strip()
        artist_description = await self.get_wikipedia_extract(first_artist)
        #split after first paragraph
        artist_description = artist_description.split("\n")[0]
        #print("ARTIST DESCRIPTION: ", artist_description)
       
        music_embed.set_thumbnail(url=image_url)        
        music_embed.add_field(name=f"", value=f"```TITLE :  {track_title}\nARTIST:  {artist}```", inline=True)
        music_embed.add_field(name="About the Artist:", value=artist_description, inline=False)
        #music_embed.add_field(name="*Bring Me There!*", value=f"[*Spotify*]({spotify_link})\n", inline=False)
        
        await channel.send(embed=music_embed)
        # Send the Spotify link separately to trigger the preview
        await channel.send(f"[***Bring Me There!***]({spotify_link})")

        
    def get_auth_header(self, token):
        return {'Authorization':"Bearer " + str(token)}
    

    async def get_newest_songs_from_playlist(self, playlist_id, config_file):
        # Read the config file
        with open(config_file, 'r') as file:
            config_data = json.load(file)

        last_updated_timestamp = config_data.get(f"{playlist_id}_LAST_UPDATED", "")
        last_updated_song = config_data.get(f"{playlist_id}_LAST_UPDATED_SONG", "")

        token = await self.get_token()
        headers = self.get_auth_header(token)
        fields = "items(added_at,track(name,external_urls.spotify,artists(id,name),album(images))),next"
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
        params = {'fields': fields, 'limit': 100, 'market': 'US'}

        all_tracks = []
        while url:
            response = self.make_spotify_request(url, headers, params)
            json_result = response.json()
            all_tracks.extend(json_result.get('items', []))
            url = json_result.get('next')
            params = {}  # Clear params for pagination

        if not all_tracks:
            return []

        # Sort tracks by added_at date, most recent first
        all_tracks.sort(key=lambda x: x['added_at'], reverse=True)

        new_songs = []
        update_needed = False
        latest_added_at = last_updated_timestamp

        for track_item in all_tracks:
            track = track_item['track']
            if track is None:
                continue

            track_name = track['name']
            added_at = track_item['added_at']

            # Convert timestamps to datetime objects for comparison
            added_at_dt = datetime.fromisoformat(added_at.replace('Z', '+00:00'))
            last_updated_dt = datetime.fromisoformat(last_updated_timestamp.replace('Z', '+00:00')) if last_updated_timestamp else datetime.min.replace(tzinfo=timezone.utc)

            if added_at_dt > last_updated_dt and track_name != last_updated_song:
                artists = ', '.join(artist['name'] for artist in track['artists'])
                artist_info = track['artists'][0]
                artist_id = artist_info['id']
                spotify_link = track['external_urls']['spotify']
                album_data = track['album']
                
                image_url = album_data['images'][0]['url'] if album_data['images'] else None
                new_songs.append((track_name, artists, spotify_link, image_url, artist_id))
                update_needed = True

                if added_at_dt > datetime.fromisoformat(latest_added_at.replace('Z', '+00:00')):
                    latest_added_at = added_at
            else:
                # If we've reached a song that's not newer than the last update, we can stop
                break

        if update_needed:
            config_data[f"{playlist_id}_LAST_UPDATED"] = latest_added_at
            config_data[f"{playlist_id}_LAST_UPDATED_SONG"] = new_songs[0][0]  # Update with the latest song's name

            with open(config_file, 'w') as file2:
                json.dump(config_data, file2, indent=4)

        return new_songs

    def make_spotify_request(self, url, headers, params):
        max_retries = 3
        retry_delay = 1

        for _ in range(max_retries):
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return response
            elif response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', retry_delay))
                time.sleep(retry_after)
            else:
                response.raise_for_status()

        raise Exception("Max retries reached. Unable to get a successful response from Spotify API.")
            
    @tasks.loop(minutes=30)
    async def check_playlist_updates(self):
        try:
            print("Checking for new songs...")

            # For KPOP Radio
            channel = self.music_channel
            result = await self.get_newest_songs_from_playlist("2Mq9TtE1Hv3c20UvuX3UwB", "config/last_music_id.json")
            if result:
                for item in result:
                    track_name, artist, spotify_link, image_url, artist_id = item
                    await self.create_music_embed(channel, "KPOP Radio", track_name, artist, spotify_link, image_url, artist_id)

            # For RISING Radio
            print("Checking for new songs for pop...")
          
            result = await self.get_newest_songs_from_playlist("37i9dQZF1DWUa8ZRTfalHk", "config/last_music_id.json")
            if result:
                for item in result:
                    track_name, artist, spotify_link, image_url, artist_id = item
                    await self.create_music_embed(channel, "RISING Radio", track_name, artist, spotify_link, image_url, artist_id)

            print("Finished checking for new songs...")
        
        except Exception as e:
            print(f"Error occurred while checking playlist updates: {e}")
        finally:
            print("Loop completed, waiting for next cycle.")
   
    
    @commands.command()
    async def test_kpop(self, ctx):
        result = await self.get_newest_songs_from_playlist("2Mq9TtE1Hv3c20UvuX3UwB", "music/pop_music.json")
        if result:
            for item in result:
                track_name, artist, spotify_link, image_url, artist_id = item  # Include image_url
                await self.create_music_embed(ctx.channel.id, "RISING Radio", track_name, artist, spotify_link, image_url, artist_id)
        else:
            await ctx.send("No new tracks found.")

      
async def setup(bot):
    helpers.log("MUSIC", "Setting up MUSIC cog...")
    await bot.add_cog(Music(bot))