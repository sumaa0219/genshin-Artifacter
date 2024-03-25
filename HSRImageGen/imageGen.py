from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageOps
from pydantic import BaseModel
from io import BytesIO
import requests
import json

with open('API-docs/store/hsr/hsr.json', 'r', encoding="utf-8") as json_file:
    HSR = json.load(json_file)

baseHsrUrl = "https://enka.network/ui/hsr/"


class status(BaseModel):
    type: str
    value: float


class relic(BaseModel):
    nameID: int
    level: int
    type: str
    rarity: str
    mainStatus: status
    imagePath: str
    setID: int
    subAffix: list
    score: float


class elementAddedRatio(BaseModel):
    element: str
    value: float


class charaInfo(BaseModel):
    nameID: int
    nameHash: int
    level: int
    promotion: int
    element: str
    avatarBaseType: str
    imagePath: str
    rank: int
    rankImagePathList: list
    HP: float
    ATK: float
    DEF: float
    speed: float
    critical_per: float
    criticak_Dmg: float
    breakDamageAddedRatio: float
    SPRatio: float
    statusProbability: float
    statusResistanc: float
    elementAddedRatio: elementAddedRatio


class statusInfo(BaseModel):
    HP: float
    HP_per: float
    ATK: float
    ATK_per: float
    DEF: float
    DEF_per: float
    speed: float
    speed_per: float
    critical_per: float
    criticak_Dmg: float
    breakDamageAddedRatio: float
    SPRatio: float
    statusProbability: float
    statusResistanc: float
    elementAddedRatio: elementAddedRatio


class weapon(BaseModel):
    nameID: int
    level: int
    rank: int
    promotion: int
    rarity: str
    avatarBaseType: str
    equipmentNameHash: int
    imagePath: str
    nameHash: int
    statusList: list
    addedStatusList: list


class skill(BaseModel):
    level: int
    pointID: int
    addedStatusList: list
    imagePath: str


class setList(BaseModel):
    setID: int
    setNameHash: int
    setCount: list
    setEffectlist: list


def HSR_generate(language: str, charaInfoData: charaInfo, weaponInfo: weapon, relicList: list, skillList: list, relicSetList: list):

    # ベースとなる画像を開く
    base = Image.open('HSRImageGen/assets/Base.png').convert('RGBA')
    draw = ImageDraw.Draw(base)
    charaName = HSR[language][str(charaInfoData.nameHash)]
    drawText(base, charaName, 45, 65, 25, (255, 255, 255))
    charaLevel = "Lv." + str(charaInfoData.level)
    drawText(base, charaLevel, 25, 65, 85, hex_to_rgb("#e4c992"))

    element = charaInfoData.element
    drawImage(base, 'HSRImageGen/assets/element/' +
              element + '.png', 200, 85, (30, 30))
    avatarBaseType = charaInfoData.avatarBaseType
    drawImage(base, 'HSRImageGen/assets/avatarBaseType/' +
              avatarBaseType + '.png', 250, 85, (30, 30))

    charaInfoData.imagePath = baseHsrUrl + charaInfoData.imagePath
    response = requests.get(charaInfoData.imagePath)
    overlay = Image.open(BytesIO(response.content)).convert('RGBA')
    overlay = overlay.resize((1024, 1024))
    overlay = overlay.crop((0, 0, 1000, 746))
    baselay = Image.open(
        "HSRImageGen/assets/CharacterMask.png").convert('RGBA')
    baselay = baselay.resize((1000, 746))
    baselay = ImageOps.invert(baselay.convert('L')).convert('RGBA')
    base_blank = Image.new('RGBA', (1000, 746), (0, 0, 0, 0))
    base_IN = Image.composite(overlay, base_blank, baselay)

    # 結果をbaseに貼り付けます。
    base.paste(base_IN, (430, 0), base_IN)

    statusList = []
    statusList.append(["MaxHP", round(charaInfoData.HP)])
    statusList.append(["Attack", round(charaInfoData.ATK)])
    statusList.append(["Defence", round(charaInfoData.DEF)])
    statusList.append(["Speed", round(charaInfoData.speed)])
    statusList.append(["CriticalChance", str(
        round(charaInfoData.critical_per, 1))+"%"])
    statusList.append(["CriticalDamage", str(
        round(charaInfoData.criticak_Dmg, 1))+"%"])
    statusList.append(["BreakDamageAddedRatio",
                       str(round(charaInfoData.breakDamageAddedRatio, 1)) + "%"])
    statusList.append(["SPRatio", str(round(charaInfoData.SPRatio, 1)) + "%"])
    statusList.append(
        ["StatusProbability", str(round(charaInfoData.statusProbability, 1)) + "%"])
    statusList.append(["StatusResistance", str(
        round(charaInfoData.statusResistanc, 1)) + "%"])
    statusList.append([charaInfoData.elementAddedRatio.element + "AddedRatio",
                       str(round(charaInfoData.elementAddedRatio.value, 1)) + "%"])

    for i, status in enumerate(statusList):
        if i % 2 == 0:
            drawImage(base, 'HSRImageGen/assets/StatusBG.png', 65, 150+(i*60))

        # ステータスアイコンの表示
        drawImage(base, 'HSRImageGen/assets/status/Icon' +
                  status[0] + '.png', 80, 150+(i*60), size=(50, 50))
        # ステータスの表示
        drawText(base, HSR[language][str(status[0])],
                 25, 141, 160+(i*60), (255, 255, 255))
        drawText(base, str(status[1]),
                 25, 400, 160+(i*60), (255, 255, 255))

    # 武器情報の表示
    if weaponInfo is not None:
        weaponlevel = "Lv." + str(weaponInfo.level)
        drawText(base, weaponlevel, 15, 50, 860, hex_to_rgb("#e4c992"))

        drawImagefromURL(base, baseHsrUrl + weaponInfo.imagePath,
                         100, 880, size=(85, 119))
        drawImage(base, 'HSRImageGen/assets/wepRank.png',
                  175, 865, size=(25, 25))
        weaponRank = str(weaponInfo.rank)
        drawText(base, weaponRank, 15, 182, 869, hex_to_rgb("#e4c992"))
        rarity = weaponInfo.rarity
        drawImage(base, 'HSRImageGen/assets/rank/' +
                  str(rarity) + '.png', 80, 970, size=(128, 45))

        weaponName = HSR[language][str(weaponInfo.nameHash)]
        drawText(base, weaponName, 20, 230, 865, hex_to_rgb("#e4c992"))

        for i, status in enumerate(weaponInfo.statusList):
            if str(status.type) == "BaseHP":
                status.type = "MaxHP"
            if str(status.type) == "BaseAttack":
                status.type = "Attack"
            if str(status.type) == "BaseDefence":
                status.type = "Defence"

            drawImage(base, 'HSRImageGen/assets/status/Icon' +
                      str(status.type)+'.png', 235, 880+(i*45), size=(40, 40))
            # ステータスの表示
            drawText(base, HSR[language][str(status.type)],
                     20, 280, 890+(i*45), (255, 255, 255))
            drawText(base, str(round(status.value)),
                     20, 430, 890+(i*45), (255, 255, 255))

    totalScore = 0
    if relicList is not None:
        for i, relic in enumerate(relicList):
            drawImagefromURL(base, baseHsrUrl + relic.imagePath,
                             1360, 60+(i*170), size=(100, 100))

            mainType = relic.mainStatus.type
            if mainType == "HPDelta":
                mainType = "MaxHP"
            if mainType == "AttackDelta":
                mainType = "Attack"
            if mainType == "DefenceDelta":
                mainType = "Defence"
            if mainType == "SpeedDelta":
                mainType = "Speed"
            if "Base" in mainType:
                mainType = mainType.replace("Base", "")
            drawImage(base, 'HSRImageGen/assets/status/Icon' +
                      mainType+'.png', 1460, 85+(i*170), size=(30, 30))
            mainStatusName = HSR[language][str(mainType)]
            if "ダメージ" in mainStatusName:
                mainStatusName = mainStatusName.replace("ダメージ", "ダメ")
            if "属性与" in mainStatusName:
                mainStatusName = mainStatusName.replace("属性与", "与")
            drawText(base, mainStatusName,
                     20, 1500, 85+(i*170), (255, 255, 255))

            if "Ratio" in mainType or "CriticalChance" in mainType or "CriticalDamage" in mainType or "StatusProbability" in mainType or "StatusResistance" in mainType:
                mainStatusValue = str(round(relic.mainStatus.value*100, 1))
                mainStatusValue += "%"
            else:
                mainStatusValue = str(round(relic.mainStatus.value))
            drawText(base, mainStatusValue,
                     30, 1480, 130+(i*165), (255, 255, 255))

            level = "+" + str(relic.level)
            drawText(base, level, 20, 1560, 50+(i*170), hex_to_rgb("#e4c992"))

            rarity = relic.rarity
            drawImage(base, 'HSRImageGen/assets/rank/' + str(rarity) + '.png',
                      1460, 160+(i*165), size=(128, 45))

            # スコアの表示
            score = str(round(relic.score, 1))
            drawText(base, "スコア",
                     17, 1815, 75+(i*170),  hex_to_rgb("#e4c992"))
            drawText(base, score,
                     20, 1820, 95+(i*170),  hex_to_rgb("#e4c992"))
            totalScore += relic.score

            if round(relic.score, 1) >= 100:
                scoreRank = "SS"
            elif round(relic.score, 1) >= 80:
                scoreRank = "S"
            elif round(relic.score, 1) >= 60:
                scoreRank = "A"
            elif round(relic.score, 1) >= 40:
                scoreRank = "B"
            elif round(relic.score, 1) >= 20:
                scoreRank = "C"
            else:
                scoreRank = "D"

            drawText(base, scoreRank,
                     20, 1830, 130+(i*170),  hex_to_rgb("#e4c992"))

            # サブステータスの表示
            for j, subStatus in enumerate(relic.subAffix):
                subType = subStatus.type
                if subType == "HPDelta":
                    subType = "MaxHP"
                if subType == "AttackDelta":
                    subType = "Attack"
                if subType == "DefenceDelta":
                    subType = "Defence"
                if subType == "SpeedDelta":
                    subType = "Speed"
                if "Base" in subType:
                    subType = subType.replace("Base", "")
                drawImage(base, 'HSRImageGen/assets/status/Icon' +
                          subType+'.png', 1600, 50+(i*170)+(j*35), size=(30, 30))
                subStatusName = HSR[language][str(subType)]
                if "ダメージ" in subStatusName:
                    subStatusName = subStatusName.replace("ダメージ", "ダメ")
                if "属性与" in subStatusName:
                    subStatusName = subStatusName.replace("属性与", "与")
                drawText(base, subStatusName,
                         20, 1630, 50+(i*170)+(j*35
                                               ), (255, 255, 255))

                if "Ratio" in subType or "CriticalChance" in subType or "CriticalDamage" in subType or "StatusProbability" in subType or "StatusResistance" in subType:
                    subStatusValue = str(round(subStatus.value*100, 1))
                    subStatusValue += "%"
                else:
                    subStatusValue = str(round(subStatus.value))
                drawText(base, subStatusValue,
                         20, 1730, 50+(i*170)+(j*35), (255, 255, 255))

    if round(totalScore, 1) >= 600:
        scoreRank = "SS"
    elif round(totalScore, 1) >= 540:
        scoreRank = "S"
    elif round(totalScore, 1) >= 360:
        scoreRank = "A"
    elif round(totalScore, 1) >= 240:
        scoreRank = "B"
    elif round(totalScore, 1) >= 120:
        scoreRank = "C"
    else:
        scoreRank = "D"
    drawText(base, str(round(totalScore, 1)), 70, 1000, 850, (255, 255, 255))
    drawText(base, scoreRank, 40, 1220, 865, hex_to_rgb("#e4c992"))
    # セット効果の表示
    for i, set in enumerate(relicSetList):
        drawText(base, HSR[language][str(set.setNameHash)],
                 20, 600, 830+(i*70), hex_to_rgb("#e4c992"))
        count = str(set.setCount[len(set.setCount)-1])
        drawText(base, count + " セット",
                 25, 605, 805+(i*70), hex_to_rgb("#e4c992"))

    # #凸数の反映
    rank = charaInfoData.rank
    for i, rankImagePath in enumerate(charaInfoData.rankImagePathList):
        draw.ellipse((1270, 39+(i*110), 1270+85, 39+(i*110)+85), fill='black')
        drawImagefromURL(base, baseHsrUrl + rankImagePath,
                         1270, 39+(i*110), size=(85, 85))
        if i+1 > rank:
            drawImage(base, "HSRImageGen/assets/LOCK.png",
                      1270, 39+(i*110), size=(85, 85))

    # スキルの表示
    for i, skill in enumerate(skillList):
        if i < 4:
            draw.ellipse((530, 260+(i*110), 530+85,
                         260+(i*110)+85), fill='black')
            drawImagefromURL(base, baseHsrUrl + skill.imagePath,
                             530, 260+(i*110), size=(85, 85))
            drawImage(base, "HSRImageGen/assets/skillNum.png",
                      555, 330+(i*110), size=(35, 30))
            drawText(base, str(skill.level),
                     15, 568, 335+(i*110), (255, 255, 255))

    # 結果を保存
    base.save('HSRImageGen/output.png')


def drawText(base, text, size, x, y, color):
    draw = ImageDraw.Draw(base)
    font = ImageFont.truetype('HSRImageGen/assets/ja-jp.ttf', size)
    draw.text((x, y), text, font=font, fill=color)


def drawImage(base, imagePath, x, y, size=None):
    overlay = Image.open(imagePath).convert('RGBA')
    # サイズが指定されている場合、画像をリサイズ
    if size is not None:
        overlay = overlay.resize(size)
    # アルファチャンネルを考慮して画像を貼り付け
    base.paste(overlay, (x, y), overlay)


def drawImagefromURL(base, url, x, y, size=None):
    response = requests.get(url)
    overlay = Image.open(BytesIO(response.content)).convert('RGBA')
    # サイズが指定されている場合、画像をリサイズ
    if size is not None:
        overlay = overlay.resize(size)
    # アルファチャンネルを考慮して画像を貼り付け
    base.paste(overlay, (x, y), overlay)


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
