import json
from HSRImageGen.imageGen import relic
import requests

with open('assetData/HSR_max.json', 'r', encoding="utf-8") as json_file:
    HSR_max = json.load(json_file)


def calculationScore(charaID: int, relicInfo: relic):
    score = 0
    # メインステータスのスコア計算
    score += addScore(charaID, "main", relicInfo.level, relicInfo.type,
                      relicInfo.mainStatus.type, relicInfo.mainStatus.value)
    # サブステータスのスコア計算
    for sub in relicInfo.subAffix:
        score += addScore(charaID, "weight", relicInfo.level,
                          relicInfo.type, sub.type, sub.value)

    return score


def addScore(charaID: int, MainOrSub: str, level: int, place: str, type: str, value: float):

    res = requests.get(f"https://hcs.lenlino.com/weight/{str(charaID)}")
    if res.status_code == 200:
        HSR_weight = res.json()

    # 色々変換
    place = place.lower()
    if place == "foot":
        place = "feet"
    if place == "neck":
        place = "sphere"
    if place == "object":
        place = "rope"

    if MainOrSub == "main":
        weight = HSR_weight[MainOrSub]["w"+place][type]
        return (level + 1) / 16 * weight * 50
    elif MainOrSub == "weight":
        if type == "CriticalChance" or type == "CriticalDamage" or type == "StatusProbability" or type == "StatusResistance" or type == "BreakDamageAddedRatio":
            type += "Base"
        weight = HSR_weight[MainOrSub][type]
        max = HSR_max[type]
        return value / max * weight * 50

