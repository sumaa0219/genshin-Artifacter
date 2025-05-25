import discord
import discord.opus
from discord.ext import commands
import os
from dotenv import load_dotenv
import argparse
import update
import locale
from cog.manage import init_manage, send_console
from mylogger import set_logger, getLogger

set_logger()
logger = getLogger(__name__)


# mac用
# discord.opus.load_opus("libopus.dylib")
# discord.opus.load_opus("/usr/local/Cellar/opus/1.4/lib/libopus.dylib")

# ubuntu用
if not discord.opus.is_loaded():
    discord.opus.load_opus("libopus/lib/libopus.so.0")
    if not discord.opus.is_loaded():
        discord.opus.load_opus("/usr/lib/x86_64-linux-gnu/libopus.so.0")
        print("subopus loaded")
    logger.info("opus loaded")

locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')

load_dotenv()


parser = argparse.ArgumentParser()
parser.add_argument("--debug", action="store_true",
                    help="Use the debug token")
args = parser.parse_args()

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())
adminServer = os.environ['adminServer']
if args.debug:
    TOKEN = os.environ['debug']
    adminChannel = os.environ['adminDebugChannel']
    logger.info("debug mode")
else:
    TOKEN = os.environ['token']
    adminChannel = os.environ['adminChannel']
    logger.info("product mode")
logger.info("genshinArtifacter bot  -> starting...")

init_manage(adminServer, adminChannel)


@bot.event
async def setup_hook():
    logger.debug("setup_hook executed")
    await bot.load_extension("cog.cogmanager")


@bot.event
async def on_ready():
    update.update()
    await bot.change_presence(activity=discord.Game(name=str(len(bot.guilds))+"servers"))
    await bot.change_presence(activity=discord.Game(name="サーバー試験運用"))
    logger.info("bot is ready")


bot.run(TOKEN)
