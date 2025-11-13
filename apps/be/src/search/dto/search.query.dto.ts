import { IsIn, IsInt, IsOptional, IsString, Max, Min } from "class-validator";
import { Type } from "class-transformer";

export class SearchQueryDto {
  // 검색어
  @IsString()
  query?: string;

  // 페이지
  @IsOptional()
  @Type(() => Number)
  @IsInt()
  @Min(1)
  page: number = 1;

  @IsOptional()
  @Type(() => Number)
  @IsInt()
  @Min(1)
  @Max(100)
  size: number = 20;

  // 정렬
  @IsOptional()
  @IsString()
  @IsIn(["accuracy", "like"])
  sort: "accuracy" | "like" = "accuracy";
}
