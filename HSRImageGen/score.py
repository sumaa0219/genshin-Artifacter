import json
from HSRImageGen.imageGen import relic

with open('assetData/HSR_max.json', 'r', encoding="utf-8") as json_file:
    HSR_max = json.load(json_file)

with open('StarRailScore/score.json', 'r', encoding="utf-8") as json_file:
    HSR_weight = json.load(json_file)


def calculationScore(charaID: int, relicInfo: relic):
    score = 0
    # メインステータスのスコア計算
    score += addScore(charaID, "main", relicInfo.level, relicInfo.type,
                      relicInfo.mainStatus.type, relicInfo.mainStatus.value)
    # サブステータスのスコア計算
    for sub in relicInfo.subAffix:
        score += addScore(charaID, "sub", relicInfo.level,
                          relicInfo.type, sub.type, sub.value)

    return score


def addScore(charaID: int, MainOrSub: str, level: int, place: str, type: str, value: float):
    # 色々変換
    place = place.lower()
    if place == "foot":
        place = "feet"
    if place == "neck":
        place = "sphere"
    if place == "object":
        place = "rope"

    if MainOrSub == "main":
        weight = HSR_weight[str(charaID)][MainOrSub][place][type]
        return (level + 1) / 16 * weight * 50
    elif MainOrSub == "sub":
        if type == "CriticalChance" or type == "CriticalDamage" or type == "StatusProbability" or type == "StatusResistance" or type == "BreakDamageAddedRatio":
            type += "Base"
        weight = HSR_weight[str(charaID)][MainOrSub][type]
        max = HSR_max[type]
        return value / max * weight * 50
