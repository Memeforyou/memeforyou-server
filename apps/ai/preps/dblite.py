# Handle intermediate status with local SQLite3 DB with status tracking
# Once done, export to seeddummy.py compatible json files
# Apply to Railway prod volume with seeddummy.py

# This script will be dedicated to SQLite3 interactions and file management
import sqlite3
import json

conn = sqlite3.connect("prepdb.sqlite3")
cursor = conn.cursor()

