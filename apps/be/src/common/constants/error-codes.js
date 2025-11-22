"use strict";
/*
what: 공통 에러 코드/메시지 상수(예: NOT_FOUND_IMAGE, BAD_REQUEST_PARAM).
why: 서비스 전반에서 재사용/일관.
*/
Object.defineProperty(exports, "__esModule", { value: true });
exports.ERROR_CODES = void 0;
exports.messageOf = messageOf;
exports.ERROR_CODES = {
    NOT_FOUND_IMAGE: "요청하신 이미지를 찾을 수 없습니다.",
    BAD_REQUEST_PARAM: "잘못된 요청 파라미터입니다.",
    INTERNAL_SERVER_ERROR: "서버 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.",
    BAD_REQUEST: "잘못된 요청입니다.",
    NOT_FOUND: "찾을 수 없는 리소스입니다.",
    UNPROCESSABLE_ENTITY: "처리할 수 없는 요청입니다.",
    TOO_MANY_REQUESTS: "요청이 너무 많습니다. 잠시 후 다시 시도해 주세요.",
};
function messageOf(code) {
    return exports.ERROR_CODES[code];
}
