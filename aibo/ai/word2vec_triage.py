import MeCab
import gensim
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# MeCabを使った形態素解析（基本形を取得）
def tokenize_text(text):
    mecab = MeCab.Tagger("-Ochasen")  # 詳細な解析
    parsed_text = mecab.parse(text)
    tokens = []
    for line in parsed_text.splitlines():
        if line != "EOS":
            cols = line.split("\t")
            if len(cols) > 3:
                # 基本形 (辞書形) を使用
                tokens.append(cols[2])  # cols[2]が基本形
            else:
                tokens.append(cols[0])  # デフォルトの表層形
    return tokens

# Word2Vecモデルの読み込み
model_path = 'aibo/ai/word2vec/word2vec.gensim.model'  # モデルのパスを指定
model = gensim.models.Word2Vec.load(model_path)

# コサイン類似度を計算する関数
def calculate_cosine_similarity(word_vector, target_word_vectors):
    word_vector = np.array(word_vector).reshape(1, -1)
    similarities = cosine_similarity(word_vector, target_word_vectors)
    return similarities[0]

# 対象テキストを解析して既存ワードリストと類似度を計算
def analyze_and_calculate_similarity(text, word_list, words2scores, negative_words):
    tokens = tokenize_text(text)
    similarities = {}

    # スコアの合計とネガティブワードのカウント
    total_score = 0
    negative_word_count = 0

    # word2vecに存在する単語に対して類似度を計算
    for token in tokens:
        if token in model.wv:
            word_vector = model.wv[token]
            target_word_vectors = [model.wv[word] for word in word_list if word in model.wv]

            if target_word_vectors:
                target_word_vectors = np.array(target_word_vectors)
                cos_sim = calculate_cosine_similarity(word_vector, target_word_vectors)

                # ネガティブワードかどうかの確認
                if token in negative_words:
                    # 重みづけされたスコアを計算
                    weight = words2scores.get(token, 1)  # スコアが存在しない場合は1をデフォルトに
                    weighted_score = weight * np.mean(cos_sim)
                    total_score += weighted_score  # 合計スコアに加算
                    negative_word_count += 1  # ネガティブワードのカウントを増加
                    similarities[token] = f"Weighted Similarity: {weighted_score}"
                else:
                    similarities[token] = f"Cosine Similarity: {np.mean(cos_sim)}"
            else:
                similarities[token] = "No similar words found in word list"
        else:
            similarities[token] = "Word not in word2vec model"

    # 平均スコアを計算
    average_score = total_score / negative_word_count if negative_word_count > 0 else 0

    return similarities, average_score

if __name__ == "__main__":
    # 解析するテキスト
    input_text = "死にたい"

    # 既存のワードリストとスコアの辞書を読み込み
    with open("aibo/ai/word2vec/wordlist.txt", "r", encoding="utf-8") as f:
        lines = f.readlines()
        word_list = [word.split(":")[0].strip() for word in lines]  # ワードリスト
        words2scores = {word.split(":")[0].strip(): int(word.split(":")[1]) for word in lines}  # スコアの辞書

    # ネガティブワードリストの定義
    negative_words = word_list  # wordlist.txtに含まれるすべての単語をネガティブワードとみなす

    # 類似度とスコアの計算
    result, average_score = analyze_and_calculate_similarity(input_text, word_list, words2scores, negative_words)

    # 結果を表示
    for word, similarity in result.items():
        print(f"Word: {word}, Similarity: {similarity}")
    print(f"Average Score: {average_score*4}")
