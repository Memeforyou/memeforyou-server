import { Controller, Get, Param, Post } from "@nestjs/common";
import { ImageService } from "./image.service";

@Controller("image")
export class ImageController {
  constructor(private readonly imageService: ImageService) {}

  @Get(":image_id")
  async getImageById(@Param("image_id") imageId: number) {
    return await this.imageService.getImageById(imageId);
  }

  @Get(":image_id/download")
  async downloadImage(@Param("image_id") imageId: number) {
    return await this.imageService.downloadImage(imageId);
  }

  @Post(":image_id/like")
  async likeImage(@Param("image_id") imageId: number) {
    return await this.imageService.likeImage(imageId);
  }

  @Post(":image_id/like")
  async unlikeImage(@Param("image_id") imageId: number) {
    return await this.imageService.unlikeImage(imageId);
  }
}
