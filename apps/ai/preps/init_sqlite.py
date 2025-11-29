import sqlite3
import json

conn = sqlite3.connect("prepdb.sqlite3")
cursor = conn.cursor()

# Dedicated local SQLite3 schema
cursor.execute("""
CREATE TABLE IF NOT EXISTS Image (
    image_id INTEGER PRIMARY KEY AUTOINCREMENT,
    original_url TEXT,
    like_cnt INTEGER DEFAULT 0,
    width INTEGER NOT NULL,
    height INTEGER NOT NULL,
    src_url TEXT,
    caption TEXT,
    cloud_url TEXT,
    status TEXT
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS ImageTag (
    image_tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    image_id INTEGER NOT NULL,
    tag TEXT,
    FOREIGN KEY (image_id) REFERENCES Image(image_id)
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS Tag (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_name TEXT NOT NULL UNIQUE
)
""")
tags_to_insert = ["웃긴", "슬픈", "귀여운", "동물", "사람", "카툰", "캐릭터"]
cursor.executemany(
    "INSERT OR IGNORE INTO Tag (tag_name) VALUES (?)",
    tags_to_insert
)
conn.commit()