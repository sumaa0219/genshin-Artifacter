from discord.ext import commands
from discord import app_commands, ui
import discord
import pandas as pd
import time
import HSRImageGen.HSR as HSR
import HSRImageGen.format as HSRformat
import HSRImageGen.imageGen as HSRImageGen
import os
from dotenv import load_dotenv
from mylogger import getLogger
logger = getLogger(__name__)

load_dotenv()
adminID = os.environ['adminID']
baseHsrUrl = "https://enka.network/ui/hsr/"

# commands.Cogを継承する


class StarrailCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.default_user = None
        self.default_HSR_UID = None

    # イベントリスナー(ボットが起動したときやメッセージを受信したとき等)
    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog starrail.py ready!")

    @app_commands.command(name="buildhsr", description="崩壊スターレイルのUIDから遺物ビルドを生成します")
    async def buid_hsr(self, interaction: discord.Interaction):
        User_UID_Data_HSR = pd.read_csv(
            "./assetData/user_UID_data_hsr.csv", header=None).values.tolist()
        try:
            print(f"<HSR buid command>\n**{interaction.guild.name}**:{interaction.guild_id}\n**{interaction.channel.name}**:{interaction.channel_id}\n**userName**:{interaction.user.name}  **userID**:{interaction.user.id}")
        except AttributeError as e:
            logger.debug(f"Guild/Channel info unavailable: {e}")

        self.default_user = interaction.user.id
        self.default_HSR_UID = 0
        for x in User_UID_Data_HSR:
            if x[0] == interaction.user.id:
                self.default_HSR_UID = x[1]
                break

        modal = InputHSRUID(self)
        await interaction.response.send_modal(modal)


class InputHSRUID(ui.Modal):
    def __init__(self, cog: StarrailCog):
        super().__init__(
            title="崩壊スターレイルのUIDを入力してください",
        )
        self.cog = cog
        self.uid = discord.ui.TextInput(
            label="UID",
            default=self.cog.default_HSR_UID,
        )
        self.add_item(self.uid)

    async def on_submit(self, interaction: discord.Interaction) -> None:
        if interaction.user.id == self.cog.default_user or interaction.user.id == int(adminID):
            # すでに登録されているUIDを取得もしくは新規登録
            User_UID_Data_HSR = pd.read_csv(
                "./assetData/user_UID_data_hsr.csv", header=None).values.tolist()
            wronFlag = 0

            for i, x in enumerate(User_UID_Data_HSR):
                if int(x[0]) == interaction.user.id:  # ID同じ場合
                    if int(x[1]) == int(self.uid.value):  # 同じかつUIDが同じ場合
                        pass
                    elif int(x[1]) != int(self.uid.value):  # UIDだけ違う場合
                        User_UID_Data_HSR[i][1] = str(self.uid.value)
                        pd.DataFrame(User_UID_Data_HSR).to_csv(
                            "./assetData/user_UID_data_hsr.csv", index=False, header=False)
                else:  # IDが違う
                    wronFlag += 1

            if wronFlag == len(User_UID_Data_HSR):
                new = [str(interaction.user.id), str(self.uid.value)]
                User_UID_Data_HSR.append(new)
                print(User_UID_Data_HSR)

                pd.DataFrame(User_UID_Data_HSR).to_csv(
                    "./assetData/user_UID_data_hsr.csv", index=False, header=False)

            self.cog.default_HSR_UID = int(self.uid.value)
            # プレイヤーデータの取得
            try:
                playerInfo, showCharaInfoList = HSR.getInfo(
                    int(self.uid.value))
            except Exception as e:
                logger.error(f"Failed to get HSR player info: {e}")
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
            view = SelectHSRCharacter(self.cog, showCharaInfoList)
            embed.set_footer(text="UID: " + str(self.uid.value))
            print("UID:"+str(self.uid.value))

            for i, x in enumerate(showCharaInfoList):
                view.selectMenu.add_option(
                    label=HSR.getNamefromHash("ja",
                                              str(HSR.getCharacaterInfo(str(x.nameId))["AvatarName"]["Hash"])),
                    description="Lv:" + str(x.level),
                    value=i,
                )

            await interaction.response.send_message(embeds=[embed], view=view)


class SelectHSRCharacter(ui.View):
    def __init__(self, cog: StarrailCog, showCharaInfoList):
        super().__init__()
        self.cog = cog
        self.showCharaInfoList = showCharaInfoList

    @discord.ui.select(
        cls=ui.Select,
        placeholder="キャラクターを選択",
    )
    async def selectMenu(self, interaction: discord.Interaction, select: ui.Select):
        if interaction.user.id == self.cog.default_user or interaction.user.id == int(adminID):
            selectCharacterID = int(select.values[0])
            await interaction.response.defer(thinking=True)
            res = HSR.getDataFromUID(self.cog.default_HSR_UID)
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


def help_starrail():
    command_list = [
        ["/buildhsr", "崩壊スターレイルのUIDから遺物ビルドを生成します\n"],
    ]
    return command_list


async def setup(bot):
    await bot.add_cog(StarrailCog(bot))
