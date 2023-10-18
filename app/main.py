from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
import requests
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import WordPunctTokenizer

# Google Cloud Translation 라이브러리를 가져옵니다.
from google.cloud import translate_v2 as translate

app = FastAPI()

# 구글 클라우드 키 경로 설정하기
translate_client = translate.Client.from_service_account_json("my-key.json")

@app.post("/generate_image/", response_class=HTMLResponse)
async def generate_image(request: Request):
    form_data = await request.form()

    text = form_data.get("text")

    # Translate the input text to English using Google Cloud Translation API.
    result = translate_client.translate(text, target_language="en")

    # Get the translated text.
    translated_text = result["input"]

    tokenizer = WordPunctTokenizer()

    stop_words = [
        ".",
        ",",
        '"',
        "their",
        "a",
        "other",
        "so",
        "that",
        "being",
        "between",
        "ours",
        "yourselves",
        "what",
        "if",
        "each",
        "haven",
        "you",
        "they",
        "not",
        "because",
        "against",
        "mustn't",
        "them",
        "over",
        "you're",
        "are",
        "won't",
        "its",
        "off",
        "am",
        "with",
        "there",
        "needn't",
        "hadn't",
        "about",
        "nor",
        "just",
        "by",
        "should",
        "needn",
        "shan",
        "until",
        "that'll",
        "more",
        "you'll",
        "you've",
        "will",
        "mightn",
        "you'd",
        "up",
        "yours",
        "through",
        "hasn't",
        "ma",
        "my",
        "such",
        "itself",
        "under",
        "too",
        "which",
        "during",
        "was",
        "than",
        "an",
        "been",
        "down",
        "these",
        "should've",
        "how",
        "herself",
        "the",
        "here",
        "to",
        "having",
        "don",
        "t",
        "theirs",
        "does",
        "on",
        "both",
        "wouldn't",
        "don't",
        "only",
        "who",
        "when",
        "were",
        "into",
        "any",
        "shouldn",
        "and",
        "why",
        "couldn't",
        "haven't",
        "or",
        "where",
        "she",
        "me",
        "him",
        "at",
        "below",
        "his",
        "her",
        "then",
        "did",
        "this",
        "he",
        "it's",
        "few",
        "most",
        "can",
        "mustn",
        "very",
        "s",
        "himself",
        "again",
        "ll",
        "yourself",
        "further",
        "doing",
        "some",
        "but",
        "i",
        "couldn",
        "aren't",
        "it",
        "now",
        "ourselves",
        "re",
        "have",
        "after",
        "our",
        "your",
        "out",
        "wasn't",
        "mightn't",
        "themselves",
        "whom",
        "once",
        "is",
        "hadn",
        "y",
        "doesn't",
        "weren",
        "we",
        "before",
        "as",
        "o",
        "own",
        "above",
        "wouldn",
        "of",
        "all",
        "shan't",
        "be",
        "weren't",
        "while",
        "d",
        "from",
        "aren",
        "isn",
        "won",
        "didn",
        "no",
        "hasn",
        "those",
        "didn't",
        "isn't",
        "she's",
        "ain",
        "same",
        "shouldn't",
        "do",
        "m",
        "for",
        "hers",
        "had",
        "doesn",
        "myself",
        "in",
        "wasn",
        "has",
        "ve",
    ]  # Exclude articles and punctuation

    vectorizer = TfidfVectorizer(tokenizer=tokenizer.tokenize, stop_words=stop_words)

    tfidf_matrix = vectorizer.fit_transform([translated_text])

    feature_names = vectorizer.get_feature_names_out()

    # Sort by tf-idf score and get top 5 keywords
    sorted_keywords_indices = tfidf_matrix.toarray().argsort()[0][::-1][:5]

    keywords_prompt = " ".join(
        [feature_names[index] for index in sorted_keywords_indices]
    )

    REST_API_KEY = "9ea943bc1dce2cd5fe7a41bdba661924"

    try:
        r = requests.post(
            "https://api.kakaobrain.com/v2/inference/karlo/t2i",
            json={
                "prompt": keywords_prompt,
            },
            headers={
                "Authorization": f"KakaoAK {REST_API_KEY}",
                "Content-Type": "application/json",
            },
        )

        if r.status_code != 200:
            raise HTTPException()

        response_json = r.json()
    
        image_url = response_json["images"][0]["image"]

        return {
            'isSuccess': True,
            'code': 200,
            'message': '요청에 성공하였습니다.',
            'data': image_url,
        }

    except HTTPException as e:
        return {
        'isSuccess': False,
        'code': 400,
        'message': '이미지 생성에 실패하였습니다.'
    }