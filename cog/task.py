from discord.ext import commands, tasks
from discord import app_commands
import discord
import json
import datetime
from cog.manage import send

interval_seconds = 60  # 60秒ごとにタスクを確認
taskList = {}
weekday = ["月", "火", "水", "木", "金"]
weekendday = ["土", "日"]

# commands.Cogを継承する


class TaskCog(commands.Cog):
    def __init__(self, bot):  # コンストラクタ
        self.bot = bot
        update_task()

    @tasks.loop(seconds=interval_seconds)  # タスクを定期的に実行する
    async def task_message(self):
        update_task()
        task_keys_list = list(taskList.keys())
        taskExcute = False
        for key in task_keys_list:
            guild_id = 0
            channel_id = 0
            message = ""
            if taskList[key]["status"] == "active":
                dt_now = datetime.datetime.now()
                if dt_now.strftime('%a') == str(taskList[key]["day"]):
                    taskExcute = True
                elif str(taskList[key]["day"]) == "なし":
                    taskExcute = True
                elif str(taskList[key]["day"]) == "平日" and dt_now.strftime('%a') in weekday:
                    taskExcute = True
                elif str(taskList[key]["day"]) == "休日" and dt_now.strftime('%a') in weekendday:
                    taskExcute = True
                if taskExcute == True:
                    # 時間が一致したらメッセージを送信
                    if dt_now.strftime('%H%M') == "{:02}".format(int(taskList[key]["time"]["h"]))+"{:02}".format(int(taskList[key]["time"]["m"])):
                        guild_id = taskList[key]["serverID"]
                        channel_id = taskList[key]["chanelID"]
                        message = taskList[key]["message"]
                        await send(guild_id, channel_id, message)

    # イベントリスナー(ボットが起動したときやメッセージを受信したとき等)
    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog task.py ready!")
        self.task_message.start()

    @app_commands.command(name="addtask", description="指定時間に毎日送信するメッセージ追加できます。メッセージはこのコマンドが使われたところに送信されます。")
    async def addTask(self, interaction: discord.Interaction, taskname: str, hour: str, minutes: str, day: str, message: str):
        global taskList
        newtask = {
            taskname: {
                "status": "active",
                "time": {
                    "h": hour,
                    "m": minutes
                },
                "day": day,
                "serverID": interaction.guild.id,
                "chanelID": interaction.channel.id,
                "DMID": "",
                "userID": interaction.user.id,
                "message": message
            }
        }
        taskList.update(newtask)  # 新規タスクをtaskListに追加
        with open('./assetData/task.json', 'w', encoding="utf-8") as json_file:
            json.dump(taskList, json_file, ensure_ascii=False, indent=2)
        update_task()

        await interaction.response.send_message(f"新規タスク`{taskname}'を{hour}時{minutes}分に追加しました。")

    @app_commands.command(name="switchtask", description="指定されたタスクのアクティブ状態を切り替えます")
    async def switchTask(self, interaction: discord.Interaction, taskname: str):
        global taskList
        if taskList[taskname]["status"] == "active":
            taskList[taskname]["status"] = "inactive"
            await interaction.response.send_message(f"タスク`{taskname}'を無効化しました。")
        else:
            taskList[taskname]["status"] = "active"
            await interaction.response.send_message(f"タスク`{taskname}'を有効化しました。")
        with open('./assetData/task.json', 'w', encoding="utf-8") as json_file:
            json.dump(taskList, json_file, ensure_ascii=False, indent=2)
        update_task()

    @app_commands.command(name="deletetask", description="指定されたタスクを削除します")
    async def deleteTask(self, interaction: discord.Interaction, taskname: str):
        global taskList
        taskList.pop(taskname)
        await interaction.response.send_message(f"タスク`{taskname}'を削除しました。")
        with open('./assetData/task.json', 'w', encoding="utf-8") as json_file:
            json.dump(taskList, json_file, ensure_ascii=False, indent=2)
        update_task()

    @app_commands.command(name="listtask", description="ユーザが作成したタスクを表示します")
    async def listTask(self, interaction: discord.Interaction):
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


def update_task():
    global taskList
    with open('./assetData/task.json', 'r', encoding="utf-8") as json_file:
        taskList = json.load(json_file)


def help_task():
    commandList = [
        ["/addtask",
            "指定時間に毎日送信するメッセージ追加できます。メッセージはこのコマンドが使われたところに送信されます。時間は24時間表記です。\n曜日指定(dayオプション)は'なし'、'平日','休日','月〜日'のいずれかで指定してください\n"],
        ["/switchtask", "指定された名前のタスクの有効状態を切り替えます\n"],
        ["/deletetask", "指定されたタスクを削除します\n"],
        ["/listtask", "ユーザが作成したタスクを表示します\n"]
    ]
    return commandList


async def setup(bot):
    await bot.add_cog(TaskCog(bot))
