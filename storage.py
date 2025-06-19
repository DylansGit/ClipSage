# storage.py

import os  # For file path operations
import sqlite3  # SQLite for local database storage
from datetime import datetime  # To timestamp clipboard entries
from PIL import Image  # For saving image files

# Define where the database and image files will be stored
DATA_DIR = "data"
DB_PATH = os.path.join(DATA_DIR, "clip_history.db")
IMAGES_DIR = os.path.join(DATA_DIR, "images")

# Ensure data and images directories exist
os.makedirs(IMAGES_DIR, exist_ok=True)

# Create the SQLite database and table if not already present
def init_db():
    """
    Initializes the SQLite database by creating the 'history' table.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT NOT NULL,            -- 'text' or 'image'
            content TEXT,                  -- Text content or OCR result
            image_path TEXT,               -- Path to saved image (if type == image)
            timestamp TEXT NOT NULL        -- ISO-formatted timestamp
        )
    ''')
    conn.commit()
    conn.close()

# Call this once when the module is imported
init_db()

def save_clipboard_item(item_type, content, image=None):
    """
    Saves a clipboard item into the database.
    :param item_type: 'text' or 'image'
    :param content: Text content or OCR result
    :param image: PIL Image object (only if item_type is 'image')
    """
    timestamp = datetime.now().isoformat()
    image_path = None

    # If the item is an image, save it as a PNG and store the file path
    if item_type == "image" and image:
        filename = f"clip_{timestamp.replace(':', '-')}.png"
        image_path = os.path.join(IMAGES_DIR, filename)
        try:
            image.save(image_path)
            print(f"[Storage] Image saved to {image_path}")
        except Exception as e:
            print(f"[Storage] Failed to save image: {e}")
            image_path = None

    # Save entry to the SQLite database
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO history (type, content, image_path, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (item_type, content, image_path, timestamp))
        conn.commit()
        conn.close()
        print(f"[Storage] Saved {item_type} clipboard entry at {timestamp}")
    except Exception as e:
        print(f"[Storage] Failed to write to DB: {e}")

def fetch_all_items():
    """
    Fetches all clipboard history items from the database.
    :return: List of rows as dictionaries
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM history ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        conn.close()

        # Map rows to dicts for easy use in GUI
        return [
            {
                "id": row[0],
                "type": row[1],
                "content": row[2],
                "image_path": row[3],
                "timestamp": row[4],
            }
            for row in rows
        ]
    except Exception as e:
        print(f"[Storage] Failed to fetch items: {e}")
        return []


def clear_all_items():
    """
    Wipes all clipboard history from the database.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM history")  # Delete all rows
        conn.commit()
        conn.close()
        print("[Storage] All clipboard items deleted.")
    except Exception as e:
        print(f"[Storage] Failed to clear items: {e}")
