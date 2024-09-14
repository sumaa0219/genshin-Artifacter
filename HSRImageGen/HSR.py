import json
import requests
from pydantic import BaseModel

myuid = 802620912

with open('API-docs/store/hsr/honker_avatars.json', 'r', encoding="utf-8") as json_file:
    HSR_Avatars = json.load(json_file)

with open('API-docs/store/hsr/hsr.json', 'r', encoding="utf-8") as json_file:
    HSR_hash = json.load(json_file)

with open('API-docs/store/hsr/honker_characters.json', 'r', encoding="utf-8") as json_file:
    HSR_characters = json.load(json_file)


class playerData(BaseModel):
    uid: int
    name: str
    level: int
    headIcon: int
    friendCount: int
    achievmentCount: int
    worldLevel: int


class showCharaData(BaseModel):
    nameId: str
    level: int


def getDataFromUID(UID: int):
    # データ取得
    url = "https://enka.network/api/hsr/uid/" + str(UID)
    response = requests.get(url)
    # サーバー停止などのエラー処理
    status = response.status_code
    if status == 424:
        return "EnkaAPIが停止しています\nしばらくお待ちください"
    elif status == 404:
        return "UIDが違います\nもう一度確認してください"
    else:
        pass
    return response.json()


def getInfo(UID: int):
    # playerInfoのインスタンス化
    playerInfo = playerData(
        uid=0,
        name="",
        level=0,
        headIcon=0,
        friendCount=0,
        achievmentCount=0,
        worldLevel=0
    )
    # データ取得
    resJson = getDataFromUID(UID)

    # playerInfoにデータを格納
    playerInfo.uid = int(resJson["uid"])
    playerInfo.name = resJson["detailInfo"]["nickname"]
    playerInfo.level = resJson["detailInfo"]["level"]
    playerInfo.headIcon = resJson["detailInfo"]["headIcon"]
    playerInfo.friendCount = resJson["detailInfo"]["friendCount"]
    playerInfo.achievmentCount = resJson["detailInfo"]["recordInfo"]["achievementCount"]
    playerInfo.worldLevel = resJson["detailInfo"]["worldLevel"]

    showCharaInfoList = []
    for chara in resJson["detailInfo"]["avatarDetailList"]:
        showCharaInfo = showCharaData(
            nameId="",
            level=0
        )
        showCharaInfo.nameId = chara["avatarId"]
        showCharaInfo.level = chara["level"]
        showCharaInfoList.append(showCharaInfo)

    return playerInfo, showCharaInfoList


def getAvatorURL(avatorID: int):
    return HSR_Avatars[str(avatorID)]["Icon"]


def getNamefromHash(language: str, hash: str):
    return HSR_hash[language][hash]


def getCharacaterInfo(charaID: str):
    return HSR_characters[charaID]
