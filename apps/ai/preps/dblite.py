import sqlite3
from typing import List, Dict
import json
from loguru import logger
from preps.init_sqlite import init_db
import os

DB_PATH = os.path.join("prepdb.sqlite3")

# --- Database helpers ---
def _get_conn():
    """Get a new SQLite connection."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# For DLmanager.py
def add_meme(original_url: str, width: int, height: int, src_url: str) -> int:
    """Adds a new meme to the database with PENDING status."""
    with _get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO Image (original_url, width, height, src_url, status)
            VALUES (?, ?, ?, ?, 'PENDING')
            """,
            (original_url, width, height, src_url)
        )
        conn.commit()
        return cursor.lastrowid

# Retrieve memes by status
def get_memes(status: str) -> List[sqlite3.Row]:
    """Retrieves all memes with a given status."""
    with _get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Image WHERE status = ?", (status,))
        return cursor.fetchall()

# For captioner.py
def update_captioned(image_ids: List[int], captions: List[str], tags_list: List[List[str]]) -> None:
    """Updates memes with captions and tags, sets status to CAPTIONED."""
    with _get_conn() as conn:
        cursor = conn.cursor()
        update_data = [(caption, image_id) for caption, image_id in zip(captions, image_ids)]
        cursor.executemany(
            "UPDATE Image SET caption = ?, status = 'CAPTIONED' WHERE image_id = ?", update_data
        )

        all_tags_data = []
        for image_id, tags in zip(image_ids, tags_list):
            all_tags_data.extend([(image_id, tag) for tag in tags])
        cursor.executemany(
            "INSERT INTO ImageTag (image_id, tag) VALUES (?, ?)", all_tags_data
        )
        conn.commit()

# For embedder.py
def update_ready(image_ids: List[int]) -> None:
    """Updates memes' status to READY in a batch."""
    with _get_conn() as conn:
        cursor = conn.cursor()
        cursor.executemany(
            "UPDATE Image SET status = 'READY' WHERE image_id = ?", [(id,) for id in image_ids]
        )
        conn.commit()

# Export to JSON
def export_json(images_path: str, tags_path: str) -> None:
    """Exports 'READY' memes and all unique tags to JSON files."""
    logger.info("Starting JSON export process...")
    with _get_conn() as conn:
        cursor = conn.cursor()

        # Export all tags from the Tag table
        cursor.execute("SELECT tag_id, tag_name FROM Tag ORDER BY tag_id")
        tags_data = [{"tag_id": row['tag_id'], "tag_name": row['tag_name']} for row in cursor.fetchall()]

        with open(tags_path, 'w', encoding='utf-8') as f:
            json.dump(tags_data, f, ensure_ascii=False, indent=2)
        logger.success(f"Exported {len(tags_data)} unique tags to {tags_path}")

        # Export READY memes
        ready_memes = get_memes("READY")
        if not ready_memes:
            logger.warning("No 'READY' memes found to export.")
            return

        images_data = []
        for image_row in ready_memes:
            cursor.execute("SELECT tag FROM ImageTag WHERE image_id = ?", (image_row['image_id'],))
            image_tags = [row['tag'] for row in cursor.fetchall()]

            image_tag_create_list = [{"tag": {"connect": {"tag_name": tag}}} for tag in image_tags]

            makeshift_cloud_url = "https://storage.googleapis.com/gdg-ku-meme4you-test/"+str(image_row['image_id'])+".jpg"

            images_data.append({
                "image_id": image_row['image_id'],
                "original_url": image_row['original_url'],
                "src_url": image_row['src_url'],
                "cloud_url": makeshift_cloud_url,
                "caption": image_row['caption'],
                "width": image_row['width'],
                "height": image_row['height'],
                "like_cnt": image_row['like_cnt'],
                "ImageTag": {"create": image_tag_create_list}
            })

        with open(images_path, 'w', encoding='utf-8') as f:
            json.dump(images_data, f, ensure_ascii=False, indent=2)
        logger.success(f"Exported {len(images_data)} 'READY' memes to {images_path}")

# Status counts
def get_status_counts() -> Dict[str, int]:
    """Returns counts of images per status, treating NULL as 'PENDING'."""
    statuses = ["PENDING", "CAPTIONED", "READY"]
    counts = {status: 0 for status in statuses}

    with _get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COALESCE(status, 'PENDING') AS status, COUNT(*) 
            FROM Image 
            GROUP BY COALESCE(status, 'PENDING')
        """)
        for status, count in cursor.fetchall():
            counts[status] = count

    return counts

def get_all_img_urls() -> List[str]:
    """
    Get all image urls for dedup
    
    :return: As a list of strings
    :rtype: List[str]
    """
    
    with _get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT original_url FROM Image")
        # Fetch all non-null URLs
        urls = [row['original_url'] for row in cursor.fetchall() if row['original_url']]
        logger.info(f"Fetched {len(urls)} existing URLs from the database for de-duplication.")
        return urls

# --- DB Management Helpers ---

def get_image_count() -> int:
    """Returns the total number of images in the database."""
    with _get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Image")
        return cursor.fetchone()[0]

def get_paginated_images(limit: int, offset: int) -> List[sqlite3.Row]:
    """Retrieves a page of images, ordered by image_id."""
    with _get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM Image ORDER BY image_id LIMIT ? OFFSET ?",
            (limit, offset)
        )
        return cursor.fetchall()

def get_tags_for_image(image_id: int) -> List[str]:
    """Retrieves all tags for a given image_id."""
    with _get_conn() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT tag FROM ImageTag WHERE image_id = ?", (image_id,))
        return [row['tag'] for row in cursor.fetchall()]

def update_status_only(image_ids: List[int], new_status: str) -> None:
    """Updates memes' status to whatever user wants."""

    with _get_conn() as conn:
        cursor = conn.cursor()
        cursor.executemany(
            "UPDATE Image SET status = ? WHERE image_id = ?", [(new_status, id) for id in image_ids]
        )
        conn.commit()

def delete_rows_by_id(image_ids: List[int]) -> None:

    with _get_conn() as conn:
        cursor = conn.cursor()
        logger.info(f"Deleting {len(image_ids)} rows...")
        cursor.executemany(
            "UPDATE Image SET status = DELETED WHERE image_id = ?", [(id,) for id in image_ids]
        )
        logger.success(f"Deletion complete.")
        conn.commit()

def flush_db() -> None:

    os.remove(DB_PATH)
    logger.info(f"Database file deleted.")
    init_db()
    logger.success(f"Database regenarated.")