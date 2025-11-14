import { Controller, Get, Param, Post, Res } from "@nestjs/common";
import { ImageService } from "./image.service";
import axios from "axios";
import { Response } from "express";

@Controller("image")
export class ImageController {
  constructor(private readonly imageService: ImageService) {}

  @Get(":image_id")
  async getImageById(@Param("image_id") imageId: number) {
    return await this.imageService.getImageById(imageId);
  }

  @Get(":image_id/download")
  async downloadImage(
    @Param("image_id") imageId: number,
    @Res() res: Response
  ) {
    const { downloadUrl, filename } = await this.imageService.downloadImage(
      imageId
    );
    const fileResponse = await axios.get(downloadUrl, {
      responseType: "stream",
    });
    res.setHeader(
      "Content-Disposition",
      `attachment; filename="${encodeURIComponent(filename)}"`
    );
    res.setHeader(
      "Content-Type",
      fileResponse.headers["content-type"] ?? "application/octet-stream"
    );
    fileResponse.data.pipe(res);
    return { downloadUrl, filename };
  }

  @Post(":image_id/like")
  async likeImage(@Param("image_id") imageId: number) {
    return await this.imageService.likeImage(imageId);
  }

  @Post(":image_id/like")
  async unlikeImage(@Param("image_id") imageId: number) {
    return await this.imageService.unlikeImage(imageId);
  }

  @Get("popular")
  async getPopularImages() {
    return await this.imageService.getPopularImages();
  }
}
