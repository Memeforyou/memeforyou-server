/*
what: 앱 포트, API prefix(/api), 기본 버전(v1), 실행 모드(dev/prod) 등.
why: 부트스트랩(main.ts)에서 프리픽스/버전/포트를 한 번에 읽어 적용하기 위해.
*/
import { registerAs } from "@nestjs/config";

export default registerAs("app", () => ({
  port: parseInt(process.env.PORT || "3000", 10),
  apiPrefix: process.env.API_PREFIX || "/api",
  apiVersion: process.env.API_VERSION || "v1",
  nodeEnv: process.env.NODE_ENV || "development",
}));
