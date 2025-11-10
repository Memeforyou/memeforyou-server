| code          | message              | example               | HTTP status |
| ------------- | -------------------- | --------------------- | ----------- |
| INVALID_PARAM | 잘못된 쿼리 파라미터 | size가 음수           | 400         |
| NOT_FOUND     | data 없음            | 존재하지 않는 id 조회 | 404         |
| INTERNAL      | 내부 오류            | Milvus 연결 실페      | 500         |
| RATE_LIMITED  | 요청 초과            | 초당 요청 초과        | 429         |
