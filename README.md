# OnLog_Image_Generation

## 🌐 프로젝트 개요

본 프로젝트의 목표는 사용자가 작성한 게시글의 썸네일을 추천하는 서비스를 개발하는 것입니다.
이 서비스는 사용자가 작성한 게시글의 내용을 깊이 이해하고, 이를 바탕으로 가장 적절한 썸네일을 추천하여 사용자의 편의성을 향상시키는 것을 목표로 합니다.

## 🛠️ 프로젝트 개발 환경

프로젝트는 아래 환경에서 개발되었습니다.

> OS: macOS Sonoma   
> IDE: Pycharm  
> Python: 3.11.6

## 🔗 프로젝트 구조

```text
.
├── .dockerignore            🚫 Docker 이미지 생성 시 무시하는 파일 목록
├── .env                     🔐 프로젝트에서 사용하는 환경 변수 설정 파일
├── .git                     📂 Git 버전 관리를 위한 디렉토리
├── .gitignore               🙈 Git 버전 관리 시 무시하는 파일 목록
├── .idea                    🧠 IntelliJ IDEA 설정 파일이 저장된 디렉토리
├── Dockerfile               🐳 Docker 이미지 생성을 위한 스크립트
├── README.md                📚 프로젝트에 대한 설명과 사용 방법 등을 담은 문서
├── __pycache__              🗂️ 파이썬이 컴파일한 버전의 파일을 저장하는 디렉토리
├── main.py                  🚀 프로그램의 시작점
├── my-key.json              🔑 서비스 인증을 위한 개인 키
└── requirements.txt         📌 프로젝트에서 필요한 파이썬 패키지 목록
```

## ✅ 프로젝트 개발/실행

해당 프로젝트를 추가로 개발 혹은 실행시켜보고 싶으신 경우 아래의 절차에 따라 진행해주세요

#### 1. 가상 환경 생성

```commandline
python3 -m venv venv
```

### 2. 가상 환경 활성화

```commandline
source venv/bin/activate
```

### 3. requirements 다운로드

```commandline
pip install -r requirements.txt
```

### 4. `.env` 파일 생성

```commandline
touch .env
```

### 5. `.env` 파일에 Karlo API Key 정보 입력

```text
KARLO_API_KEY = "{KARLO_API_KEY}"
```

### 6. google translate 사용을 위한 my-key.json 추가 (예시)

```text
{
    "type": "{type}",
    "project_id": "{project_id}",
    "private_key_id": "{private_key_id}",
    "private_key": "{private_key}",
    "client_email": "{client_email}",
    "client_id": "{client_id}",
    "auth_uri": "{auth_uri}",
    "token_uri": "{token_uri}",
    "auth_provider_x509_cert_url": "{auth_provider_x509_cert_url}",
    "client_x509_cert_url": "{client_x509_cert_url}",
    "universe_domain": "{universe_domain}"
}
```

> 참고) Google Cloud Translation API의 키 발급 방법  
>> 1. Google Cloud Console에 로그인합니다.  
>> 2. 좌측 메뉴에서 'IAM & Admin' > 'Service Accounts'를 클릭합니다.  
>> 3. 상단의 '+ CREATE SERVICE ACCOUNT' 버튼을 클릭합니다.  
>> 4. 서비스 계정 이름과 설명을 입력하고 'CREATE' 버튼을 클릭합니다.  
>> 5. 'Service Account Permissions' 화면에서 'Role' 드롭다운 메뉴에서 'Cloud Translation > Cloud Translation API User'를 선택하고 'CONTINUE'를 클릭합니다.  
>> 6. 'Grant users access to this service account' 화면에서 'DONE'을 클릭하여 서비스 계정 생성을 완료합니다.  
>> 7. 생성한 서비스 계정을 클릭하고, 'Keys' 탭에서 'ADD KEY'를 클릭한 후 'Create new key'를 선택합니다.  
>> 8. 'Key type'에서 'JSON'을 선택하고 'CREATE'를 클릭합니다.  


### 7. 프로그램 실행

```commandline
uvicorn main:app --port 8000 --reload
```

**참고) 프로젝트가 실행 중인 환경에 한해 아래 URL에서 API 명세서를 확인할 수 있습니다**

```commandline
http://localhost:8000/docs
http://localhost:8000/redoc
```
