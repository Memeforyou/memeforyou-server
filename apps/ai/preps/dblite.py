import sqlite3
from typing import List, Optional
import json
from loguru import logger

conn = sqlite3.connect("prepdb.sqlite3")
conn.row_factory = sqlite3.Row
cursor = conn.cursor() 

# For DLmanager.py
def add_meme(original_url: str, width: int, height: int, src_url: str) -> int:
    """
    Adds a new meme to the database with PENDING status.
    Called by the downloader module.
    """
    cursor.execute(
        """
        INSERT INTO Image (original_url, width, height, src_url, status)
        VALUES (?, ?, ?, ?, 'PENDING')
        """,
        (original_url, width, height, src_url)
    )
    conn.commit()
    return cursor.lastrowid

# For all modules to fetch rows by status
def get_memes(status: str) -> List[sqlite3.Row]:
    """
    Retrieves all memes with a given status.
    """
    cursor.execute("SELECT * FROM Image WHERE status = ?", (status,))
    return cursor.fetchall()

# For captioner.py
def update_captioned(image_ids: List[int], captions: List[str], tags_list: List[List[str]]) -> None:
    """
    Updates memes with captions and tags, and sets their status to CAPTIONED.
    Called by the captioner module.
    """
    # Update caption and status in Image table
    update_data = [(caption, image_id) for caption, image_id in zip(captions, image_ids)]
    cursor.executemany(
        "UPDATE Image SET caption = ?, status = 'CAPTIONED' WHERE image_id = ?", update_data
    )

    # Insert tags into ImageTag table
    all_tags_data = []
    for image_id, tags in zip(image_ids, tags_list):
        all_tags_data.extend([(image_id, tag) for tag in tags])
    cursor.executemany(
        "INSERT INTO ImageTag (image_id, tag) VALUES (?, ?)", all_tags_data
    )
    conn.commit()

# For embedder.py
def update_ready(image_ids: List[int]) -> None:
    """
    Updates memes' status to READY in a batch.
    Called by the embedder module.
    """
    cursor.executemany("UPDATE Image SET status = 'READY' WHERE image_id = ?", [(id,) for id in image_ids])
    conn.commit()

# Export ready-made data into seeddummy.py compatible json files
def export_json(images_path: str, tags_path: str) -> None:
    """
    Exports 'READY' memes and all unique tags from the SQLite database
    into JSON files compatible with seeddummy.py.
    """
    logger.info("Starting JSON export process...")

    # 1. Export all unique tags to tags.json
    cursor.execute("SELECT DISTINCT tag FROM ImageTag")
    all_tags = [row['tag'] for row in cursor.fetchall()]
    
    tags_data = []
    for i, tag_name in enumerate(all_tags, start=1):
        tags_data.append({"tag_id": i, "tag_name": tag_name})

    with open(tags_path, 'w', encoding='utf-8') as f:
        json.dump(tags_data, f, ensure_ascii=False, indent=4)
    logger.success(f"Successfully exported {len(tags_data)} unique tags to {tags_path}")

    # 2. Export 'READY' images to images.json
    ready_memes = get_memes(status="READY")
    if not ready_memes:
        logger.warning("No 'READY' memes found to export.")
        return

    images_data = []
    for image_row in ready_memes:
        # Fetch tags for the current image
        cursor.execute("SELECT tag FROM ImageTag WHERE image_id = ?", (image_row['image_id'],))
        image_tags = [row['tag'] for row in cursor.fetchall()]

        # Build the 'ImageTag' structure for Prisma seeding
        image_tag_create_list = []
        for tag in image_tags:
            image_tag_create_list.append({
                "tag": {
                    "connect": {"tag_name": tag}
                }
            })

        # Construct the final image object for the JSON file
        image_dict = {
            "image_id": image_row['image_id'],
            "original_url": image_row['original_url'],
            "src_url": image_row['src_url'],
            "cloud_url": image_row['cloud_url'],
            "caption": image_row['caption'],
            "width": image_row['width'],
            "height": image_row['height'],
            "like_cnt": image_row['like_cnt'],
            "ImageTag": {"create": image_tag_create_list}
        }
        images_data.append(image_dict)

    with open(images_path, 'w', encoding='utf-8') as f:
        json.dump(images_data, f, ensure_ascii=False, indent=2)
    logger.success(f"Successfully exported {len(images_data)} 'READY' memes to {images_path}")
