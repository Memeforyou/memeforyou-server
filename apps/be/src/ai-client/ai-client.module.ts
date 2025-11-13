import { Module } from "@nestjs/common";
import { AiClientController } from "./ai-client.controller";
import { AiClientService } from "./ai-client.service";
import { HttpModule } from "@nestjs/axios";

@Module({
  imports: [HttpModule],
  exports: [AiClientService],
  controllers: [AiClientController],
  providers: [AiClientService],
})
export class AiClientModule {}
