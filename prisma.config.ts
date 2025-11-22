import { defineConfig, env } from "prisma/config";
// prisma.config.ts
import "dotenv/config"; // 프로젝트 루트의 .env 자동 로드
// 만약 .env가 prisma 폴더 안에 있다면:
import { config } from "dotenv";
config({ path: "./prisma/.env" }); // prisma/.env를 명시적으로 로드

export default defineConfig({
  schema: "apps/be/prisma/schema.prisma",
  migrations: {
    path: "apps/be/prisma/migrations",
  },
  engine: "classic",
  datasource: {
    url: env("DATABASE_URL"),
  },
});
