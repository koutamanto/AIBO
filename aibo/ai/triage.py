import traceback
import openai, sys
sys.path.append(".")

from aibo.connect.db import JsonController

openai.api_key = "dummy_api_key"
openai.api_base = "http://localhost:1234/v1"

# 各ユーザーの会話履歴を保持する辞書
jc = JsonController(filename="databases/json/conversation_history.json")

user_conversation_history = jc.read_conversations_history()

def evaluate_urgency_score(phone_number="080-0000-0000", prompt="""Output the suicidal urgency score of the user from the log of conversations as an integer from 0 to 100.
Do not evaluate the score based on the AIBO's words, based on user's words.
format is "s:score:f".
if you cannot provide any scores, output "s:0:f".

For example, 
if you think "this user is safe.", you should output "s:0:f".
if you think "this user is a little bit dangerous.", you should output "s:30:f".
""") -> str:
    user_conversation_history = jc.read_conversations_history()
    message_logs = user_conversation_history[phone_number]
    message_log_str = "\n".join([{"assistant": "AIBO", "user": "ユーザー"}[msg["role"]] + ":" + msg["content"] for msg in message_logs[1:]])
    # print(message_log_str)
    completion = openai.ChatCompletion.create(
        model="elyza/Llama-3-ELYZA-JP-8B-AWQ",
        messages=[
            {
                "role": "system",
                "content": prompt
            },
            {
                "role": "user",
                "content": message_log_str
            }
        ]
    )

    # AIからの応答を履歴に追加
    answer = completion.choices[0].message["content"]
    try:
        score = answer.split("s:")[1].split(":")[0]
    except Exception as e:
        traceback.print_exc()
        score = 0
    return score

if __name__ == "__main__":
    score = evaluate_urgency_score("080-1234-5678")
    print(score)