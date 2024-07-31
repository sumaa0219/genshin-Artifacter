from discord.ext import commands, tasks
from discord import app_commands
import discord
import random
import base64
from io import BytesIO
import datetime
import os
from mylogger import getLogger
logger = getLogger(__name__)

catCafeID = 836846944517226526
hsbfig = os.listdir("assetData/catcafe")
deleteMessages = []


class CatcafeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(seconds=1)  # タスクを定期的に実行する
    async def deleteTask(self):
        global deleteMessages
        if len(deleteMessages) > 0:
            for message in deleteMessages:
                if (datetime.datetime.now() - message[1]).seconds > 30:
                    await message[0].delete()
                    deleteMessages.remove(message)

    @commands.Cog.listener()
    async def on_ready(self):
        self.deleteTask.start()
        print("Cog catcafe.py ready!")

    @app_commands.command(name="buildhsb", description="HSBのビルドをします")
    @app_commands.guilds(catCafeID)
    async def buildhsb(self, interaction: discord.Interaction):
        wordList = ["あ、あのっ小林先生", "あ、あのっ….", "ふーーー", "フーー", "(鼻息)"]
        message = generate_number_with_zero_probability(wordList)
        await interaction.response.send_message(message)

    @app_commands.command(name="buildhsbfig", description="HSBの画像をビルドします")
    @app_commands.guilds(catCafeID)
    async def buildhsbfig(self, interaction: discord.Interaction):
        global deleteMessages
        with open("assetData/catcafe/"+random.choice(hsbfig), "rb") as f:
            image_base64 = f.read()
            image_bytes = base64.b64decode(
                image_base64)  # Base64でエンコードされた文字列をデコード
            await interaction.response.send_message(content="?_?", file=discord.File(fp=BytesIO(image_bytes), filename="SPOILER_hsb.png"))
            async for message in interaction.channel.history(limit=200):
                if message.author.bot:
                    deleteMessages.append([message, datetime.datetime.now()])
                    break
            print(deleteMessages)


def generate_number_with_zero_probability(wordlist: list, probability_of_zero=0.03):
    # 0から10までの数字をランダムに生成
    number = random.randint(0, len(wordlist)-1)
    # 0から1までのランダムな数値を生成し、それが指定された確率以下であれば0を出力
    if random.random() < probability_of_zero:
        return wordlist[0]
    else:
        return wordlist[number]


async def setup(bot):
    await bot.add_cog(CatcafeCog(bot))
