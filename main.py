import discord
from discord import app_commands
from discord.ext import commands
from discord import ui
import os
from dotenv import load_dotenv
import arttifacter
import pandas as pd
import asyncio
import time
import ArtifacterImageGen.Generater as gen
import csv

load_dotenv()


TOKEN = os.environ['token']


servers = [425854769668816896]


CharacterInfodata = pd.read_csv("./assetData/CharacterInfo.csv", header=None).values.tolist()
CharaInfo = pd.read_csv("./assetData/chara.csv", header=None).values.tolist()





intents = discord.Intents.default()#適当に。
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
flag = 0
defaultUID = None

@client.event
async def on_ready():
    print("起動完了")
    await tree.sync()#スラッシュコマンドを同期


class InputUID(ui.Modal):
    global defaultUID
    def __init__(self):
        super().__init__(
            title="原神のUIDを入力してください",
        )
        self.uid = discord.ui.TextInput(
            label="UID",
            default = defaultUID,
            )
        self.add_item(self.uid)


    async def on_submit(self, interaction: discord.Interaction) -> None:
        global defaultUser
        if interaction.user.id == defaultUser:
            User_UID_Data = pd.read_csv("./assetData/user_UID_data.csv", header=None).values.tolist()
            data = []
            dataSet = []
            wronFlag = 0
            for x in User_UID_Data:
                if x[0] == interaction.user.id:#ID同じ場合
                    print("justID")
                    if int(x[1]) == int(self.uid.value): #同じかつUIDが同じ場合
                        print("same_all")
                        data=[x[0],x[1]]
                    elif int(x[1]) is not  int(self.uid.value):#UIDだけ違う場合
                        data=[x[0],int(self.uid.value)]
                        print("same_user")
                    dataSet.append(data)
                else:#IDが違う
                    print("diffrent")
                    wronFlag += 1
                    data=[x[0],x[1]]
                    dataSet.append(data)
            
            if wronFlag == len(User_UID_Data):
                data = [interaction.user.id,self.uid.value]
                dataSet.append(data)
                print("newID")

            with open('assetData/user_UID_data.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                for row in dataSet:
                    writer.writerow(row)

            file.close()





            global DataBase,showAvatarlist,AvatarINFOlist,PlayerInfo
            DataBase,showAvatarlist,AvatarINFOlist,PlayerInfo = arttifacter.getData(int(self.uid.value))

            embed = discord.Embed(title=PlayerInfo[0], color=discord.Color.blurple())
            embed.set_thumbnail(url=PlayerInfo[4])
            embed.add_field(name="冒険者ランク", value=PlayerInfo[1] )
            embed.add_field(name="世界ランク", value=PlayerInfo[2])
            embed.set_image(url=PlayerInfo[3])
            view = SelectCharacter()
            embed.set_footer(text="UID: " + str(self.uid.value))
            print("UID:"+str(self.uid.value))

            showCharaNameList = []
            showCharaLevelList = []

            global selectStatus
            # selectStatus = 0

            for x in showAvatarlist:
                charaID = DataBase[int(DataBase[x]["avatarId"])]
                charaLv = DataBase[int(DataBase[x]["level"])]
                for y in CharacterInfodata:
                    if y[0] == charaID:
                        charaName = y[2]
                    else:
                        pass
                showCharaNameList.append(charaName)
                showCharaLevelList.append(charaLv)

            for x in range(len(showCharaNameList)):
                view.selectMenu.add_option(
                    label=showCharaNameList[x],
                    description="Lv:"+ str(showCharaLevelList[x]),
                    value=showAvatarlist[x],
                )
            

            await interaction.response.send_message(embeds=[embed],view=view)

            # while selectStatus == 0:
            #     await asyncio.sleep(1)
        else:
            pass
            

   

    
class SelectCharacter(ui.View):
    @discord.ui.select(
        cls=ui.Select,
        placeholder="キャラクターを選択",


    )
    async def selectMenu(self, interaction: discord.Interaction, select: ui.Select):
        if interaction.user.id == defaultUser:
            view = SelectScoreState()
            embed = discord.Embed(title=PlayerInfo[0], color=discord.Color.blurple())
            for x in CharaInfo:
                baseAvatar = "https://enka.network/ui/UI_AvatarIcon_"
                if x[0] == DataBase[int(DataBase[int(select.values[0])]["avatarId"])]:
                    AvatarNameURL = baseAvatar + x[1] + ".png"
                else:
                    pass
            global selectCharacterID
            selectCharacterID = select.values[0]
            embed.set_image(url=AvatarNameURL)
            await interaction.response.edit_message(embeds=[embed],view=view) 
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
        if interaction.user.id == defaultUser:
            global selectCharacterID,selectID
            ScoreState = select.values[0]
            selectID = DataBase[int(selectCharacterID)]["avatarId"]
 
            # print(AvatarINFOlist)
            # print(ScoreState)
            global Name
            Name = DataBase[selectID]
            for x in CharacterInfodata:
                if Name == x[0]:
                    if Name == 10000005 or Name == 10000007:#主人公の元素判断
                        TravererSklillId = DataBase[int(DataBase[int(AvatarInfo["inherentProudSkillList"])][0])]
                        for y in TravereInfo:
                            if int(y[1]) == int(TravererSklillId):
                                print("getElment")
                                Element = y[0]
                            else:
                                pass
                    
                        Name = x[2] +"(" + Element +")"

                    elif Name == 10000041 and int(defaultUser) == 672094270072553533:
                        Name = x[2] + "(ゴリラ)"
                        Element = x[3]


                    else:
                        Name = x[2]
                        Element = x[3]
                else:
                    pass
            
            arttifacter.genJson(DataBase,int(selectID),AvatarINFOlist,ScoreState,defaultUser)
            time.sleep(0.3)
            await interaction.response.defer(thinking=True)
            generate()
            message = PlayerInfo[0] +":"+str(defaultUID)+"の" + str(Name)
            await asyncio.sleep(0.5)
            await interaction.message.delete()
            await interaction.followup.send(content=message,file=discord.File(fp="ArtifacterImageGen/Image.png"))
        else:
            pass

def generate():
    gen.generation(gen.read_json('ArtifacterImageGen/data.json'))
    

@tree.command(name= "build",description="UIDから聖遺物ビルドを生成します")
async def build_command(interaction: discord.Interaction):
    User_UID_Data = pd.read_csv("./assetData/user_UID_data.csv", header=None).values.tolist()
    print(interaction.user.id)


    global defaultUID,defaultUser
    defaultUser = interaction.user.id
    defaultUID = None
    for x in User_UID_Data:
        
        if x[0] == interaction.user.id:
            defaultUID = x[1]
            
        else:
            if defaultUID == None:
                print("bbb")
                defaultUID = None
    # print(defaultUID)
    modal = InputUID()
    await interaction.response.send_modal(modal)

def is_bot(interaction: discord.Interaction):
    return interaction.user.id == 425853700112908289





@tree.command(name= "say",description="発言させます")
@app_commands.check(is_bot)
async def say_command(interaction: discord.Interaction,text:str):
 
    await interaction.response.send_message(text)




client.run(TOKEN)
