import { Module } from "@nestjs/common";
import { PrismaModule } from "../prisma/prisma.module";
import { SearchController } from "./search.controller";
import { SearchService } from "./search.service";
import { AiClientModule } from "../ai-client/ai-client.module";

@Module({
  imports: [PrismaModule, AiClientModule],
  controllers: [SearchController],
  providers: [SearchService],
  exports: [SearchService],
})
export class SearchModule {}
