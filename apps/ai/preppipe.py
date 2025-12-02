from loguru import logger
import questionary
import sys
from downloader.DLmanager import managed_download
from preps.captioner import captioner_operation
from preps.embedder import embedder_operation
from preps.dblite import export_json, get_status_counts
from preps.init_sqlite import init_db

COMMANDS = {
    "Initialize Database": lambda: ...,
    "Download New Memes": lambda: ...,
    "Run Captioner": lambda: ...,
    "Run Embedder": lambda: ...,
    "Export JSON": lambda: ...,
    "Show local DB Status": lambda: ...,
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

if __name__ == "__main__":
    main()