/*
what: 허용 origin(화이트리스트), 허용 메서드, 허용 헤더, credentials 허용 여부.
why: 프론트 도메인만 열어 보안 강화, 프리플라이트(OPTIONS) 성공 보장.
*/

import { registerAs } from "@nestjs/config";

export default registerAs("cors", () => ({
  origin: process.env.CORS_ORIGIN || "https://www.memeforyou.app",
  methods: (process.env.CORS_METHODS || "GET,POST").split(","),
  allowedHeaders: (
    process.env.CORS_HEADERS || "Content-Type,Authorization,X-Request-Id"
  ).split(","),
  credentials: process.env.CORS_CREDENTIALS === "true",
}));
