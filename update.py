import requests
import json
import os
import subprocess

with open('./API-docs/store/characters.json', 'r', encoding="utf-8") as json_file:
    characters = json.load(json_file)

with open('./API-docs/store/loc.json', 'r', encoding="utf-8") as json_file:
    nameItem = json.load(json_file)


def updateWeightHSR():
    # git pullを実行するディレクトリ
    directory = 'StarRailScore'
    # subprocessを使用してgit pullを実行
    subprocess.Popen(['git', 'pull'], cwd=directory)


def updateAPI():
    # git pullを実行するディレクトリ
    directory = 'API-docs'
    # subprocessを使用してgit pullを実行
    subprocess.Popen(['git', 'pull'], cwd=directory)


def convertNameGenshin(nameHash):
    return nameItem["ja"][nameHash]


def saveImage(name, path):
    baseURL = "https://enka.network/ui/"
    r = requests.get(baseURL + name + ".png")
    with open(path, 'wb') as f:
        f.write(r.content)


def updateGenshin_Character():
    with open('./API-docs/store/characters.json', 'r', encoding="utf-8") as json_file:
        characters = json.load(json_file)
    addedCharaList = []
    for chara in characters:

        name = convertNameGenshin(str(characters[chara]["NameTextMapHash"]))
        dir = f"./ArtifacterImageGen/character/{name}"
        if not os.path.exists(dir):
            os.makedirs(dir)
            # 画像の保存
            # 凸画像
            for i, name in enumerate(characters[chara]["Consts"]):
                saveImage(name, dir+f"/{str(i+1)}.png")
            # キャラ画像
            charaENname = characters[chara]["SideIconName"].split("_")
            charaBase = "UI_Gacha_AvatarImg_" + charaENname[3]
            saveImage(charaBase, dir+"/avatar.png")
            # スキル画像
            for skill in characters[chara]["Skills"]:
                type = characters[chara]["Skills"][skill].split("_")
                if type[1] == "A":
                    saveImage(characters[chara]["Skills"]
                              [skill], dir+f"/通常.png")
                elif type[1] == "S":
                    saveImage(characters[chara]["Skills"]
                              [skill], dir+f"/スキル.png")
                elif type[1] == "E":
                    saveImage(characters[chara]["Skills"]
                              [skill], dir+f"/爆発.png")
            addedCharaList.append(name)
        # 　衣装画像
        try:
            if characters[chara]["Costumes"]:
                for costume in characters[chara]["Costumes"]:
                    saveImage(characters[chara]["Costumes"]
                              [costume]["art"], dir+f"/{costume}.png")
        except KeyError:
            pass
    return addedCharaList


def checkUpdateGenshin_weapon(nameHash, itemName):
    name = convertNameGenshin(nameHash)
    if not os.path.exists(f"./ArtifacterImageGen/weapon/{name}.png"):
        saveImage(itemName, f"./ArtifacterImageGen/weapon/{name}.png")


def checkUpdateGenshin_relic(equipType, icon, nameTextMapHash):
    name = convertNameGenshin(nameTextMapHash)
    dir = f"./ArtifacterImageGen/Artifact/{name}"
    if not os.path.exists(dir):
        os.makedirs(dir)
    if equipType == "EQUIP_BRACER":
        typeName = "flower"
    elif equipType == "EQUIP_NECKLACE":
        typeName = "wing"
    elif equipType == "EQUIP_SHOES":
        typeName = "clock"
    elif equipType == "EQUIP_RING":
        typeName = "cup"
    elif equipType == "EQUIP_DRESS":
        typeName = "crown"
    if not os.path.exists(dir+f"/{typeName}.png"):
        saveImage(icon, dir+f"/{typeName}.png")


def update():
    updateAPI()
    updateWeightHSR()
