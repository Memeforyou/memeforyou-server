import { IsNotEmpty, IsString } from "class-validator";
import { ApiProperty } from "@nestjs/swagger";
export class FindSimilarImagesDto {
  @ApiProperty({
    description: "The query to search for similar images",
    example: "cat",
  })
  @IsString()
  @IsNotEmpty()
  query?: string;
}
