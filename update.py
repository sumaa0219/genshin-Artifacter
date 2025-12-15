import requests
import json
import os
import subprocess
from mylogger import getLogger
logger = getLogger(__name__)

with open('./API-docs/store/characters.json', 'r', encoding="utf-8") as json_file:
    characters = json.load(json_file)

with open('./API-docs/store/loc.json', 'r', encoding="utf-8") as json_file:
    nameItem = json.load(json_file)


def updateAPI():
    logger.info("update API-docs from github")
    # git pullを実行するディレクトリ
    directory = 'API-docs'
    # subprocessを使用してgit pullを実行
    subprocess.Popen(['git', 'pull'], cwd=directory)


def convertNameGenshin(nameHash):
    """ハッシュからまず日本語(`ja`)で取得し、存在しなければ英語(`en`)を返す。
    両方に存在しない場合は KeyError を発生させる。"""
    sid = str(nameHash)
    try:
        return nameItem["ja"][sid]
    except KeyError:
        # ja に無ければ en を試す
        try:
            return nameItem["en"][sid]
        except KeyError:
            logger.error(f"Name not found in ja/en for hash: {sid}")
            raise


def saveImage(name, path):
    baseURL = "https://enka.network/ui/"
    r = requests.get(baseURL + name + ".png")
    with open(path, 'wb') as f:
        f.write(r.content)


def updateGenshin_Character():
    with open('./API-docs/store/characters.json', 'r', encoding="utf-8") as json_file:
        characters = json.load(json_file)
    addedCharaList = []
    for chara in characters.keys():
        try :
            name = convertNameGenshin(str(characters[chara]["NameTextMapHash"]))
            dir = f"./ArtifacterImageGen/character/{name}"
            print(dir)
            if not os.path.exists(dir):
                logger.warning(f"New character found: {name}")
                logger.info(f"start to download character: {name}")
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
        except KeyError:
            logger.error(f"KeyError: {chara}のデータが不完全です。")
            continue
    return addedCharaList


def checkUpdateGenshin_weapon(nameHash, itemName):
    name = convertNameGenshin(nameHash)
    if not os.path.exists(f"./ArtifacterImageGen/weapon/{name}.png"):
        saveImage(itemName, f"./ArtifacterImageGen/weapon/{name}.png")


def checkUpdateGenshin_relic(equipType, icon, nameTextMapHash):
    name = convertNameGenshin(nameTextMapHash)
    dir = f"./ArtifacterImageGen/Artifact/{name}"
    if not os.path.exists(dir):
        logger.warning(f"New relic found: {name}")
        logger.info(f"start to download relic: {name}")
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
    updateGenshin_Character()
    logger.info("update complete!")
