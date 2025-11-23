import { Module } from "@nestjs/common";
import { SearchModule } from "./search/search.module";
import { AiClientModule } from "./ai-client/ai-client.module";
import { ImageModule } from "./image/image.module";
import { ConfigModule } from "@nestjs/config";

@Module({
  imports: [
    ConfigModule.forRoot({
      isGlobal: true,
    }),
    SearchModule,
    AiClientModule,
    ImageModule,
  ],
})
export class AppModule {}
