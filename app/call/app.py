from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import numpy as np
import vosk
import json
import time

app = Flask(__name__)
socketio = SocketIO(app)

# Voskモデルのロード
model = vosk.Model("./vosk-model-ja-0.22")

# グローバル変数の定義
audio_buffer = []  # 音声データを蓄積
last_received_time = time.time()  # 最後に音声データが送られた時刻
SILENCE_THRESHOLD = 2  # 無音と判断するまでの秒数

@app.route("/")
def index_page():
    return render_template("index.html")

# 接続が確立された際に音声ストリーム受信を開始
@socketio.on('connect')
def handle_connect():
    global audio_buffer, last_received_time
    print("クライアントが接続されました")
    audio_buffer = []  # バッファを初期化
    last_received_time = time.time()  # タイムスタンプを初期化

# 音声ストリームを受信して蓄積
@socketio.on('audio_stream')
def handle_audio_stream(data):
    global audio_buffer, last_received_time
    audio_data = np.frombuffer(data, dtype=np.int16)

    # 音声データを蓄積
    audio_buffer.append(audio_data)
    last_received_time = time.time()  # データ受信時刻を更新

    # 無音かどうかを確認
    check_for_silence()

# 無音かどうかをチェックし、無音なら音声認識を実行
def check_for_silence():
    global audio_buffer, last_received_time
    current_time = time.time()

    # 一定時間無音が続いたら発話が完了したと判断
    if current_time - last_received_time > SILENCE_THRESHOLD:
        if len(audio_buffer) > 0:
            process_audio_data()
        audio_buffer = []  # バッファをクリア

# 音声認識を実行し、結果をemit
def process_audio_data():
    global audio_buffer

    # 音声データを結合して1つの音声データに
    audio_data = np.concatenate(audio_buffer)

    recognizer = vosk.KaldiRecognizer(model, 16000)

    # 音声認識を実行
    if recognizer.AcceptWaveform(audio_data.tobytes()):
        result = json.loads(recognizer.Result())
        recognized_text = result.get('text', '')
        print(f"認識されたテキスト: {recognized_text}")
        if recognized_text.strip():
            emit('recognition_result', recognized_text)

# 切断された際の処理
@socketio.on('disconnect')
def handle_disconnect():
    print("クライアントが切断されました")
    # 切断されたときに残っているデータを処理
    if len(audio_buffer) > 0:
        process_audio_data()

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, debug=True)
