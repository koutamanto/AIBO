// チャットボックスと入力欄の要素を取得
const chatBox = document.getElementById("chat-box");
const chatInput = document.getElementById("chat-input");
const sendButton = document.getElementById("send-button");

// サーバーからの応答をシミュレートする関数 (generate_answerの代わり)
function generate_answer(userMessage) {
    return fetch("/generate_answer", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: userMessage })
    })
    .then(response => response.json())
    .then(data => data.reply);  // APIからの応答をここで返す
}

function check_suicidality(userMessage) {
    return fetch("/check_suicidality", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message: userMessage })
    })
    .then(response => response.json())
    .then(data => data.reply);  // APIからの応答をここで返す
}

// メッセージを追加する関数
function addMessage(content, isUser) {
    const messageElement = document.createElement("div");
    messageElement.classList.add(isUser ? "user-message" : "bot-message");
    messageElement.innerHTML = content;
    chatBox.appendChild(messageElement);
    chatBox.scrollTop = chatBox.scrollHeight; // 最新のメッセージまでスクロール
}

// メッセージを送信する関数
function sendMessage() {
    const userMessage = chatInput.value.trim();
    if (userMessage === "") return; // 空のメッセージは無視

    // ユーザーのメッセージを追加
    addMessage(userMessage, true);
    chatInput.value = ""; // 送信後、入力欄をクリア
    // ボットからの応答を生成して追加
    generate_answer(userMessage).then((botMessage) => {
        addMessage(botMessage, false);
    }).then(check_suicidality(userMessage).then((is_suicidal) => {
        if(is_suicidal) {
            addMessage("[AI分析結果]<br>あなたは今、サポートを受けるべきかもしれません。<br>ためらわずに以下の相談窓口に電話をかけてください。<br>チャット対応も可能な相談窓口もあります。<br><br>こころの健康相談統一ダイヤル<br>0570-064-556<br><br>いのちの電話（一般社団法人 日本いのちの電話連盟） <br> 0120-783-556 （フリーダイヤル・無料） ", false)
        }
    }));
}

// 送信ボタンのクリックイベント
sendButton.addEventListener("click", sendMessage);

// エンターキーでメッセージを送信
chatInput.addEventListener("keypress", function (e) {
    if (e.key === "Enter") {
        sendMessage();
    }
});
