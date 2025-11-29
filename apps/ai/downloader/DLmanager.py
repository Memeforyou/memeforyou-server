from PIL import Image
from loguru import logger
from ai.downloader.instagram import run_instagram_scrape
from ai.downloader.pinterest import run_pinterest_scrape
from ai.preps.dblite import add_meme

def managed_download():

    # Initialize image_id counter for id assignment coordination
    # Indicates the id the next meme should be assigned
    id_counter = 1

    # Run instagram download
    logger.info(f"Running Instagram crawl... (with beginning id {id_counter})")
    try: 
        after_id = run_instagram_scrape(start_id=id_counter)
        logger.success(f"Successfully downloaded from Instagram; {after_id-id_counter} images.")
        id_counter = after_id
    except Exception as e:
        logger.error(f"Instagram crawl failed: {e}")

    # Run Pinterest download
    logger.info(f"Running Pinterest crawl... (with beginning id {id_counter})")
    try:
        after_id = run_pinterest_scrape(start_id=id_counter)
        logger.success(f"Successfully downloaded from Pinterest; {after_id-id_counter} images.")
        id_counter = after_id
    except Exception as e:
        logger.error(f"Pinterest crawl failed: {e}")

if __name__ == "__main__":
    managed_download()