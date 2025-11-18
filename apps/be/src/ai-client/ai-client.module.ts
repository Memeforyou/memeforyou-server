import { Module } from "@nestjs/common";
import { AiClientController } from "./ai-client.controller";
import { AiClientService } from "./ai-client.service";
import { HttpModule } from "@nestjs/axios";
import { ConfigService } from "@nestjs/config";

@Module({
  imports: [
    HttpModule.registerAsync({
      inject: [ConfigService],
      useFactory: (configService: ConfigService) => ({
        baseURL: configService.get("AI_BASE_URL"),
        timeout: 5000,
      }),
    }),
  ],
  exports: [AiClientService],
  controllers: [AiClientController],
  providers: [AiClientService],
})
export class AiClientModule {}
