# AIBO File & Folder Structure
```python
.
├── aibo      #ライブラリ
│  ├── ai             #AI関連の関数・プログラム
│  |  ├── word2vec                  #Word2vecによる緊急性スコアの算出用のモデル
│  |  |  ├── word2vec.gensim.model
│  |  |  ├── word2vec.gensim.model.syn1neg.npy
│  |  |  ├── word2vec.gensim.model.wv.syn0.npy
│  |  |  └── wordlist.txt
│  |  ├── word2vec_triage.py        #緊急性スコア算出(Word2Vec方式)
│  |  ├── generate_answer.py        #相談に対する回答の推論・生成
│  |  └── triage.py                 #緊急性スコア算出(ローカルLLM)
│  ├── connect        #DBのコントローラーなど
│  |  ├── db.py                     #Jsonによるログ残し機能
│  |  └── nosql_crud.py             #MongoDBの処理自体
│  └── settings.py    #最初に空っぽで作ったまま、設定を読み出すプログラム
├── app       #クライアントのアプリケーション
│  ├── call   #電話処理系
│  └── chat   #チャット処理系
├── databases #データベースのファイル群 
│  ├── json           #Json関係
│  |  └── conversation_history.json #AIBOに与えるプロンプト用json兼会話履歴保存用 / 機能の一部は今後DBに移される
│  └── mongo          #MongonDBの中身(.gitignoreに登録済み)
├── env       #環境情報(.env)
│  └── .env           #envファイル
└── test      #開発用testフォルダー
```
