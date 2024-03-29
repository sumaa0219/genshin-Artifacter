import discord
from discord import app_commands
from discord.ext import commands, tasks
from discord import ui
import os
from dotenv import load_dotenv
import artifacter2 as arttifacter
import pandas as pd
import asyncio
import time
import ArtifacterImageGen.Generater as gen
import json
import requests
import datetime
from PIL import Image
import shutil
from io import BytesIO
import pprint
import re
import voicevox
from collections import defaultdict, deque
import glob
import argparse
import HSRImageGen.HSR as HSR
import HSRImageGen.format as HSRformat
import HSRImageGen.imageGen as HSRImageGen

parser = argparse.ArgumentParser()
parser.add_argument("--debug", action="store_true", help="Use the debug token")
args = parser.parse_args()

load_dotenv()

if args.debug:
    TOKEN = os.environ['debug']
    adminChannel = os.environ['adminDebugChannel']
    print("------------------debug mode------------------")
else:
    TOKEN = os.environ['token']
    adminChannel = os.environ['adminChannel']


adminID = os.environ['adminID']

adminServer = os.environ['adminServer']


baseURL = "https://enka.network/ui/"
baseHsrUrl = "https://enka.network/ui/hsr/"

connected_channel = {}
vc_connected_channel = {}


with open('./API-docs/store/characters.json', 'r', encoding="utf-8") as json_file:
    characters = json.load(json_file)

with open('./API-docs/store/loc.json', 'r', encoding="utf-8") as json_file:
    nameItem = json.load(json_file)


# mac用
# discord.opus.load_opus("libopus.dylib")
# discord.opus.load_opus("/usr/local/Cellar/opus/1.4/lib/libopus.dylib")

# ubuntu用
discord.opus.load_opus("libopus.so.0")
discord.opus.load_opus("/usr/lib/x86_64-linux-gnu/libopus.so.0")

intents = discord.Intents.default()  # 適当に。
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
flag = 0
defaultUID = None
default_HSR_UID = None
modeFlag = 0


@client.event
async def on_ready():
    update_task()
    await send_console("起動しました")
    files = glob.glob(f"/home/sumaa/genshin-Artifacter/VC/*.wav")
    for file in files:
        os.remove(file)
    await tree.sync()  # スラッシュコマンドを同期

    # 何秒おきに確認するか？
    interval_seconds = 60
    # 定期的なタスクを作成

    @tasks.loop(seconds=interval_seconds)
    async def task_message():
        task_keys_list = list(taskList.keys())
        for key in task_keys_list:
            guild_id = 0
            channel_id = 0
            message = ""
            if taskList[key]["status"] == "active":
                dt_now = datetime.datetime.now()
                if dt_now.strftime('%H%M') == str(taskList[key]["time"]["h"])+str(taskList[key]["time"]["m"]):
                    guild_id = taskList[key]["serverID"]
                    channel_id = taskList[key]["chanelID"]
                    message = taskList[key]["message"]
                    guild = client.get_guild(guild_id)
                    channel = guild.get_channel(channel_id)
                    await channel.send(message)

    # タスクを開始
    task_message.start()


class inputHSRUID(ui.Modal):
    def __init__(self):
        super().__init__(
            title="崩壊スターレイルのUIDを入力してください",
        )
        self.uid = discord.ui.TextInput(
            label="UID",
            default=default_HSR_UID,
        )
        self.add_item(self.uid)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        global default_HSR_UID, defaultUser
        if interaction.user.id == defaultUser or interaction.user.id == int(adminID):

            # すでに登録されているUIDを取得もしくは新規登録
            User_UID_Data_HSR = pd.read_csv(
                "./assetData/user_UID_data_hsr.csv", header=None).values.tolist()
            wronFlag = 0

            for i, x in enumerate(User_UID_Data_HSR):
                if int(x[0]) == interaction.user.id:  # ID同じ場合
                    if int(x[1]) == int(self.uid.value):  # 同じかつUIDが同じ場合
                        pass
                    elif int(x[1]) is not int(self.uid.value):  # UIDだけ違う場合
                        User_UID_Data_HSR[i][1] = str(self.uid.value)
                        pd.DataFrame(User_UID_Data_HSR).to_csv(
                            "./assetData/user_UID_data_hsr.csv", index=False, header=False)
                else:  # IDが違う
                    wronFlag += 1

            if wronFlag == len(User_UID_Data_HSR):
                new = [str(interaction.user.id), str(self.uid.value)]
                User_UID_Data_HSR.append(new)
                await send_console(User_UID_Data_HSR)

                pd.DataFrame(User_UID_Data_HSR).to_csv(
                    "./assetData/user_UID_data_hsr.csv", index=False, header=False)

            # プレイヤーデータの取得
            try:
                playerInfo, showCharaInfoList = HSR.getInfo(
                    int(self.uid.value))
            except:
                errer_msg = HSR.getInfo(
                    int(self.uid.value))
                await interaction.response.send_message(errer_msg)
                return
            embed = discord.Embed(
                title=playerInfo.name, color=discord.Color.blurple())
            embed.set_thumbnail(url=baseHsrUrl +
                                HSR.getAvatorURL(int(playerInfo.headIcon)))
            embed.add_field(name="開拓者レベル", value=playerInfo.level)
            embed.add_field(name="均衡レベル", value=playerInfo.worldLevel)
            embed.add_field(name="フレンド数", value=playerInfo.friendCount)
            view = SelectHSRCharacter()
            embed.set_footer(text="UID: " + str(self.uid.value))
            await send_console("UID:"+str(self.uid.value))

            for i, x in enumerate(showCharaInfoList):
                view.selectMenu.add_option(
                    label=HSR.getNamefromHash("ja",
                                              str(HSR.getCharacaterInfo(str(x.nameId))["AvatarName"]["Hash"])),
                    description="Lv:" + str(x.level),
                    value=i,
                )

            await interaction.response.send_message(embeds=[embed], view=view)


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
        global defaultUser

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
                await send_console(User_UID_Data)

                pd.DataFrame(User_UID_Data).to_csv(
                    "./assetData/user_UID_data.csv", index=False, header=False)

            global DataBase, showAvatarlist, PlayerInfo
            try:
                DataBase, showAvatarlist, PlayerInfo, = arttifacter.getData(
                    int(self.uid.value))
            except:
                errer_msg = arttifacter.getData(
                    int(self.uid.value))
                await interaction.response.send_message(errer_msg)
                return

            embed = discord.Embed(
                title=PlayerInfo[0], color=discord.Color.blurple())
            embed.set_thumbnail(url=PlayerInfo[4])
            embed.add_field(name="冒険者ランク", value=PlayerInfo[1])
            embed.add_field(name="世界ランク", value=PlayerInfo[2])
            embed.set_image(url=PlayerInfo[3])
            view = SelectCharacter()
            embed.set_footer(text="UID: " + str(self.uid.value))
            await send_console("UID:"+str(self.uid.value))

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


class SelectHSRCharacter(ui.View):
    @discord.ui.select(
        cls=ui.Select,
        placeholder="キャラクターを選択",


    )
    async def selectMenu(self, interaction: discord.Interaction, select: ui.Select):
        global default_HSR_UID, defaultUser
        if interaction.user.id == int(defaultUser) or interaction.user.id == adminID:

            global selectCharacterID
            selectCharacterID = select.values[0]
            await interaction.response.defer(thinking=True)
            res = HSR.getDataFromUID(default_HSR_UID)
            charaInfoData, weaponInfo, relicList, skillList, relicSetList = HSRformat.formatCharaData(
                res["detailInfo"]["avatarDetailList"][int(selectCharacterID)])
            HSRImageGen.HSR_generate(
                "ja", charaInfoData, weaponInfo, relicList, skillList, relicSetList)

            if charaInfoData.rank == 0:
                rankMessage = "無凸"
            elif charaInfoData.rank == 6:
                rankMessage = "完凸"
            else:
                rankMessage = str(charaInfoData.rank) + "凸"
            message = res["detailInfo"]["nickname"]+":" + res["uid"] + \
                "("+interaction.user.display_name + ")の" + HSR.getNamefromHash("ja",
                                                                               str(charaInfoData.nameHash)) + " " + rankMessage
            time.sleep(0.7)
            await interaction.message.delete()
            await interaction.followup.send(content=message, file=discord.File(fp="HSRImageGen/output.png"))


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
                Element = arttifacter.transeElement(TravelerElement)
                Name = Name + "(" + Element + ")"

            authorInfo = interaction.user

            arttifacter.genJson(DataBase, showAvatarData,
                                ScoreState, authorInfo)
            time.sleep(0.3)
            await interaction.response.defer(thinking=True)
            generate()
            message = PlayerInfo[0] + ":"+str(defaultUID)+"の" + str(Name)
            await asyncio.sleep(0.5)
            await interaction.message.delete()
            await interaction.followup.send(content=message, file=discord.File(fp="ArtifacterImageGen/Image.png"))
        else:
            pass


def generate():
    gen.generation(gen.read_json('ArtifacterImageGen/data.json'))


@tree.command(name="buildhsr", description="崩壊スターレイルのUIDから遺物ビルドを生成します")
async def buid_hsr(interaction: discord.Interaction):
    global defaultUser, default_HSR_UID
    User_UID_Data_HSR = pd.read_csv(
        "./assetData/user_UID_data_hsr.csv", header=None).values.tolist()
    try:
        await send_console(f"<HSR buid command>\n**{interaction.guild.name}**:{interaction.guild_id}\n**{interaction.channel.name}**:{interaction.channel_id}\n**userName**:{interaction.user.name}  **userID**:{interaction.user.id}")
    except:
        pass

    defaultUser = interaction.user.id
    default_HSR_UID = 0
    for x in User_UID_Data_HSR:

        if x[0] == interaction.user.id:
            default_HSR_UID = x[1]

        else:
            if default_HSR_UID == None:
                default_HSR_UID = None
    # print(defaultUID)
    modal = inputHSRUID()
    await interaction.response.send_modal(modal)


@tree.command(name="build", description="原神のUIDから聖遺物ビルドを生成します")
async def build_command(interaction: discord.Interaction):
    User_UID_Data = pd.read_csv(
        "./assetData/user_UID_data.csv", header=None).values.tolist()
    try:
        await send_console(f"<Genshin buid command>\n**{interaction.guild.name}**:{interaction.guild_id}\n**{interaction.channel.name}**:{interaction.channel_id}\n**userName**:{interaction.user.name}  **userID**:{interaction.user.id}")
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


def is_bot(interaction: discord.Interaction):
    return interaction.user.id == 425853700112908289


@tree.command(name="say", description="発言させます")
@app_commands.check(is_bot)
async def say_command(interaction: discord.Interaction, text: str):

    await interaction.response.send_message(text)


@tree.command(name="delete_messages", description="Deletes a lot messages from 200 messegases",)
async def delete_messages(interaction: discord.Interaction, member: discord.Member, limit: int):
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


@tree.command(name="selectfavoritecharacter", description="ビルド生成時にオリジナルの画像を使用できるように登録します")
async def select(interaction: discord.Interaction, photurl: str):
    global user, modeFlag, photoURL
    photoURL = photurl
    user = interaction.user
    modeFlag = 1
    User_UID_Data = pd.read_csv(
        "./assetData/user_UID_data.csv", header=None).values.tolist()
    await send_console(interaction.user.id)

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


@tree.command(name="deletefavoritecharacter", description="オリジナルの画像を削除します")
async def delselect(interaction: discord.Interaction):
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


def update_task():
    global taskList
    with open('assetData/task.json', 'r', encoding="utf-8") as json_file:
        taskList = json.load(json_file)


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

# ボイスチャンネルに接続


@tree.command(name="join", description="ボイスチャンネルに接続します")
async def join(interaction: discord.Interaction):
    clear_queue(interaction.guild_id)
    await send_console(f"<join command>\n**{interaction.guild.name}**:{interaction.guild_id}\n**{interaction.channel.name}**:{interaction.channel_id}\n**userName**:{interaction.user.name}  **userID**:{interaction.user.id}")
    if interaction.user.voice is None:
        await interaction.response.send_message("ボイスチャンネルに接続していません", ephemeral=True)
        return

    if interaction.guild.voice_client is not None:  # 他のボイスチャンネルに接続していた場合
        await interaction.guild.voice_client.move_to(interaction.user.voice.channel)
        await interaction.response.send_message("ボイスチャンネルを移動しました", ephemeral=False)
        return
    connected_channel[int(interaction.guild_id)] = interaction.channel_id
    vc_connected_channel[int(interaction.guild_id)
                         ] = interaction.user.voice.channel.id

    await interaction.response.send_message("接続しました")
    await interaction.user.voice.channel.connect()


# ボイスチャンネルから切断


@tree.command(name="disconnect", description="ボイスチャンネルから切断します")
async def disconnect(interaction: discord.Interaction):
    if interaction.user.voice is None:
        await interaction.response.send_message("ボイスチャンネルに接続していません", ephemeral=True)
        return

    await interaction.guild.voice_client.disconnect(force=True)
    await interaction.response.send_message("切断しました")
    connected_channel.pop(interaction.guild_id)

# 辞書

# 辞書を読み込み


def load_dict(interaction: discord.Interaction):
    if os.path.isfile(f"./VC/{interaction.guild.id}.json"):
        with open(f"./VC/{interaction.guild.id}.json", "r", encoding="UTF-8")as f:
            dict = json.load(f)
    else:
        dict = {}
    return dict

# 辞書に単語と読み方を追加


@tree.command(name="add", description="辞書に単語の読み方登録します")
async def addWords(interaction: discord.Interaction, vocabulary: str, pronunciation: str):
    if not os.path.exists("VC"):
        os.makedirs("VC")
    if not os.path.exists(f"./VC/{interaction.guild.id}.json"):
        newJson = {}
        with open(f"./VC/{interaction.guild.id}.json", "w", encoding="UTF-8")as f:
            json.dump(newJson, f, indent=2, ensure_ascii=False)
    word = load_dict(interaction)

    word[vocabulary] = pronunciation
    with open(f"./VC/{interaction.guild.id}.json", "w", encoding="UTF-8")as f:
        f.write(json.dumps(word, indent=2, ensure_ascii=False))
    dict_add_embed = discord.Embed(title="辞書追加", color=0x3399cc)
    dict_add_embed.add_field(name="単語", value=f"{vocabulary}", inline="false")
    dict_add_embed.add_field(
        name="読み", value=f"{pronunciation}", inline="false")
    await interaction.response.send_message(embed=dict_add_embed)

# 登録されている単語の読み方を削除


@tree.command(name="delete", description="辞書に単語の読み方削除します")
async def delWords(interaction: discord.Interaction, vocabulary: str):
    word = load_dict(interaction)
    del word[vocabulary]
    with open(f"./VC/{interaction.guild.id}.json", "w", encoding="UTF-8")as f:
        f.write(json.dumps(word, indent=2, ensure_ascii=False))
    await interaction.response.send_message(f"辞書から`{vocabulary}`を削除しました")
    return

# 登録されてる単語を表示


@tree.command(name="list", description="辞書に登録された単語を表示します")
async def listWords(interaction: discord.Interaction):
    word = load_dict(interaction)
    await interaction.response.send_message("辞書を表示します\n```" + pprint.pformat(word, depth=1) + "```")


class SelectSpeakerTention(ui.View):
    @discord.ui.select(
        cls=ui.Select,
        placeholder="読み上げキャラクターのテンション",


    )
    async def selectMenu(self, interaction: discord.Interaction, select: ui.Select):
        fileName = "./VC/user_speaker.json"
        if os.path.isfile(fileName):
            with open(fileName, "r", encoding="UTF-8")as f:
                dict = json.load(f)
        else:
            dict = {}
        dict[interaction.user.id] = select.values[0]
        with open(fileName, "w", encoding="UTF-8")as f:
            json.dump(dict, f, indent=2, ensure_ascii=False)
        await interaction.response.send_message(f"変更が完了しました")


class SelectSpeaker(ui.View):
    @discord.ui.select(
        cls=ui.Select,
        placeholder="読み上げキャラクター",


    )
    async def selectMenu(self, interaction: discord.Interaction, select: ui.Select):
        view = SelectSpeakerTention()
        for info in speakerInfo[int(select.values[0])]["styles"]:
            view.selectMenu.add_option(
                label=info["name"],
                value=info["id"]
            )
        await interaction.response.send_message("テンション一覧", view=view)


@tree.command(name="selectspeaker", description="話者の変更を行います")
async def selectSpeaker(interaction: discord.Interaction):
    global speakerInfo
    with open(f"./VC/speaker.json", "r", encoding="UTF-8")as f:
        speakerInfo = json.load(f)
    view = SelectSpeaker()
    for i, info in enumerate(speakerInfo):
        view.selectMenu.add_option(
            label=info["name"],
            value=i
        )
    await interaction.response.send_message("一覧", view=view)


# # メッセージが送られた時

# キュー
queue_dict = defaultdict(deque)


def enqueue(voice_client, guild, source):
    queue = queue_dict[guild.id]
    queue.append(source)
    if not voice_client.is_playing():
        play(voice_client, queue)


def play(voice_client, queue):
    if not queue or voice_client.is_playing():
        return
    source = queue.popleft()
    voice_client.play(source, after=lambda e: play(voice_client, queue))


def clear_queue(guild_id):
    if guild_id in queue_dict:
        del queue_dict[guild_id]


@client.event
async def on_message(message):

    # コマンドをコマンドとしてトリガーし、読み上げから除外
    if message.content.startswith("/"):
        return

    # # botの発言は無視
    # if message.author.bot:
    #     return

    # 読み上げ

    if message.channel.id in connected_channel.values() and message.guild.voice_client is not None:
        read_msg = message.content
        # await send_console(read_msg)

        # 話者の設定の読み込み
        with open("./VC/user_speaker.json", "r", encoding="UTF-8")as f:
            speaker = json.load(f)
        try:
            speaker_id = int(speaker[str(message.author.id)])
        except:
            speaker_id = 8

        read_msg = read_msg.replace("_", "")  # アンダーバー削除
        # 辞書置換
        if os.path.isfile(f"VC/{message.guild.id}.json"):
            with open(f"./VC/{message.guild.id}.json", "r", encoding="UTF-8")as f:
                word = json.load(f)
            read_list = []  # あとでまとめて変換するときの読み仮名リスト
            # one_dicは単語と読みのタプル。添字はそれぞれ0と1。
            for i, one_dic in enumerate(word.items()):
                read_msg = read_msg.replace(one_dic[0], '{'+str(i)+'}')
                read_list.append(one_dic[1])  # 変換が発生した順に読みがなリストに追加
            read_msg = read_msg.format(*read_list)  # 読み仮名リストを引数にとる

        # URL置換
        read_msg = re.sub(r"https?://.*?\s|https?://.*?$", "URL", read_msg)

        # ネタバレ置換
        read_msg = re.sub(r"\|\|.*?\|\|", "ネタバレ", read_msg)

        # メンション置換
        if "<@" and ">" in message.content:
            Temp = re.findall("<@!?([0-9]+)>", message.content)
            for i in range(len(Temp)):
                Temp[i] = int(Temp[i])
                user = message.guild.get_member(Temp[i])
                read_msg = re.sub(
                    f"<@!?{Temp[i]}>", "アットマーク" + user.display_name, read_msg)

        # サーバー絵文字置換
        read_msg = re.sub(r"<:(.*?):[0-9]+>", r"\1", read_msg)

        # *text*置換
        read_msg = re.sub(r"\*(.*?)\*", r"\1", read_msg)

        # _hoge_置換
        read_msg = re.sub(r"_(.*?)_", r"\1", read_msg)

        try:
            await send_console("**"+message.guild.name+"**"+message.author.name+":"+read_msg)
        except:
            pass

        if len(read_msg) > 40:
            read_msg = read_msg[:40] + '以下略'
        # debug
        # 音声読み上げ
        voice_data = voicevox.text_2_wav(read_msg, speaker_id)

        # BytesIOオブジェクトを作成
        byte_io = BytesIO(voice_data)

        # 音声を再生
        source = discord.FFmpegPCMAudio(byte_io, pipe=True)
        enqueue(message.guild.voice_client, message.guild, source)

        # # # 音声ファイル削除
        # with wave.open(voiceFileName, "rb")as f:
        #     wave_length = (f.getnframes() / f.getframerate()/100)  # 再生時間
        # # logger.info(f"PlayTime:{wave_length}")
        # await asyncio.sleep(wave_length + 10)

        # os.remove(voiceFileName)

    # URL自動変換

    # # URLを見つけるための正規表現パターン
    # url_pattern = re.compile(r"(https?://[^\s]+)")

    # # メッセージ内のURLを見つける
    # urls = url_pattern.findall(message.content)

    # # URLを変換する
    # for url in urls:
    #     if "vxtwitter.com" in url:
    #         pass
    #     elif "twitter.com" in url or "x.com" in url:
    #         new_url = url.replace("twitter.com", "vxtwitter.com").replace(
    #             "x.com", "vxtwitter.com")

    #         await message.reply(f"{new_url}")


@client.event
async def on_voice_state_update(member, before, after):
    read_msg = ""
    print(queue_dict)
    if (member.guild.voice_client is not None and member.id != client.user.id and member.guild.voice_client.channel is before.channel and len(member.guild.voice_client.channel.members) == 1):  # ボイスチャンネルに自分だけ参加していたら
        await member.guild.voice_client.disconnect()
        return

    if before.channel is not None and client.user in before.channel.members or after.channel is not None and client.user in after.channel.members:
        if before.channel is not None and before.channel != after.channel and client.user in before.channel.members:
            read_msg = f"{member.display_name}が退出しました"
        if after.channel is not None and before.channel != after.channel and client.user in after.channel.members:
            read_msg = f"{member.display_name}が参加しました"

        try:
            await send_console(f"<Status chenged viceChannel>**{member.guild.name}**  :{read_msg}")
        except:
            pass

        with open("./VC/user_speaker.json", "r", encoding="UTF-8")as f:
            speaker = json.load(f)
        try:
            speaker_id = int(speaker[str(member.id)])
        except:
            speaker_id = 8

        # 辞書置換
        if os.path.isfile(f"./VC/{member.guild.id}.json"):
            with open(f"./VC/{member.guild.id}.json", "r", encoding="UTF-8")as f:
                word = json.load(f)
            read_list = []  # あとでまとめて変換するときの読み仮名リスト
            # one_dicは単語と読みのタプル。添字はそれぞれ0と1。
            for i, one_dic in enumerate(word.items()):
                read_msg = read_msg.replace(one_dic[0], '{'+str(i)+'}')
                read_list.append(one_dic[1])  # 変換が発生した順に読みがなリストに追加
            read_msg = read_msg.format(*read_list)  # 読み仮名リストを引数にとる

        voice_data = voicevox.text_2_wav(read_msg, speaker_id)

        # BytesIOオブジェクトを作成
        byte_io = BytesIO(voice_data)

        # 音声を再生
        source = discord.FFmpegPCMAudio(byte_io, pipe=True)
        enqueue(member.guild.voice_client, member.guild, source)

        try:
            await send_console(read_msg)
        except:
            pass


@tree.command(name="addtask", description="指定時間に毎日送信するメッセージ追加できます。メッセージはこのコマンドが使われたところに送信されます")
async def addTask(interaction: discord.Interaction, taskname: str, hour: str, minutes: str, message: str):
    global taskList
    newtask = {
        taskname: {
            "status": "active",
            "time": {
                "h": hour,
                "m": minutes
            },
            "serverID": interaction.guild.id,
            "chanelID": interaction.channel.id,
            "DMID": "",
            "userID": interaction.user.id,
            "message": message
        }
    }
    taskList.update(newtask)  # 新規タスクをtaskListに追加
    with open('assetData/task.json', 'w', encoding="utf-8") as json_file:
        json.dump(taskList, json_file, ensure_ascii=False, indent=2)
    update_task()

    await interaction.response.send_message(f"新規タスク`{taskname}'を{hour}時{minutes}分に追加しました。")


@tree.command(name="switchtask", description="指定されたタスクのアクティブ状態を切り替えます")
async def addTask(interaction: discord.Interaction, taskname: str):
    global taskList
    if taskList[taskname]["status"] == "active":
        taskList[taskname]["status"] = "inactive"
        await interaction.response.send_message(f"タスク`{taskname}'を無効化しました。")
    else:
        taskList[taskname]["status"] = "active"
        await interaction.response.send_message(f"タスク`{taskname}'を有効化しました。")
    with open('assetData/task.json', 'w', encoding="utf-8") as json_file:
        json.dump(taskList, json_file, ensure_ascii=False, indent=2)
    update_task()


@tree.command(name="deletetask", description="指定されたタスクを削除します")
async def deleteTask(interaction: discord.Interaction, taskname: str):
    global taskList
    taskList.pop(taskname)
    await interaction.response.send_message(f"タスク`{taskname}'を削除しました。")
    with open('assetData/task.json', 'w', encoding="utf-8") as json_file:
        json.dump(taskList, json_file, ensure_ascii=False, indent=2)
    update_task()


@tree.command(name="listtask", description="ユーザが作成したタスクを表示します")
async def listTask(interaction: discord.Interaction):
    global taskList
    user_taskList = []
    update_task()
    user_id = interaction.user.id  # インタラクションしたユーザーのIDを取得
    # ユーザーのタスクリストを取得（存在しない場合は空の辞書を返す）
    for task in taskList:
        if taskList[task]["userID"] == user_id:
            user_taskList.append(task)

    # タスクリストが空の場合、特定のメッセージを返す
    if not user_taskList:
        await interaction.response.send_message("タスクが登録されていません。")
        return

    embed = discord.Embed(
        title="タスク一覧", description="以下のタスクが登録されています。", color=discord.Color.blurple())
    for task in user_taskList:
        embed.add_field(
            name=task, value=f"状態:{taskList[task]['status']}\n時間:{taskList[task]['time']['h']}時{taskList[task]['time']['m']}分\nメッセージ:{taskList[task]['message']}", inline=False)
    await interaction.response.send_message(embed=embed)


@tree.command(name="help", description="各種コマンドの機能を詳しく紹介します")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="コマンド一覧", description="以下のコマンドが利用可能です。\n", color=discord.Color.blurple())

    embed.add_field(name="/help", value="全コマンドの詳細を表示します。\n", inline=False)
    embed.add_field(
        name="/build", value="原神のuidを入力することでプロフィールに設定しているキャラ1体の詳細をビルドカードにして表示します。\n**※ただし原神のプロフィールでキャラの詳細を表示を許可しないとできません**\n", inline=False)
    embed.add_field(name="/selectfavoritecharacter",
                    value="ビルドカード生成時にキャラクターにオリジナルの画像を使用できるように登録します。登録には画像の**URL**が必要です。\n", inline=False)
    embed.add_field(name="/deletefavoritecharacter",
                    value="キャラクターのオリジナルの画像を削除します\n", inline=False)
    embed.add_field(
        name="/join", value="ボイスチャンネルに接続します。/joinが実行されたテキストチャンネルをVC内で読み上げます\n", inline=False)
    embed.add_field(name="/disconnect",
                    value="ボイスチャンネルから切断します\n", inline=False)
    embed.add_field(name="/selectspeaker",
                    value="メッセージの読み上げの際、あなたのメッセージを読み上げるキャラクターを変更します\n", inline=False)
    embed.add_field(
        name="/add", value="辞書に単語と読み方を追加します。設定はサーバー単位で行われます\n", inline=False)
    embed.add_field(
        name="/delete", value="辞書に登録されている単語を削除します。設定はサーバー単位で行われます\n", inline=False)
    embed.add_field(
        name="/list", value="辞書に登録されている単語を表示します。辞書はそのサーバーで登録されたものを表示します\n", inline=False)
    embed.add_field(
        name="/addtask", value="指定時間に毎日送信するメッセージ追加できます。メッセージはこのコマンドが使われたところに送信されます。時間は24時間表記です。\n", inline=False)
    embed.add_field(name="/switchtask",
                    value="指定されたタスクのアクティブ状態を切り替えます\n", inline=False)
    embed.add_field(name="/deletetask", value="指定されたタスクを削除します\n", inline=False)
    embed.add_field(name="/listtask",
                    value="ユーザが作成したタスクを表示します\n", inline=False)
    embed.add_field(name="/delete_messages",
                    value="コマンドが実行されたテキストチャンネルの指定されたユーザの最新のメッセージを指定された数だけ遡って削除します", inline=False)

    # 他のコマンドも同様に追加してください。

    await interaction.response.send_message(embed=embed)


def update_task():
    global taskList
    with open('assetData/task.json', 'r', encoding="utf-8") as json_file:
        taskList = json.load(json_file)


async def send_console(message):
    guild = client.get_guild(int(adminServer))
    channel = guild.get_channel(int(adminChannel))
    await channel.send(message)


@tree.command(name="adminsay", description="開発者専用")
async def send_message(interaction: discord.Interaction, guild_id: str, channel_id: str, message: str):
    guild = client.get_guild(int(guild_id))
    channel = guild.get_channel(int(channel_id))
    await channel.send(message)
    await interaction.response.send_message("送信完了")


@tree.command(name="palstart", description="パルワールドサーバーを起動します")
async def palstart(interaction: discord.Interaction):
    await interaction.response.defer()
    os.system("steamcmd +login anonymous +app_update 2394010 validate +quit")
    os.system("sudo systemctl start PalServer")
    await interaction.followup.send("起動完了 sssumaa.com:8211")


@tree.command(name="palstop", description="パルワールドサーバーを停止します")
async def palstop(interaction: discord.Interaction):
    await interaction.response.defer()
    os.system("sudo systemctl stop PalServer")
    await interaction.followup.send("停止完了")

# @tree.command(name="vote", description="投票を行います")
# async def vote(interaction: discord.Interaction, title: str, options: str):
#     options = options.split()  # 選択肢を分割
#     if len(options) < 2 or len(options) > 6:
#         await interaction.channel.send("選択肢は2-6択である必要があります。")
#         return

#     reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣']

#     description = []
#     for x, option in enumerate(options):
#         description += '\n {} {}'.format(reactions[x], option)
#     embed = discord.Embed(title=title, description=''.join(description))

#     react_message = await interaction.channel.send(embed=embed)

#     for reaction in reactions[:len(options)]:
#         await react_message.add_reaction(reaction)

#     votes = {}

#     def check(reaction, user):
#         if user == interaction.user and str(reaction.emoji) in reactions[:len(options)]:
#             votes[user.id] = str(reaction.emoji)
#             return True
#         return False

#     while True:
#         try:
#             reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
#         except asyncio.TimeoutError:
#             # 投票が締め切られた後、結果を表示
#             react_message = await react_message.channel.fetch_message(react_message.id)
#             results = {
#                 react.emoji: react.count for react in react_message.reactions}
#             result_message = "\n".join(
#                 [f"{emoji}: {count}" for emoji, count in results.items()])
#             await interaction.channel.send(f'投票が締め切られました。\n結果:\n{result_message}')
#             break
#         else:
#             # リアクションが取り消されたらその人の投票も取り消す
#             def remove_check(payload):
#                 return payload.user_id == user.id and payload.message_id == react_message.id and str(payload.emoji) in reactions[:len(options)]

#             try:
#                 payload = await client.wait_for('raw_reaction_remove', timeout=60.0, check=remove_check)
#             except asyncio.TimeoutError:
#                 pass
#             else:
#                 del votes[payload.user_id]


client.run(TOKEN)
