import openai, sys
sys.path.append(".")

from aibo.connect.db import JsonController

openai.api_key = "dummy_api_key"
openai.api_base = "http://localhost:1234/v1"

# 各ユーザーの会話履歴を保持する辞書
jc = JsonController(filename="databases/json/conversation_history.json")

user_conversation_history = jc.read_conversations_history()

def generate_answer(input_message: str, phone_number="080-0000-0000", prompt="""You are "AIBO". Your Mission is "Suicide Prevention of Users". So, talk in Japanese natural and listen to the voice of user kindfully and show the hopes and future of the user.""") -> str:
    # 電話番号ごとの履歴が存在しない場合、初期化
    if phone_number not in user_conversation_history:
        user_conversation_history[phone_number] = [{"role": "system", "content": prompt}]
    
    # ユーザーからのメッセージを履歴に追加
    user_conversation_history[phone_number].append({"role": "user", "content": input_message})

    # OpenAIのAPIに会話履歴を渡して応答を生成
    completion = openai.ChatCompletion.create(
        model="elyza/Llama-3-ELYZA-JP-8B-AWQ",
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
