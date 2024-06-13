import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import argparse
import update
import locale
from cog.manage import init_manage, send_console
import asyncio


async def main():
    # mac用
    # discord.opus.load_opus("libopus.dylib")
    # discord.opus.load_opus("/usr/local/Cellar/opus/1.4/lib/libopus.dylib")

    # ubuntu用
    discord.opus.load_opus("libopus.so.0")
    discord.opus.load_opus("/usr/lib/x86_64-linux-gnu/libopus.so.0")

    locale.setlocale(locale.LC_TIME, 'ja_JP.UTF-8')
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true",
                        help="Use the debug token")
    args = parser.parse_args()
    load_dotenv()

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

    intents = discord.Intents.default()  # 適当に。
    intents.message_content = True
    bot = commands.Bot(command_prefix="/", intents=intents)

    update.update()
    await bot.load_extension("cog.genshin")
    await bot.load_extension("cog.manage")
    init_manage(adminServer, adminChannel)
    await bot.load_extension("cog.starrail")
    await bot.load_extension("cog.task")
    await bot.load_extension("cog.voicevox")
    await bot.load_extension("cog.help")

    # await send_console("botを起動しました")

    await bot.start(TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
