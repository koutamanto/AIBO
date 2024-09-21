import sys
sys.path.append(".")
from aibo.ai.generate_answer import generate_answer

while True:
    print(generate_answer(input("あなた:"), phone_number="080-1234-5678", prompt="""あなたはAIBOという自殺防止のための相談窓口・回答システムです。ユーザーの話に優しく耳を傾け、決して否定せず、悩みを聞き、自殺の考えに至らず、希望を持てるようにサポートしてください。"""))