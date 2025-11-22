"use strict";
/*
what: 성공/에러 응답의 형태 상수/타입 규약, ErrorResponse 빌더 등.
why: 필터/컨트롤러가 같은 포맷을 쉽게 출력하도록 보조.
*/
Object.defineProperty(exports, "__esModule", { value: true });
exports.buildErrorResponse = buildErrorResponse;
exports.buildSuccessResponse = buildSuccessResponse;
const nowIso = () => new Date().toISOString();
function buildErrorResponse(message, statusCode) {
    return {
        message,
        status_code: statusCode,
        timestamp: nowIso(),
    };
}
function buildSuccessResponse(data) {
    return {
        data,
        status_code: 200,
        timestamp: nowIso(),
    };
}
