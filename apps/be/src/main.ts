import { ValidationPipeConfig } from "./common/pipes/validation.pipe";
import { NestFactory } from "@nestjs/core";
import { AppModule } from "./app.module";
import appConfig from "./common/config/app.config";
import { ValidationPipe } from "@nestjs/common";
import { DocumentBuilder, SwaggerModule } from "@nestjs/swagger";

async function bootstrap() {
  // Nest application 부팅
  const app = await NestFactory.create(AppModule);
  // 🔹 여기서 CORS 설정
  app.enableCors({
    origin: [
      "http://localhost:3000", // 로컬 프론트
      "https://meme4you.netlify.app",
    ],
    methods: "GET,HEAD,PUT,PATCH,POST,DELETE,OPTIONS",
    credentials: true,
  });
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      transform: true,
      forbidNonWhitelisted: false,
    })
  );
  const port = process.env.PORT || 3000;

  const config = new DocumentBuilder()
    .setTitle("memeforyou API")
    .setDescription("memeforyou API documentation")
    .setVersion("1.0")
    .addTag("memeforyou")
    .build();
  const document = SwaggerModule.createDocument(app, config);
  SwaggerModule.setup("api-docs", app, document);

  await app.listen(port);
}
bootstrap();
