/*
what: 위 설정/컴포넌트들을 한 모듈에 묶어서 전역(Global)제공. 
앱 부트스트랩 단계에서 CORS/버전닝/보안헤더 적용, 
전역 파이프/필터/인터셉터를 등록하도록 팩토리/프로바이더로 노출.
why: 앱 시작 시점에 공통 정책을 일괄 등록하여, 다른 모듈이 자동 혜택.
*/

import { Module } from "@nestjs/common";
import { ConfigModule } from "@nestjs/config";
import configs from "./config";
import { ValidationPipeConfig } from "./pipes/validation.pipe";
import { Global } from "@nestjs/common";

@Global()
@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
      envFilePath: ".env",
      load: configs,
    }),
  ],
  exports: [ConfigModule],
})
export class CommonModule {}
