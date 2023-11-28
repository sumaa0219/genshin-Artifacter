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
import csv
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
import wave

load_dotenv()


TOKEN = os.environ['token']

adminID = os.environ['adminID']


servers = [425854769668816896]
baseURL = "https://enka.network/ui/"

connected_channel = {}


with open('./API-docs/store/characters.json', 'r', encoding="utf-8") as json_file:
    characters = json.load(json_file)

with open('./API-docs/store/loc.json', 'r', encoding="utf-8") as json_file:
    nameItem = json.load(json_file)

# discord.opus.load_opus("libopus.dylib")
discord.opus.load_opus("/usr/local/Cellar/opus/1.4/lib/libopus.dylib")
intents = discord.Intents.default()  # 適当に。
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
flag = 0
defaultUID = None
modeFlag = 0


@client.event
async def on_ready():
    update_task()
    print("起動完了")
    await tree.sync()  # スラッシュコマンドを同期


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
            print(User_UID_Data)
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
                print("はじめて")
                new = [int(interaction.user.id), int(self.uid.value), None]
                User_UID_Data.append(new)
                print(User_UID_Data)

                pd.DataFrame(User_UID_Data).to_csv(
                    "./assetData/user_UID_data.csv", index=False, header=False)

            global DataBase, showAvatarlist, PlayerInfo
            DataBase, showAvatarlist, PlayerInfo = arttifacter.getData(
                int(self.uid.value))

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


@tree.command(name="build", description="UIDから聖遺物ビルドを生成します")
async def build_command(interaction: discord.Interaction):
    User_UID_Data = pd.read_csv(
        "./assetData/user_UID_data.csv", header=None).values.tolist()
    print(interaction.user.id)

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
            time.sleep(0.5)
    await interaction.followup.send(
        f"{member.display_name}'s last {limit} messages deleted."
    )


@tree.command(name="ip", description="get ip")
@app_commands.check(is_bot)
async def say_command(interaction: discord.Interaction):
    res = requests.get('https://ifconfig.me')
    await interaction.response.send_message(res.text)


@tree.command(name="id", description="get ip")
@app_commands.check(is_bot)
async def id_command(interaction: discord.Interaction):
    await interaction.response.send_message(os.getpid())


@tree.command(name="selectfavoritecharacter", description="ビルド生成時にオリジナルの画像を使用できるように登録します")
async def select(interaction: discord.Interaction, photurl: str):
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
    if interaction.user.voice is None:
        await interaction.response.send_message("ボイスチャンネルに接続していません", ephemeral=True)
        return

    if interaction.guild.voice_client is not None:  # 他のボイスチャンネルに接続していた場合
        await interaction.guild.voice_client.move_to(interaction.user.voice.channel)
        await interaction.response.send_message("ボイスチャンネルを移動しました", ephemeral=False)
        return

    await interaction.user.voice.channel.connect()
    await interaction.response.send_message("接続しました")
    connected_channel[interaction.guild_id] = interaction.channel_id

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


@client.event
async def on_message(message):

    # コマンドをコマンドとしてトリガーし、読み上げから除外
    if message.content.startswith("/"):
        return

    # botの発言は無視
    if message.author.bot:
        return

    # 読み上げ

    if message.channel.id in connected_channel.values() and message.guild.voice_client is not None:
        read_msg = message.content

        # 話者の設定の読み込み
        with open("./VC/user_speaker.json", "r", encoding="UTF-8")as f:
            speaker = json.load(f)
        try:
            speaker_id = int(speaker[str(message.author.id)])
        except:
            speaker_id = 8

        # 辞書置換
        if os.path.isfile(f"./VC/{message.guild.id}.json"):
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

        # debug
        print(read_msg)

        voiceFileName = voicevox.text_2_wav(read_msg, speaker_id)

        # # 音声読み上げ
        enqueue(message.guild.voice_client, message.guild, discord.FFmpegPCMAudio(
            voiceFileName))

        # # 音声ファイル削除
        with wave.open(voiceFileName, "rb")as f:
            wave_length = (f.getnframes() / f.getframerate()/100)  # 再生時間
        # logger.info(f"PlayTime:{wave_length}")
        await asyncio.sleep(wave_length + 10)

        os.remove(voiceFileName)


@client.event
async def on_voice_state_update(member, before, after):
    if (member.guild.voice_client is not None and member.id != client.user.id and member.guild.voice_client.channel is before.channel and len(member.guild.voice_client.channel.members) == 1):  # ボイスチャンネルに自分だけ参加していたら
        await member.guild.voice_client.disconnect()
        return

    if after is not before and after.self_mute is before.self_mute and after.self_stream is before.self_stream and after.self_deaf is before.self_deaf:
        await asyncio.sleep(1)
        if before.channel is None:
            read_msg = f"{member.display_name}が参加しました"
        elif after.channel is None:
            read_msg = f"{member.display_name}が退出しました"

        print(read_msg)

        voiceFileName = voicevox.text_2_wav(read_msg, 30)

        # print(member.guild.voice_client, member.guild)
        # # # 音声読み上げ
        if member.guild.voice_client and member.guild.voice_client.is_connected():
            enqueue(member.guild.voice_client, member.guild, discord.FFmpegPCMAudio(
                voiceFileName))

            # 音声ファイル削除
            with wave.open(voiceFileName, "rb")as f:
                wave_length = (f.getnframes() / f.getframerate()/100)  # 再生時間

            await asyncio.sleep(wave_length + 5)

        os.remove(voiceFileName)


client.run(TOKEN)
