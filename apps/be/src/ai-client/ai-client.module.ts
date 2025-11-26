import { Module } from "@nestjs/common";
import { AiClientService } from "./ai-client.service";
import { HttpModule } from "@nestjs/axios";

@Module({
  imports: [
    HttpModule.register({
      timeout: 60000, // 60초
      maxRedirects: 5,
    }),
  ],
  providers: [AiClientService],
  exports: [AiClientService],
})
export class AiClientModule {}
