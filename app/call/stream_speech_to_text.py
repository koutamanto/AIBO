import os
import queue
import sounddevice as sd
import vosk
import sys
import json
import urllib.parse
import pyttsx3, requests
from playsound import playsound

# 初期化
engine = pyttsx3.init()

# 読み上げスピードの設定
engine.setProperty('rate', 150)
engine.setProperty("voice", "Japanese")

sys.path.append(".")
from aibo.ai.generate_answer import generate_answer

q = queue.Queue()

def callback(indata, frames, time, status):
    q.put(bytes(indata))

def main():
    model = vosk.Model("app/call/vosk-model-ja-0.22")  # ダウンロードしたモデルパスを指定
    samplerate = 16000

    # AirPodsのマイクのデバイスIDを指定（pulseを試す）
    device_id = 7  # 'pulse' デバイスID

    # 1チャンネルを指定（AirPodsのマイクはモノラルなので1）
    channels = 1

    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype='int16', channels=channels, callback=callback, device=device_id):
        rec = vosk.KaldiRecognizer(model, samplerate)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                input_text = json.loads(rec.Result())['text']
                if input_text.rstrip("\n") != "":
                    print(input_text)
                    output_answer = generate_answer(input_text, "080-1000-1003")
                    print(output_answer)
                    # 音素データ生成
                    text = urllib.parse.quote(output_answer)
                    response = requests.post("http://localhost:50021/audio_query?text=" + text + "&speaker=47")
                    resp_mp3 = requests.post("http://localhost:50021/synthesis?speaker=47", json=response.json())
                    # バイナリデータ取り出し
                    data_binary = resp_mp3.content
                    # wavとして書き込み
                    path = "test.mp3"
                    wr = open(path, "wb")
                    wr.write(data_binary)
                    wr.close()

                    # 再生
                    playsound(path)
            else:
                # print(json.loads(rec.PartialResult())['partial'])
                pass

if __name__ == '__main__':
    main()
