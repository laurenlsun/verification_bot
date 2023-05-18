import os

import discord as ds
import psycopg2
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB = os.getenv('POSTGRES_DB')
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_PORT = os.getenv('POSTGRES_PORT')

intents = ds.Intents.default()
intents.members = True  # bot will not see all members without this line
client = commands.Bot(command_prefix="!", intents=intents)

# psycopg conn
conn = psycopg2.connect(host=POSTGRES_HOST,
                        dbname=POSTGRES_DB,
                        user=POSTGRES_USER,
                        password=POSTGRES_PASSWORD,
                        port=POSTGRES_PORT)
cur = conn.cursor()

def get_member_list():
    cur.execute("SELECT * FROM members")
    names_from_db = []
    for member in cur.fetchall():
        names_from_db.append(member[1])
    return names_from_db

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    guild = ds.utils.get(client.guilds, name=GUILD) # get() creates predicate
    print(
        f'{client.user} is connected to the following guild:\n'
        f'{guild.name}(id: {guild.id})'
    )

    print('Guild Members:')
    for member in guild.members:
        print(member, end="")
        if str(member) in get_member_list():
            print(" | verified")
        else:
            print(" | not verified")


@client.event
async def on_member_join(member):
    role = ds.utils.get(member.server.roles, name="basic member")
    await client.add_roles(member, role)
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, welcome to yeetum!'
    )
    if str(member) not in get_member_list():
        await member.dm_channel.send(
            'It seems that you aren\'t a member of Yeetum yet.'
        )
    else:
        # assign verified member role
        await member.dm_channel.send(
            'It seems that you\'re already a Yeetum member. You\'ve been given the basic member role.'
        )
    

@client.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    # Ignore messages that do not start with the command prefix
    if not message.content.startswith(client.command_prefix):
        return


@client.command()
async def test(ctx):
    await ctx.send("Hi there I'm the bot")


@client.command(pass_context=True)
@commands.has_role("Admin") # This must be exactly the name of the appropriate role
async def addrole(ctx):
    member = ctx.message.author
    role = ds.utils.get(member.server.roles, name="basic member")
    await client.add_roles(member, role)


conn.commit()

cur.close()
conn.close()
