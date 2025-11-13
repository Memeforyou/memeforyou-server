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

## Serve API
파라미터 구조 및 예시는 코드 또는 Swagger UI 참고  
현재는 더미 데이터 반환함
- `cd apps\ai\`  
`uvicorn main:app --reload`  
*uv를 이용하는 경우, 최초 1회는 `uv run uvicorn main:app --reload`, 이후에는 둘 다 가능*
- 포트: 8000
- Swagger DOCS: http://localhost:8000/docs

## Misc.
- 현재 DB와 연결은 미완성으로, 아직 Prisma DB는 비어 있는 상황임
- Google Cloud Storage에는 더미 데이터에 상응하는 1.jpg ~ 5.jpg 업로드 완료
    - BE 또는 FE에서 테스트를 원할 경우,  
    `https://storage.googleapis.com/gdg-ku-meme4you-test/1.jpg`  
    와 같은 방식으로 직접 URL 구성하여 접근 가능
- Prisma DB는 빠른 시일 내로 작업해서, 시딩 스크립트 제공 예정임
- 요청/반환 형식에 수정이 필요한 경우 피드백 바람

### To Do
- prep & search 역할 정리 및 DB 연결 (Prisma, Google Cloud Storage)
    - [Prisma Client Python](https://prisma-client-py.readthedocs.io/en/stable/)
    - [MySQL Connector/Python Dev Guide](https://dev.mysql.com/doc/connector-python/en/)
    - [Google Cloud Storage DOCS](https://cloud.google.com/storage/docs)
- 다운로드 형식 통일 & Google Cloud Storage 연결