from loguru import logger
import questionary
import sys
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
    pass

def worker_embed():
    pass

def worker_export():
    pass

def worker_dbstat():
    pass

if __name__ == "__main__":
    main()