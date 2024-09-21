import os
import queue
import sounddevice as sd
import vosk
import sys
import json

sys.path.append(".")

q = queue.Queue()

def callback(indata, frames, time, status):
    q.put(bytes(indata))

def main():
    model = vosk.Model("app/call/vosk-model-small-ja-0.22")  # ダウンロードしたモデルパスを指定
    samplerate = 16000
    device = None

    with sd.RawInputStream(samplerate=samplerate, blocksize=8000, dtype='int16', channels=1, callback=callback):
        rec = vosk.KaldiRecognizer(model, samplerate)
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                print(json.loads(rec.Result())['text'])
            else:
                print(json.loads(rec.PartialResult())['partial'])

if __name__ == '__main__':
    main()
