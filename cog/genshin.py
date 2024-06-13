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

baseURL = "https://enka.network/ui/"
defaultUID = None
defaultUser = None
selectStatus = ""
user = ""
photoURL = ""
showAvatarlist = []
showAvatarData = None
selectCharacterID = None
DataBase = None
PlayerInfo = None
Name = None
modeFlag = 0
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

        global defaultUID, defaultUser, modeFlag
        modeFlag = 0
        defaultUser = interaction.user.id
        defaultUID = None
        for x in User_UID_Data:

            if x[0] == interaction.user.id:
                defaultUID = x[1]

            else:
                if defaultUID == None:
                    defaultUID = None
        # print(defaultUID)
        modal = InputUID()
        await interaction.response.send_modal(modal)

    @app_commands.command(name="selectfavoritecharacter", description="ビルド生成時にオリジナルの画像を使用できるように登録します")
    async def select(self, interaction: discord.Interaction, photurl: str):
        global user, modeFlag, photoURL
        photoURL = photurl
        user = interaction.user
        modeFlag = 1
        User_UID_Data = pd.read_csv(
            "./assetData/user_UID_data.csv", header=None).values.tolist()
        print(interaction.user.id)

        global defaultUID, defaultUser
        defaultUser = interaction.user.id
        defaultUID = None
        for x in User_UID_Data:

            if x[0] == interaction.user.id:
                defaultUID = x[1]

            else:
                if defaultUID == None:
                    defaultUID = None
        # print(defaultUID)
        modal = InputUID()
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
    @discord.ui.select(
        cls=ui.Select,
        placeholder="キャラクターを選択",


    )
    async def selectMenu(self, interaction: discord.Interaction, select: ui.Select):
        if interaction.user.id == defaultUser or interaction.user.id == adminID:
            global modeFlag

            if modeFlag == 0:
                view = SelectScoreState()
                embed = discord.Embed(
                    title=PlayerInfo[0], color=discord.Color.blurple())

                global showAvatarlist, showAvatarData
                ProfileAvatarID = showAvatarlist[int(
                    select.values[0])]["avatarId"]
                showAvatarData = showAvatarlist[int(select.values[0])]

                ProfileAvatarname = characters[str(
                    ProfileAvatarID)]["SideIconName"]
                name = ProfileAvatarname.split("_")
                AvatarNameURL = baseURL + \
                    name[0] + "_" + name[1]+"_"+name[3]+".png"

                global selectCharacterID
                selectCharacterID = select.values[0]
                embed.set_image(url=AvatarNameURL)
                await interaction.response.edit_message(embeds=[embed], view=view)

            elif modeFlag == 1:
                global DataBase, photoURL
                selectCharacterID = select.values[0]

                DataBase = DataBase[int(selectCharacterID)]
                ScoreState = select.values[0]
                selectCharaID = showAvatarlist[int(
                    selectCharacterID)]["avatarId"]
                selectCharaHashID = characters[str(
                    selectCharaID)]["NameTextMapHash"]
                Name = nameItem["ja"][str(selectCharaHashID)]

                User_UID_Data = pd.read_csv(
                    "./assetData/user_UID_data.csv", header=None).values.tolist()

                for i, x in enumerate(User_UID_Data):
                    if x[0] == user.id:
                        if Name == x[2]:
                            setOriginalCharacter(photoURL, 1, Name, user.name)
                        else:
                            setOriginalCharacter(
                                photoURL, 2, Name, user.name, x[2])
                            User_UID_Data[i][2] = Name
                            pd.DataFrame(User_UID_Data).to_csv(
                                "./assetData/user_UID_data.csv", index=False, header=False)

                await interaction.response.edit_message(content="変更完了しました", embed=None, view=None)

        else:
            pass


class SelectScoreState(ui.View):
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
        if interaction.user.id == defaultUser or interaction.user.id == adminID:
            global selectCharacterID, DataBase
            DataBase = DataBase[int(selectCharacterID)]
            ScoreState = select.values[0]
            selectCharaID = showAvatarlist[int(selectCharacterID)]["avatarId"]
            selectCharaHashID = characters[str(
                selectCharaID)]["NameTextMapHash"]

            # print(AvatarINFOlist)
            # print(ScoreState)
            global Name
            Name = nameItem["ja"][str(selectCharaHashID)]
            if Name == "旅人":  # 主人公の元素判断
                TravelerElementID = DataBase["skillDepotId"]
                TravelerElement = characters[str(
                    selectCharaID) + "-" + str(TravelerElementID)]["Element"]
                Element = artifacter2.transeElement(TravelerElement)
                Name = Name + "(" + Element + ")"

            authorInfo = interaction.user

            artifacter2.genJson(DataBase, showAvatarData,
                                ScoreState, authorInfo)
            time.sleep(0.3)
            await interaction.response.defer(thinking=True)
            generate()
            message = PlayerInfo[0] + ":"+str(defaultUID)+"の" + str(Name)
            await asyncio.sleep(0.5)
            await interaction.message.delete()
            await interaction.followup.send(content=message, file=discord.File(fp="./ArtifacterImageGen/Image.png"))
        else:
            pass


class InputUID(ui.Modal):
    global defaultUID

    def __init__(self):
        super().__init__(
            title="原神のUIDを入力してください",
        )
        self.uid = discord.ui.TextInput(
            label="UID",
            default=defaultUID,
        )
        self.add_item(self.uid)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        global defaultUser, defaultUID, modeFlag

        if interaction.user.id == defaultUser or interaction.user.id == int(adminID):
            User_UID_Data = pd.read_csv(
                "./assetData/user_UID_data.csv", header=None).values.tolist()
            pd.set_option('display.float_format', lambda x: '%.0f' % x)
            data = []
            dataSet = []
            wronFlag = 0
            for i, x in enumerate(User_UID_Data):
                if x[0] == interaction.user.id:  # ID同じ場合
                    if int(x[1]) == int(self.uid.value):  # 同じかつUIDが同じ場合
                        pass
                    elif int(x[1]) is not int(self.uid.value):  # UIDだけ違う場合
                        User_UID_Data[i][1] = int(self.uid.value)
                        pd.DataFrame(User_UID_Data).to_csv(
                            "./assetData/user_UID_data.csv", index=False, header=False)
                else:  # IDが違う
                    wronFlag += 1

            if wronFlag == len(User_UID_Data):
                new = [int(interaction.user.id), int(self.uid.value), None]
                User_UID_Data.append(new)
                print(User_UID_Data)

                pd.DataFrame(User_UID_Data).to_csv(
                    "./assetData/user_UID_data.csv", index=False, header=False)

            defaultUID = int(self.uid.value)
            global DataBase, showAvatarlist, PlayerInfo
            try:
                DataBase, showAvatarlist, PlayerInfo, = artifacter2.getData(
                    int(self.uid.value))
            except:
                errer_msg = artifacter2.getData(
                    int(self.uid.value))
                # print(errer_msg)
                await interaction.response.send_message(errer_msg)
                return

            # print(showAvatarlist)

            embed = discord.Embed(
                title=PlayerInfo[0], color=discord.Color.blurple())
            embed.set_thumbnail(url=PlayerInfo[4])
            embed.add_field(name="冒険者ランク", value=PlayerInfo[1])
            embed.add_field(name="世界ランク", value=PlayerInfo[2])
            embed.set_image(url=PlayerInfo[3])
            view = SelectCharacter()
            embed.set_footer(text="UID: " + str(self.uid.value))
            print("UID:"+str(self.uid.value))

            showCharaNameList = []
            showCharaLevelList = []

            global selectStatus

            for x in showAvatarlist:
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

            await interaction.response.send_message(embeds=[embed], view=view)

            # while selectStatus == 0:
            #     await asyncio.sleep(1)
        else:
            print("your not same person", interaction.user.id)


def generate():
    generation(read_json('ArtifacterImageGen/data.json'))


def setOriginalCharacter(url, mode, Name, userName, beforName=None):
    # 透過背景の画像を作成
    background = Image.new("RGBA", (2048, 1024), (0, 0, 0, 0))

    # 画像を取得
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))

    # 画像がRGBAモードでない場合、RGBAモードに変換
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    # 新しい縦のサイズを指定
    new_height = 1024

    # 縦のサイズを新しいサイズに変更（横幅は自動調整）
    original_width, original_height = image.size
    new_width = int(original_width * (new_height / original_height))
    resized_image = image.resize((new_width, new_height))

    # 透過度情報がある場合のみ透過背景の中央に合成
    if "A" in resized_image.getbands():
        alpha = resized_image.split()[3]

        # 透過背景の中央座標
        center_x = (background.width - resized_image.width) // 2
        center_y = (background.height - resized_image.height) // 2

        background.paste(resized_image, (center_x, center_y), mask=alpha)
    else:
        # 透過背景の中央座標
        center_x = (background.width - resized_image.width) // 2
        center_y = (background.height - resized_image.height) // 2

        background.paste(resized_image, (center_x, center_y))

    save_path = "ArtifacterImageGen/character/" + \
        Name + "(" + userName + ")/avatar.png"

    if mode == 1:  # 変わらない
        pass
        # 保存するファイル名を指定

    elif mode == 2:
        shutil.copytree("ArtifacterImageGen/character/"+Name,
                        "ArtifacterImageGen/character/" + Name + "(" + userName + ")")
        try:
            shutil.rmtree("ArtifacterImageGen/character/" +
                          beforName+"(" + userName+")")
        except:
            pass

    # 画像を指定した名前で保存
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
