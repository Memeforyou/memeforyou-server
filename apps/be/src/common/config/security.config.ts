/*
what: 보안 헤더(helmet) 옵션, 응답 압축 on/off, HSTS 등 운영 정책.
why: 기본 보안(클릭재킹/XSS) 강화와 응답 크기 줄여 성능↑.
*/

import { registerAs } from "@nestjs/config";

export default registerAs("security", () => ({
  helmet: {
    contentSecurityPolicy: false,
    crossOriginEmbedderPolicy: false,
  },
  compression: (process.env.RESPONSE_COMPRESSION ?? "true") === "true",
  hsts: (process.env.HSTS ?? "false") === "true",
}));
