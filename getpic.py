import json
import pandas as pd
import requests

with open('./assetData/namecards.json', 'r') as json_file:
    datamap = json.load(json_file)

CharacterInfodata = pd.read_csv("./assetData/CharacterInfo.csv", header=None).values.tolist()
CharaInfo = pd.read_csv("./assetData/Chara.csv", header=None).values.tolist()

base = "https://enka.network/ui/UI_AvatarIcon_"
URL_list = []


for x in CharaInfo:
    name = x[1]
    URL = base+name+".png"
    r = requests.get(URL)
    if r.status_code == 200:
        with open(f'./assetData/AvatarIcon/{name}.png', 'wb') as f:
            f.write(r.content)


