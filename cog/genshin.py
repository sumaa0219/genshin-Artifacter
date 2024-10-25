from discord.ext import commands
from discord import app_commands, ui
import discord
from ArtifacterImageGen.Generater import generation, read_json
from PIL import Image
import pandas as pd
import json
import os
from dotenv import load_dotenv
import shutil
import artifacter2
import requests
from io import BytesIO
import asyncio
import time
from mylogger import getLogger
logger = getLogger(__name__)

baseURL = "https://enka.network/ui/"
load_dotenv()
adminID = os.environ['adminID']

with open('./API-docs/store/characters.json', 'r', encoding="utf-8") as json_file:
    characters = json.load(json_file)

with open('./API-docs/store/loc.json', 'r', encoding="utf-8") as json_file:
    nameItem = json.load(json_file)

# commands.Cogを継承する


class GenshinCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.defaultUID = None
        self.defaultUser = None
        self.modeFlag = 0
        self.photoURL = ""
        self.user = ""
        self.showAvatarlist = []
        self.showAvatarData = None
        self.selectCharacterID = None
        self.DataBase = None
        self.PlayerInfo = None
        self.Name = None

    # イベントリスナー(ボットが起動したときやメッセージを受信したとき等)
    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog genshin.py ready!")

    @app_commands.command(name="build", description="原神のUIDから聖遺物ビルドを生成します")
    async def build_command(self, interaction: discord.Interaction):
        User_UID_Data = pd.read_csv(
            "./assetData/user_UID_data.csv", header=None).values.tolist()
        try:
            print(
                f"<Genshin buid command>\n**{interaction.guild.name}**:{interaction.guild_id}\n**{interaction.channel.name}**:{interaction.channel_id}\n**userName**:{interaction.user.name}  **userID**:{interaction.user.id}")
        except:
            pass

        self.modeFlag = 0
        self.defaultUser = interaction.user.id
        self.defaultUID = None
        for x in User_UID_Data:
            if x[0] == interaction.user.id:
                self.defaultUID = x[1]
                break

        modal = InputUID(self)
        await interaction.response.send_modal(modal)

    @app_commands.command(name="selectfavoritecharacter", description="ビルド生成時にオリジナルの画像を使用できるように登録します")
    async def select(self, interaction: discord.Interaction, photourl: str):
        self.photoURL = photourl
        self.user = interaction.user
        self.modeFlag = 1
        User_UID_Data = pd.read_csv(
            "./assetData/user_UID_data.csv", header=None).values.tolist()
        print(interaction.user.id)

        self.defaultUser = interaction.user.id
        self.defaultUID = None
        for x in User_UID_Data:
            if x[0] == interaction.user.id:
                self.defaultUID = x[1]
                break

        modal = InputUID(self)
        await interaction.response.send_modal(modal)

    @app_commands.command(name="deletefavoritecharacter", description="オリジナルの画像を削除します")
    async def delselect(self, interaction: discord.Interaction):
        User_UID_Data = pd.read_csv(
            "./assetData/user_UID_data.csv", header=None).values.tolist()
        for i, x in enumerate(User_UID_Data):
            if interaction.user.id == x[0]:
                try:
                    shutil.rmtree("ArtifacterImageGen/character/" +
                                  x[2]+"(" + interaction.user.name+")")
                except:
                    pass
                User_UID_Data[i][2] = None
                pd.DataFrame(User_UID_Data).to_csv(
                    "./assetData/user_UID_data.csv", index=False, header=False)
                await interaction.response.send_message(content="削除完了しました")


class SelectCharacter(ui.View):
    def __init__(self, cog):
        super().__init__()
        self.cog = cog

    @discord.ui.select(
        cls=ui.Select,
        placeholder="キャラクターを選択",
    )
    async def selectMenu(self, interaction: discord.Interaction, select: ui.Select):
        if interaction.user.id == self.cog.defaultUser or interaction.user.id == adminID:
            if self.cog.modeFlag == 0:
                view = SelectScoreState(self.cog)
                embed = discord.Embed(
                    title=self.cog.PlayerInfo[0], color=discord.Color.blurple())

                self.cog.showAvatarData = self.cog.showAvatarlist[int(
                    select.values[0])]
                ProfileAvatarID = self.cog.showAvatarData["avatarId"]

                ProfileAvatarname = characters[str(
                    ProfileAvatarID)]["SideIconName"]
                name = ProfileAvatarname.split("_")
                AvatarNameURL = baseURL + \
                    name[0] + "_" + name[1] + "_" + name[3] + ".png"

                self.cog.selectCharacterID = select.values[0]
                embed.set_image(url=AvatarNameURL)
                await interaction.response.edit_message(embeds=[embed], view=view)

            elif self.cog.modeFlag == 1:
                self.cog.selectCharacterID = select.values[0]

                DataBase = self.cog.DataBase[int(self.cog.selectCharacterID)]
                selectCharaID = self.cog.showAvatarlist[int(
                    self.cog.selectCharacterID)]["avatarId"]
                selectCharaHashID = characters[str(
                    selectCharaID)]["NameTextMapHash"]
                Name = nameItem["ja"][str(selectCharaHashID)]

                User_UID_Data = pd.read_csv(
                    "./assetData/user_UID_data.csv", header=None).values.tolist()

                for i, x in enumerate(User_UID_Data):
                    if x[0] == self.cog.user.id:
                        if Name == x[2]:
                            setOriginalCharacter(
                                self.cog.photoURL, 1, Name, self.cog.user.name)
                        else:
                            setOriginalCharacter(
                                self.cog.photoURL, 2, Name, self.cog.user.name, x[2])
                            User_UID_Data[i][2] = Name
                            pd.DataFrame(User_UID_Data).to_csv(
                                "./assetData/user_UID_data.csv", index=False, header=False)

                await interaction.response.edit_message(content="変更完了しました", embed=None, view=None)


class SelectScoreState(ui.View):
    def __init__(self, cog):
        super().__init__()
        self.cog = cog

    @discord.ui.select(
        cls=ui.Select,
        placeholder="ビルド画像を生成",
        options=[
            discord.SelectOption(label="攻撃パーセンテージ"),
            discord.SelectOption(label="HPパーセンテージ"),
            discord.SelectOption(label="元素チャージ効率"),
            discord.SelectOption(label="元素熟知"),
            discord.SelectOption(label="防御パーセンテージ"),
        ],
    )
    async def selectMenu(self, interaction: discord.Interaction, select: ui.Select):
        if interaction.user.id == self.cog.defaultUser or interaction.user.id == adminID:
            self.cog.DataBase = self.cog.DataBase[int(
                self.cog.selectCharacterID)]
            ScoreState = select.values[0]
            selectCharaID = self.cog.showAvatarlist[int(
                self.cog.selectCharacterID)]["avatarId"]
            selectCharaHashID = characters[str(
                selectCharaID)]["NameTextMapHash"]

            self.cog.Name = nameItem["ja"][str(selectCharaHashID)]
            if self.cog.Name == "旅人":
                TravelerElementID = self.cog.DataBase["skillDepotId"]
                TravelerElement = characters[str(
                    selectCharaID) + "-" + str(TravelerElementID)]["Element"]
                Element = artifacter2.transeElement(TravelerElement)
                self.cog.Name = self.cog.Name + "(" + Element + ")"

            authorInfo = interaction.user
            artifacter2.genJson(
                self.cog.DataBase, self.cog.showAvatarData, ScoreState, authorInfo)
            time.sleep(0.3)
            await interaction.response.defer(thinking=True)
            generate()
            with open('./ArtifacterImageGen/data.json', 'r', encoding="utf-8") as json_file:
                data = json.load(json_file)
            const = data["Character"]["Const"]
            if int(const) == 0:
                const_message = "無凸"
            elif int(const) == 6:
                const_message = "完凸"
            else:
                const_message = str(const) + "凸"
            message = self.cog.PlayerInfo[0] + ":" + str(
                self.cog.defaultUID) + "の" + str(self.cog.Name) + " " + const_message
            await asyncio.sleep(0.5)
            await interaction.message.delete()
            await interaction.followup.send(content=message, file=discord.File(fp="./ArtifacterImageGen/Image.png"))


class InputUID(ui.Modal):
    def __init__(self, cog):
        super().__init__(title="原神のUIDを入力してください")
        self.cog = cog
        self.uid = discord.ui.TextInput(
            label="UID", default=self.cog.defaultUID)
        self.add_item(self.uid)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if interaction.user.id == self.cog.defaultUser or interaction.user.id == int(adminID):
            User_UID_Data = pd.read_csv(
                "./assetData/user_UID_data.csv", header=None).values.tolist()
            pd.set_option('display.float_format', lambda x: '%.0f' % x)
            wronFlag = 0
            await interaction.response.defer()
            for i, x in enumerate(User_UID_Data):
                if x[0] == interaction.user.id:
                    if int(x[1]) == int(self.uid.value):
                        pass
                    elif int(x[1]) != int(self.uid.value):
                        User_UID_Data[i][1] = int(self.uid.value)
                        pd.DataFrame(User_UID_Data).to_csv(
                            "./assetData/user_UID_data.csv", index=False, header=False)
                else:
                    wronFlag += 1

            if wronFlag == len(User_UID_Data):
                new = [int(interaction.user.id), int(self.uid.value), None]
                User_UID_Data.append(new)
                print(User_UID_Data)
                pd.DataFrame(User_UID_Data).to_csv(
                    "./assetData/user_UID_data.csv", index=False, header=False)

            self.cog.defaultUID = int(self.uid.value)
            try:
                self.cog.DataBase, self.cog.showAvatarlist, self.cog.PlayerInfo = artifacter2.getData(
                    int(self.uid.value))
            except Exception as e:
                await interaction.followup.send(str(e))
                return

            embed = discord.Embed(
                title=self.cog.PlayerInfo[0], color=discord.Color.blurple())
            embed.set_thumbnail(url=self.cog.PlayerInfo[4])
            embed.add_field(name="冒険者ランク", value=self.cog.PlayerInfo[1])
            embed.add_field(name="世界ランク", value=self.cog.PlayerInfo[2])
            embed.set_image(url=self.cog.PlayerInfo[3])
            view = SelectCharacter(self.cog)
            embed.set_footer(text="UID: " + str(self.uid.value))
            print("UID:" + str(self.uid.value))

            showCharaNameList = []
            showCharaLevelList = []
            for x in self.cog.showAvatarlist:
                charaID = x["avatarId"]
                HashID = characters[str(charaID)]["NameTextMapHash"]
                charaName = nameItem["ja"][str(HashID)]
                charaLv = x["level"]
                showCharaNameList.append(charaName)
                showCharaLevelList.append(charaLv)

            for i, x in enumerate(showCharaNameList):
                view.selectMenu.add_option(
                    label=x,
                    description="Lv:" + str(showCharaLevelList[i]),
                    value=i,
                )

            # await interaction.response.send_message(embeds=[embed], view=view)
            await interaction.followup.send(embeds=[embed], view=view)


def generate():
    generation(read_json('ArtifacterImageGen/data.json'))


def setOriginalCharacter(url, mode, Name, userName, beforName=None):
    background = Image.new("RGBA", (2048, 1024), (0, 0, 0, 0))

    response = requests.get(url)
    image = Image.open(BytesIO(response.content))

    if image.mode != "RGBA":
        image = image.convert("RGBA")

    new_height = 1024
    original_width, original_height = image.size
    new_width = int(original_width * (new_height / original_height))
    resized_image = image.resize((new_width, new_height))

    if "A" in resized_image.getbands():
        alpha = resized_image.split()[3]
        center_x = (background.width - resized_image.width) // 2
        center_y = (background.height - resized_image.height) // 2
        background.paste(resized_image, (center_x, center_y), mask=alpha)
    else:
        center_x = (background.width - resized_image.width) // 2
        center_y = (background.height - resized_image.height) // 2
        background.paste(resized_image, (center_x, center_y))

    save_path = "ArtifacterImageGen/character/" + \
        Name + "(" + userName + ")/avatar.png"

    if mode == 1:
        pass
    elif mode == 2:
        shutil.copytree("ArtifacterImageGen/character/" + Name,
                        "ArtifacterImageGen/character/" + Name + "(" + userName + ")")
        try:
            shutil.rmtree("ArtifacterImageGen/character/" +
                          beforName + "(" + userName + ")")
        except:
            pass

    background.save(save_path)


def help_genshin():
    command_list = [
        ["/build", "原神のuidを入力することでプロフィールに設定しているキャラ1体の詳細をビルドカードにして表示します。\n**※ただし原神のプロフィールでキャラの詳細を表示を許可しないとできません**\n"],
        ["/selectfavoritecharacter",
            "ビルドカード生成時に1体のキャラクターに対してオリジナルの画像を使用できるように登録します。登録には画像の**URL**が必要です。\n"],
        ["/deletefavoritecharacter", "キャラクターのオリジナルの画像を削除します\n"],
    ]
    return command_list


async def setup(bot):
    await bot.add_cog(GenshinCog(bot))
