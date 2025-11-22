/*
what: 버전 방식(URI versioning), 기본 버전(v1), 지원 버전 목록.
why: /api/v1 고정 운용 → 추후 /v2 병행 운영 시 충돌 없이 확장.
*/

import { registerAs } from "@nestjs/config";

export default registerAs("versioning", () => ({
  type: "URI" as const,
  defaultVersion: process.env.API_VERSION ?? "v1",
  enabled: process.env.VERSIONING_ENABLED === "true",
}));
