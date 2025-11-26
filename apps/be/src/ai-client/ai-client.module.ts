import { Module } from "@nestjs/common";
import { AiClientController } from "./ai-client.controller";
import { AiClientService } from "./ai-client.service";
import { HttpModule } from "@nestjs/axios";
import { ConfigService } from "@nestjs/config";

@Module({
  imports: [
    HttpModule.register({
      timeout: 15000, // 15초
      maxRedirects: 5,
    }),
  ],
  providers: [AiClientService],
  exports: [AiClientService],
})
export class AiClientModule {}
