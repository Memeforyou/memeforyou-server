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
def update_captioned(image_id: int, caption: str, tags: List[str]) -> None:
    """
    Updates a meme with caption and tags, and sets status to CAPTIONED.
    Called by the captioner module.
    """
    # Update caption and status in Image table
    cursor.execute(
        "UPDATE Image SET caption = ?, status = 'CAPTIONED' WHERE image_id = ?",
        (caption, image_id)
    )

    # Insert tags into ImageTag table
    tag_data = [(image_id, tag) for tag in tags]
    cursor.executemany(
        "INSERT INTO ImageTag (image_id, tag) VALUES (?, ?)",
        tag_data
    )
    conn.commit()

# For embedder.py
def update_ready(image_id: int) -> None:
    """
    Updates a meme's status to READY.
    Called by the embedder module.
    """
    cursor.execute("UPDATE Image SET status = 'READY' WHERE image_id = ?", (image_id,))
    conn.commit()
