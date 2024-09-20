import traceback, sys
from flask import Flask, jsonify, render_template, request

sys.path.append(".")

from aibo.ai.generate_answer import generate_answer
from aibo.ai.evaluate_suicidality_score import is_suicidal

app = Flask(__name__)

@app.route("/")
def chat_page():
    return render_template("index.html")

@app.route("/generate_answer", methods=["POST"])
def generate_answer_endpoint():
    try:
        user_message = request.get_json()["message"]
        answer = generate_answer(user_message, request.remote_addr)
        return jsonify({"reply": answer})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"reply": "error"})

@app.route("/check_suicidality", methods=["POST"])
def check_suicidality_endpoint():
    try:
        user_message = request.get_json()["message"]
        answer = is_suicidal(user_message)
        return jsonify({"reply": answer})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"reply": "error"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)