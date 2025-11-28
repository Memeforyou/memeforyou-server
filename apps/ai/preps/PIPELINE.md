# 전처리 모듈

```
apps/
└── ai/
    ├── preppipe.py
    └── downloader/
        ├── DLmanager.py
        ├── instagram.py
        └── pinterest.py
    └── preps/
        ├── captioner.py
        ├── embedder.py
        ├── dblite.py
        ├── init_sqlite.py
        ├── PIPELINE.md
        └── prepdb.sqlite3 [init_sqlite.py를 실행하면 생성됨]
```

## 대략적 과정

1. 실제 MySQL & Prisma DB와 거의 유사한 구조의 로컬 SQLite3 DB를 통해 전처리 과정을 진행
   - 전처리 로컬 DB는 스키마를 그대로 따라가되, 전처리 상태 표기를 위한 status 컬럼 추가
2. 전처리가 모두 완료되어 그대로 업로드하면 되는 상태로 되었을 때, 기존 시드 데이터와 같은 형태의 .json으로 추출
3. 검증된 seeddummy.py로 Railway MySQL volume에 업로드

## 각 모듈 설명

- preppipe.py: 전처리 과정 총괄 스크립트
- downloader/DLmanager.py: 다운로드 관리 스크립트
  - 다운로드한 밈 별로 SQLite3 DB에 row 생성, status를 `PENDING`으로 설정
  - instagram.py: 인스타그램 담당
  - pinterest.py: 핀터레스트 담당
- preps/init_sqlite.py: 전처리 관리를 위한 로컬 SQLite3 DB 초기화
  - 각 환경별 최초 1회만 실행하면 됨 (또는 스키마 변경 시)
- preps/dblite.py: SQLite3 상호작용 담당 모듈
- preps/captioner.py: `PENDING` 상태에 있는 밈에 대해서, {ocr, caption, humor} 및 ImageTag 처리
  - 해당 처리된 밈의 status를 `CAPTIONED`로 설정
- preps/embedder.py: `CAPTIONED` 상태인 밈에 대해서, caption을 임베딩 후 Firestore에 저장
  - 해당 처리된 밈의 status를 `READY`로 설정

## 구체적 과정

```
[1] init_sqlite.py 실행 {환경별 최초 1회 또는 스키마 변경 시}
      ↓
SQLite3 로컬 DB 생성

[2] DLmanager.py 실행 → 이미지 다운로드
      ↓
낮은 화질 이미지 필터링 (최소 256x256)
각 이미지 row 생성
(이 과정이 완료된 row는 status = PENDING)

[3] captioner.py 실행
      ↓
status = PENDING인 row를 확보해서,
OCR, caption, humor, ImageTag 생성
(이 과정이 완료된 row는 status = CAPTIONED)

[4] embedder.py 실행
      ↓
status = CAPTIONED인 row를 확보해서,
caption 임베딩 → Firestore 저장
(이 과정이 완료된 row는 status = READY)

[5] preppipe.py 또는 별도 스크립트로 JSON Export
      ↓
현재 apps/ai/seed에 있는 것과 같은 형식의 seed JSON 형태로 변환

[6] seeddummy.py 사용하여 Railway MySQL로 업로드
```
