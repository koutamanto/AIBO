# -*- coding: utf-8 -*-
from flask import Flask, request, abort
from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
	ApiClient, Configuration, MessagingApi,
	ReplyMessageRequest, PushMessageRequest,
	TextMessage, PostbackAction
)
from linebot.v3.webhooks import (
	FollowEvent, MessageEvent, PostbackEvent, TextMessageContent
)
import os, sys
from dotenv import load_dotenv

sys.path.append(".")

from aibo.ai.generate_answer import generate_answer
from aibo.ai.triage import evaluate_urgency_score

load_dotenv("./app/chat/.env")

CHANNEL_ACCESS_TOKEN = os.environ["CHANNEL_ACCESS_TOKEN"]
CHANNEL_SECRET = os.environ["CHANNEL_SECRET"]

app = Flask(__name__)

configuration = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/callback", methods=['POST'])
def callback():
	# get X-Line-Signature header value
	signature = request.headers['X-Line-Signature']

	# get request body as text
	body = request.get_data(as_text=True)
	app.logger.info("Request body: " + body)

	# handle webhook body
	try:
		handler.handle(body, signature)
	except InvalidSignatureError:
		app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
		abort(400)

	return 'OK'

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    
	with ApiClient(configuration) as api_client:
		line_bot_api = MessagingApi(api_client)
	received_message = event.message.text
	

	profile = line_bot_api.get_profile(event.source.user_id)
	display_name = profile.display_name
	
	if received_message == "/score":
		reply = "あなたの現在の緊急性スコア: " + evaluate_urgency_score(phone_number=profile.user_id) + "点"
	else:
		reply = generate_answer(received_message, phone_number=profile.user_id)

	line_bot_api.reply_message(ReplyMessageRequest(
		replyToken=event.reply_token,
		messages=[TextMessage(text=reply)]
	))

## ボット起動コード
if __name__ == "__main__":
	app.run(host="0.0.0.0", port=5678, debug=True)