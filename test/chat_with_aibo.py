import sys
sys.path.append(".")
from aibo.ai.generate_answer import generate_answer

while True:
    print(generate_answer(input("あなた:"), phone_number="080-1234-5678"))