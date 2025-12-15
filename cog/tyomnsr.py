from discord.ext import commands
from discord import app_commands
import discord
import random
import datetime
import jsonDB
import math
from mylogger import getLogger
logger = getLogger(__name__)

serverID = 929432903534923857
announcementChannelID = 929436378301886484
moderaterOnlyChannelID = 1161612212243284089
tyomnserUserData = {}
userDataFile = "assetData/typmnsr.json"
nakanoFlag = False


class TyomnsrCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.gomikasuFlag = False

    @commands.Cog.listener()
    async def on_ready(self):
        loadUserData()
        print("Cog tyomnsr.py ready!")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        global tyomnserUserData
        if member.guild.id == serverID:
            setupUser(member.id)
            channnel = self.bot.get_guild(
                serverID).get_channel(announcementChannelID)
            await channnel.send(f"やったー！\n{member.mention} を　つかまえたぞ！")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        global tyomnserUserData
        userName = member.display_name
        if member.guild.id == serverID:
            del tyomnserUserData[member.id]
            channnel = self.bot.get_guild(
                serverID).get_channel(announcementChannelID)
            await channnel.send(f"{userName}を　逃がしてあげた\nばいばい　{userName}")

    @app_commands.command(name="nakano", description="中野への返信を切り替えます。")
    @app_commands.guilds(serverID)
    @commands.has_permissions(administrator=True)
    async def nakano(self, interaction: discord.Interaction):
        global nakanoFlag
        if nakanoFlag == False:
            nakanoFlag = True
            await interaction.response.send_message("中野への返信を有効にしました。", ephemeral=True)
        else:
            nakanoFlag = False
            await interaction.response.send_message("中野への返信を無効にしました。", ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        global tyomnserUserData
        pass
        if message.author.bot:
            return
        else:
            if message.guild.id == serverID:
                if message.author.id == 812948479973523486 and nakanoFlag == True:
                    await message.reply("ざーこ")
                try:
                    loadUserData()
                    userID = str(message.author.id)
                    addExp = random.randint(1, 5)
                    data = tyomnserUserData[userID]
                    level = data["level"]
                    data["exp"] += addExp
                    data["expCum"] += addExp
                    data["commentNum"] += 1
                    data["userName"] = message.author.display_name
                    jsonDB.update_db(userDataFile, userID, data)
                    levelUpFlag = checkLevelUp(userID, int(level))
                    if levelUpFlag == True:
                        announceChannnel = self.bot.get_guild(
                            serverID).get_channel(announcementChannelID)
                        await announceChannnel.send(f"{message.author.mention} がLv.{level + 1}にレベルアップした！")
                except KeyError as e:
                    logger.debug(f"User not registered in DB: {e}")

            if self.gomikasuFlag == True:
                if message.content == "!gomikasu" or message.content == "ゴミカス" or message.content == "ごみかす":
                    await message.channel.send("https://cdn.discordapp.com/attachments/929437569123516446/1299313779443499018/RPReplay_Final1620286734.mov?ex=671cbfc1&is=671b6e41&hm=10e7edc3fcc0c5fdb4c0ece22744c305f78d2a8f73f5ce28a153d02e2bfcbb5d&")

    @app_commands.command(name="gomikasu", description="ゴミカスを切り替えます ")
    @app_commands.guilds(serverID)
    async def gomikasu(self, interaction: discord.Interaction):
        if self.gomikasuFlag == False:
            self.gomikasuFlag = True
            await interaction.response.send_message("ゴミカスを有効にしました。")
        else:
            self.gomikasuFlag = False
            await interaction.response.send_message("ゴミカスを無効にしました。")

    @app_commands.command(name="rank", description="レベルを確認します。")
    @app_commands.guilds(serverID)
    async def rank(self, interaction: discord.Interaction, member: discord.Member):
        global tyomnserUserData
        loadUserData()
        userID = str(member.id)
        level = tyomnserUserData[userID]["level"]
        exp = tyomnserUserData[userID]["exp"]
        expCum = tyomnserUserData[userID]["expCum"]
        commentNum = tyomnserUserData[userID]["commentNum"]
        tPoint = tyomnserUserData[userID]["tPoint"]
        neccesarExp = get_neccesarExp(level)
        await interaction.response.send_message(f"{member.mention}のステータス\nLv.{level}\n**経験値**:{exp}/{neccesarExp} Exp\n**累計経験値**:{expCum}\n**コメント数**:{commentNum}\n**Tポイント**:{tPoint}")

    @app_commands.command(name="adduser", description="ユーザーを追加します。(はやくやれ)")
    @app_commands.guilds(serverID)
    async def addUser(self, interaction: discord.Interaction, member: discord.Member):
        setupUser(member.id, member.display_name)
        await interaction.response.send_message("ユーザーを追加しました。")

    @app_commands.command(name="ranking", description="累計経験値順にランキングを表示します。")
    @app_commands.guilds(serverID)
    async def ranking(self, interaction: discord.Interaction):
        global tyomnserUserData
        loadUserData()
        ranking = sorted(tyomnserUserData.items(),
                         key=lambda x: x[1]["expCum"], reverse=True)
        rank = 1
        rankMessage = "ランキング\n"
        for user in ranking:
            rankMessage += f"{rank}位 **{user[1]['userName']}**\t累計経験値:{user[1]['expCum']}\n"
            rank += 1
        await interaction.response.send_message(rankMessage)

    @app_commands.command(name="roleranking", description="role(同一人物の複数アカウントをまとめた)ごとの累計経験値順にランキングを表示します。")
    @app_commands.guilds(serverID)
    async def roleranking(self, interaction: discord.Interaction):
        global tyomnserUserData
        loadUserData()
        roleRanking = {}
        removeList = []
        addFromAtherAccount = 0
        for user in tyomnserUserData.values():
            if str(user["userID"]) not in removeList:
                try:
                    linkAccountList = user["link"]
                except KeyError as e:
                    logger.debug(f"No linked accounts found for user: {e}")
                    linkAccountList = []

                if len(linkAccountList) > 0:
                    for linkAccount in linkAccountList:
                        addFromAtherAccount += tyomnserUserData[str(
                            linkAccount)]["expCum"]
                        removeList.append(str(linkAccount))
                else:
                    addFromAtherAccount = 0
                roleRanking[user["userName"]] = user["expCum"] + \
                    addFromAtherAccount

        ranking = sorted(roleRanking.items(), key=lambda x: x[1], reverse=True)
        rank = 1
        rankMessage = "ランキング\n"
        for user in ranking:
            rankMessage += f"{rank}位 **{user[0]}**\t累計経験値:{user[1]}\n"
            rank += 1
        await interaction.response.send_message(rankMessage)

    @app_commands.command(name="checklevel", description="ユーザーのレベルを再計算します。")
    @app_commands.guilds(serverID)
    @commands.has_permissions(administrator=True)
    async def checkLevel(self, interaction: discord.Interaction, member: discord.Member):
        global tyomnserUserData
        loadUserData()
        userID = str(member.id)
        level = tyomnserUserData[userID]["level"]
        levelUpFlag = checkLevelUp(userID, int(level))
        while levelUpFlag == True:
            levelUpFlag = checkLevelUp(userID, int(level))
            loadUserData()
            level = tyomnserUserData[userID]["level"]

        await interaction.response.send_message(f"{member.mention}のレベルを再計算しました。", ephemeral=True)


def loadUserData():
    global tyomnserUserData
    tyomnserUserData = jsonDB.read_db(userDataFile)


def setupUser(userID: int, userName: str):
    global tyomnserUserData
    newData = {
        "userID": userID,
        "userName": userName,
        "level": 1,
        "exp": 0,
        "expCum": 0,
        "commentNum": 0,
        "tPoint": 0,
    }
    print(newData)

    jsonDB.update_db(userDataFile, str(userID), newData)


def get_neccesarExp(level: int):
    if level <= 30:
        neccesarExp = (
            9326.75901744283 * math.exp(0.07031758954601629 * level) - 9400.389398914305)/10
    elif level >= 30 and level <= 100:
        neccesarExp = (17439.307465577403 *
                       math.exp(0.09038117561749462 * level) - 2069901.34556948)/5
    elif level > 100:
        print("level over 100")
        neccesarExp = (17439.307465577403 *
                       math.exp(0.09038117561749462 * level) - 2069901.34556948)*2
    return int(neccesarExp)


def checkLevelUp(userID, level: int):
    neccesarExp = get_neccesarExp(level)
    data = tyomnserUserData[userID]
    if int(data["exp"]) >= neccesarExp:
        data["level"] += 1
        data["exp"] = data["exp"] - neccesarExp
        jsonDB.update_db(userDataFile, userID, data)
        return True
    else:
        return False


async def setup(bot):
    await bot.add_cog(TyomnsrCog(bot))
