FROM python:3.11.4

WORKDIR /app

# requirements.txt 를 보고 모듈 전체 설치(-r)
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]