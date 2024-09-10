# Welcome To Project Croc Bot

# How to Setup
- Clone this repository
- Install Requirements, You should create a .venv if your cool
- pip install -r requirements.txt

# update config
Your config folder is missing. Lets add that to your local repo
!IMPORTANT - NEVER push the config folder to git
- Create a folder called 'config'
- inside that folder create another folder called 'settings'
- inside the settings folder create 'dev.json' and add fill in the credentials below
```
{
    "Version": "1.0.0",
    "ENVIRONMENT": "dev",
    "DISCORD_API": "YOUR TOKEN",
    "GUILD_ID": SERVER_ID (INT NOT STRING) (RIGHT CLICK SERVER ICON and COPT SERVER ID)  
}
```

# How to make a discord bot
- head to https://discord.com/developers/applications.
- create a new application
- in oauth2 click on bot and administrator and copy paste the link at the bottom to add it to your dev server.


# run the bot by doing:
```python main.py dev```