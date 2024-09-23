import wave
from flask import Flask, send_file, request
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
from pyngrok import ngrok
import os, urllib.parse, requests, sys, vosk
sys.path.append(".")

from aibo.ai.generate_answer import generate_answer
# Twilio設定
TWILIO_ACCOUNT_SID = os.environ['TWILIO_ACCOUNT_SID']
TWILIO_AUTH_TOKEN = os.environ['TWILIO_AUTH_TOKEN']
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Flaskアプリケーションの作成
app = Flask(__name__)

callers = {}
model = vosk.Model("app/call/vosk-model-ja-0.22")

def text_to_speech(text: str, phone_number: str):
    text = urllib.parse.quote(text)
    response = requests.post("http://localhost:50021/audio_query?text=" + text + "&speaker=47")
    resp_wav = requests.post("http://localhost:50021/synthesis?speaker=47", json=response.json())
    # バイナリデータ取り出し
    data_binary = resp_wav.content
    # wavとして書き込み
    path = f"play-audio/response_{phone_number}.wav"
    wr = open(path, "wb")
    wr.write(data_binary)
    wr.close()

def download_audio(audio_url, file_path="audio.wav"):
    # Twilioの録音データをダウンロードしてローカルに保存
    audio_content = requests.get(audio_url).content
    with open(file_path, "wb") as audio_file:
        audio_file.write(audio_content)

# 音声データをダウンロードしてVoskで文字起こしを実行
def process_recording_vosk(audio_url, phone_number):
    download_audio(audio_url, "app/call/play-audio/response_" + phone_number)
    transcription = transcribe_audio_vosk("app/call/play-audio/response_" + phone_number)
    print(f"日本語の文字起こし結果: {transcription}")
    return transcription

def transcribe_audio_vosk(audio_file_path):
    global model
    wf = wave.open(audio_file_path, "rb")
    rec = vosk.KaldiRecognizer(model, wf.getframerate())

    transcription = ""

    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            result = rec.Result()
            transcription += result

    return transcription

# 音声通話のルーティング
@app.route("/voice", methods=["POST"])
def voice():
    response = VoiceResponse()
    # 着信電話番号を取得
    phone_number = request.form.get("From")
    call_sid = request.form.get("CallSid")

    # 発信者の電話番号をCallSidに基づいて保存
    callers[call_sid] = phone_number
    print(f"CallSid: {call_sid}, From: {phone_number}")
    # こちらで用意したwavファイルを再生
    ngrok_url = ngrok.get_tunnels()[0].public_url
    wav_url = f"{ngrok_url}/static/first.wav"
    response.play(wav_url)
    response.record(max_length=60, play_beep=True, transcribe=False, recording_status_callback="/recording")
    print(response)

    return str(response)

# Twilioが録音データを送信するエンドポイント
@app.route("/recording", methods=["POST"])
def recording():
    # 文字起こし結果に基づいて回答を生成
    print(dict(request.form))
    call_sid = request.form.get("CallSid")
    recording_url = request.form.get("RecordingUrl")

    # CallSidから着信電話番号を取得
    phone_number = callers.get(call_sid, "Unknown number")
    # phone_number = request.form['From']
    print(f"着信電話番号: {phone_number}")

    recording_url = request.form.get("RecordingUrl")
    transcription_text = process_recording_vosk(recording_url, phone_number)
    print(f"日本語の文字起こし結果: {transcription_text}")

    answer = generate_answer(transcription_text, phone_number=phone_number)
    print(f"回答: {answer}")

    text_to_speech(answer, phone_number)

    response = VoiceResponse()
    response.play("/play-audio/" + phone_number)  # 音声ファイルを再生
    response.record(max_length=60, play_beep=True, transcribe=False, recording_status_callback="/recording")

    return str(response)
    # 他の処理（文字起こし結果を使って回答生成など）
    # return "OK", 200

# # Twilioの文字起こし結果を受け取るエンドポイント
# @app.route("/transcribe", methods=["POST"])
# def transcribe():
#     transcription_text = request.form.get("TranscriptionText")
#     print(f"文字起こし結果: {transcription_text}")

#     # 文字起こし結果に基づいて回答を生成
#     phone_number = request.form['From']
#     print(f"着信電話番号: {phone_number}")

#     answer = generate_answer(transcription_text, phone_number=phone_number)
#     print(f"回答: {answer}")

#     text_to_speech(answer, phone_number)

#     response = VoiceResponse()
#     response.play("/play-audio/" + phone_number)  # 音声ファイルを再生
#     response.record(transcribe_callback="/transcribe", max_length=30, play_beep=True)  # 再度録音

#     return str(response)

#     # Twilioに通話の応答を返す（別の発信やSMSなどが必要な場合は別途処理）
#     return "OK", 200

# wavファイルを再生するエンドポイント
@app.route("/play-audio/<phone_number>")
def play_audio(phone_number):
    wav_filename = f"app/call/play-audio/response_{phone_number}.wav"
    if os.path.exists(wav_filename):
        return send_file(wav_filename, mimetype="audio/mpeg")
    else:
        return "音声ファイルが見つかりません", 404

# # ローカルのwavファイルを提供するエンドポイント
# @app.route('/play-audio')
# def play_audio():
#     return send_file('first.wav', mimetype='audio/mpeg')

# Twilioでwavを再生するレスポンスを生成
# def play_wav(phone_number: str):
#     response = VoiceResponse()
#     response.play("/play-audio/")  # ローカルのwavファイルを再生
#     return response

# Twilioで使用するWebhookの設定
def configure_twilio_webhook(ngrok_url):
    twilio_number = "+"
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