from loguru import logger
import questionary
import sys
import time
import os
from downloader.DLmanager import managed_download
from preps.captioner import captioner_operation
from preps.embedder import embedder_operation, embed_rows
from preps.dblite import export_json, get_status_counts, get_image_count, get_paginated_images, get_tags_for_image
from preps.init_sqlite import init_db

COMMANDS = {
    "Initialize Database": lambda: worker_init_db(),
    "Manage Database": lambda: worker_manage_db(),
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
                questionary.print("Your chosen action succeeded.", style="fg:green")
            else:
                questionary.print("Your chosen action failed.", style="fg:red")

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

MANAGE_COMMANDS = {
    "View DB": lambda: manage_db_viewer(),
    "Update Image(s) Status": lambda: manage_db_updater(),
    "Delete Image(s)": lambda: manage_db_deleter(),
    "Flush DB": lambda: manage_db_flusher(),
    "Return to main menu": lambda: ...
}

def worker_manage_db():

    res = 0

    while True:

        choice = questionary.select(
            "Choose an action:",
            choices=list(MANAGE_COMMANDS.keys())
        ).ask()

        if choice == "Return to main menu":
            break

        try:
            result = MANAGE_COMMANDS[choice]()

            if result == 0:
                questionary.print("Your chosen management action succeeded.", style="fg:green")
            else:
                questionary.print("Your chosen management action failed.", style="fg:red")
        
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            res = 1

    return res

# --- DB management functions start ---

def manage_db_viewer():
    """An interactive CLI viewer for database rows."""
    page_size = 10  # Number of images to show per page
    current_page = 1

    while True:
        total_images = get_image_count()
        if total_images == 0:
            questionary.print("The database is empty. Nothing to show.", style="fg:yellow")
            return 0

        total_pages = (total_images + page_size - 1) // page_size
        offset = (current_page - 1) * page_size

        # Fetch data for the current page
        images = get_paginated_images(limit=page_size, offset=offset)

        # Clear screen and display
        os.system('cls' if os.name == 'nt' else 'clear')
        questionary.print(f"--- Memes Database Viewer (Page {current_page}/{total_pages}) ---", style="bold")
        # Print header
        print(f"{'ID':<5} | {'Status':<10} | {'OrigURL':<7} | {'SrcURL':<6} | {'Likes':<5} | {'Dims':<9} | {'Caption':<7} | {'CloudURL':<8} | {'SrcPlat':<7} | {'ImgExist'}")
        print("-" * 80)

        for image in images:
            # Check for existence of URL and caption fields
            has_orig_url = 'Y' if image['original_url'] else 'N'
            has_src_url = 'Y' if image['src_url'] else 'N'
            has_caption = 'Y' if image['caption'] else 'N'
            has_cloud_url = 'Y' if image['cloud_url'] else 'N'
            dimensions = f"{image['width']}x{image['height']}"
            # Assign source platform initial
            if "pinterest" in image['src_url']:
                src_plat = "P"
            else:
                src_plat = "I"
            img_exists = 'Y' if os.path.exists(f"images/{image['image_id']}.jpg") else '\033[31mN\033[0m'
            
            # Print single line per image
            print(f"{image['image_id']:<5} | {image['status']:<10} | {has_orig_url:<7} | {has_src_url:<6} | {image['like_cnt']:<5} | {dimensions:<9} | {has_caption:<7} | {has_cloud_url:<8} | {src_plat:<7} | {img_exists}")
        
        # Navigation
        action = questionary.text(
            "Navigate: [N]ext, [P]revious, [G]oto page, [Q]uit to menu",
            validate=lambda text: text.lower() in ['n', 'p', 'g', 'q', '']
        ).ask().lower()

        if action == 'q':
            break
        elif action == 'n' or action == '': # Default to next page
            if current_page < total_pages:
                current_page += 1
        elif action == 'p':
            if current_page > 1:
                current_page -= 1
        elif action == 'g':
            try:
                page_num = int(questionary.text(f"Enter page number (1-{total_pages}):").ask())
                if 1 <= page_num <= total_pages:
                    current_page = page_num
            except (ValueError, TypeError):
                questionary.print("Invalid page number.", style="fg:red")
                time.sleep(1)
    
    return 0

def manage_db_updater():
    pass

def manage_db_deleter():
    pass

def manage_db_flusher():
    pass

# --- DB management functions end ---

def worker_download():

    res = 0

    dl_target = questionary.checkbox(
        "Choose target platform to download from:",
        choices=["Instagram", "Pinterest"]
    ).ask()

    pinterest_max = 0

    if "Pinterest" in dl_target:

        pinterest_max = int(questionary.text(
            "Enter maximum Pinterest images to acquire in positive integer:"
        ).ask())

    # Calculate next id to assign
    logger.info(f"Checking local DB to see next id")
    total = get_image_count()
    logger.info(f"Current total: {total}, next id: {total+1}")

    try:
        managed_download(target=dl_target, next_id=total+1, pin_max=pinterest_max)

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

def worker_dbstat():
    
    res = 0

    try:
        logger.info(f"Calling dblite to fetch status...")
        stat_res = get_status_counts()
        logger.success(f"Status fetch completed.")

        # Format the dictionary into a readable string for printing
        status_string = "\n".join([f"  - {status}: {count}" for status, count in stat_res.items()])
        total = sum(stat_res.values())
        questionary.print(f"Image Status Counts:\n{status_string}\n---------------------\nTotal Images: {total}")

    except Exception as e:
        logger.error(f"Status fetch failed: {e}")
        res = 1

    return res

if __name__ == "__main__":
    main()