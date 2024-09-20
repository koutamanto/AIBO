from transformers import pipeline
from translate import Translator

classifier = pipeline("sentiment-analysis", model="sentinetyd/suicidality")
translator = Translator(to_lang="en", from_lang="ja")

def is_suicidal(message: str) -> str:
    en_message = translator.translate(message)
    print(en_message)
    result = classifier(en_message)
    print(result)
    return result[0]["label"] == "LABEL_1"

if __name__ == "__main__":
    while True:
        is_suicidal(input("あなた:"))