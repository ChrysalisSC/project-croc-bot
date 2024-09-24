import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta

import utils.helpers as helpers
import sqlite3
import random
import asyncio


descriptions = [
"Tick tock, the croc's clock is ticking! You've got {minutes} minutes before this thread's time is up, so hop to it!",
"The croc in the suit is feeling impatient - you've got {minutes} minutes to get your business done in this thread!",
"This crocodile CEO is about to bite if you don't finish up in the next {minutes} minutes!",
"The reptilian rainmaker is ready to close the deal - finish up in the next {minutes} minutes or this thread gets the chomp!",
"Sharpen your negotiating skills, the croc in the Armani is giving you {minutes} minutes to seal the deal!",
"This crocodile corporate shark is circling - you'd better make your moves in the next {minutes} minutes!",
"The croc in the corner office says you've got {minutes} minutes to wrap up your business in this thread!",
"The reptilian robber baron is tapping his scaly fingers - better make it snappy in the next {minutes} minutes!",
"This crocodile capitalist is about to lose his cool - you've got {minutes} minutes before he swallows up this thread!",
"The croc in the corner suite is watching the clock - finish up in the next {minutes} minutes or else!",
"Tick tock goes the croc's clock - you've got {minutes} minutes to make your pitch in this thread!",
"The reptilian mogul is eyeing his Rolex - better conclude your business in the next {minutes} minutes!",
"This crocodile chairman is about to call a board meeting to shut down this thread - {minutes} minutes left!",
"The croc in the corner office says time is money - you've got {minutes} minutes to make your money moves!",
"Beware the crocodile CEO, he's ready to close the books on this thread in the next {minutes} minutes!",
"The reptilian tycoon is ready to make his power play - finish up in the next {minutes} minutes or else!",
"This crocodile corporate titan is about to swallow up this thread - {minutes} minutes left to stake your claim!",
"The croc in the corner suite is getting antsy - better wrap up your business in the next {minutes} minutes!",
"Tick tock, the crocodile capitalist is watching the clock - {minutes} minutes to close the deal in this thread!",
"This reptilian robber baron says time's a-wastin' - {minutes} minutes to make your move in this thread!",
"The croc in the corner office is tapping his Gucci loafers - {minutes} minutes left to seal the deal!",
"Beware the reptilian real estate mogul, he's ready to gobble up this thread in the next {minutes} minutes!",
"This crocodile CEO is about to call an emergency board meeting to shut down the thread - {minutes} minutes to make your pitch!",
"The croc in the Armani suit is eyeing his Rolex, better make it snappy in the next {minutes} minutes!",
"Tick tock goes the reptilian robber baron's clock, you've got {minutes} minutes to cash in on this thread!",
"This crocodile capitalist is about to swallow up the competition, {minutes} minutes left to state your case!",
"The croc in the corner suite is circling, {minutes} minutes to seal the deal before he takes a bite!",
"Sharpen your briefcase, the reptilian rainmaker is ready to close the books on this thread in {minutes} minutes!",
"This crocodile corporate shark is smelling blood in the water, {minutes} minutes to make your move!",
"The croc in the suit is getting impatient, {minutes} minutes to wrap up your business in this thread!",
"Beware the reptilian real estate tycoon, he's ready to devour this thread in the next {minutes} minutes!",
"This crocodile CEO is about to call an emergency shareholder meeting to shut it down - {minutes} minutes left!",
"The croc in the Armani is eyeing his golden Rolex, better make it count in the next {minutes} minutes!",
"Tick tock goes the reptilian robber baron's clock, {minutes} minutes to cash in on this thread!",
"This crocodile capitalist is about to swallow up the competition, {minutes} minutes to state your case!",
"The croc in the corner suite is circling, {minutes} minutes to seal the deal before he takes a bite!",
"Sharpen your briefcase, the reptilian rainmaker is ready to close the books in {minutes} minutes!",
"This crocodile corporate shark is smelling blood in the water, {minutes} minutes to make your move!",
"The croc in the suit is getting impatient, {minutes} minutes to wrap up your business here!",
"Beware the reptilian real estate tycoon, he's ready to devour this thread in {minutes} minutes!"
]

class ThreadManager(commands.Cog):
    def __init__(self, bot, config):
        self.bot = bot
        self.thread_task.start()
        self.config = config
        self.current_thread_ids = {}
        self.user_threads = {}  # Dictionary to track user threads
  

        # Register event listener
        bot.add_listener(self.on_thread_delete, 'on_thread_delete')

    async def create_thread(self, channel_id, thread_name, duration, thread_extended_duration, author):

        channel = self.bot.get_channel(int(channel_id))
        if channel:
            # Check if the user already has a thread in this channel
            user_channel_key = (channel_id, author.id)
            if user_channel_key in self.user_threads:
               
                return False

            # Create the thread
            thread = await channel.create_thread(
                name=thread_name, auto_archive_duration=60
            )
            self.current_thread_ids[thread.id] = duration
            self.user_threads[user_channel_key] = thread.id  # Track the thread for the user
           
            await thread.add_user(author)

            minutes = (duration // 60) + 1
            selected_description = random.choice(descriptions).format(minutes=minutes)
            
            embed = discord.Embed(
                title= f"A Thread Appears! - {thread_name}",
                description=selected_description,
                color=0xFFFFFF,
            )
            await thread.send(embed=embed)

            # Run the thread deletion in the background
            asyncio.create_task(
                self.delete_thread_after_duration(
                    thread, duration, thread_extended_duration, author
                )
            )

            return thread
        else:
            return False

    async def delete_thread_after_duration(
        self, thread, duration, thread_extended_duration, author
    ):
        try:
            await asyncio.sleep(duration)
            while True:
                if not await self.is_thread_active(thread.id):
                    break
                
                button_pressed = False

                view_identifier = f"keep_thread_open_{thread.id}"
                view = discord.ui.View(timeout=None)
                button = discord.ui.Button(
                    style=discord.ButtonStyle.secondary,
                    label="Extend Time",
                    custom_id=view_identifier,
                )
                view.add_item(button)

                embed = discord.Embed(
                    title="WARNING:",
                    description=f"THIS THREAD WILL BE DELETED IN 1 MINUTE - CLICK TO EXTEND DURATION BY {thread_extended_duration} SECONDS",
                    color=0xFFFFFF,
                )

                async def button_callback(interaction):
                    nonlocal button_pressed
                    button_pressed = True
                    await interaction.response.send_message(
                        "Thread duration extended", ephemeral=True
                    )

                button.callback = button_callback
                await thread.send(embed=embed, view=view)

                await asyncio.sleep(60)

                if button_pressed:
                    await asyncio.sleep(thread_extended_duration)
                else:
                    try:
                        if await self.is_thread_active(thread.id):
                            await thread.delete()
                            print(f"Thread deleted: {thread.name}")
                            self.current_thread_ids.pop(thread.id, None)
                            user_channel_key = (thread.parent.id, author.id)
                            self.user_threads.pop(user_channel_key, None)  # Remove the tracking entry
                        break
                    except Exception as e:
                        print(f"Thread could not be deleted: {thread.name} - ERROR {e}")
                        break

        except Exception as e:
            print(f"Error deleting thread: {e}")
            return

    async def is_thread_active(self, thread_id):
        return self.bot.get_channel(thread_id) is not None

    async def on_thread_delete(self, thread):
        print("ON THREAD DELETE!")
        if thread.id in self.current_thread_ids:
            self.current_thread_ids.pop(thread.id, None)
            for key, value in list(self.user_threads.items()):
                if value == thread.id:
                    self.user_threads.pop(key, None)
                    break

    @tasks.loop(hours=24)
    async def thread_task(self):
        now = datetime.now()
        if now.hour == 0 and now.minute == 0:
            guild = self.bot.get_guild(self.config["GUILD_ID"])
            if guild:
                for channel in guild.text_channels:
                    if channel.is_thread():
                        await channel.delete()

    @thread_task.before_loop
    async def before_thread_task(self):
        await self.bot.wait_until_ready()

async def setup(bot, config):
    await bot.add_cog(ThreadManager(bot, config))
    helpers.log("EXAMPLE", "Setting up Example cog...")

