import requests
import pandas as pd
import json
import time
import discord
import update

baseURL = "https://enka.network/ui/"

with open('API-docs/store/namecards.json', 'r', encoding="utf-8") as json_file:
    namecard = json.load(json_file)

with open('API-docs/store/characters.json', 'r', encoding="utf-8") as json_file:
    characters = json.load(json_file)

with open('assetData/OptionInfo.json', 'r', encoding="utf-8") as json_file:
    OptionName = json.load(json_file)

with open('API-docs/store/loc.json', 'r', encoding="utf-8") as json_file:
    nameItem = json.load(json_file)


GUID = 0


def transeElement(Element):
    if Element == "Wind":
        return "風"
    elif Element == "Rock":
        return "岩"
    elif Element == "Electric":
        return "雷"
    elif Element == "Grass":
        return "草"
    elif Element == "Ice":
        return "氷"
    elif Element == "Fire":
        return "炎"
    elif Element == "Water":
        return "水"


def getData(UID):
    global GUID
    GUID = UID
    URL = "https://enka.network/api/uid/" + str(UID)
    print(URL)
    r = requests.get(URL)
    status = r.status_code
    if status == 424:
        return "EnkaAPIが停止しています\nしばらくお待ちください"
    elif status == 404:
        return "UIDが違うか、キャラ詳細が公開されていません"
    else:
        pass
    response = r.json()
    DataBase = response["avatarInfoList"]
    PlayerINFO = response["playerInfo"]  # プレイヤー情報目次

    PlayerInfo = []

    PlayerName = PlayerINFO["nickname"]
    PlayerLevel = PlayerINFO["level"]
    WorldLevel = PlayerINFO["worldLevel"]
    showAvatarlistID = PlayerINFO["showAvatarInfoList"]

    NameCardID = PlayerINFO["nameCardId"]

    NameCardName = namecard[str(NameCardID)]["icon"]
    NameCardURL = baseURL + NameCardName + ".png"

    try:
        ProfileAvatarID = PlayerINFO["profilePicture"]["avatarId"]
        ProfileAvatarname = characters[str(ProfileAvatarID)]["SideIconName"]
        name = ProfileAvatarname.split("_")
        AvatarNameURL = baseURL + name[0] + "_" + name[1]+"_"+name[3]+".png"
    except:
        AvatarNameURL = None

    PlayerInfo.append(PlayerName)
    PlayerInfo.append(PlayerLevel)
    PlayerInfo.append(WorldLevel)
    PlayerInfo.append(NameCardURL)
    PlayerInfo.append(AvatarNameURL)
    showAvatarlist = showAvatarlistID

    # print(showAvatarlist)
    # print(AvatarINFOlist)

    return DataBase, showAvatarlist, PlayerInfo


def getCharacterStatusfromselect(DataBase, showAvatarData, ScoreState, authorInfo):
    User_UID_Data = pd.read_csv(
        "./assetData/user_UID_data.csv", header=None).values.tolist()

    StatusList = []
    global GUID

    # CharacterStatus
    # name
    selectCharaID = DataBase["avatarId"]
    characterDataBase = characters[str(selectCharaID)]
    selectCharaHashID = characterDataBase["NameTextMapHash"]
    Name = nameItem["ja"][str(selectCharaHashID)]
    if Name == "旅人":  # 主人公の元素判断
        TravelerElementID = DataBase["skillDepotId"]
        characterDataBase = characters[str(
            selectCharaID) + "-" + str(TravelerElementID)]
        # print(characterDataBase)
        TravelerElement = characterDataBase["Element"]
        Element = transeElement(TravelerElement)
        if selectCharaID == 10000005:
            Name = "空"
        else:
            Name = "蛍"
        Name = Name + "(" + Element + ")"
    else:  # 主人公じゃない場合元素を取得
        CharaElement = characters[str(selectCharaID)]["Element"]
        Element = transeElement(CharaElement)

    for i, x in enumerate(User_UID_Data):
        if GUID == x[1]:
            if Name == x[2]:
                Name = Name + "("+authorInfo.name+")"
                print(Name)
            else:
                print("unmatch")

    print(Name)

    # const
    try:
        Const = len(DataBase["talentIdList"])
    except:
        Const = 0
    # level
    Level = showAvatarData["level"]
    # costume
    try:
        global CostuneID
        CostuneID = showAvatarData["costumeId"]
    except:
        CostuneID = ""
        pass

    # love
    Love = DataBase["fetterInfo"]["expLevel"]

    # statusmap
    StatusMap = DataBase["fightPropMap"]
    # HP
    BaseHP = StatusMap["1"]
    try:
        artHP = StatusMap["2"]
    except:
        artHP = 0
    try:
        artHPpersent = StatusMap["3"]
    except:
        artHPpersent = 0
    HP = BaseHP + (BaseHP*artHPpersent+artHP)
    # attack
    BaseAttack = StatusMap["4"]
    try:
        artAttack = StatusMap["5"]
    except:
        artAttack = 0
    try:
        artAttackpersent = StatusMap["6"]
    except:
        artAttackpersent = 0
    Attack = BaseAttack + (BaseAttack*artAttackpersent+artAttack)
    # Defence
    BaseDefence = StatusMap["7"]
    try:
        artDefence = StatusMap["8"]
    except:
        artDefence = 0
    try:
        artDefencepersent = StatusMap["9"]
    except:
        artDefencepersent = 0
    Defence = BaseDefence + (BaseDefence*artDefencepersent+artDefence)
    # ElemntalMastery
    ElemntalMastery = StatusMap["28"]
    # CriticalPresent
    CriticalPresent = StatusMap["20"]*100
    # CriticalDamage
    CriticalDamage = StatusMap["22"]*100
    # ElementDamageBuff
    buffname = ""
    count = 0
    buffvalue = 0
    bufflist = [[30, "物理ダメージ"], [40, "炎元素ダメージ"], [41, "雷元素ダメージ"], [42, "水元素ダメージ"], [
        43, "草元素ダメージ"], [44, "風元素ダメージ"], [45, "岩元素ダメージ"], [46, "氷元素ダメージ"]]
    for i, id in bufflist:
        buffvalueDummy = StatusMap[str(i)] * 100
        if buffvalueDummy > 0 and buffvalue < buffvalueDummy:
            buffname = id
            buffvalue = buffvalueDummy
        else:
            count += 1
            pass
    if count == 8:
        buffvalue = 0
        buffname = Element + "元素ダメージ"

    # ElementChargeEfficiency
    ElementChargeEfficiency = StatusMap["23"]*100
    # skillLevel
    SkillLevelMap = DataBase["skillLevelMap"]
    TalentDataMap = characterDataBase["SkillOrder"]
    # TalentBaseLevel
    TalentBase = TalentDataMap[0]
    TalentBaseLevel = SkillLevelMap[str(TalentBase)]
    # TalentExtraLevel
    TalentExtra = TalentDataMap[1]
    BootsExtraSkillLevelID = characterDataBase["ProudMap"][str(TalentExtra)]
    try:
        BootsExtraSkillLevel = DataBase["proudSkillExtraLevelMap"][str(
            BootsExtraSkillLevelID)]
    except:
        BootsExtraSkillLevel = 0
    TalentExtraLevel = int(
        SkillLevelMap[str(TalentExtra)]) + int(BootsExtraSkillLevel)
    # TalentBurstLevel
    TalentBurst = TalentDataMap[2]
    BootsBurstSkillLevelID = characterDataBase["ProudMap"][str(TalentBurst)]
    try:
        BootsBurstSkillLevel = DataBase["proudSkillExtraLevelMap"][str(
            BootsBurstSkillLevelID)]
    except:
        BootsBurstSkillLevel = 0
    TalentBurstLevel = int(
        SkillLevelMap[str(TalentBurst)]) + int(BootsBurstSkillLevel)

    StatusList.append(Name)
    StatusList.append(Const)
    StatusList.append(Level)
    StatusList.append(Love)
    StatusList.append(round(HP))
    StatusList.append(round(Attack))
    StatusList.append(round(Defence))
    StatusList.append(round(ElemntalMastery))
    StatusList.append(round(CriticalPresent, 1))
    StatusList.append(round(CriticalDamage, 1))
    StatusList.append(round(ElementChargeEfficiency, 1))
    StatusList.append(buffname)
    StatusList.append(round(buffvalue, 1))
    StatusList.append(TalentBaseLevel)
    StatusList.append(TalentExtraLevel)
    StatusList.append(TalentBurstLevel)
    StatusList.append(round(BaseHP))
    StatusList.append(round(BaseAttack))
    StatusList.append(round(BaseDefence))

    print(StatusList)

    # CharacterWeapon&ArtifactStatus
    WeaponID = ""
    ArtifactID = []
    WeaponStatus = []
    for x in DataBase["equipList"]:
        try:
            # 聖遺物
            x["reliquary"]
            ArtifactID.append(x)

        except:
            # 武器
            x["weapon"]
            Weapon = x

    # WeaponStatus
    # WeaponName
    WeaponNameID = Weapon["flat"]["nameTextMapHash"]
    itemPath = Weapon["flat"]["icon"]
    update.checkUpdateGenshin_weapon(WeaponNameID, itemPath)
    WeaponName = nameItem["ja"][str(WeaponNameID)]

    # WeponBaseData
    WeaponBaseData = Weapon["weapon"]
    # WeaponLevel
    WeaponLevel = WeaponBaseData["level"]
    # WeaponRank
    try:
        WeaponRank = int(WeaponBaseData["affixMap"]
                         ["1" + str(Weapon["itemId"])])+1
    except:
        WeaponRank = 1

    # WeaponStatusBaseData
    WeaponStatusBaseData = Weapon["flat"]
    # WeaponRarelity
    WeaponRarelity = WeaponStatusBaseData["rankLevel"]
    # WeaponBase
    WeapnBase = WeaponStatusBaseData["weaponStats"]
    for x in WeapnBase:
        if x["appendPropId"] == "FIGHT_PROP_BASE_ATTACK":
            # WeaponBaseattack
            WeaponBaseattack = x["statValue"]
        else:
            # WeaponSubStatusName
            WeaponSubStatusName = x["appendPropId"]
            WeaponSubStatusName = nameItem["ja"][str(WeaponSubStatusName)]

            # WeaponSubStatusValue
            WeaponSubStatusValue = x["statValue"]

    WeaponStatus.append(WeaponName)
    WeaponStatus.append(WeaponLevel)
    WeaponStatus.append(WeaponRank)
    WeaponStatus.append(WeaponRarelity)
    WeaponStatus.append(WeaponBaseattack)
    WeaponStatus.append(WeaponSubStatusName)
    WeaponStatus.append(WeaponSubStatusValue)

    print(WeaponStatus)

    Status = []
    flowerStatus = []
    wingStatus = []
    clockStatus = []
    cupStatus = []
    crownStatus = []
    ArtifactSub1Op = ""
    ArtifactSub2Op = ""
    ArtifactSub3Op = ""
    ArtifactSub4Op = ""
    ArtifactSub1Value = ""
    ArtifactSub2Value = ""
    ArtifactSub3Value = ""
    ArtifactSub4Value = ""
    # EQUIP_BRACER
    # EQUIP_NECKLACE
    # EQUIP_SHOES
    # EQUIP_RING
    # EQUIP_DRESS

    for x in ArtifactID:
        # print(DataBase[x])
        # TypeArtifact
        TypeArtifactID = x["flat"]["equipType"]

        # ArtifactType
        setNameID = x["flat"]["setNameTextMapHash"]
        ArtifactType = nameItem["ja"][str(setNameID)]
        update.checkUpdateGenshin_relic(
            TypeArtifactID, x["flat"]["icon"], setNameID)
        print(TypeArtifactID, x["flat"]["icon"], setNameID)
        print("--------------------check--------------------")
        # ArtifactLevel
        level = x["reliquary"]["level"]
        ArtifactLevel = level - 1
        # ArtifactRarelity
        ArtifactRarelity = x["flat"]["rankLevel"]
        # ArtifactMainOp
        MainOpMap = x["flat"]["reliquaryMainstat"]
        MainOpMapName = MainOpMap["mainPropId"]
        ArtifactMainOp = OptionName[str(MainOpMapName)]

        # ArtifactMainValue
        ArtifactMainValue = MainOpMap["statValue"]
        # ArtifactSub
        SubOpMap = x["flat"]["reliquarySubstats"]
        # print(SubOpMap)
        # ArtifactSubOpName
        for i, y in enumerate(SubOpMap):

            OpName = y["appendPropId"]
            OpName = OptionName[str(OpName)]
            # ArtifactSubOpValue
            OpValue = y["statValue"]
            if i == 0:
                ArtifactSub1Op = OpName
                ArtifactSub1Value = OpValue
            elif i == 1:
                ArtifactSub2Op = OpName
                ArtifactSub2Value = OpValue
            elif i == 2:
                ArtifactSub3Op = OpName
                ArtifactSub3Value = OpValue
            elif i == 3:
                ArtifactSub4Op = OpName
                ArtifactSub4Value = OpValue

        Status.append(ArtifactType)
        Status.append(ArtifactLevel)
        Status.append(ArtifactRarelity)
        Status.append(ArtifactMainOp)
        Status.append(ArtifactMainValue)
        Status.append(ArtifactSub1Op)
        Status.append(ArtifactSub1Value)
        Status.append(ArtifactSub2Op)
        Status.append(ArtifactSub2Value)
        Status.append(ArtifactSub3Op)
        Status.append(ArtifactSub3Value)
        Status.append(ArtifactSub4Op)
        Status.append(ArtifactSub4Value)

        if TypeArtifactID == "EQUIP_BRACER":
            flowerStatus = Status
        elif TypeArtifactID == "EQUIP_NECKLACE":
            wingStatus = Status
        elif TypeArtifactID == "EQUIP_SHOES":
            clockStatus = Status
        elif TypeArtifactID == "EQUIP_RING":
            cupStatus = Status
        elif TypeArtifactID == "EQUIP_DRESS":
            crownStatus = Status

        Status = []

    print(flowerStatus)
    print(wingStatus)
    print(clockStatus)
    print(cupStatus)
    print(crownStatus)

    Score = OutputScore(flowerStatus, wingStatus, clockStatus,
                        cupStatus, crownStatus, ScoreState)
    print(Score)
    print(Element)

    return StatusList, WeaponStatus, flowerStatus, wingStatus, clockStatus, cupStatus, crownStatus, Score, Element


def calcScore(List, State):
    State_Value = 0
    Critical_percent = 0
    Critical_damege = 0

    for i, x in enumerate(List):

        if i < 4:
            pass
        elif x == "会心率":
            Critical_percent = List[i+1]*2
        elif x == "会心ダメージ":
            Critical_damege = List[i+1]
        elif x == State:

            if State == "元素熟知":
                State_Value = List[i+1]/4
            elif State_Value != 0:
                pass
            else:
                State_Value = List[i+1]

    toal = Critical_damege + Critical_percent + State_Value

    return round(toal, 1)
    # return toal


def OutputScore(flower, wing, clock, cup, crown, State):
    XX = []
    XX.append(State)

    X1 = calcScore(flower, State)
    X2 = calcScore(wing, State)
    X3 = calcScore(clock, State)
    X4 = calcScore(cup, State)
    X5 = calcScore(crown, State)
    XX.append(round(X1+X2+X3+X4+X5, 1))
    XX.append(X1)
    XX.append(X2)
    XX.append(X3)
    XX.append(X4)
    XX.append(X5)

    return XX


def genJson(DataBase, showAvatarData, ScoreState, authorInfo):
    status, weapon, flower, wing, clock, cup, crown, score, element = getCharacterStatusfromselect(
        DataBase, showAvatarData, ScoreState, authorInfo)

    global CostuneID

    BASE = json.dumps({
        "uid":  0,
        "input": "",
        "Character": {
            "Name": status[0],
            "Const": status[1],
            "Level": status[2],
            "Love": status[3],
            "Costume": CostuneID,
            "Status": {
                "HP": status[4],
                "攻撃力": status[5],
                "防御力": status[6],
                "元素熟知": status[7],
                "会心率": status[8],
                "会心ダメージ": status[9],
                "元素チャージ効率": status[10],
                status[11]: status[12]
            },
            "Talent": {
                "通常": status[13],
                "スキル": status[14],
                "爆発": status[15]
            },
            "Base": {
                "HP": status[16],
                "攻撃力": status[17],
                "防御力": status[18]
            }

        },
        "Weapon": {
            "name": weapon[0],
            "Level": weapon[1],
            "totu": weapon[2],
            "rarelity": weapon[3],
            "BaseATK": weapon[4],
            "Sub": {
                "name": weapon[5],
                "value": weapon[6]
            }
        },
        "Score": {
            "State": score[0],
            "total": score[1],
            "flower": score[2],
            "wing": score[3],
            "clock": score[4],
            "cup": score[5],
            "crown": score[6]
        }}, ensure_ascii=False)

    addArtifact = []
    AllArtifacts = ""

    if len(flower) > 0:

        flowerStatus = json.dumps({
            "flower": {
                "type": flower[0],
                "Level": flower[1],
                "rarelity": flower[2],
                "main": {
                    "option": flower[3],
                    "value": flower[4]
                },
                "sub": [
                    {
                        "option": flower[5],
                        "value": flower[6]
                    },
                    {
                        "option": flower[7],
                        "value": flower[8]
                    },
                    {
                        "option": flower[9],
                        "value": flower[10]
                    },
                    {
                        "option": flower[11],
                        "value": flower[12]
                    }
                ]
            }, }, ensure_ascii=False)

        addArtifact.append(flowerStatus[1:-1])
    else:
        pass

    if len(wing) > 0:
        wingStatus = json.dumps({"wing": {
            "type": wing[0],
            "Level": wing[1],
            "rarelity": wing[2],
            "main": {
                "option": wing[3],
                "value":    wing[4]
            },
            "sub": [
                {
                    "option": wing[5],
                    "value": wing[6]
                },
                {
                    "option": wing[7],
                    "value": wing[8]
                },
                {
                    "option": wing[9],
                    "value": wing[10]
                },
                {
                    "option": wing[11],
                    "value": wing[12]
                }
            ]
        }}, ensure_ascii=False)
        addArtifact.append(wingStatus[1:-1])
    else:
        pass

    if len(clock) > 0:
        clockStatus = json.dumps({
            "clock": {
                "type": clock[0],
                "Level": clock[1],
                "rarelity": clock[2],
                "main": {
                    "option": clock[3],
                    "value": clock[4]
                },
                "sub": [
                    {
                        "option": clock[5],
                        "value": clock[6]
                    },
                    {
                        "option": clock[7],
                        "value": clock[8]
                    },
                    {
                        "option": clock[9],
                        "value": clock[10]
                    },
                    {
                        "option": clock[11],
                        "value": clock[12]
                    }
                ]
            }}, ensure_ascii=False)

        addArtifact.append(clockStatus[1:-1])
    else:
        pass

    if len(cup) > 0:
        cupStatus = json.dumps({
            "cup": {
                "type": cup[0],
                "Level": cup[1],
                "rarelity": cup[2],
                "main": {
                    "option": cup[3],
                    "value": cup[4]
                },
                "sub": [
                    {
                        "option": cup[5],
                        "value": cup[6]
                    },
                    {
                        "option": cup[7],
                        "value": cup[8]
                    },
                    {
                        "option": cup[9],
                        "value": cup[10]
                    },
                    {
                        "option": cup[11],
                        "value": cup[12]
                    }
                ]
            }}, ensure_ascii=False)

        addArtifact.append(cupStatus[1:-1])
    else:
        pass

    if len(crown) > 0:
        crownStatus = json.dumps({
            "crown": {
                "type": crown[0],
                "Level": crown[1],
                "rarelity": crown[2],
                "main": {
                    "option": crown[3],
                    "value": crown[4]
                },
                "sub": [
                    {
                        "option": crown[5],
                        "value": crown[6]
                    },
                    {
                        "option": crown[7],
                        "value": crown[8]
                    },
                    {
                        "option": crown[9],
                        "value": crown[10]
                    },
                    {
                        "option": crown[11],
                        "value": crown[12]
                    }
                ]
            }
        }, ensure_ascii=False)

        addArtifact.append(crownStatus[1:-1])
    else:
        pass
    Element = json.dumps({"元素": element}, ensure_ascii=False)

    for i, x in enumerate(addArtifact):
        if i == len(addArtifact) - 1:
            AllArtifacts += x
        else:
            AllArtifacts += x+","

    artifact = '"Artifacts":{' + AllArtifacts + "}"

    jsonCode = BASE[:-1]+","+artifact[:-1]+"},"+Element[1:]

    with open('ArtifacterImageGen/data.json', 'w', encoding='utf-8') as f:
        f.write(jsonCode)
