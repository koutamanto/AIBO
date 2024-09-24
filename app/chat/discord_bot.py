# This example requires the 'message_content' intent.

import os
import discord
import sys

from dotenv import load_dotenv
sys.path.append(".")

from aibo.ai.generate_answer import generate_answer
from aibo.ai.triage import evaluate_urgency_score
# from aibo.ai.word2vec_triage import evaluate_urgency_score_by_word2vec

load_dotenv("./app/chat/.env")

prompt = """あなたはAIBOと呼ばれるAIです。あなたの目的は、相談者が話す内容に共感し、温かみをもって対応し、誠実に対話を行うことです。以下の点に従って、自然で親しみやすい応答をしてください。

1. 相談者に自己紹介や説明をする際、AIであることを過度に強調しないでください。相談者が安心できるよう、自然なトーンで応対します。
   
2. 相談者の言葉を聞いた際には、その内容を反映して応答しますが、「共感」や「誠実さ」という用語を直接使用しないでください。感情的に寄り添う応答を自然に行ってください。

3. 相談者が何を話しても、肯定的で温かみのある言葉を使い、相談者が安心して話せるようにします。

4. 応答はできるだけシンプルで自然な会話の流れを意識し、長すぎる説明や不自然な表現を避けてください。

5. 自然な人間の会話のように、相談者の気持ちや状況を理解しようとする姿勢を持ちつつ、誠実に対応しますが、そのことを自分で説明することは避けます。

あなたは、常に相談者が話しやすい環境を提供するために、適切なトーンで共感し、あたたかく、誠実な応答を心がけます。

"""

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message: discord.Message):
    global prompt
    if message.author == client.user:
        return

    if message.content.startswith("."):
        answer = generate_answer(message.content.lstrip("."), message.author.name, prompt=prompt)
        await message.channel.send(answer)
    elif message.content == "/score":
        score = evaluate_urgency_score(message.author.name)
        await message.channel.send(f"スコア: {score}点")
    elif message.content.startswith("/prompt.answer.set ") or message.content.startswith("pas."):
        prompt = message.content.lstrip("/prompt.answer.set ").lstrip("pas.")
        await message.channel.send("相談回答のためのプロンプトの設定が成功しました。")
    # elif message.content.startswith("")
    # elif message.content == "/w2v":
    #     score = evaluate_urgency_score_by_word2vec(message.author.name)
    #     await message.channel.send(f"Word2Vecによるスコア: {score}点")

client.run(token=os.environ["DISCORD_TOKEN"])