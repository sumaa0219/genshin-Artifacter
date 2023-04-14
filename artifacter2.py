import requests
import pandas as pd
import json
import time

baseURL = "https://enka.network/ui/"

with open('./API-docs/store/namecards.json', 'r') as json_file:
    namecard = json.load(json_file)

with open('./API-docs/store/characters.json', 'r') as json_file:
    characters = json.load(json_file)

with open('./API-docs/store/loc.json', 'r') as json_file:
    nameItem = json.load(json_file)


def getData(UID):
    URL = "https://enka.network/api/uid/" + str(UID)
    print(URL)
    r=requests.get(URL)
    response = r.json()
    DataBase = response["avatarInfoList"]
    PlayerINFO = response["playerInfo"]      #プレイヤー情報目次


    PlayerInfo = []


    PlayerName = PlayerINFO["nickname"]
    PlayerLevel = PlayerINFO["level"]
    WorldLevel = PlayerINFO["worldLevel"]
    showAvatarlistID = PlayerINFO["showAvatarInfoList"]

    NameCardID = PlayerINFO["nameCardId"]

    NameCardName = namecard[str(NameCardID)]["icon"]
    NameCardURL = baseURL + NameCardName + ".png"


    ProfileAvatarID = PlayerINFO["profilePicture"]["avatarId"]

    ProfileAvatarname = characters[str(ProfileAvatarID)]["SideIconName"]
    name = ProfileAvatarname.split("_")
    AvatarNameURL = baseURL + name[0] + "_" +name[1]+"_"+name[3]+".png"

    PlayerInfo.append(PlayerName)
    PlayerInfo.append(PlayerLevel)
    PlayerInfo.append(WorldLevel)
    PlayerInfo.append(NameCardURL)
    PlayerInfo.append(AvatarNameURL)
    showAvatarlist = showAvatarlistID

    # print(showAvatarlist)
    # print(AvatarINFOlist)

    return DataBase,showAvatarlist,PlayerInfo

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

getData(800900921)