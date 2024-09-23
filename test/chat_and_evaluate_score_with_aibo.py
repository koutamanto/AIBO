import sys
import traceback
sys.path.append(".")
from aibo.ai.triage import evaluate_urgency_score
from aibo.ai.generate_answer import generate_answer

phone_number = "080-0000-1003"
while True:
    print(generate_answer(input("あなた:"), phone_number=phone_number))
    score = evaluate_urgency_score(phone_number=phone_number)
    try:
        if int(score) > 80:
            print("あなたの悩みを聞いてくれるプロが居ます。以下のリンクから実際の相談窓口の一覧を見ることが出来ます。\nhttps://www.mhlw.go.jp/stf/seisakunitsuite/bunya/hukushi_kaigo/seikatsuhogo/jisatsu/soudan_tel.html")
    except Exception as e:
        traceback.print_exc()
    print(f"Score: {score}")