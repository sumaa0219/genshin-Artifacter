import discord
from discord import app_commands
from discord.ext import commands
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

load_dotenv()


TOKEN = os.environ['token']


servers = [425854769668816896]
baseURL = "https://enka.network/ui/"




with open('./API-docs/store/characters.json', 'r', encoding="utf-8") as json_file:
    characters = json.load(json_file)

with open('./API-docs/store/loc.json', 'r', encoding="utf-8") as json_file:
    nameItem = json.load(json_file)



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





            global DataBase,showAvatarlist,PlayerInfo
            DataBase,showAvatarlist,PlayerInfo = arttifacter.getData(int(self.uid.value))

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

            for x in showAvatarlist:
                charaID = x["avatarId"]
                HashID = characters[str(charaID)]["NameTextMapHash"]
                charaName = nameItem["ja"][str(HashID)]
                charaLv = x["level"]
                showCharaNameList.append(charaName)
                showCharaLevelList.append(charaLv)
                
            

            for i,x in enumerate(showCharaNameList):
                view.selectMenu.add_option(
                    label=x,
                    description="Lv:"+ str(showCharaLevelList[i]),
                    value=i,
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

            global showAvatarlist,showAvatarData 
            ProfileAvatarID = showAvatarlist[int(select.values[0])]["avatarId"]
            showAvatarData = showAvatarlist[int(select.values[0])]



            ProfileAvatarname = characters[str(ProfileAvatarID)]["SideIconName"]
            name = ProfileAvatarname.split("_")
            AvatarNameURL = baseURL + name[0] + "_" +name[1]+"_"+name[3]+".png"

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
            global selectCharacterID,DataBase
            DataBase = DataBase[int(selectCharacterID)]
            ScoreState = select.values[0]
            selectCharaID = showAvatarlist[int(selectCharacterID)]["avatarId"]
            selectCharaHashID = characters[str(selectCharaID)]["NameTextMapHash"]
 
            # print(AvatarINFOlist)
            # print(ScoreState)
            global Name
            Name = nameItem["ja"][str(selectCharaHashID)]
            if Name == "旅人":#主人公の元素判断
                TravelerElementID = DataBase["skillDepotId"]
                TravelerElement = characters[str(selectCharaID) + "-" + str(TravelerElementID)]["Element"]
                Element = arttifacter.transeElement(TravelerElement)
                Name = Name + "(" + Element + ")"
                
            
            arttifacter.genJson(DataBase,showAvatarData,ScoreState)
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

@tree.command(name="delete_messages",description="Deletes a lot messages from 200 messegases",)
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






client.run(TOKEN)
