# Genshin-Artifacter

## 概要
Discord上で原神のプロフィールに設定しているキャラのビルドカードを生成します。
そのほかにもVOICEVOXのサーバーを起動していれば読み上げもしてくれます！

使用例
![image](https://cdn.discordapp.com/attachments/1000374955462107236/1191592073837674536/Image.png?ex=65d42419&is=65c1af19&hm=0c448fc3ffb25be65c58175144073d74a7b1b23bb1041d3628d39f527b0c41aa&)

## セットアップ(Mac & linux)
設定用ファイル".env"ファイルを作成します。
```
touch .env
```
ファイルの中身は以下の通りです.
```
token = "(str)<your discord bot token>"
adminID = <(int)your discord account ID>
adminServer = <(int)the server for console>
adminChannel = <(int)the text channel for console>
```
必要なパッケージをインストールします。
```
pip install -r requirements.txt
```
botを起動します
```
python main.py
```

## 使い方

ビルドカードの出し方
1. discord上で起動したBotがいるチャンネルに移動します。
2. /buildと打ち込んで実行
3. 原神のUIDを打ち込むとビルドするための対話形式のUIが起動します

その他のコマンドに関しては"/help"で確認できます。
