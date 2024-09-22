from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import numpy as np
import vosk
import json

app = Flask(__name__)
socketio = SocketIO(app)

# Voskモデルのロード
model = vosk.Model("path_to_vosk_model")

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('audio_data')
def handle_audio(data):
    # クライアントからの音声データを処理する
    audio_data = np.frombuffer(data, dtype=np.float32)  # 送信された音声データをバッファから変換
    recognizer = vosk.KaldiRecognizer(model, 16000)

    # Voskを使って音声データを処理
    if recognizer.AcceptWaveform(audio_data.tobytes()):
        result = recognizer.Result()
        recognized_text = json.loads(result)['text']
        emit('recognition_result', recognized_text)  # 認識結果をクライアントに送信
    else:
        partial = recognizer.PartialResult()
        partial_text = json.loads(partial)['partial']
        emit('recognition_result', partial_text)  # 部分的な認識結果をクライアントに送信

if __name__ == '__main__':
    socketio.run(app, debug=True)
