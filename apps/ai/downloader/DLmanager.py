from PIL import Image
from loguru import logger
from typing import List
from downloader.instagram import run_instagram_scrape
from downloader.pinterest import run_pinterest_scrape
from preps.dblite import add_meme

BASEPATH = "images/"

def managed_download(target: List[str] = ["Instagram", "Pinterest"], next_id: int = 1, pin_max: int = 50):

    # Initialize image_id counter for id assignment coordination
    # Indicates the id the next meme should be assigned
    id_counter = next_id

    # Run instagram download
    if "Instagram" in target:
        logger.info(f"Running Instagram scraping... (with beginning id {id_counter})")
        try: 
            after_id = run_instagram_scrape(start_id=id_counter, base_path=BASEPATH)
            logger.success(f"Successfully downloaded from Instagram; {after_id-id_counter} images.")
            id_counter = after_id
        except Exception as e:
            logger.error(f"Instagram scraping failed: {e}")

    # Run Pinterest download
    if "Pinterest" in target:
        logger.info(f"Running Pinterest scraping... (with beginning id {id_counter})")
        try:
            after_id = run_pinterest_scrape(start_id=id_counter, base_path=BASEPATH, max=pin_max)
            logger.success(f"Successfully downloaded from Pinterest; {after_id-id_counter} images.")
            id_counter = after_id
        except Exception as e:
            logger.error(f"Pinterest scraping failed: {e}")

if __name__ == "__main__":
    managed_download()