from discord.ext import commands
from discord import app_commands
import discord
import time
import os
from dotenv import load_dotenv
import datetime
from mylogger import getLogger
logger = getLogger(__name__)


load_dotenv()
adminID = os.environ['adminID']


def is_admin(interaction: discord.Interaction):
    return str(interaction.user.id) == str(adminID)

# commands.Cogを継承する


class ManageCog(commands.Cog):
    def __init__(self, bot):
        global bott
        self.bot = bot
        bott = bot
        self.AdminID = adminID
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
        logger.info(f"{member.display_name}'s last {limit} messages deleted.")
        await interaction.followup.send(
            f"{member.display_name}'s last {limit} messages deleted."
        )

    @app_commands.command(name="adminsay", description="開発者専用")
    @app_commands.check(is_admin)
    async def send_message(self, interaction: discord.Interaction, guild_id: str, channel_id: str, message: str):
        guild = self.bot.get_guild(int(guild_id))
        channel = guild.get_channel(int(channel_id))
        await interaction.response.send_message("送信完了")
        await channel.send(message)

    @app_commands.command(name="palstart", description="パルワールドサーバーを起動します")
    async def palstart(self, interaction: discord.Interaction):
        await interaction.response.defer()
        os.system("steamcmd +login anonymous +app_update 2394010 validate +quit")
        os.system("sudo systemctl start PalServer")
        logger.info(f"PalServer started excuted by {interaction.user.name}")
        await interaction.followup.send("起動完了 sssumaa.com:8211")

    @app_commands.command(name="palstop", description="パルワールドサーバーを停止します")
    async def palstop(self, interaction: discord.Interaction):
        await interaction.response.defer()
        os.system("sudo systemctl stop PalServer")
        logger.info(f"PalServer stopped excuted by {interaction.user.name}")
        await interaction.followup.send("停止完了")

    @app_commands.command(name="minecraftstart", description="マイクラサーバーを起動します")
    async def palstart(self, interaction: discord.Interaction):
        await interaction.response.defer()
        os.system("sudo systemctl start minecraftserver")
        logger.info(
            f"MinecraftServer started excuted by {interaction.user.name}")
        await interaction.followup.send("起動完了 sssumaa.com:25565")

    @app_commands.command(name="minecraftstop", description="マイクラサーバーを停止します")
    async def palstop(self, interaction: discord.Interaction):
        await interaction.response.defer()
        os.system("sudo systemctl stop minecraftserver")
        logger.info(
            f"MinecraftServer stopped excuted by {interaction.user.name}")
        await interaction.followup.send("停止完了")

    @app_commands.command(name="restart", description="botを再起動します")
    async def restart(self, interaction: discord.Interaction):
        await interaction.response.send_message("再起動します")
        logger.info(f"Restart excuted by {interaction.user.name}")
        os.system("sudo systemctl restart genshin-artifacter")

    @app_commands.command(name="reloadcog", description="指定したcogを更新します")
    async def reloadcog(self, interaction: discord.Interaction, cogname: str):
        await interaction.response.defer()
        print("reload cog...", cogname)
        await self.bot.reload_extension(cogname)
        await self.bot.tree.sync()
        await interaction.followup.send("リロード完了")

    @app_commands.command(name="loadcog", description="cogをロードします")
    async def loadcog(self, interaction: discord.Interaction, cogname: str):
        await interaction.response.defer()
        print("load cog...", cogname)
        await self.bot.load_extension(cogname)
        await self.bot.tree.sync()
        await interaction.followup.send("ロード完了")

    @app_commands.command(name="timeout", description="指定した時間、メンションされたユーザーをタイムアウトします。")
    @commands.has_permissions(administrator=True)
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, time: str):
        if member.id == self.AdminID:
            print("bot管理者をタイムアウトすることはできません。")
            logger.info(f"{interaction.user.name} tried to timeout bot admin.")
            await interaction.response.send_message("bot管理者をタイムアウトすることはできません。")
            return
        timeUnit = time[-1]
        timeoutDuration = time[:-1]
        if not timeoutDuration.isdigit():
            await interaction.response.send_message("時間は数値で指定してください。")
            return

        timeoutDuration = int(timeoutDuration)
        if timeUnit == "秒":
            await member.timeout(datetime.timedelta(seconds=timeoutDuration))
            unit = "秒"
        elif timeUnit == "分":
            await member.timeout(datetime.timedelta(minutes=timeoutDuration))
            unit = "分"
        elif timeUnit == "時日":
            await member.timeout(datetime.timedelta(hours=timeoutDuration))
            unit = "時"
        elif timeUnit == "日":
            await member.timeout(datetime.timedelta(days=timeoutDuration))
            unit = "日"
        else:
            await interaction.response.send_message("時間の単位が不正です。秒、分、時、日のいずれかを使用してください。")
            return
        logger.info(
            f"{interaction.user.name} timed out {member.name} for {timeoutDuration}{unit}")
        await interaction.response.send_message("タイムアウトを実行しました。", ephemeral=True)

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
