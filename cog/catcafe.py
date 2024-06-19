from discord.ext import commands
from discord import app_commands
import discord
import random

catCafeID = 836846944517226526


class CatcafeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog catcafe.py ready!")

    @app_commands.command(name="buildhsb", description="HSBのビルドをします")
    @app_commands.guilds(catCafeID)
    async def buildhsb(self, interaction: discord.Interaction):
        wordList = ["あ、あのっ小林先生", "あ、あのっ….", "ふーーー", "フーー", "(鼻息)"]
        message = generate_number_with_zero_probability(wordList)
        await interaction.response.send_message(message)


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
