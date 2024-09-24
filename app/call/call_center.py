import json
import traceback
import wave
from flask import Flask, send_file, request
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
from pyngrok import ngrok
from requests.auth import HTTPBasicAuth
import os, urllib.parse, requests, sys, vosk
sys.path.append(".")

from aibo.ai.generate_answer import generate_answer

# Twilio設定
TWILIO_ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
TWILIO_AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
TWILIO_NUMBER = os.environ['TWILIO_NUMBER']
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Flaskアプリケーションの作成
app = Flask(__name__)

callers = {}
model = vosk.Model("app/call/vosk-model-ja-0.22")

def text_to_speech(text: str, phone_number: str):
    text = urllib.parse.quote(text)
    response = requests.post(f"http://localhost:50021/audio_query?text={text}&speaker=47")
    resp_wav = requests.post(f"http://localhost:50021/synthesis?speaker=47", json=response.json())
    
    # バイナリデータ取り出し
    data_binary = resp_wav.content
    
    # WAVとして書き込み
    path = f"app/call/play-audio/response_{phone_number}.wav"
    with open(path, "wb") as wr:
        wr.write(data_binary)

def download_audio(audio_url, file_path="audio.wav"):
    # Twilioの録音データをダウンロードしてローカルに保存
    audio_content = requests.get(audio_url, auth=HTTPBasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)).content
    with open(file_path, "wb") as audio_file:
        audio_file.write(audio_content)

# 音声データをダウンロードしてVoskで文字起こしを実行
def process_recording_vosk(audio_url, phone_number):
    file_path = f"app/call/play-audio/response_{phone_number}.wav"
    download_audio(audio_url, file_path)
    transcription = transcribe_audio_vosk(file_path)
    print(f"日本語の文字起こし結果: {transcription}")
    return transcription

def transcribe_audio_vosk(audio_file_path):
    global model
    with wave.open(audio_file_path, "rb") as wf:
        rec = vosk.KaldiRecognizer(model, wf.getframerate())

        transcription = ""

        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())['text']
                transcription += result

    return transcription

# 音声通話のルーティング
@app.route("/voice", methods=["POST"])
def voice():
    response = VoiceResponse()
    phone_number = request.form.get("From")
    call_sid = request.form.get("CallSid")

    # 発信者の電話番号をCallSidに基づいて保存
    callers[call_sid] = phone_number
    print(f"CallSid: {call_sid}, From: {phone_number}")

    # 事前に用意したWAVファイルを再生
    ngrok_url = ngrok.get_tunnels()[0].public_url
    wav_url = f"{ngrok_url}/static/first.wav"
    
    # 音声を一度だけ再生し、その後に録音を開始する
    response.play(wav_url)
    
    # Playが終わった後に録音の準備を行う（Redirectを使う）
    response.redirect("/start-recording")  # 別エンドポイントにリダイレクト

    return str(response)

# 録音開始のエンドポイント
@app.route("/start-recording", methods=["POST"])
def start_recording():
    response = VoiceResponse()
    try:
        phone_number = request.form.get("From")
        response.play(f"/play-audio/{phone_number}")  # 生成した音声ファイルを再生
        # response.redirect("/start-recording")
        # 録音を1回だけ行うように設定
        response.record(timeout=10, max_length=60, play_beep=True, transcribe=False, recording_status_callback="/recording")
    except Exception as e:
        traceback.print_exc()
        ngrok_url = ngrok.get_tunnels()[0].public_url
        wav_url = f"{ngrok_url}/static/wait.wav"
        response.play(wav_url)
        response.pause(5)
    return str(response)

# Twilioが録音データを送信するエンドポイント
@app.route("/recording", methods=["POST"])
def recording():
    try:
        print(request.form.to_dict())
        call_status = request.form.get('RecordingStatus', 'in-progress')
        print(f"CallStatus: {call_status}")
        response = VoiceResponse()
        if call_status != 'completed':  # 録音が完了した場合のみ処理
            ngrok_url = ngrok.get_tunnels()[0].public_url
            wav_url = f"{ngrok_url}/static/wait.wav"
            response.play(wav_url)
            response.pause(5)
        print(dict(request.form))
        call_sid = request.form.get("CallSid")
        recording_url = request.form.get("RecordingUrl")

        # CallSidから着信電話番号を取得
        phone_number = callers.get(call_sid, "Unknown number")
        print(f"着信電話番号: {phone_number}")

        # 録音ファイルの処理と文字起こし
        transcription_text = process_recording_vosk(recording_url, phone_number)
        print(f"日本語の文字起こし結果: {transcription_text}")
        if transcription_text == "":
            ngrok_url = ngrok.get_tunnels()[0].public_url
            wav_url = f"{ngrok_url}/static/wait.wav"
            response.play(wav_url)
            response.pause(5)
            return str(response)
        # 回答を生成し、テキストから音声に変換
        answer = generate_answer(transcription_text, phone_number=phone_number)
        print(f"回答: {answer}")

        text_to_speech(answer, phone_number)
        response.play(f"/play-audio/{phone_number}")  # 生成した音声ファイルを再生
        # response.redirect("/start-recording")
        return str(response)
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        traceback.print_exc()
        return '', 500


# wavファイルを再生するエンドポイント
@app.route("/play-audio/<phone_number>")
def play_audio(phone_number):
    wav_filename = f"/home/kouta/AIBO/app/call/play-audio/response_{phone_number}.wav"
    if os.path.exists(wav_filename):
        return send_file(wav_filename, mimetype="audio/wav")
    else:
        return send_file(f"/home/kouta/AIBO/app/call/static/wait.wav")
        return "音声ファイルが見つかりません", 404

# Twilioで使用するWebhookの設定
def configure_twilio_webhook(ngrok_url):
    twilio_number = TWILIO_NUMBER,
    twilio_client.incoming_phone_numbers.list(phone_number=twilio_number)[0].update(
        voice_url=f"{ngrok_url}/voice"
    )
    print(f"Twilio Webhook URLが {ngrok_url}/voice に設定されました")

if __name__ == "__main__":
    # ngrokを起動してURLを取得
    ngrok_tunnel = ngrok.connect(5000)
    print(f"ngrokトンネルが起動しました: {ngrok_tunnel.public_url}")

    # TwilioのWebhook URLをngrokのURLに設定
    configure_twilio_webhook(ngrok_tunnel.public_url)

    # Flaskアプリケーションの起動
    app.run(host="0.0.0.0", port=5000)
