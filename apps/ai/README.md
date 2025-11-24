## Environment 구성

명령어 Windows CMD 기준, 본인이 편한 다른 방법으로 해도 됨  
dependency는 pyproject.toml로 명시되어 있음

### 기본 pip를 이용하는 경우

- ./apps/ai/에 가상환경 생성 및 활성화  
  `cd apps\ai\`  
  `python -m venv .venv`  
  `.venv\scripts\activate`
- 패키지 설치  
  `pip install -e .`

### [uv](https://docs.astral.sh/uv/)를 이용하는 경우

- ./apps/ai/에 가상환경 생성 및 활성화  
  `cd apps\ai`  
  `uv venv`  
  `.venv\scripts\activate`
- 개별 스크립트를 실행하려는 경우:  
  `uv run {scriptname}.py`

## .env & .auth

각종 인증 키

### .env

.env.example 파일 참고

- apps/ai/.env 생성
- GEMINI_API_KEY=발급한 GEMINI API 키
- DATABASE_URL=BE에서 설정한 사항과 동일하게
- GOOGLE_PROJECT_ID=gen-lang-client-0594938383
- GOOGLE_APPLICATION_CREDENTIALS=Firestore에 필요한 service account 인증 정보; 아래에서 서술함

### .auth

- apps/ai/.auth/ 폴더에 Google service account 인증 키 파일(json)이 위치해야 함
  - 해당 파일은 카톡에 공유함
- .env의 `GOOGLE_APPLICATION_CREDENTIALS`는 해당 json 키 파일의 path임. 예를 들어,
  - GOOGLE_APPLICATION_CREDENTIALS=.auth/gen-lang-client-xxxxxx.json

## Seeding

20개의 예시 데이터 시딩  
MySQL DB 생성과 Prisma Client Generate가 완료되어 있음을 상정함  
_DB 세팅에 문제가 있는 경우 BE에 문의 요망_

- `cd apps\ai\`  
  `python seeddummy.py` 또는 `uv run seeddummy.py`

## Serve API

파라미터 구조 및 예시는 코드 또는 Swagger UI 참고

- `cd apps\ai\`  
  `uvicorn main:app --reload`  
  _uv를 이용하는 경우, `uv run uvicorn main:app --reload`_
- 포트: 8000
- Swagger DOCS: http://localhost:8000/docs

## Misc.

- 일반 메타데이터는 Prisma DB와 연결 완료
- Google Cloud Storage에 20개 시딩 데이터에 상응하는 1.jpg ~ 20.jpg 업로드 완료
  - BE 또는 FE에서 테스트를 원할 경우,  
    `https://storage.googleapis.com/gdg-ku-meme4you-test/1.jpg`  
    와 같은 방식으로 직접 URL 구성하여 접근 가능
- Google Firestore에 20개의 벡터 업로드 완료 및 Firestore에서 제공하는 벡터 유사도 계산 이용함
- AI API는 20개 데이터 중에서 실제 검색을 수행함
  - 1차 벡터 검색 후보가 기본 10개로 설정되어 있어, count가 10을 초과할 경우 오류가 발생할 수 있음
  - 요청/반환 형식에 수정이 필요한 경우 피드백 바람

### To Do

- prep & downloader 체계화, 실제 배포를 위한 밈 수집 및 전처리 수행

### DOCS

- [Prisma Client Python](https://prisma-client-py.readthedocs.io/en/stable/)
- [Google Cloud Storage DOCS](https://cloud.google.com/storage/docs)
- [Google Firestore in Native mode DOCS](https://docs.cloud.google.com/firestore/native/docs)
- [Google Gemini API DOCS](https://ai.google.dev/gemini-api/docs/)
- [FastAPI DOCS](https://fastapi.tiangolo.com/)
