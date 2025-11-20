import asyncio
import json
from prisma import Prisma, register
from prisma.models import Tag, Image, Embedding
from loguru import logger

# Define seed file paths
TAGS_PATH = "./seed/tags.json"
IMAGES_PATH = "./seed/images.json"
EBDS_PATH = "./seed/embeddings.json"

# Util function to open and load json file
def load_json(path: str):
    with open(path, "r", encoding="utf8") as f:
        return json.load(f)

# Main function. All Prisma operations must be async.
async def main() -> None:

    # Make Prisma class and register
    db = Prisma()
    register(db)

    # Connect to DB
    await db.connect()
    logger.info("Connected to Prisma.")

    # Seed Tags
    logger.info("Beginning Tags seeding...")
    tags_count, tags_total = await seed_tags(TAGS_PATH)
    logger.success(f"Tags seeded successfully. {tags_count} out of {tags_total} samples.")

    # Seed Images
    logger.info("Beginning Images seeding...")
    images_count, images_total = await seed_images(IMAGES_PATH)
    logger.success(f"Images seeded successfully. {images_count} out of {images_total} samples.")

    # Seed Embeddings
    logger.info("Beginning Embeddings seeding...")
    ebds_count, ebds_total = await seed_embeddings(EBDS_PATH)
    logger.success(f"Embeddings seeded successfully. {ebds_count} out of {ebds_total} samples.")

    # Disconnect from DB
    await db.disconnect()
    logger.info("Disconnected from Prisma.")

# Function to seed Tags; each of these functions return successfully seeded entries count & total entries present in json.
async def seed_tags(path):

    # Load tags.json from path
    data = load_json(path)
    total = len(data)
    count = 0

    # Insert operations
    for idx, row in enumerate(data, start=1):
        await Tag.prisma().create(data=row)
        logger.trace(f"Seeded Tag {idx}/{total}: {row.get('tag_name')}")
        count += 1

    return count, total

# Function to seed Images
async def seed_images(path):

    # Load images.json from path
    data = load_json(path)
    total = len(data)
    count = 0

    # Insert operations
    for idx, row in enumerate(data, start=1):
        await Image.prisma().create(data=row)
        logger.trace(f"Seeded Image {idx}/{total}")
        count += 1

    return count, total

# Function to seed Embeddings
async def seed_embeddings(path):

    # Load embeddings.json from path
    data = load_json(path)
    total = len(data)
    count = 0

    # Insert operations
    for idx, row in enumerate(data, start=1):
        await Embedding.prisma().create(data=row)
        logger.trace(f"Seeded Embedding {idx}/{total}")
        count += 1

    return count, total

if __name__=="__main__":
    asyncio.run(main())