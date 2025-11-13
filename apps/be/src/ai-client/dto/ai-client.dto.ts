import { IsNotEmpty, IsString } from "class-validator";

export class FindSimilarImagesDto {
  @IsString()
  @IsNotEmpty()
  query?: string;
}
