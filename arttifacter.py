import requests
import pandas as pd
import json
import time

#UID = "800900921" おれ
#UID = "829061557"　みかん
# UID = "801713238"　まんぼう
#UID = "856275185"　ごりら
#UID = "802047702"　せんぱい
#UID = "850274276"　なかの


CharacterInfodata = pd.read_csv("./assetData/CharacterInfo.csv", header=None).values.tolist()
OptinInfoData = pd.read_csv("./assetData/OptionInfo.csv", header=None).values.tolist()
WeapoInfo = pd.read_csv("./assetData/weaponInfo.csv", header=None).values.tolist()
CharaInfo = pd.read_csv("./assetData/chara.csv", header=None).values.tolist()
TravereInfo = pd.read_csv("./assetData/TravererSkilMap.csv", header=None).values.tolist()
with open('./assetData/ApiDataMap.json', 'r', encoding="utf-8") as json_file:
    datamap = json.load(json_file)
with open('./assetData/namecards.json', 'r', encoding="utf-8") as json_file:
    namecardmap = json.load(json_file)

baseAvatar = "https://enka.network/ui/UI_AvatarIcon_"
baseNamecard = "https://enka.network/ui/"



def getData(UID):
    URL = "https://enka.network/u/" + str(UID) + "/__data.json"
    print(URL)
    r=requests.get(URL)
    response = r.json()
    DataBase = response["nodes"][1]["data"]
    PlayerINFO = DataBase[int(DataBase[0]["playerInfo"])]       #プレイヤー情報目次
    AvatarINFOlist = DataBase[int(DataBase[0]["avatarInfoList"])]

    PlayerInfo = []


    PlayerNameID = PlayerINFO["nickname"]
    PlayerLevelID = PlayerINFO["level"]
    WorldLevelID = PlayerINFO["worldLevel"]
    ProfileAvatarID = PlayerINFO["profilePicture"]
    showAvatarlistID = PlayerINFO["showAvatarInfoList"]
    
    try:
        NameCardID = PlayerINFO["showNameCardIdList"]
        for x in namecardmap:
            if int(x) == DataBase[int(DataBase[NameCardID][0])]:
                NameCardURL = baseNamecard + str(namecardmap[x]["picPath"][1]) + ".png"
            else:
                pass
    except:
        print("nonecardlist")
        NameCardURL = baseNamecard + "UI_NameCardPic_0_P.png"

    for x in CharaInfo:
        if x[0] == DataBase[int(DataBase[ProfileAvatarID]["avatarId"])]:
            AvatarNameURL = baseAvatar + x[1] + ".png"
        else:
            pass

    PlayerInfo.append(DataBase[PlayerNameID])
    PlayerInfo.append(DataBase[PlayerLevelID])
    PlayerInfo.append(DataBase[WorldLevelID])
    PlayerInfo.append(NameCardURL)
    PlayerInfo.append(AvatarNameURL)
    showAvatarlist = DataBase[showAvatarlistID]

    # print(showAvatarlist)
    # print(AvatarINFOlist)

    return DataBase,showAvatarlist,AvatarINFOlist,PlayerInfo



# def getAvatarIDList(DataBase,showAvatarlist):

#     for showCharactorID in showAvatarlist:
#         info = DataBase[showCharactorID]
#         IDcharacter = info["avatarId"]#if分でこれつかう
#         IDcharacterLevel = info["level"]


#         xxx = ""
#         for x in CharacterInfodata:
#                     if DataBase[IDcharacter] == x[0]:
#                         xxx = x[2]
#                     else:
#                         pass
#         print(IDcharacter)
#         print("キャラクターは"+ xxx + "("+str(DataBase[IDcharacter])+")")
#         print("キャラクターのレベルは"+str(DataBase[IDcharacterLevel]))

#     selectCharacterID = input() ##変える
#     ScoreState = input()
#     return selectCharacterID,ScoreState



def getCharacterStatusfromselect(DataBase,selectCharacterID,AvatarINFOlist,ScoreState,defaultUser):
    for i in AvatarINFOlist:
        
        if int(selectCharacterID) == int(DataBase[int(i)]["avatarId"]):
            AvatarInfo = DataBase[int(i)]
            StatusList = []
            
            #CharacterStatus
            #name
            Name = DataBase[int(AvatarInfo["avatarId"])]
            for x in CharacterInfodata:
                if Name == x[0]:
                    if Name == 10000005 or Name == 10000007:#主人公の元素判断
                        TravererSklillId = DataBase[int(DataBase[int(AvatarInfo["inherentProudSkillList"])][0])]
                        for y in TravereInfo:
                            if int(y[1]) == int(TravererSklillId):
                                print("getElment")
                                Element = y[0]
                            else:
                                pass
                    
                        Name = x[2] +"(" + Element +")"

                    elif Name == 10000041 and int(defaultUser) == 672094270072553533:
                        Name = x[2] + "(ゴリラ)"
                        Element = x[3]


                    else:
                        Name = x[2]
                        Element = x[3]
                else:
                    pass
            
            #const
            try:
                Const = len(DataBase[int(AvatarInfo["talentIdList"])])
            except:
                Const = 0
            #level
            Level = DataBase[int(DataBase[int(selectCharacterID)-1]["level"])]
            #costume
            try:
                global CostuneID
                CostuneID= DataBase[int(DataBase[int(selectCharacterID)-1]["costumeId"])]
                print(Name)
            except:
                CostuneID = ""
                pass

           



            #love
            Love = DataBase[int(DataBase[int(AvatarInfo["fetterInfo"])]["expLevel"])]
            
            #statusmap
            StatusMap=DataBase[int(AvatarInfo["fightPropMap"])]
            #HP
            BaseHP = DataBase[int(StatusMap["1"])]
            try:
                artHP =DataBase[int(StatusMap["2"])]
            except:
                artHP = 0
            try:
                artHPpersent = DataBase[int(StatusMap["3"])]
            except:
                artHPpersent = 0
            HP = BaseHP + (BaseHP*artHPpersent+artHP)
            #attack
            BaseAttack = DataBase[int(StatusMap["4"])]
            try:
                artAttack = DataBase[int(StatusMap["5"])]
            except:
                artAttack = 0
            try:
                artAttackpersent = DataBase[int(StatusMap["6"])]
            except:
                artAttackpersent = 0
            Attack = BaseAttack + (BaseAttack*artAttackpersent+artAttack)
            #Defence
            BaseDefence = DataBase[int(StatusMap["7"])]
            try: 
                artDefence = DataBase[int(StatusMap["8"])] 
            except:
                artDefence=0
            try:
                artDefencepersent = DataBase[int(StatusMap["9"])]
            except:
                artDefencepersent = 0
            Defence = BaseDefence + (BaseDefence*artDefencepersent+artDefence)
            #ElemntalMastery
            ElemntalMastery = DataBase[int(StatusMap["28"])]
            #CriticalPresent
            CriticalPresent = DataBase[int(StatusMap["20"])]*100
            #CriticalDamage
            CriticalDamage = DataBase[int(StatusMap["22"])]*100
            #ElementDamageBuff
            buffname = ""
            count = 0
            buffvalue = 0
            bufflist = [[30,"物理ダメージ"],[40,"炎元素ダメージ"],[41,"雷元素ダメージ"],[42,"水元素ダメージ"],[43,"草元素ダメージ"],[44,"風元素ダメージ"],[45,"岩元素ダメージ"],[46,"氷元素ダメージ"]]
            for i,id in bufflist:
                buffvalueDummy = DataBase[int(StatusMap[str(i)])] * 100
                if buffvalueDummy > 0 and buffvalue < buffvalueDummy:
                    buffname = id
                    buffvalue = buffvalueDummy
                else:
                    count += 1
                    pass
            if count == 8:
                buffvalue = 0
                buffname = Element + "元素ダメージ"



            #ElementChargeEfficiency
            ElementChargeEfficiency = DataBase[int(StatusMap["23"])]*100
            #skillLevel
            SkillLevelMap=DataBase[int(AvatarInfo["skillLevelMap"])]
            SkillID = []
            for key in SkillLevelMap:
                SkillID.append(key)
            #TalentBaseLevel
            if Name[:1] == "蛍" or Name[:1] == "空":
                TalentBaseLevel = DataBase[int(SkillLevelMap[SkillID[2]])]

            elif Name == "神里綾華":
                TalentBaseLevel = DataBase[int(SkillLevelMap[SkillID[1]])]
            else:  
                TalentBaseLevel = DataBase[int(SkillLevelMap[SkillID[0]])]
            #TalentExtraLevel
            TalentExtraLevel = 1
            for x in CharacterInfodata:
                if Name[:1] == "蛍" or Name[:1] == "空":
                    for y in TravereInfo:
                        if Const <= 2:
                            TalentExtraLevel = int(DataBase[int(SkillLevelMap[SkillID[0]])])
                        elif Const >= 3:
                            if Const >=3 and y[2] == 1:
                                TalentExtratLevel = int(DataBase[int(SkillLevelMap[SkillID[0]])]) 
                            elif Const >= 3 and y[2] != 1:
                                TalentExtraLevel = int(DataBase[int(SkillLevelMap[SkillID[0]])])+3
                            
                        elif Const >= 5 and y[2] != 1:
                            TalentExtraLevel = int(DataBase[int(SkillLevelMap[SkillID[0]])]) + 3
                
                elif Name == "神里綾華":
                    for y in TravereInfo:
                        if Const <= 2:
                            TalentExtraLevel = int(DataBase[int(SkillLevelMap[SkillID[2]])])
                        elif Const >= 3:
                            if Const >=3 and x[1] == 1:
                                TalentExtraLevel = int(DataBase[int(SkillLevelMap[SkillID[2]])]) 
                            elif Const >= 3 and x[1] != 1:
                                TalentExtraLevel = int(DataBase[int(SkillLevelMap[SkillID[2]])])+3
                            
                        elif Const >= 5 and y[2] != 1:
                            TalentExtraLevel = int(DataBase[int(SkillLevelMap[SkillID[2]])]) + 3

                else:           
                    if Const <= 2:
                        TalentExtraLevel = int(DataBase[int(SkillLevelMap[SkillID[1]])])
                    elif Const >= 3 and Name == x[2]:
                        if Const >=3 and x[1] == 1:
                            TalentExtraLevel = int(DataBase[int(SkillLevelMap[SkillID[1]])])
                        elif Const >= 3 and x[1] != 1:
                            TalentExtraLevel = int(DataBase[int(SkillLevelMap[SkillID[1]])]) +3

                    elif Const >= 5 and Name == x[2] and x[1] != 0:
                        TalentExtraLevel = int(DataBase[int(SkillLevelMap[SkillID[1]])]) + 3

            #TalentBurstLevel
            TalentBurstLevel = 1
            for x in CharacterInfodata:
                if Name[:1] == "蛍" or Name[:1] == "空":
                    for y in TravereInfo:
                        if Const <= 2:
                            TalentBurstLevel = int(DataBase[int(SkillLevelMap[SkillID[1]])])
                        elif Const >= 3:
                            if Const >=3 and y[2] == 1:
                                TalentBurstLevel = int(DataBase[int(SkillLevelMap[SkillID[1]])]) +3
                            elif Const >= 3 and y[2] != 1:
                                TalentBurstLevel = int(DataBase[int(SkillLevelMap[SkillID[1]])])
                            
                        elif Const >= 5 and y[2] != 1:
                            TalentBurstLevel = int(DataBase[int(SkillLevelMap[SkillID[1]])]) + 3
                        
                elif Name == "神里綾華":
                    for y in TravereInfo:
                        if Const <= 2:
                            TalentBurstLevel = int(DataBase[int(SkillLevelMap[SkillID[3]])])
                        elif Const >= 3:
                            if Const >=3 and x[1] == 1:
                                TalentBurstLevel = int(DataBase[int(SkillLevelMap[SkillID[3]])]) +3
                            elif Const >= 3 and x[1] != 1:
                                TalentBurstLevel = int(DataBase[int(SkillLevelMap[SkillID[3]])])

                            
                        elif Const >= 5 and y[2] != 1:
                            TalentBurstLevel = int(DataBase[int(SkillLevelMap[SkillID[3]])]) + 3

                elif Name == "モナ" or Name == "モナ(ゴリラ)":
                    for y in TravereInfo:
                        if Const <= 2:
                            TalentBurstLevel = int(DataBase[int(SkillLevelMap[SkillID[3]])])
                        elif Const >= 3:
                            if Const >=3 and x[1] == 1:
                                TalentBurstLevel = int(DataBase[int(SkillLevelMap[SkillID[3]])]) +3
                            elif Const >= 3 and x[1] != 1:
                                TalentBurstLevel = int(DataBase[int(SkillLevelMap[SkillID[3]])])
                            
                        elif Const >= 5 and y[2] != 1:
                            TalentBurstLevel = int(DataBase[int(SkillLevelMap[SkillID[3]])]) + 3
                
                else:
                
                    if Const <= 2:
                        TalentBurstLevel = int(DataBase[int(SkillLevelMap[SkillID[2]])])
                    elif Const >= 3 and Name == x[2]:
                        if Const >=3 and x[1] == 1:
                            TalentBurstLevel = int(DataBase[int(SkillLevelMap[SkillID[2]])]) +3
                        elif Const >= 3 and x[1] != 1:
                            TalentBurstLevel = int(DataBase[int(SkillLevelMap[SkillID[2]])])
                        
                    elif Const >= 5 and Name == x[2] and x[1] != 1:
                        TalentBurstLevel = int(DataBase[int(SkillLevelMap[SkillID[2]])]) + 3
                    



            StatusList.append(Name)
            StatusList.append(Const)
            StatusList.append(Level)
            StatusList.append(Love)
            StatusList.append(round(HP))
            StatusList.append(round(Attack))
            StatusList.append(round(Defence))
            StatusList.append(round(ElemntalMastery))
            StatusList.append(round(CriticalPresent,1))
            StatusList.append(round(CriticalDamage,1))
            StatusList.append(round(ElementChargeEfficiency,1))
            StatusList.append(buffname)
            StatusList.append(round(buffvalue,1))
            StatusList.append(TalentBaseLevel)
            StatusList.append(TalentExtraLevel)
            StatusList.append(TalentBurstLevel)
            StatusList.append(round(BaseHP))
            StatusList.append(round(BaseAttack))
            StatusList.append(round(BaseDefence))

            DataBase[int(i)]
            print(StatusList)


            #CharacterWeapon&ArtifactStatus
            WeaponID = ""
            ArtifactID = []
            WeaponStatus = []
            for x in DataBase[int(AvatarInfo["equipList"])]:
                try:
                    #聖遺物
                    DataBase[int(DataBase[x]["reliquary"])]
                    ArtifactID.append(x)
                    
                except:
                    #武器
                    DataBase[int(DataBase[x]["weapon"])]
                    WeaponID = x
            
            #WeaponStatus
            #WeaponName
            WeaponNameID = DataBase[int(DataBase[WeaponID]["itemId"])]
            for x in WeapoInfo:
                if WeaponNameID == x[0]:
                    WeaponName  = x[1]

                else:
                    pass
            #WeponBaseData
            WeaponBaseData = DataBase[int(DataBase[WeaponID]["weapon"])]
            #WeaponLevel
            WeaponLevel = DataBase[int(WeaponBaseData["level"])]
            #WeaponRank
            for value in DataBase[int(WeaponBaseData["affixMap"])].values():
                WeaponRankID = value
                WeaponRank = DataBase[WeaponRankID]
            #WeaponStatusBaseData
            WeaponStatusBaseData = DataBase[int(DataBase[WeaponID]["flat"])]
            #WeaponRarelity
            WeaponRarelity = DataBase[int(WeaponStatusBaseData["rankLevel"])]
            #WeaponBase
            WeapnBase = DataBase[int(WeaponStatusBaseData["weaponStats"])]
            for x in WeapnBase:
                if DataBase[int(DataBase[x]["appendPropId"])] == "FIGHT_PROP_BASE_ATTACK":
                    #WeaponBaseattack
                    WeaponBaseattack = DataBase[int(DataBase[x]["statValue"])]
                else:
                    #WeaponSubStatusName
                    for y in OptinInfoData:
                        if y[0] == DataBase[int(DataBase[x]["appendPropId"])]:
                            WeaponSubStatusName = y[1]
                        else:
                            pass
                    #WeaponSubStatusValue
                    WeaponSubStatusValue = DataBase[int(DataBase[x]["statValue"])]


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
                #print(DataBase[x])
                #TypeArtifact
                TypeArtifactID = DataBase[int(DataBase[x]["flat"])]["equipType"]


                #ArtifactType
                setNameID = DataBase[int(DataBase[int(DataBase[x]["flat"])]["setNameTextMapHash"])]
                ArtifactType = datamap[setNameID]
                #ArtifactLevel
                level=DataBase[int(DataBase[int(DataBase[x]["reliquary"])]["level"])]
                ArtifactLevel = level - 1
                #ArtifactRarelity
                RarelityID=DataBase[int(DataBase[x]["flat"])]["rankLevel"]
                ArtifactRarelity = DataBase[RarelityID]
                #ArtifactMainOp
                MainOpMap=DataBase[int(DataBase[int(DataBase[x]["flat"])]["reliquaryMainstat"])]
                for y in OptinInfoData:
                        if y[0] == DataBase[int(MainOpMap["mainPropId"])]:
                            ArtifactMainOp = y[1]
                        else:
                            pass
                #ArtifactMainValue
                ArtifactMainValue=DataBase[int(MainOpMap["statValue"])]
                #ArtifactSub
                SubOpMap=DataBase[int(DataBase[int(DataBase[x]["flat"])]["reliquarySubstats"])]
                # print(SubOpMap)
                #ArtifactSubOpName
                for i,y in enumerate(SubOpMap):
                    for z in OptinInfoData:
                        if z[0] == DataBase[int(DataBase[y]["appendPropId"])]:
                            OpName = z[1]
                        else:
                            pass
                    #ArtifactSubOpValue
                    OpValue = DataBase[int(DataBase[y]["statValue"])]
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


                if DataBase[TypeArtifactID] == "EQUIP_BRACER":
                    flowerStatus = Status
                elif DataBase[TypeArtifactID] == "EQUIP_NECKLACE":
                    wingStatus = Status
                elif DataBase[TypeArtifactID] == "EQUIP_SHOES":
                    clockStatus = Status
                elif DataBase[TypeArtifactID] == "EQUIP_RING":
                    cupStatus = Status
                elif DataBase[TypeArtifactID] == "EQUIP_DRESS":
                    crownStatus = Status

                

                Status = []
            
            print(flowerStatus)
            print(wingStatus)
            print(clockStatus)
            print(cupStatus)
            print(crownStatus)

            Score = OutputScore(flowerStatus,wingStatus,clockStatus,cupStatus,crownStatus,ScoreState)
            print(Score)
            print(Element)



           
            return StatusList,WeaponStatus,flowerStatus,wingStatus,clockStatus,cupStatus,crownStatus,Score,Element
        
        else:
            print("error")

       

def calcScore(List,State):
    State_Value = 0
    Critical_percent = 0
    Critical_damege = 0

    for i,x in enumerate(List):
        
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
    
    return round(toal,1)
    # return toal
            
def OutputScore(flower,wing,clock,cup,crown,State):
    XX = []
    XX.append(State)

    X1 = calcScore(flower,State)  
    X2 = calcScore(wing,State)   
    X3 = calcScore(clock,State) 
    X4 = calcScore(cup,State)  
    X5 = calcScore(crown,State) 
    XX.append(round(X1+X2+X3+X4+X5,1))
    XX.append(X1)
    XX.append(X2)
    XX.append(X3)
    XX.append(X4)
    XX.append(X5)

    return XX



def genJson(DataBase,selectCharacterID,AvatarINFOlist,ScoreState,defaultUser):
    print("selectID:"+str(selectCharacterID))
    print(AvatarINFOlist)
    status,weapon,flower,wing,clock,cup,crown,score,element = getCharacterStatusfromselect(DataBase,selectCharacterID,AvatarINFOlist,ScoreState,defaultUser)

    global CostuneID

    BASE=json.dumps({
    "uid":  0,
    "input": "",
    "Character": {
        "Name": status[0],
        "Const": status[1],
        "Level": status[2],
        "Love": status[3],
        "Costume":CostuneID,
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
            },}, ensure_ascii=False) 
        
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
        },ensure_ascii=False)

        addArtifact.append(crownStatus[1:-1])
    else:
        pass
    Element = json.dumps({"元素": element}, ensure_ascii=False)





    for x in addArtifact:
        AllArtifacts += x+","
    artifact = '"Artifacts":{' +AllArtifacts
    

    jsonCode = BASE[:-1]+","+artifact[:-1]+"},"+Element[1:]

    with open('ArtifacterImageGen/data.json', 'w',encoding='utf-8') as f:
        f.write(jsonCode)




# DataBase,showAvatarlist,AvatarINFOlist,PlayerInfo = getData(800900921)
# selectCharacterID,ScoreState = getAvatarIDList(DataBase,showAvatarlist)
# genJson(DataBase,selectCharacterID,AvatarINFOlist,ScoreState)

# time.sleep(1)
# import ArtifacterImageGen.Generater