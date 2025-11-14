import { ValidationPipeConfig } from "./common/pipes/validation.pipe";
import { NestFactory } from "@nestjs/core";
import { AppModule } from "./app.module";
import appConfig from "./common/config/app.config";
import { ValidationPipe } from "@nestjs/common";

async function bootstrap() {
  // Nest application 부팅
  const app = await NestFactory.create(AppModule);
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      transform: true,
      forbidNonWhitelisted: false,
    })
  );
  await app.listen(appConfig().port);
}
bootstrap();
