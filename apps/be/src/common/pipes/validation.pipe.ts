/*
what: 전역 ValidationPipe 옵션 설계 (예: whitelist, transform, forbidNonWhitelisted, disableErrorMessages 등).
why: 모든 요청 DTO/쿼리에 유효성/형변환을 자동 적용해 컨트롤러를 “깨끗하게”.
목표: 컨트롤러에 들어오는 값이 항상 타입/스키마에 맞게 정리되어 오도록 전역 파이프를 세팅한다. 
*/

// whitelist: true -> DTO에 정의되지 않은 필드는 자동 제거
// transform: true -> DTO에 정의된 필드는 자동 형변환
// forbidNonWhitelisted: 정의 안 된 필드가 오면 400으로 막아 빠르게 문제 발견
// disableErrorMessages: 운영에서 상세 검증 메시지 숨김
// validationError: 에러 응답에 원본 객체/값을 넣지 않음

import { ValidationPipe } from "@nestjs/common";
import appConfig from "../config/app.config";

const isDev = appConfig().nodeEnv === "development";

export const ValidationPipeConfig = (): ValidationPipe => {
  return new ValidationPipe({
    whitelist: true,
    transform: true,
    transformOptions: {
      enableImplicitConversion: true,
    },
    forbidNonWhitelisted: isDev,
    disableErrorMessages: !isDev,
    validationError: {
      target: false,
      value: false,
    },
  });
};
