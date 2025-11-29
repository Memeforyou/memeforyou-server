import sqlite3
from typing import List, Optional

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
