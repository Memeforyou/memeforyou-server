import {
  BadRequestException,
  Injectable,
  NotFoundException,
} from "@nestjs/common";
import { PrismaService } from "../../prisma/prisma.service";
import { SearchQueryDto } from "../dto/search.query.dto";
import { AiClientService } from "../../ai-client/ai-client.service";

// 검색 파라미터 전처리, AI 호출, DB 메타데이터 조회, 결과 정렬/조립

@Injectable()
export class SearchService {
  constructor(
    private prisma: PrismaService,
    private aiClientService: AiClientService
  ) {}

  async search({ query, page, size, sort }: SearchQueryDto) {
    // 실제 DB에서 검색하는 로직
    // 검색 파라미터 전처리
    let cleanedQuery = query ?? "";
    cleanedQuery = cleanedQuery.trim().toLowerCase();
    cleanedQuery = cleanedQuery.replace(/\s+/g, " ");

    const currentPage = Math.max(1, page);
    const pageSize = Math.min(Math.max(size, 1), 100);
    const offset = (currentPage - 1) * pageSize;

    const allowedSorts = ["accuracy", "like"];
    const validSort = allowedSorts.includes(sort) ? sort : "accuracy";

    if (!cleanedQuery) {
      throw new BadRequestException("검색어를 입력해주세요.");
    }
    // AI 서버에 검색 요청 보내고 응답 받기
    const aiReq = { query: cleanedQuery };
    const aiRes = await this.aiClientService.similarSearch(aiReq);

    if (aiRes.candidates.length === 0) {
      throw new NotFoundException("검색 결과가 없습니다.");
    }

    const imageIds = aiRes.candidates.map((candidate) => candidate.imageId);
    // 페이지네이션 계산
    const total = imageIds.length;
    if (offset >= total) {
      throw new NotFoundException("더 이상 결과가 없습니다.");
    }

    if (validSort === "accuracy") {
      const pagedImageIds = imageIds.slice(offset, offset + pageSize);
      const images = await this.prisma.image.findMany({
        where: { image_id: { in: pagedImageIds } },
      });
      const imageMap = new Map(images.map((image) => [image.image_id, image]));
      const orderedImages = pagedImageIds
        .map((imageId) => imageMap.get(imageId))
        .filter(Boolean);
      return {
        items: orderedImages,
        total,
        page: currentPage,
        size: pageSize,
        sort: validSort,
      };
    }
    // DB 조회
    const images = await this.prisma.image.findMany({
      where: { image_id: { in: imageIds } },
      orderBy: {
        like_cnt: "desc",
      },
      skip: offset,
      take: pageSize,
    });
    // 응답 객체 조립
    return {
      items: images,
      total,
      page: currentPage,
      size: pageSize,
      sort: validSort,
    };
  }
}
