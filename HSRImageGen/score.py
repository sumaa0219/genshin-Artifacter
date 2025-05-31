import json
from HSRImageGen.imageGen import relic
import requests

with open('assetData/HSR_max.json', 'r', encoding="utf-8") as json_file:
    HSR_max = json.load(json_file)
    
exCharaID = ""
HSR_weight = {}

def calculationScore(charaID: int, relicInfo: relic):
    score = 0
    print(relicInfo)
    # メインステータスのスコア計算
    score += addScore(charaID, "main", relicInfo.level, relicInfo.type,
                      relicInfo.mainStatus.type, relicInfo.mainStatus.value)
    # サブステータスのスコア計算
    for sub in relicInfo.subAffix:
        score += addScore(charaID, "weight", relicInfo.level,
                          relicInfo.type, sub.type, sub.value)

    return score


def addScore(charaID: int, MainOrSub: str, level: int, place: str, type: str, value: float):
    global exCharaID, HSR_weight
    if exCharaID != str(charaID):
        exCharaID = str(charaID)
        res = requests.get(f"https://tools.jabrek.net/StarRail/api/weights/?character_ids={str(charaID)}")
        HSR_weight = res.json()["body"][0]["weights"]

    # 色々変換
    place = place.lower()
    if place == "1":
        place = "head"
    if place == "2":
        place = "hand"
    if place == "3":
        place = "body"
    if place == "4":
        place = "feet"
    if place == "5":
        place = "sphere"
    if place == "6":
        place = "rope"

    if MainOrSub == "main":
        weight = HSR_weight[place][type]
        return (level + 1) / 16 * weight * 50
    elif MainOrSub == "weight":
        if type == "CriticalChance" or type == "CriticalDamage" or type == "StatusProbability" or type == "StatusResistance" or type == "BreakDamageAddedRatio":
            type += "Base"
        weight = HSR_weight["sub"][type]
        max = HSR_max[type]
        return value / max * weight * 50

