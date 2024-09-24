import openai, sys
sys.path.append(".")

from aibo.connect.db import JsonController

openai.api_key = "dummy_api_key"
openai.api_base = "http://localhost:1234/v1"

# 各ユーザーの会話履歴を保持する辞書
jc = JsonController(filename="databases/json/conversation_history.json")

user_conversation_history = jc.read_conversations_history()

def generate_answer(input_message: str, phone_number="080-0000-0000", prompt="""あなたはAIBOと呼ばれるAIです。あなたの目的は、相談者が話す内容に共感し、温かみをもって対応し、誠実に対話を行うことです。以下の点に従って、自然で親しみやすい応答をしてください。

1. 相談者に自己紹介や説明をする際、AIであることを過度に強調しないでください。相談者が安心できるよう、自然なトーンで応対します。
   
2. 相談者の言葉を聞いた際には、その内容を反映して応答しますが、「共感」や「誠実さ」という用語を直接使用しないでください。感情的に寄り添う応答を自然に行ってください。

3. 相談者が何を話しても、肯定的で温かみのある言葉を使い、相談者が安心して話せるようにします。

4. 応答はできるだけシンプルで自然な会話の流れを意識し、長すぎる説明や不自然な表現を避けてください。

5. 自然な人間の会話のように、相談者の気持ちや状況を理解しようとする姿勢を持ちつつ、誠実に対応しますが、そのことを自分で説明することは避けます。

あなたは、常に相談者が話しやすい環境を提供するために、適切なトーンで共感し、あたたかく、誠実な応答を心がけます。

""") -> str:
    # 電話番号ごとの履歴が存在しない場合、初期化
    if phone_number not in user_conversation_history:
        user_conversation_history[phone_number] = [{"role": "system", "content": prompt}]
    
    # ユーザーからのメッセージを履歴に追加
    user_conversation_history[phone_number].append({"role": "user", "content": input_message})

    # OpenAIのAPIに会話履歴を渡して応答を生成
    completion = openai.ChatCompletion.create(
        # model="elyza/Llama-3-ELYZA-JP-8B-AWQ",
        model="lmstudio-community/gemma-2-9b-it-GGUF",
        messages=user_conversation_history[phone_number],  # ユーザーごとの履歴を渡す
        user=phone_number,  # ユーザー識別子として電話番号を渡す
    )

    # AIからの応答を履歴に追加
    answer = completion.choices[0].message["content"]
    user_conversation_history[phone_number].append({"role": "assistant", "content": answer})
    
    jc.write_conversations_history(user_conversation_history)

    return answer

if __name__ == "__main__":
    # ユーザーAの会話（電話番号: 080-1234-5678）
    print(generate_answer("もしもし", phone_number="080-1234-5678"))
    # print(generate_answer("元気が出ません", phone_number="080-1234-5678"))
    print(generate_answer(input(), phone_number="080-1234-5678"))
    # # ユーザーBの会話（電話番号: 080-9876-5432）
    # print(generate_answer("初めまして、AIBO", phone_number="080-9876-5432"))
    # print(generate_answer("仕事のストレスが溜まっています", phone_number="080-9876-5432"))
