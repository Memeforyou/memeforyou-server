/*
  Warnings:

  - You are about to drop the `ImageCaption` table. If the table is not empty, all the data it contains will be lost.
  - Added the required column `caption` to the `Image` table without a default value. This is not possible if the table is not empty.
  - Added the required column `cloud_url` to the `Image` table without a default value. This is not possible if the table is not empty.
  - Added the required column `height` to the `Image` table without a default value. This is not possible if the table is not empty.
  - Added the required column `src_url` to the `Image` table without a default value. This is not possible if the table is not empty.
  - Added the required column `width` to the `Image` table without a default value. This is not possible if the table is not empty.

*/
-- DropForeignKey
ALTER TABLE `ImageCaption` DROP FOREIGN KEY `ImageCaption_image_id_fkey`;

-- AlterTable
ALTER TABLE `Image` ADD COLUMN `caption` TEXT NOT NULL,
    ADD COLUMN `cloud_url` TEXT NOT NULL,
    ADD COLUMN `height` INTEGER NOT NULL,
    ADD COLUMN `src_url` TEXT NOT NULL,
    ADD COLUMN `width` INTEGER NOT NULL,
    MODIFY `original_url` TEXT NOT NULL;

-- DropTable
DROP TABLE `ImageCaption`;

-- CreateTable
CREATE TABLE `Embedding` (
    `vector` VECTOR(1536) NOT NULL,
    `image_id` INTEGER NOT NULL,

    PRIMARY KEY (`image_id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- AddForeignKey
ALTER TABLE `Embedding` ADD CONSTRAINT `Embedding_image_id_fkey` FOREIGN KEY (`image_id`) REFERENCES `Image`(`image_id`) ON DELETE CASCADE ON UPDATE CASCADE;
