import json
from pydantic import BaseModel
from collections import Counter

with open('API-docs/store/hsr/honker_weps.json', 'r', encoding="utf-8") as json_file:
    HSR_weps = json.load(json_file)

with open('API-docs/store/hsr/honker_relics.json', 'r', encoding="utf-8") as json_file:
    HSR_relics = json.load(json_file)

with open('API-docs/store/hsr/honker_characters.json', 'r', encoding="utf-8") as json_file:
    HSR_chara = json.load(json_file)

with open('API-docs/store/hsr/honker_meta.json', 'r', encoding="utf-8") as json_file:
    HSR_meta = json.load(json_file)

with open('API-docs/store/hsr/honker_skills.json', 'r', encoding="utf-8") as json_file:
    HSR_skills = json.load(json_file)


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
    critical_per: float
    criticak_Dmg: float
    breakDamageAddedRatio: float
    SPRatio: float
    statusProbability: float
    statusResistanc: float
    elementAddedRatio: elementAddedRatio


class status(BaseModel):
    type: str
    value: float


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


class relic(BaseModel):
    nameID: int
    level: int
    type: str
    rarity: str
    mainStatus: status
    imagePath: str
    setID: int
    subAffix: list


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


def formatCharaData(allCharaData):

    # キャラ情報の取得
    charaInfoData = charaInfo(
        nameID=allCharaData["avatarId"],
        nameHash=0,
        level=allCharaData["level"],
        promotion=allCharaData["promotion"],
        element="",
        avatarBaseType="",
        HP=0,
        ATK=0,
        DEF=0,
        speed=0,
        critical_per=0,
        criticak_Dmg=0,
        breakDamageAddedRatio=0,
        SPRatio=0,
        statusProbability=0,
        statusResistanc=0,
        elementAddedRatio=elementAddedRatio(
            element="",
            value=0
        )
    )
    statusInfos = statusInfo(
        HP=0,
        HP_per=0,
        ATK=0,
        ATK_per=0,
        DEF=0,
        DEF_per=0,
        speed=0,
        critical_per=0,
        criticak_Dmg=0,
        breakDamageAddedRatio=0,
        SPRatio=0,
        statusProbability=0,
        statusResistanc=0,
        elementAddedRatio=elementAddedRatio(
            element=HSR_chara[str(charaInfoData.nameID)]["Element"],
            value=0
        )
    )

    # 武器情報の取得
    weaponInfo = weapon(
        nameID=allCharaData["equipment"]["tid"],
        level=allCharaData["equipment"]["level"],
        rank=allCharaData["equipment"]["rank"],
        promotion=allCharaData["equipment"]["promotion"],
        rarity="",
        avatarBaseType="",
        equipmentNameHash=0,
        imagePath="",
        nameHash=0,
        statusList=[],
        addedStatusList=[]
    )
    weaponInfo.rarity = HSR_weps[str(weaponInfo.nameID)]["Rarity"]
    weaponInfo.avatarBaseType = HSR_weps[str(
        weaponInfo.nameID)]["AvatarBaseType"]
    weaponInfo.equipmentNameHash = HSR_weps[str(
        weaponInfo.nameID)]["EquipmentName"]["Hash"]
    weaponInfo.imagePath = HSR_weps[str(weaponInfo.nameID)]["ImagePath"]
    weaponInfo.nameHash = allCharaData["equipment"]["_flat"]["name"]

    for wepAddedStatus in allCharaData["equipment"]["_flat"]["props"]:
        statusdata = status(
            type=wepAddedStatus["type"],
            value=wepAddedStatus["value"]
        )
        addStatus(statusInfos, statusdata.type, statusdata.value)
        weaponInfo.statusList.append(statusdata)

    for wepAddedStatus in HSR_meta["equipmentSkill"][str(weaponInfo.nameID)][str(weaponInfo.rank)]["props"].keys():
        statusdata = status(
            type=wepAddedStatus,
            value=HSR_meta["equipmentSkill"][str(weaponInfo.nameID)][str(
                weaponInfo.rank)]["props"][wepAddedStatus]
        )
        addStatus(statusInfos, statusdata.type, statusdata.value)
        weaponInfo.addedStatusList.append(statusdata)

    # 遺物情報の取得
    relicList = []
    for relicData in allCharaData["relicList"]:
        print("--------")
        relicInfo = relic(
            nameID=relicData["tid"],
            level=relicData["level"],
            type="",
            rarity=str(HSR_relics[str(relicData["tid"])]
                       ["Rarity"]),  # 整数を文字列に変換
            mainStatus=status(
                type="",
                value=0
            ),
            subAffix=[],
            imagePath=HSR_relics[str(relicData["tid"])
                                 ]["Icon"],  # imagePathを追加
            setID=HSR_relics[str(relicData["tid"])]["SetID"]  # setIDを追加
        )
        relicInfo.type = HSR_relics[str(relicData["tid"])]["Type"]
        relicInfo.mainStatus.type = relicData["_flat"]["props"][0]["type"]
        relicInfo.mainStatus.value = relicData["_flat"]["props"][0]["value"]

        addStatus(statusInfos, relicInfo.mainStatus.type,
                  relicInfo.mainStatus.value)

        for subStatus in relicData["_flat"]["props"][1:]:
            subStatusInfo = status(
                type=subStatus["type"],
                value=subStatus["value"]
            )
            addStatus(statusInfos, subStatusInfo.type, subStatusInfo.value)
            relicInfo.subAffix.append(subStatusInfo)
        relicList.append(relicInfo)

    # スキル情報の取得
    skillList = []
    for skillData in allCharaData["skillTreeList"]:
        skillInfo = skill(
            level=skillData["level"],
            pointID=skillData["pointId"],
            addedStatusList=[],
            imagePath=""
        )
        skillInfo.imagePath = HSR_skills[str(skillInfo.pointID)]["IconPath"]
        try:
            for skillAddedStatus in HSR_meta["tree"][str(skillInfo.pointID)]["1"]["props"].keys():
                statusdata = status(
                    type=skillAddedStatus,
                    value=HSR_meta["tree"][str(
                        skillInfo.pointID)]["1"]["props"][skillAddedStatus]
                )
                addStatus(statusInfos, statusdata.type, statusdata.value)
                print(statusdata.value)
                skillInfo.addedStatusList.append(statusdata)
        except:
            pass
        skillList.append(skillInfo)

    # 遺物セット効果の取得
    relicSetList = []
    setlistNum = []
    for reliclist in relicList:
        setlistNum.append(reliclist.setID)
    # 各数字の出現回数を数える
    num_counts = Counter(setlistNum)

    # 結果を表示
    for num, count in num_counts.items():
        # 2セット以上の場合は2セットにする
        if count >= 2:
            setListInfo = setList(
                setID=num,
                setNameHash=0,
                setCount=[2],
                setEffectlist=[]
            )
            # 4セット以上の場合は4セットにする
            if count >= 4:
                setListInfo.setCount.append(4)

            # セット名のハッシュ値を取得
            for reliclist in allCharaData["relicList"]:
                if num == reliclist["_flat"]["setID"]:
                    setListInfo.setNameHash = reliclist["_flat"]["setName"]
                    break

            for setEffectCount in setListInfo.setCount:
                for type in HSR_meta["relic"]["setSkill"][str(num)][str(setEffectCount)]["props"].keys():
                    statusdata = status(
                        type=type,
                        value=HSR_meta["relic"]["setSkill"][str(
                            num)][str(setEffectCount)]["props"][type]
                    )
                addStatus(statusInfos, statusdata.type, statusdata.value)
                setListInfo.setEffectlist.append(statusdata)
            relicSetList.append(setListInfo)

    print("charaInfoData", charaInfoData, "\n\nweaponInfo", weaponInfo,
          "\n\nrelicList", relicList, "\n\nskillList", skillList, "\n\nrelicSetList", relicSetList, "\n\nstatusInfos", statusInfos)


def addStatus(statusInfos: statusInfo, type: str, value: float):
    print(type, value)
    if type == "HPDelta" or type == "BaseHP":
        statusInfos.HP += value
    elif type == "HPAddedRatio":
        statusInfos.HP_per += value
    elif type == "AttackDelta" or type == "BaseAttack":
        statusInfos.ATK += value
    elif type == "AttackAddedRatio":
        statusInfos.ATK_per += value
    elif type == "DefenceDelta" or type == "BaseDefence":
        statusInfos.DEF += value
    elif type == "DefenceAddedRatio":
        statusInfos.DEF_per += value
    elif type == "SpeedDelta":
        statusInfos.speed += value
    elif type == "CriticalChanceBase" or type == "CriticalChance":
        statusInfos.critical_per += value
    elif type == "CriticalDamageBase" or type == "CriticalDamage":
        statusInfos.criticak_Dmg += value
    elif type == "StatusProbabilityBase" or type == "StatusProbability":
        statusInfos.statusProbability += value
    elif type == "StatusResistanceBase" or type == "StatusResistance":
        statusInfos.statusResistanc += value
    elif type == "ElementAddedRatio" or type == "AllDamageTypeAddedRatio" or statusInfos.elementAddedRatio.element in type:
        statusInfos.elementAddedRatio.value += value
    elif type == "BreakDamageAddedRatio" or type == "BreakDamageAddedRatioBase":
        statusInfos.breakDamageAddedRatio += value
    elif type == "SPRatio" or type == "SPRatioBase":
        statusInfos.SPRatio += value
    else:
        pass
