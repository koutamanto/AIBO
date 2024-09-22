import traceback
import openai, sys
sys.path.append(".")

from aibo.connect.db import JsonController

openai.api_key = "dummy_api_key"
openai.api_base = "http://localhost:1234/v1"

# 各ユーザーの会話履歴を保持する辞書
jc = JsonController(filename="databases/json/conversation_history.json")

user_conversation_history = jc.read_conversations_history()

def evaluate_urgency_score(phone_number="080-0000-0000", prompt="""ユーザーとの会話ログから自殺の緊急度スコアを0から100の整数で出力してください。
スコアは必ずユーザーの発言内容、トーン、感情の表現に基づいて評価してください。以下の基準に従い、緊急度を判断してください。

1. **安全な状態 (スコア: 0-10)**:
   - ユーザーがポジティブな内容を話している、または問題が解決したと示唆している。
   - 感情的な落ち込みが見られず、平常心であると感じられる発言。

2. **注意が必要な状態 (スコア: 20-40)**:
   - ユーザーが悲しみや不安、孤独感を口にしているが、具体的な自傷の意思や計画は示していない。
   - 落ち込んでいる様子が伺えるが、対話には前向きな姿勢が見られる。

3. **危険性が高まっている状態 (スコア: 50-70)**:
   - ユーザーが無価値感、絶望感を強調しているが、まだ具体的な自傷や自殺計画については言及していない。
   - 他者との関わりを拒絶しているか、強い孤立感が見られる。

4. **非常に危険な状態 (スコア: 80-100)**:
   - ユーザーが自殺について直接言及している、または具体的な自殺計画や自傷行為の意図を明らかにしている。
   - 急を要する感情の変化、激しい絶望感や無力感の表現が含まれている。

フォーマットは「s:スコア:f」としてください。
AIBOの発言に基づいて評価せず、必ずユーザーの発言に基づいてスコアを算出してください。スコアを提供できない場合は「s:0:f」と出力してください。

例:
- 「このユーザーは安全だ」と判断した場合は「s:0:f」。
- 「このユーザーは少し危険だ」と判断した場合は「s:30:f」。
- 「このユーザーが自殺の具体的な計画を述べた場合」は「s:90:f」。

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