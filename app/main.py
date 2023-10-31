import os
import sys
import logging
from fastapi import FastAPI, HTTPException
import requests
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import WordPunctTokenizer
from google.cloud import translate_v2 as translate
from typing import List
from pydantic import BaseModel


class ImageRequest(BaseModel):
    content: str
    hashtag: List[str]

class ImageData(BaseModel):
    imageUrl: List[str]

class ImageResponse(BaseModel):
    isSuccess: bool
    code: int
    message: str
    data: ImageData

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p',
    stream=sys.stdout  # 로그를 표준 출력으로 전송
)

app = FastAPI()

# 구글 클라우드 키 경로 설정
translate_client = translate.Client.from_service_account_json("/code/my-key.json")

# TF-IDF를 이용해 키워드를 추출하는 함수를 정의합니다.
def get_keywords(text, num_keywords):
    # 토크나이저를 생성합니다.
    tokenizer = WordPunctTokenizer()

    # TF-IDF 벡터라이저를 생성합니다.
    stop_words = [
        ".", ",", '"', "their", "a", "other", "so", "that", "being", "between", "ours",
        "yourselves", "what", "if", "each", "haven", "you", "they", "not", "because", "against",
        "mustn't", "them", "over", "you're", "are", "won't", "its", "off", "am", "with", "there",
        "needn't", "hadn't", "about", "nor", "just", "by", "should", "needn", "shan", "until",
        "that'll", "more", "you'll", "you've", "will", "mightn", "you'd", "up", "yours",
        "through", "hasn't", "ma", "my", "such", "itself", "under", "too", "which", "during",
        "was", "than", "an", "been", "down", "these", "should've", "how", "herself", "the",
        "here", "to", "having", "don", "t", "theirs", "does", "on", "both", "wouldn't", "don't",
        "only", "who", "when", "were", "into", "any", "shouldn", "and", "why", "couldn't",
        "haven't", "or", "where", "she", "me", "him", "at", "below", "his", "her", "then",
        "did", "this", "he", "it's", "few", "most", "can", "mustn", "very", "s", "himself",
        "again", "ll", "yourself", "further", "doing", "some", "but", "i", "couldn", "aren't",
        "it", "now", "ourselves", "re", "have", "after", "our", "your", "out", "wasn't",
        "mightn't", "themselves", "whom", "once", "is", "hadn", "y", "doesn't", "weren", "we",
        "before", "as", "o", "own", "above", "wouldn", "of", "all", "shan't", "be", "weren't",
        "while", "d", "from", "aren", "isn", "won", "didn", "no", "hasn", "those", "didn't",
        "isn't", "she's", "ain", "same", "shouldn't", "do", "m", "for", "hers", "had", "doesn",
        "myself", "in", "wasn", "has", "ve",
    ]

    vectorizer = TfidfVectorizer(tokenizer=tokenizer.tokenize, stop_words=stop_words)

    # 입력 텍스트에 대해 TF-IDF를 계산합니다.
    tfidf_matrix = vectorizer.fit_transform([text])

    # 벡터라이저에서 피처 이름을 가져옵니다.
    feature_names = vectorizer.get_feature_names_out()

    # 계산한 TF-IDF 값에 따라 키워드를 정렬하고, 상위 num_keywords개의 키워드 인덱스를 가져옵니다.
    sorted_keywords_indices = tfidf_matrix.toarray().argsort()[0][::-1][:num_keywords]

    # 인덱스에 해당하는 키워드를 가져옵니다.
    keywords = [feature_names[index] for index in sorted_keywords_indices]

    # 로그 작성
    logging.info(f"Generated keywords: {keywords}")

    return keywords


# 키워드를 영어로 번역하는 함수를 정의합니다.
def translate_keywords(keywords):
    translated_keywords = []

    # 각 키워드에 대해 번역을 진행합니다.
    for keyword in keywords:
        result = translate_client.translate(keyword, target_language="en")
        translated_keywords.append(result["input"])

    # 로그 작성
    logging.info(f"Translated keywords: {translated_keywords}")

    return translated_keywords


# Karlo에 이미지 생성 요청을 보내는 함수를 정의합니다.
def request_image_to_karlo(keywords):
    karlo_api_key = "9ea943bc1dce2cd5fe7a41bdba661924"

    # 요청 헤더를 정의합니다.
    headers = {
        "Authorization": f"KakaoAK {karlo_api_key}",
        "Content-Type": "application/json",
    }

    # 요청 본문을 정의합니다.
    data = {
        "prompt": ", ".join(keywords),
        "width": 600,
        "height": 600,
        "samples": 8,
    }

    # Karlo API에 POST 요청을 보냅니다.
    response = requests.post(
        "https://api.kakaobrain.com/v2/inference/karlo/t2i",
        json=data,
        headers=headers,
    )

    # 응답을 JSON 형식으로 해석합니다.
    response_json = response.json()

    # 응답 내용을 로그로 출력합니다.
    logging.info(f"Response from Karlo: {response_json}")

    # 응답에서 이미지 URL을 추출합니다.
    try:
        image_urls = [image["image"] for image in response_json["images"]]
    except KeyError:
        logging.error(f"Cannot find 'images' key in the response: {response_json}")
        image_urls = []

    # 로그 작성
    logging.info(f"Image URLs from Karlo: {image_urls}")

    return image_urls

# 이미지 생성 API 엔드포인트를 정의합니다.
@app.post("/generate-images", response_model=ImageResponse)
async def generate_image(request: ImageRequest):
    # 요청에서 텍스트를 추출합니다.
    text = request.content

    # 로그 작성
    logging.info(f"Received request: {request}")

    # TF-IDF를 이용해 5개의 키워드를 생성합니다.
    keywords = get_keywords(text, 5 - len(request.hashtag)) + request.hashtag

    # 키워드를 영어로 번역합니다.
    translated_keywords = translate_keywords(keywords)

    # Karlo에 이미지 생성 요청을 보냅니다.
    image_urls = request_image_to_karlo(translated_keywords)

    # 응답을 생성하고 반환합니다.
    return ImageResponse(
        isSuccess=True,
        code=200,
        message='요청에 성공하였습니다.',
        data=ImageData(imageUrl=image_urls),
    )
