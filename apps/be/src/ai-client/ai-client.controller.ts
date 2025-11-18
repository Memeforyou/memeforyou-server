// 내부에서만 사용하는 http 클라이언트이기 때문에 컨트롤러가 꼭 필요하지는 않다.

import { Body, Controller, Post, Query } from "@nestjs/common";
import { AiClientService } from "./ai-client.service";
import { FindSimilarImagesDto } from "./dto/ai-client.dto";
import { ApiTags } from "@nestjs/swagger";

@ApiTags("AI")
@Controller("ai")
export class AiClientController {
  constructor(private readonly aiClientService: AiClientService) {}

  @Post("similar")
  async findSimilarImages(@Body() body: FindSimilarImagesDto) {
    return await this.aiClientService.similarSearch({ query: body.query });
  }
}
