-- CreateTable
CREATE TABLE `Image` (
    `image_id` INTEGER NOT NULL AUTO_INCREMENT,
    `original_url` VARCHAR(191) NOT NULL,
    `like_cnt` INTEGER NOT NULL DEFAULT 0,

    PRIMARY KEY (`image_id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `Tag` (
    `tag_id` INTEGER NOT NULL AUTO_INCREMENT,
    `tag_name` VARCHAR(191) NOT NULL,

    UNIQUE INDEX `Tag_tag_name_key`(`tag_name`),
    PRIMARY KEY (`tag_id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `ImageTag` (
    `image_id` INTEGER NOT NULL,
    `tag_id` INTEGER NOT NULL,

    PRIMARY KEY (`image_id`, `tag_id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- CreateTable
CREATE TABLE `ImageCaption` (
    `image_id` INTEGER NOT NULL,
    `caption_id` INTEGER NOT NULL,

    UNIQUE INDEX `ImageCaption_image_id_key`(`image_id`),
    PRIMARY KEY (`image_id`)
) DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- AddForeignKey
ALTER TABLE `ImageTag` ADD CONSTRAINT `ImageTag_image_id_fkey` FOREIGN KEY (`image_id`) REFERENCES `Image`(`image_id`) ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `ImageTag` ADD CONSTRAINT `ImageTag_tag_id_fkey` FOREIGN KEY (`tag_id`) REFERENCES `Tag`(`tag_id`) ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE `ImageCaption` ADD CONSTRAINT `ImageCaption_image_id_fkey` FOREIGN KEY (`image_id`) REFERENCES `Image`(`image_id`) ON DELETE CASCADE ON UPDATE CASCADE;
