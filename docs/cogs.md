# Discord Cogs
Cogs are a organized collection of commands.
Learn more here, https://discordpy.readthedocs.io/en/stable/ext/commands/cogs.html

Summary of above:
- Each cog is a Python class that subclasses commands.Cog.
- Every command is marked with the commands.command() decorator.
- Every hybrid command is marked with the commands.hybrid_command() decorator.
- Every listener is marked with the commands.Cog.listener() decorator.
- Cogs are then registered with the Bot.add_cog() call.
- Cogs are subsequently removed with the Bot.remove_cog() call.

When youre done with you cog setup (see example_cog.py)
add your cog to the main.py file. 
