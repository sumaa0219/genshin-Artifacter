from discord.ext import commands
from discord import ui, app_commands
import discord
import json
import os
import pprint
from collections import defaultdict, deque
import re
from io import BytesIO
import requests


connected_channel = {}
vc_connected_channel = {}
queue_dict = defaultdict(deque)  # キュー
mainVoicevoxURL = "http://192.168.1.200:50021/"
subVoicevoxURL = "http://localhost:50021/"


# Ubuntu用
# discord.opus.load_opus("libopus.so.0")
# discord.opus.load_opus("/usr/lib/x86_64-linux-gnu/libopus.so.0")

with open(f"./VC/speaker.json", "r", encoding="UTF-8") as f:
    speakerInfo = json.load(f)


class VoicevoxCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.source = None
        self.voice = None

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog voicevox.py ready!")

    @app_commands.command(name="join", description="ボイスチャンネルに接続します")
    async def join(self, interaction: discord.Interaction):
        self.clear_queue(interaction.guild_id)
        print(f"<join command>\n**{interaction.guild.name}**:{interaction.guild_id}\n**{interaction.channel.name}**:{interaction.channel_id}\n**userName**:{interaction.user.name}  **userID**:{interaction.user.id}")
        if interaction.user.voice is None:
            await interaction.response.send_message("ボイスチャンネルに接続していません", ephemeral=True)
            return

        if interaction.guild.voice_client is not None:  # 他のボイスチャンネルに接続していた場合
            await interaction.guild.voice_client.move_to(interaction.user.voice.channel)
            await interaction.response.send_message("ボイスチャンネルを移動しました", ephemeral=False)
        else:
            connected_channel[int(interaction.guild_id)
                              ] = interaction.channel_id
            vc_connected_channel[int(
                interaction.guild_id)] = interaction.user.voice.channel.id
            try:
                await interaction.user.voice.channel.connect(timeout=10)
                if interaction.guild.voice_client.is_connected():
                    await interaction.response.send_message("接続しました")
                else:
                    await interaction.response.send_message("接続に失敗しました", ephemeral=True)

            except Exception as e:
                print(e)

    @app_commands.command(name="disconnect", description="ボイスチャンネルから切断します")
    async def disconnect(self, interaction: discord.Interaction):
        if interaction.guild.voice_client is None:
            await interaction.response.send_message("ボイスチャンネルに接続していません", ephemeral=True)
            return

        await interaction.guild.voice_client.disconnect(force=True)
        discord.AudioSource.cleanup()
        await interaction.response.send_message("切断しました")
        connected_channel.pop(interaction.guild_id, None)

    @app_commands.command(name="add", description="辞書に単語の読み方登録します")
    async def addWords(self, interaction: discord.Interaction, vocabulary: str, pronunciation: str):
        if not os.path.exists("VC"):
            os.makedirs("VC")
        if not os.path.exists(f"./VC/{interaction.guild.id}.json"):
            newJson = {}
            with open(f"./VC/{interaction.guild.id}.json", "w", encoding="UTF-8") as f:
                json.dump(newJson, f, indent=2, ensure_ascii=False)
        word = load_dict(interaction)

        word[vocabulary] = pronunciation
        with open(f"./VC/{interaction.guild.id}.json", "w", encoding="UTF-8") as f:
            f.write(json.dumps(word, indent=2, ensure_ascii=False))
        dict_add_embed = discord.Embed(title="辞書追加", color=0x3399cc)
        dict_add_embed.add_field(
            name="単語", value=f"{vocabulary}", inline=False)
        dict_add_embed.add_field(
            name="読み", value=f"{pronunciation}", inline=False)
        await interaction.response.send_message(embed=dict_add_embed)

    @app_commands.command(name="delete", description="辞書に単語の読み方削除します")
    async def delWords(self, interaction: discord.Interaction, vocabulary: str):
        word = load_dict(interaction)
        if vocabulary in word:
            del word[vocabulary]
            with open(f"./VC/{interaction.guild.id}.json", "w", encoding="UTF-8") as f:
                f.write(json.dumps(word, indent=2, ensure_ascii=False))
            await interaction.response.send_message(f"辞書から`{vocabulary}`を削除しました")
        else:
            await interaction.response.send_message(f"`{vocabulary}` は辞書に存在しません", ephemeral=True)

    @app_commands.command(name="list", description="辞書に登録された単語を表示します")
    async def listWords(self, interaction: discord.Interaction):
        word = load_dict(interaction)
        await interaction.response.send_message("辞書を表示します\n```" + pprint.pformat(word, depth=1) + "```")

    @app_commands.command(name="selectspeaker", description="話者の変更を行います")
    async def selectSpeaker(self, interaction: discord.Interaction):
        global speakerInfo

        view = SelectSpeaker()
        for i, info in enumerate(speakerInfo):
            view.selectMenu.add_option(label=info["name"], value=i)
        await interaction.response.send_message("一覧", view=view)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.startswith("/"):
            return
        if message.channel.id in connected_channel.values() and message.guild.voice_client is not None:
            read_msg = message.content
            with open("./VC/user_speaker.json", "r", encoding="UTF-8") as f:
                speaker = json.load(f)
            try:
                speaker_id = int(speaker.get(str(message.author.id), 8))
            except ValueError:
                speaker_id = 8

            read_msg = read_msg.replace("_", "")
            if os.path.isfile(f"VC/{message.guild.id}.json"):
                with open(f"VC/{message.guild.id}.json", "r", encoding="UTF-8") as f:
                    word = json.load(f)
                read_list = []
                for i, one_dic in enumerate(word.items()):
                    read_msg = read_msg.replace(one_dic[0], '{'+str(i)+'}')
                    read_list.append(one_dic[1])
                read_msg = read_msg.format(*read_list)

            read_msg = re.sub(r"https?://.*?\s|https?://.*?$", "URL", read_msg)
            read_msg = re.sub(r"\|\|.*?\|\|", "ネタバレ", read_msg)
            if "<@" and ">" in message.content:
                Temp = re.findall("<@!?([0-9]+)>", message.content)
                for i in range(len(Temp)):
                    Temp[i] = int(Temp[i])
                    user = message.guild.get_member(Temp[i])
                    read_msg = re.sub(
                        f"<@!?{Temp[i]}>", "アットマーク" + user.display_name, read_msg)

            read_msg = re.sub(r"<:(.*?):[0-9]+>", r"\1", read_msg)
            read_msg = re.sub(r"\*(.*?)\*", r"\1", read_msg)
            read_msg = re.sub(r"_(.*?)_", r"\1", read_msg)

            try:
                print(
                    f"**{message.guild.name}** {message.author.name}: {read_msg}")
            except Exception as e:
                print(e)

            if len(read_msg) > 50:
                read_msg = read_msg[:50] + '以下略'
            voice_data = text_2_wav(read_msg, speaker_id)
            byte_io = BytesIO(voice_data)
            byte_io.seek(0)
            try:
                source = discord.FFmpegPCMAudio(byte_io, pipe=True)
                self.enqueue(message.guild.voice_client,
                             message.guild, source)
            except Exception as e:
                print(e)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        read_msg = ""
        if (member.guild.voice_client is not None and member.id != self.bot.user.id and member.guild.voice_client.channel is before.channel and len(member.guild.voice_client.channel.members) == 1):
            await member.guild.voice_client.disconnect()
            return

        if before.channel is not None and self.bot.user in before.channel.members or after.channel is not None and self.bot.user in after.channel.members:
            if before.channel is not None and before.channel != after.channel and self.bot.user in before.channel.members:
                read_msg = f"{member.display_name}が退出しました"
            if after.channel is not None and before.channel != after.channel and self.bot.user in after.channel.members:
                read_msg = f"{member.display_name}が参加しました"

            try:
                print(
                    f"<Status changed voiceChannel> **{member.guild.name}** : {read_msg}")
            except Exception as e:
                print(e)

            with open("./VC/user_speaker.json", "r", encoding="UTF-8") as f:
                speaker = json.load(f)
            try:
                speaker_id = int(speaker.get(str(member.id), 8))
            except ValueError:
                speaker_id = 8

            if os.path.isfile(f"./VC/{member.guild.id}.json"):
                with open(f"./VC/{member.guild.id}.json", "r", encoding="UTF-8") as f:
                    word = json.load(f)
                read_list = []
                for i, one_dic in enumerate(word.items()):
                    read_msg = read_msg.replace(one_dic[0], '{'+str(i)+'}')
                    read_list.append(one_dic[1])
                read_msg = read_msg.format(*read_list)

            voice_data = text_2_wav(read_msg, speaker_id)
            byte_io = BytesIO(voice_data)
            byte_io.seek(0)
            try:
                source = discord.FFmpegPCMAudio(byte_io, pipe=True)
                self.enqueue(member.guild.voice_client,
                             member.guild, source)
            except Exception as e:
                print(e)

    def enqueue(self, voice_client, guild, source):
        self.queue = queue_dict[guild.id]
        self.queue.append(source)
        if not voice_client.is_playing():
            self.play(voice_client, self.queue)

    def play(self, voice_client, queue):
        if not queue or voice_client.is_playing():
            return
        source = queue.popleft()
        voice_client.play(
            source, after=lambda e: self.play(voice_client, queue))

    def clear_queue(self, guild_id):
        if guild_id in queue_dict:
            del queue_dict[guild_id]


class SelectSpeakerTention(ui.View):
    @discord.ui.select(cls=ui.Select, placeholder="読み上げキャラクターのテンション")
    async def selectMenu(self, interaction: discord.Interaction, select: ui.Select):
        fileName = "./VC/user_speaker.json"
        if os.path.isfile(fileName):
            with open(fileName, "r", encoding="UTF-8") as f:
                dict = json.load(f)
        else:
            dict = {}
        dict[interaction.user.id] = select.values[0]
        with open(fileName, "w", encoding="UTF-8") as f:
            json.dump(dict, f, indent=2, ensure_ascii=False)
        await interaction.response.send_message(f"変更が完了しました")


class SelectSpeaker(ui.View):
    @discord.ui.select(cls=ui.Select, placeholder="読み上げキャラクター")
    async def selectMenu(self, interaction: discord.Interaction, select: ui.Select):
        view = SelectSpeakerTention()
        for info in speakerInfo[int(select.values[0])]["styles"]:
            view.selectMenu.add_option(label=info["name"], value=info["id"])
        await interaction.response.send_message("テンション一覧", view=view)


def load_dict(interaction: discord.Interaction):
    if os.path.isfile(f"./VC/{interaction.guild.id}.json"):
        with open(f"./VC/{interaction.guild.id}.json", "r", encoding="UTF-8") as f:
            dict = json.load(f)
    else:
        dict = {}
    return dict


def help_voicevox():
    command_list = [
        ["/join", "ボイスチャンネルに接続します\n"],
        ["/disconnect", "ボイスチャンネルから切断します\n"],
        ["/add", "設定したサーバのみで使える単語の読み方を辞書に登録します\n"],
        ["/delete", "設定したサーバのみで使える単語の読み方を辞書から削除します\n"],
        ["/list", "設定したサーバのみで使える単語の読み方を全て表示します\n"],
        ["/selectspeaker", "読み上げキャラクターを変更します（サーバーによって変えることはできません）\n"]
    ]
    return command_list


def text_2_wav(text, speaker_id, max_retry=20):
    query_payload = {"text": text, "speaker": speaker_id}
    for query_i in range(max_retry):
        try:
            response = requests.post(
                f"{mainVoicevoxURL}audio_query", params=query_payload, timeout=10)
            if response.status_code == 200:
                query_data = response.json()
                synth_payload = {"speaker": speaker_id}
                for synth_i in range(max_retry):
                    response = requests.post(
                        f"{mainVoicevoxURL}synthesis", params=synth_payload, data=json.dumps(query_data), timeout=20)
                    if response.status_code == 200:
                        return response.content
                else:
                    raise ConnectionError('リトライ回数が上限に到達しました。')
        except:
            response = requests.post(
                f"{subVoicevoxURL}audio_query", params=query_payload, timeout=10)
            if response.status_code == 200:
                query_data = response.json()
                synth_payload = {"speaker": speaker_id}
                for synth_i in range(max_retry):
                    response = requests.post(
                        f"{subVoicevoxURL}synthesis", params=synth_payload, data=json.dumps(query_data), timeout=40)
                    if response.status_code == 200:
                        return response.content
                else:
                    raise ConnectionError('リトライ回数が上限に到達しました。')
            else:
                raise ConnectionError('リトライ回数が上限に到達しました。')


async def setup(bot: commands.Bot):
    await bot.add_cog(VoicevoxCog(bot))
