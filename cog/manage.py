from discord.ext import commands
from discord import app_commands
import discord
import time
import os
from dotenv import load_dotenv


load_dotenv()
adminID = os.environ['adminID']


def is_admin(interaction: discord.Interaction):
    return interaction.user.id == adminID

# commands.Cogを継承する


class ManageCog(commands.Cog):
    def __init__(self, bot):
        global bott
        self.bot = bot
        bott = bot
    # イベントリスナー(ボットが起動したときやメッセージを受信したとき等)

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog manage.py ready!")

    @app_commands.command(name="say", description="発言させます")
    @app_commands.check(is_admin)
    async def say_command(self, interaction: discord.Interaction, text: str):

        await interaction.response.send_message(text)

    @app_commands.command(name="delete_messages", description="Deletes a lot messages from 200 messegases",)
    async def delete_messages(self, interaction: discord.Interaction, member: discord.Member, limit: int):
        await interaction.response.defer()
        maxcuount = 0
        async for message in interaction.channel.history(limit=200):
            if message.author == member and maxcuount < limit:
                await message.delete()
                maxcuount += 1
                time.sleep(0.1)
        await interaction.followup.send(
            f"{member.display_name}'s last {limit} messages deleted."
        )

    @app_commands.command(name="adminsay", description="開発者専用")
    async def send_message(self, interaction: discord.Interaction, guild_id: str, channel_id: str, message: str):
        guild = self.bot.get_guild(int(guild_id))
        channel = guild.get_channel(int(channel_id))
        await channel.send(message)
        await interaction.response.send_message("送信完了")

    @app_commands.command(name="palstart", description="パルワールドサーバーを起動します")
    async def palstart(self, interaction: discord.Interaction):
        await interaction.response.defer()
        os.system("steamcmd +login anonymous +app_update 2394010 validate +quit")
        os.system("sudo systemctl start PalServer")
        await interaction.followup.send("起動完了 sssumaa.com:8211")

    @app_commands.command(name="palstop", description="パルワールドサーバーを停止します")
    async def palstop(self, interaction: discord.Interaction):
        await interaction.response.defer()
        os.system("sudo systemctl stop PalServer")
        await interaction.followup.send("停止完了")

    @app_commands.command(name="minecraftstart", description="マイクラサーバーを起動します")
    async def palstart(self, interaction: discord.Interaction):
        await interaction.response.defer()
        os.system("sudo systemctl start minecraftserver")
        await interaction.followup.send("起動完了 sssumaa.com:25565")

    @app_commands.command(name="minecraftstop", description="マイクラサーバーを停止します")
    async def palstop(self, interaction: discord.Interaction):
        await interaction.response.defer()
        os.system("sudo systemctl stop minecraftserver")
        await interaction.followup.send("停止完了")

    @app_commands.command(name="restart", description="botを再起動します")
    async def restart(self, interaction: discord.Interaction):
        await interaction.response.send_message("再起動完了")
        os.system("sudo systemctl restart genshin-artifacter")

    # @app_commands.command(name="load", description="指定されたcogをロードします")
    # @app_commands.check(is_admin)
    # async def loadExtention(self, interaction: discord.Interaction, cogName: str, guildID: int):
    #     print("loading selected cogs...")
    #     if guildID is None:
    #         await self.bot.load_extension(cogName)
    #         await self.bot.tree.sync()
    #     else:
    #         await self.bot.load_extension(cogName)
    #         await self.bot.tree.sync(guild=discord.Object(id=guildID))
    #     await interaction.response.send_message("ロード完了")


def init_manage(adminServer, adminChannel):
    global GadminServer, GadminChannel
    GadminServer = adminServer
    GadminChannel = adminChannel


def help_manage():
    commandList = [
        [":x:/say", "発言させます\n"],
        ["/delete_messages", "コマンドが実行されたテキストチャンネルの指定されたユーザの最新のメッセージを指定された数だけ遡って削除します\n"],
        [":x:/adminsay", "サーバーID、チャンネルIDを元にメッセージを送信します\n"],
        ["/palstart", "パルワールドサーバーを起動します\n"],
        ["/palstop", "パルワールドサーバーを停止します\n"],
        ["/minecraftstart", "マイクラサーバーを起動します\n"],
        ["/minecraftstop", "マイクラサーバーを停止します\n"],
        ["/restart", "botを再起動します\n"]
    ]
    return commandList


async def send_console(message):
    global bott
    guild = bott.get_guild(int(GadminServer))
    channel = guild.get_channel(int(GadminChannel))
    await channel.send(message)


async def send(guild_id, channel_id, message):
    print("send function")
    global bott
    guild = bott.get_guild(int(guild_id))
    channel = guild.get_channel(int(channel_id))
    await channel.send(message)


async def setup(bot):
    await bot.add_cog(ManageCog(bot))
