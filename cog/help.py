from discord import app_commands
from discord.ext import commands
import discord
from cog.genshin import help_genshin
from cog.starrail import help_starrail
from cog.task import help_task
from cog.voicevox import help_voicevox
from cog.manage import help_manage

help_command_list = ["help_genshin", "help_starrail", "help_voicevox",
                     "help_task", "help_manage"]
command_type_list = ["原神関連", "スターレイル関連", "読み上げ関連", "タスク関連", "BOT管理関連"]


class HelpCog(commands.Cog):
    def __init__(self, bot):  # コンストラクタ
        self.bot = bot

        # イベントリスナー(ボットが起動したときやメッセージを受信したとき等)
    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog help.py ready!")

    @app_commands.command(name="help", description="各種コマンドの機能を詳しく紹介します")
    async def help(self, interaction: discord.Interaction):
        print("help command executed")
        embed = discord.Embed(
            title="コマンド一覧", description="以下のコマンドが利用可能です。\n:x:はBOT管理者専用の機能です\n", color=discord.Color.blurple())

        embed.add_field(name="/help", value="全コマンドの詳細を表示します。\n", inline=False)
        for i, help_command in enumerate(help_command_list):
            # embed.add_field(name=f"*{command_type_list[i]}*",
            #                 value=f"-------------------------------\n", inline=False)
            commandList = eval(help_command + "()")
            for command in commandList:
                embed.add_field(name=command[0],
                                value=command[1], inline=False)
        # 他のコマンドも同様に追加してください。

        # await interaction.response.send_message(content="aaaaa")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(HelpCog(bot))
