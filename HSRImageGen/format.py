import json
from collections import Counter
import HSRImageGen.score as score
from HSRImageGen.imageGen import status, relic, elementAddedRatio, charaInfo, statusInfo, weapon, skill, setList


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

with open('API-docs/store/hsr/honker_ranks.json', 'r', encoding="utf-8") as json_file:
    HSR_ranks = json.load(json_file)


def formatCharaData(allCharaData):

    # キャラ情報の取得
    charaInfoData = charaInfo(
        nameID=allCharaData["avatarId"],
        nameHash=0,
        level=allCharaData["level"],
        promotion=allCharaData["promotion"],
        element="",
        avatarBaseType="",
        imagePath="",
        rank=0,
        rankImagePathList=[],
        HP=0,
        ATK=0,
        DEF=0,
        speed=0,
        critical_per=0,
        criticak_Dmg=0,
        breakDamageAddedRatio=0,
        SPRatio=1.0,
        statusProbability=0,
        statusResistanc=0,
        elementAddedRatio=elementAddedRatio(
            element="",
            value=0
        )
    )
    charaInfoData.nameHash = HSR_chara[str(
        charaInfoData.nameID)]["AvatarName"]["Hash"]
    charaInfoData.element = HSR_chara[str(charaInfoData.nameID)]["Element"]
    charaInfoData.avatarBaseType = HSR_chara[str(
        charaInfoData.nameID)]["AvatarBaseType"]
    charaInfoData.imagePath = HSR_chara[str(
        charaInfoData.nameID)]["AvatarCutinFrontImgPath"]

    try:
        charaInfoData.rank = allCharaData["rank"]
    except KeyError as e:
        logger.debug(f"Character rank not found: {e}")
        charaInfoData.rank = 0

    levelCorrection = 1
    charaInfoData.HP = float(HSR_meta["avatar"][str(charaInfoData.nameID)][str(charaInfoData.promotion)]["HPBase"]) + float(
        HSR_meta["avatar"][str(charaInfoData.nameID)][str(charaInfoData.promotion)]["HPAdd"])*(float(charaInfoData.level) - levelCorrection)
    charaInfoData.ATK = float(HSR_meta["avatar"][str(charaInfoData.nameID)][str(charaInfoData.promotion)]["AttackBase"]) + float(
        HSR_meta["avatar"][str(charaInfoData.nameID)][str(charaInfoData.promotion)]["AttackAdd"])*(float(charaInfoData.level) - levelCorrection)
    charaInfoData.DEF = float(HSR_meta["avatar"][str(charaInfoData.nameID)][str(charaInfoData.promotion)]["DefenceBase"]) + float(
        HSR_meta["avatar"][str(charaInfoData.nameID)][str(charaInfoData.promotion)]["DefenceAdd"])*(float(charaInfoData.level) - levelCorrection)
    charaInfoData.speed = HSR_meta["avatar"][str(
        charaInfoData.nameID)][str(charaInfoData.promotion)]["SpeedBase"]
    charaInfoData.critical_per = HSR_meta["avatar"][str(
        charaInfoData.nameID)][str(charaInfoData.promotion)]["CriticalChance"]
    charaInfoData.criticak_Dmg = HSR_meta["avatar"][str(
        charaInfoData.nameID)][str(charaInfoData.promotion)]["CriticalDamage"]

    statusInfos = statusInfo(
        HP=0,
        HP_per=0,
        ATK=0,
        ATK_per=0,
        DEF=0,
        DEF_per=0,
        speed=0,
        speed_per=0,
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
    try:
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
            addStatus(charaInfoData, statusdata.type, statusdata.value)
            weaponInfo.statusList.append(statusdata)

        try:
            for wepAddedStatus in HSR_meta["equipmentSkill"][str(weaponInfo.nameID)][str(weaponInfo.rank)]["props"].keys():
                statusdata = status(
                    type=wepAddedStatus,
                    value=HSR_meta["equipmentSkill"][str(weaponInfo.nameID)][str(
                        weaponInfo.rank)]["props"][wepAddedStatus]
                )
                addStatus(statusInfos, statusdata.type, statusdata.value)
                weaponInfo.addedStatusList.append(statusdata)
        except (KeyError, TypeError) as e:
            logger.debug(f"Weapon additional status not found: {e}")
    except Exception as e:
        logger.error(f"Failed to get weapon info: {e}")
        weaponInfo = None

    # 遺物情報の取得
    try:
        relicList = []
        for relicData in allCharaData["relicList"]:
            relicInfo = relic(
                nameID=relicData["tid"],
                level=0,
                type="",
                rarity=str(HSR_relics[str(relicData["tid"])]
                           ["Rarity"]),  # 整数を文字列に変換
                mainStatus=status(
                    type="",
                    value=0
                ),
                subAffix=[],
                score=0,
                imagePath=HSR_relics[str(relicData["tid"])
                                     ]["Icon"],  # imagePathを追加
                setID=HSR_relics[str(relicData["tid"])]["SetID"]  # setIDを追加
            )
            try:
                relicInfo.level = relicData["level"]
            except KeyError as e:
                logger.debug(f"Relic level not found: {e}")
                relicInfo.level = 0
            relicInfo.type = str(relicData["type"])
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
            
            try:
                relicInfo.score = score.calculationScore(
                    charaInfoData.nameID, relicInfo)
                relicList.append(relicInfo)
            except Exception as e:
                print(f"Error calculating relic score: {e}")
                relicInfo.score = 0  # Default score if calculation fails
                relicList.append(relicInfo)  # Add relic even if score calculation fails
                continue
    except Exception as e:
        logger.error(f"Failed to get relic info: {e}")
        relicList = []

    rank = charaInfoData.rank
    skillAddedfromRankList = []
    # 凸数に応じたスキルレベル補正
    for i, rankID in enumerate(HSR_chara[str(charaInfoData.nameID)]["RankIDList"]):
        rankImagePath = HSR_ranks[str(rankID)]["IconPath"]
        if i+1 < rank:
            for skillAddedLevel in HSR_ranks[str(rankID)]["SkillAddLevelList"].keys():
                skillAddedLevelfor = skillAddedLevel[:-
                                                     1] + "0" + skillAddedLevel[-1]
                skillAddedfromRankList.append(
                    {skillAddedLevelfor: HSR_ranks[str(rankID)]["SkillAddLevelList"][skillAddedLevel]})
        charaInfoData.rankImagePathList.append(rankImagePath)

    # スキル情報の取得
    try:
        skillList = []
        for skillData in allCharaData["skillTreeList"]:
            skillInfo = skill(
                level=skillData["level"],
                pointID=skillData["pointId"],
                addedStatusList=[],
                imagePath=""
            )

            if skillAddedfromRankList is not None:
                for i, skillAddedLevel in enumerate(skillAddedfromRankList):
                    for skillID in skillAddedLevel.keys():
                        if int(skillInfo.pointID) == int(skillID):
                            skillInfo.level += int(
                                skillAddedfromRankList[i][skillID])
            skillInfo.imagePath = HSR_skills[str(
                skillInfo.pointID)]["IconPath"]
            try:
                for skillAddedStatus in HSR_meta["tree"][str(skillInfo.pointID)]["1"]["props"].keys():
                    statusdata = status(
                        type=skillAddedStatus,
                        value=HSR_meta["tree"][str(
                            skillInfo.pointID)]["1"]["props"][skillAddedStatus]
                    )
                    addStatus(statusInfos, statusdata.type, statusdata.value)
                    skillInfo.addedStatusList.append(statusdata)
            except (KeyError, TypeError) as e:
                logger.debug(f"Skill added status not found: {e}")
            skillList.append(skillInfo)
    except Exception as e:
        logger.error(f"Failed to get skill info: {e}")
        skillList = []

    # 遺物セット効果の取得
    try:
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
                    try:
                        for type in HSR_meta["relic"]["setSkill"][str(num)][str(setEffectCount)]["props"].keys():
                            statusdata = status(
                                type=type,
                                value=HSR_meta["relic"]["setSkill"][str(
                                    num)][str(setEffectCount)]["props"][type]
                            )
                            if statusdata.type:
                                addStatus(statusInfos, statusdata.type,
                                          statusdata.value)
                                setListInfo.setEffectlist.append(statusdata)
                    except (KeyError, TypeError) as e:
                        logger.debug(f"Relic set effect not found: {e}")
                relicSetList.append(setListInfo)
    except Exception as e:
        logger.error(f"Failed to get relic set info: {e}")
        relicSetList = []

    # print(charaInfoData, statusInfos)
    statusCalculation(charaInfoData, statusInfos)
    # print(charaInfoData.rank, skillAddedfromRankList, skillList)

    return charaInfoData, weaponInfo, relicList, skillList, relicSetList

    # print("charaInfoData", charaInfoData, "\n\nweaponInfo", weaponInfo,
    #       "\n\nrelicList", relicList, "\n\nskillList", skillList, "\n\nrelicSetList", relicSetList, "\n\nstatusInfos", statusInfos)


def addStatus(statusInfos, type: str, value: float):
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
    elif type == "SpeedAddedRatio":
        statusInfos.speed_per += value
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
        print(type, "typeが不正です")


def statusCalculation(charaInfos: charaInfo, statusInfos: statusInfo):
    charaInfos.HP *= (1+statusInfos.HP_per)
    charaInfos.HP += statusInfos.HP
    charaInfos.ATK *= (1+statusInfos.ATK_per)
    charaInfos.ATK += statusInfos.ATK
    charaInfos.DEF *= (1+statusInfos.DEF_per)
    charaInfos.DEF += statusInfos.DEF
    charaInfos.speed *= (1+statusInfos.speed_per)
    charaInfos.speed += statusInfos.speed
    charaInfos.critical_per += statusInfos.critical_per
    charaInfos.critical_per *= 100
    charaInfos.criticak_Dmg += statusInfos.criticak_Dmg
    charaInfos.criticak_Dmg *= 100
    charaInfos.statusProbability += statusInfos.statusProbability
    charaInfos.statusProbability *= 100
    charaInfos.statusResistanc += statusInfos.statusResistanc
    charaInfos.statusResistanc *= 100
    charaInfos.elementAddedRatio.element = statusInfos.elementAddedRatio.element
    charaInfos.elementAddedRatio.value += statusInfos.elementAddedRatio.value
    charaInfos.elementAddedRatio.value *= 100
    charaInfos.breakDamageAddedRatio += statusInfos.breakDamageAddedRatio
    charaInfos.breakDamageAddedRatio *= 100
    charaInfos.SPRatio += statusInfos.SPRatio
    charaInfos.SPRatio *= 100

    return charaInfos
