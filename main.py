import discord
import discord.opus
from discord.ext import commands
import os
from dotenv import load_dotenv
import argparse
import update
import locale
from cog.manage import init_manage, send_console
import asyncio

# mac用
# discord.opus.load_opus("libopus.dylib")
# discord.opus.load_opus("/usr/local/Cellar/opus/1.4/lib/libopus.dylib")

# ubuntu用
discord.opus.load_opus("libopus.so.0")
# discord.opus.load_opus("/usr/lib/x86_64-linux-gnu/libopus.so.0")

if not discord.opus.is_loaded():
    discord.opus.load_opus("libopus.so.0")
    if not discord.opus.is_loaded():
        discord.opus.load_opus("/usr/lib/x86_64-linux-gnu/libopus.so.0")
        print("subopus loaded")
    print("opus loaded")

locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
parser = argparse.ArgumentParser()
parser.add_argument("--debug", action="store_true",
                    help="Use the debug token")
args = parser.parse_args()
load_dotenv()
bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())
adminServer = os.environ['adminServer']
if args.debug:
    TOKEN = os.environ['debug']
    adminChannel = os.environ['adminDebugChannel']
    print("------------------debug mode------------------")
else:
    TOKEN = os.environ['token']
    adminChannel = os.environ['adminChannel']
    print("------------------product mode------------------")
print("---------------------------\n|  genshinArtifacter bot  | -> starting...\n---------------------------")

init_manage(adminServer, adminChannel)
GLOBAL_INITIAL_EXTENSIONS = [
    "cog.genshin",
    "cog.manage",
    "cog.starrail",
    "cog.task",
    "cog.voicevox",
    "cog.help"

]

catCaffeCommands = [["cog.catcafe"], [836846944517226526]]


async def load_extentions_Select_Guild(cogName: str, guildID: int):
    print("loading selected cogs...")
    await bot.load_extension(cogName)
    await bot.tree.sync(guild=discord.Object(id=guildID))


async def load_extentions():
    print("loading cogs...")
    for cog in GLOBAL_INITIAL_EXTENSIONS:
        await bot.load_extension(cog)
    await bot.tree.sync()


@bot.event
async def setup_hook():
    await load_extentions()
    try:
        await load_extentions_Select_Guild(catCaffeCommands[0][0], catCaffeCommands[1][0])
        await load_extentions_Select_Guild("cog.tyomnsr", 929432903534923857)
    except Exception as e:
        print(e)


@bot.event
async def on_ready():
    update.update()
    print("bot is ready")


bot.run(TOKEN)
