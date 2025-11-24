import { IsIn, IsInt, IsOptional, IsString, Max, Min } from "class-validator";
import { Type } from "class-transformer";
import { ApiProperty } from "@nestjs/swagger";

export class SearchQueryDto {
  // 검색어
  @ApiProperty({
    description: "The query to search for images",
    example: "cat",
  })
  @IsString()
  query?: string;

  // 페이지
  @ApiProperty({
    description: "The page number to search for images",
    example: 1,
  })
  @IsOptional()
  @Type(() => Number)
  @IsInt()
  @Min(1)
  page: number = 1;

  @ApiProperty({
    description: "The number of images to search for",
    example: 20,
  })
  @IsOptional()
  @Type(() => Number)
  @IsInt()
  @Min(1)
  @Max(100)
  size: number = 20;

  // 정렬
  @ApiProperty({
    description: "The sort order to search for images",
    example: "accuracy",
  })
  @IsOptional()
  @IsString()
  @IsIn(["accuracy", "like"])
  sort: "accuracy" | "like" = "accuracy";
}
