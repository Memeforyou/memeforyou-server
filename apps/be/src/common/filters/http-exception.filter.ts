/*
what: 모든 예외를 OpenAPI의 ErrorResponse(message, status_code, timestamp) 형식으로 변환.
why: 프론트/문서와의 계약 일관성 유지. 다양한 Nest 예외를 하나의 응답 포맷으로 통합.
*/
