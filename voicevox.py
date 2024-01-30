import json
import time
import os

import requests
import simpleaudio

if not os.path.exists("VC"):
    os.makedirs("VC")


def text_2_wav(text, speaker_id, max_retry=20):
    ut = time.time()
    audio_file = f"./VC/{ut}.wav"
    # 音声合成のための、クエリを作成
    query_payload = {"text": text, "speaker": speaker_id}
    for query_i in range(max_retry):
        response = requests.post("http://localhost:50021/audio_query",
                                 params=query_payload,
                                 timeout=10)
        if response.status_code == 200:
            query_data = response.json()
            break
    else:
        raise ConnectionError('リトライ回数が上限に到達しました。')

    # 音声合成データの作成して、wavファイルに保存
    synth_payload = {"speaker": speaker_id}
    for synth_i in range(max_retry):
        response = requests.post("http://localhost:50021/synthesis",
                                 params=synth_payload,
                                 data=json.dumps(query_data),
                                 timeout=40)
        if response.status_code == 200:
            with open(audio_file, "wb") as fp:
                fp.write(response.content)
            return audio_file
    else:
        raise ConnectionError('リトライ回数が上限に到達しました。')


def play_auido_by_filename(filename: str):
    # 保存したwavファイルを、再生
    wav_obj = simpleaudio.WaveObject.from_wave_file(filename)
    play_obj = wav_obj.play()
    play_obj.wait_done()
