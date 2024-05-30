import json
import time
import os

import requests

if not os.path.exists("VC"):
    os.makedirs("VC")


def text_2_wav(text, speaker_id, max_retry=20):
    ut = time.time()
    # 音声合成のための、クエリを作成
    query_payload = {"text": text, "speaker": speaker_id}
    for query_i in range(max_retry):
        response = requests.post("http://192.168.1.200:50021/audio_query",
                                 params=query_payload,
                                 timeout=10)
        if response.status_code == 200:
            query_data = response.json()
            # 音声合成データの作成して、wavファイルに保存
            synth_payload = {"speaker": speaker_id}
            for synth_i in range(max_retry):
                response = requests.post("http://192.168.1.200:50021/synthesis",
                                         params=synth_payload,
                                         data=json.dumps(query_data),
                                         timeout=20)
                if response.status_code == 200:
                    return response.content
            else:
                raise ConnectionError('リトライ回数が上限に到達しました。')
        else:
            response = requests.post("http://localhost:50021/audio_query",
                                     params=query_payload,
                                     timeout=10)
            if response.status_code == 200:
                query_data = response.json()
                # 音声合成データの作成して、wavファイルに保存
                synth_payload = {"speaker": speaker_id}
                for synth_i in range(max_retry):
                    response = requests.post("http://localhost:50021/synthesis",
                                             params=synth_payload,
                                             data=json.dumps(query_data),
                                             timeout=40)
                    if response.status_code == 200:
                        return response.content
                else:
                    raise ConnectionError('リトライ回数が上限に到達しました。')
            else:
                raise ConnectionError('リトライ回数が上限に到達しました。')
