/*
what: 성공/에러 응답의 형태 상수/타입 규약, ErrorResponse 빌더 등.
why: 필터/컨트롤러가 같은 포맷을 쉽게 출력하도록 보조.
*/

export type ErrorResponse = {
  message: string;
  status_code: number;
  timestamp: string;
};

export type SuccessResponse<T> = {
  data: T;
  status_code: number;
  timestamp: string;
};

const nowIso = () => new Date().toISOString();

export function buildErrorResponse(
  message: string,
  statusCode: number
): ErrorResponse {
  return {
    message,
    status_code: statusCode,
    timestamp: nowIso(),
  };
}

export function buildSuccessResponse<T>(data: T): SuccessResponse<T> {
  return {
    data,
    status_code: 200,
    timestamp: nowIso(),
  };
}
