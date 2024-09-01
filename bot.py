import discord
from discord.ext import commands, tasks
import random
import asyncio
from datetime import datetime, timedelta
import os

# Create an instance of Bot with specific intents
intents = discord.Intents.default()
intents.message_content = True  # Enable the intent to read message content
intents.members = True           # Enable the intent to access member information

# Prefix to use for commands (e.g., !changeNick)
bot = commands.Bot(command_prefix='!', intents=intents)

# Load nicknames from a file
def load_nicknames():
    try:
        with open("nicknames.txt", "r") as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        return []

# Save a new nickname to the file
def save_nickname(nickname):
    with open("nicknames.txt", "a") as file:
        file.write(f"{nickname}\n")

# Load nicknames into a list at startup
nicknames = load_nicknames()

# Define an event to run when the bot is ready
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    change_nickname_daily.start()  # Start the daily nickname change task

# Task to change nickname daily at midnight
@tasks.loop(hours=24)
async def change_nickname_daily():
    await bot.wait_until_ready()  # Wait until the bot is ready
    current_time = datetime.now()
    next_midnight = datetime.combine(current_time + timedelta(days=1), datetime.min.time())
    await asyncio.sleep((next_midnight - current_time).seconds)  # Sleep until midnight

    # Change your own nickname using user ID
    guild = discord.utils.get(bot.guilds)  # Assumes bot is only in one guild; modify as needed
    if guild:
        user_id = os.getenv('DISCORD_USERID')  # Replace with your actual user ID
        member = guild.get_member(user_id)
        if member:
            new_nickname = random.choice(nicknames)
            try:
                await member.edit(nick=new_nickname)
                print(f"Changed nickname to {new_nickname}")
            except discord.Forbidden:
                print("I do not have permission to change your nickname.")
            except Exception as e:
                print(f"An error occurred: {e}")

# Define the !changeNick command for changing the invoking user's nickname
@bot.command(name='changeNick')
@commands.has_permissions(change_nickname=True)  # Ensure user has permission to change nicknames
async def change_nick(ctx):
    member = ctx.author
    new_nickname = random.choice(nicknames)
    try:
        await member.edit(nick=new_nickname)
        await ctx.send(f'Your nickname has been changed to {new_nickname}')
    except discord.Forbidden:
        await ctx.send('I do not have permission to change your nickname.')

# Define a command to change another user's nickname
@bot.command(name='changeUserNick')
@commands.has_permissions(administrator=True)  # Check if the user has administrator permissions
async def change_user_nick(ctx, user: discord.Member):
    member = user  # Use the specified user parameter
    new_nickname = random.choice(nicknames)
    try:
        await member.edit(nick=new_nickname)
        await ctx.send(f'{user.mention}\'s nickname has been changed to {new_nickname}')
    except discord.Forbidden:
        await ctx.send(f'I do not have permission to change the nickname for {user.mention}.')

# Define the !addNick command to add a new nickname to the list and file
@bot.command(name='addNick')
@commands.has_permissions(administrator=True)  # Check if the user has administrator permissions
async def add_nick(ctx, *, new_nickname: str):
    if new_nickname in nicknames:
        await ctx.send(f'The nickname "{new_nickname}" already exists.')
    else:
        nicknames.append(new_nickname)
        save_nickname(new_nickname)
        await ctx.send(f'The nickname "{new_nickname}" has been added.')




# Run the bot using the token
TOKEN = os.getenv('DISCORD_TOKEN')
bot.run(TOKEN)
