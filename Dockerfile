FROM python:3.9

# /code 폴더 만들기
WORKDIR /code

# 모든 파일과 폴더를 /code로 복사
COPY . /code

# requirements.txt 를 보고 모듈 전체 설치(-r)
RUN pip install --no-cache-dir -r /code/requirements.txt

# 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]