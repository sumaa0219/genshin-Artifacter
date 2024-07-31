from discord.ext import commands, tasks
from discord import app_commands
import discord
import os
from dotenv import load_dotenv
from mylogger import getLogger
logger = getLogger(__name__)

load_dotenv()

GLOBAL_INITIAL_EXTENSIONS = [
    "cog.genshin",
    "cog.manage",
    "cog.starrail",
    "cog.task",
    "cog.voicevox",
    "cog.help"

]


class cogManagerCog(commands.Cog):
    def __init__(self, bot):  # コンストラクタ
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog cogmanage.py ready!")
        await self.load_all_extentions()

    async def load_extentions_Select_Guild(self, cogName: str, guildID: int):
        print("loading selected cogs...", cogName)
        await self.bot.load_extension(cogName)
        await self.bot.tree.sync(guild=discord.Object(id=guildID))
        await self.bot.tree.sync(guild=discord.Object(id=os.environ['adminServer']))

    async def load_extentions(self):
        for cog in GLOBAL_INITIAL_EXTENSIONS:
            print("loading cogs...", cog)
            await self.bot.load_extension(cog)
        await self.bot.tree.sync()

    async def load_all_extentions(self):
        print("loading all cogs...")
        await self.load_extentions()
        try:
            await self.load_extentions_Select_Guild("cog.catcafe", 836846944517226526)
            await self.load_extentions_Select_Guild("cog.tyomnsr", 929432903534923857)
        except Exception as e:
            print(e)


async def setup(bot):
    await bot.add_cog(cogManagerCog(bot))
