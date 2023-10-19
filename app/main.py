from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
import requests
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.tokenize import WordPunctTokenizer

# Google Cloud Translation 라이브러리를 가져옵니다.
from google.cloud import translate_v2 as translate

import logging  # Python의 기본 로깅 모듈을 가져옵니다.

# 사용자 정의 로거를 생성합니다.
logger = logging.getLogger(__name__)

app = FastAPI()

# 구글 클라우드 키 경로 설정하기
translate_client = translate.Client.from_service_account_json("../my-key.json")

class ImageInput(BaseModel):
    keyword1: str = None  # 사용자가 제공하는 키워드1 (선택사항)
    keyword2: str = None  # 사용자가 제공하는 키워드2 (선택사항)
    keyword3: str = None  # 사용자가 제공하는 키워드3 (선택사항)
    keyword4: str = None  # 사용자가 제공하는 키워드4 (선택사항)
    keyword5: str = None  # 사용자가 제공하는 키워드5 (선택사항)
    text: str             # 이미지 생성에 필요한 입력 텍스트

@app.get("/", response_class=HTMLResponse)
def read_root():
    return """
        <html>
            <body>
                <p>Click <a href="/docs">here</a> to go to the Swagger UI and test the generate_image endpoint.</p>
            </body>
        </html>
        """

@app.post("/generate-image")
async def generate_image(input_data: ImageInput):
    
     # 사용자가 입력한 키워드를 리스트로 만듭니다.
    user_keywords_list=[input_data.keyword1,input_data.keyword2,input_data.keyword3,input_data.keyword4,input_data.keyword5]
     
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

    # 입력된 텍스트에 대해 TF-IDF 벡터라이저를 적용합니다.
    tfidf_matrix = vectorizer.fit_transform([input_data.text])

    # TF-IDF 벡터라이저에서 feature 이름들을 가져옵니다.
    feature_names = vectorizer.get_feature_names_out()

    # TF-IDF 점수 기준으로 정렬하고 상위 5개의 키워드를 가져옵니다.
    sorted_keywords_indices = tfidf_matrix.toarray().argsort()[0][::-1][:5]

    top_5_tfidf_keywords=[feature_names[index] for index in sorted_keywords_indices]
       
     # 사용자가 제공한 키워드와 TF-IDF로 추출된 키워드들을 합칩니다. 
    final_user_and_tfidf_keywrods=user_keywords_list+top_5_tfidf_keywords[:max(0, 5-len(user_keywords_list))]

    translated_final_keywords=[]
    for keyword in final_user_and_tfidf_keywrods:
        if keyword is not None:
            # Google Cloud Translation API를 사용하여 각 키워드를 영어로 번역합니다.
            result_keyword_translate=translate_client.translate(keyword,target_language='en')
            translated_final_keywords.append(result_keyword_translate['input'])

    final_translated_user_and_tfidf_keywrods = translated_final_keywords

    keywords_prompt=" ".join(final_translated_user_and_tfidf_keywrods)

    REST_API_KEY = "9ea943bc1dce2cd5fe7a41bdba661924"

    image_urls = []  
    for i in range(8):   
        r = requests.post(
            'https://api.kakaobrain.com/v2/inference/karlo/t2i',
            json={
                'prompt': keywords_prompt,
            },
            headers={
                'Authorization': f'KakaoAK {REST_API_KEY}',
                'Content-Type':'application/json'
            }
        )

        if r.status_code == 200:
            response_json = r.json()
        
            image_url = response_json["images"][0]["image"]
        
            image_urls.append(image_url)

            logger.info(f"Image generation successful for request {i+1}")  # 이미지 생성 요청이 성공적으로 완료되었음을 로그로 남깁니다.
        else:
             logger.warning(f"Image generation failed for request {i+1}")  # 이미지 생성 요청이 실패했음을 로그로 남깁니다.

    if len(image_urls) == 0:
        return {
             'isSuccess': False,
             'code': 400,
             'message': "이미지 생성에 실패하였습니다."
         }
    
    logger.info("Image generation requests completed successfully")  # 모든 이미지 생성 요청이 성공적으로 완료되었음을 로그로 남깁니다.

    return {
         'isSuccess': True,
         'code': 200,
         'message': "요청에 성공하였습니다.",
         'data': image_urls
     }