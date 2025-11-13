import { Injectable, NotFoundException } from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";

@Injectable()
export class ImageService {
  constructor(private readonly prisma: PrismaService) {}

  async getImageById(imageId: number) {
    const image = await this.prisma.image.findUnique({
      where: { image_id: imageId },
    });
    if (!image) {
      throw new NotFoundException("Image not found");
    }
    return image;
  }

  async downloadImage(imageId: number) {
    const image = await this.getImageById(imageId);
    const downloadUrl = image.cloud_url;
    if (!downloadUrl) {
      throw new NotFoundException("Download URL not found");
    }
    return {
      downloadUrl: downloadUrl,
      filename: `meme_${image.image_id.toString()}.jpg`,
    };
  }
}
