import { Injectable, NotFoundException } from "@nestjs/common";
import { PrismaService } from "../prisma/prisma.service";

@Injectable()
export class ImageService {
  constructor(private readonly prisma: PrismaService) {}

  async getImageById(imageId: number) {
    const image = await this.prisma.image.findUnique({
      where: { image_id: imageId },
      include: {
        ImageTag: {
          include: {
            tag: true,
          },
        },
      },
    });
    // 여기부터 !!!!!
    if (!image) {
      throw new NotFoundException("Image not found");
    }
    const tags = image?.ImageTag.map(
      (x: { tag: { tag_name: string } }) => x.tag.tag_name
    );
    const { ImageTag, ...rest } = image;
    return {
      ...rest,
      tags,
    };
  }

  async downloadImage(imageId: number) {
    const image = await this.getImageById(imageId);
    const downloadUrl = image.cloud_url;
    if (!downloadUrl) {
      throw new NotFoundException("Download URL not found");
    }
    // 다운로드 어케 할지
    return {
      downloadUrl: downloadUrl,
      filename: `meme_${image.image_id.toString()}.jpg`,
    };
  }

  async likeImage(imageId: number) {
    const image = await this.getImageById(imageId);
    if (!image) {
      throw new NotFoundException("Image not found");
    }
    const updatedImage = await this.prisma.image.update({
      where: { image_id: imageId },
      data: { like_cnt: { increment: 1 } },
    });
    return updatedImage;
  }
  async unlikeImage(imageId: number) {
    const image = await this.getImageById(imageId);
    if (!image) {
      throw new NotFoundException("Image not found");
    }
    if (image.like_cnt <= 0) {
      const updatedImage = await this.prisma.image.update({
        where: { image_id: imageId },
        data: { like_cnt: 0 },
      });
      return updatedImage;
    } else {
      const updatedImage = await this.prisma.image.update({
        where: { image_id: imageId },
        data: { like_cnt: { decrement: 1 } },
      });
      return updatedImage;
    }
  }

  async getPopularImages() {
    const images = await this.prisma.image.findMany({
      orderBy: { like_cnt: "desc" },
      take: 10,
    });
    return images;
  }
}
