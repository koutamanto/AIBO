import os
import queue
import sounddevice as sd
import vosk
import sys
import json

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
                    output_answer = generate_answer(input_text)
                    print(output_answer)
            else:
                print(json.loads(rec.PartialResult())['partial'])
                pass

if __name__ == '__main__':
    main()
