import {
  BadRequestException,
  Injectable,
  InternalServerErrorException,
} from "@nestjs/common";
import { HttpService } from "@nestjs/axios";
import { firstValueFrom } from "rxjs";

// AI API 호출, 에러/타임아웃/폴백 처리, 응답 파싱

export interface AiSimilarSearchResponse {
  count: number;
  recommendations: Array<{
    image_id: number;
    rank: number;
  }>;
}

@Injectable()
export class AiClientService {
  constructor(private readonly httpService: HttpService) {}

  async similarSearch(req: {
    query?: string;
  }): Promise<AiSimilarSearchResponse> {
    function isValidRes(x: any): x is AiSimilarSearchResponse {
      return (
        x &&
        Array.isArray(x.recommendations) &&
        x.recommendations.every(
          (recommendation: any) =>
            typeof recommendation.image_id === "number" &&
            typeof recommendation.rank === "number"
        ) &&
        (x.count === undefined || typeof x.count === "number")
      );
    }
    // searchService에서 받은 query를 AI 서버로 보내고 그 응답을 받아서 가공해서 돌려준다.
    // 1. AI 서버에 HTTP 요청을 보낸다.
    // AI 서버에 어떻게 접근?
    try {
      const response = await firstValueFrom(
        this.httpService.post<AiSimilarSearchResponse>(
          `http://localhost:8000/ai/similar`,
          { text: req.query, count: 10 }
        )
      );
      const data = response.data;

      // 2. 응답을 AiSimilarSearchResponse 형식으로 변환해서 돌려준다.
      const result: AiSimilarSearchResponse = {
        count: data.count,
        recommendations: data.recommendations,
      };
      if (!isValidRes(result)) {
        console.log("Invalid AI result:", JSON.stringify(result, null, 2));
        throw new BadRequestException("유효하지 않은 응답입니다.");
      }
      return result;
    } catch (error) {
      console.log("requesting to AI server with query:", req.query);
      throw new InternalServerErrorException(
        `AI 서버 요청 실패: ${
          error instanceof Error ? error.message : "알 수 없는 오류"
        }`
      );
    }
  }
}
