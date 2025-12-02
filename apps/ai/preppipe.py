from loguru import logger
import questionary
import sys
import time
import os
from downloader.DLmanager import managed_download
from preps.captioner import captioner_operation
from preps.embedder import embedder_operation
from preps.dblite import export_json, get_status_counts
from preps.init_sqlite import init_db

COMMANDS = {
    "Initialize Database": lambda: worker_init_db(),
    "Download New Memes": lambda: worker_download(),
    "Run Captioner": lambda: worker_caption(),
    "Run Embedder": lambda: worker_embed(),
    "Export JSON": lambda: worker_export(),
    "Show local DB Status": lambda: worker_dbstat(),
    "Exit": lambda: ...
}

def main():

    while True:

        choice = questionary.select(
            "Choose an action:",
            choices=list(COMMANDS.keys())
        ).ask()

        if choice == "Exit":
            sys.exit(0)

        try:
            
            result = COMMANDS[choice]()

            if result == 0:

                questionary.print("Your chosen operation succeeded.", style="fg:green")

            else:

                questionary.print("Your chosen operation failed.", style="fg:red")
        
        except Exception as e:

            logger.error(f"An error occurred: {e}")

def worker_init_db():

    res = 0

    try:
        logger.info("Initializing database...")
        init_db()
        logger.success("Database initialized successfully.")

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        res = 1

    return res

def worker_download():

    res = 0

    dl_target = questionary.checkbox(
        "Choose target platform to download from:",
        choices=["Instagram", "Pinterest"]
    ).ask()

    try:
        managed_download()

    except Exception as e:
        logger.error(f"Download failed: {e}")
        res = 1

    return res

def worker_caption():
    
    res = 0

    try:
        logger.info(f"Calling captioner...")
        captioner_operation()
        logger.success(f"Captioner operations completed.")

    except Exception as e:
        logger.error(f"Captioning failed: {e}")
        res = 1

    return res

def worker_embed():
    
    res = 0

    try:
        logger.info(f"Calling embedder...")
        embedder_operation()
        logger.success(f"Embedder operations completed.")

    except Exception as e:
        logger.error(f"Embedding failed: {e}")
        res = 1

    return res

def worker_export():

    res = 0

    # Generate timestamped directory and paths
    timestamp = time.strftime("%m%d%H%M%S")
    dir_name = f".{timestamp}_seedjson"
    os.makedirs(dir_name, exist_ok=True)
    logger.info(f"Created export directory: {dir_name}")

    images_path = os.path.join(dir_name, "images.json")
    tags_path = os.path.join(dir_name, "tags.json")

    try:
        logger.info(f"Calling dblite to export to {images_path} and {tags_path}...")
        export_json(images_path=images_path, tags_path=tags_path)
        logger.success(f"JSON export completed.")

    except Exception as e:
        logger.error(f"JSON export failed: {e}")
        res = 1

    return res

def worker_status():
    pass

def worker_dbstat():
    pass

if __name__ == "__main__":
    main()