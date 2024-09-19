# This example requires the 'message_content' intent.

import os
import discord
import sys

from dotenv import load_dotenv
sys.path.append(".")

from aibo.ai.generate_answer import generate_answer
from aibo.ai.triage import evaluate_urgency_score
from aibo.ai.word2vec_triage import evaluate_urgency_score_by_word2vec

load_dotenv("./app/chat/.env")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    if message.content.startswith("."):
        answer = generate_answer(message.content.lstrip("."), message.author.name)
        await message.channel.send(answer)
    elif message.content == "/score":
        score = evaluate_urgency_score(message.author.name)
        await message.channel.send(f"スコア: {score}点")
    elif message.content == "/w2v":
        score = evaluate_urgency_score_by_word2vec(message.author.name)
        await message.channel.send(f"Word2Vecによるスコア: {score}点")

client.run(token=os.environ["DISCORD_TOKEN"])