from ai.preps.dblite import add_meme
from .DLutils import IndvImageURL, ImageDL, download_image
import urllib.request
import re
import json
import time
from os import path
from loguru import logger
from selenium import webdriver
from typing import List

# Path of the .json file containing target boards' URLs
BOARDS_PATH = "boards.json"
# How many times to scroll on a single board
SCRLIMIT = 15

def board_browser(browser: webdriver.Chrome, board_url: str) -> List[IndvImageURL]:
    """
    Identify all raw image URLs in a given board with Selenium.
    """
    
    browser.get(board_url)

    time.sleep(1.5)

    limit = SCRLIMIT

    while limit > 0:

        lastCount = browser.execute_script("return document.body.scrollHeight;")
        time.sleep(3)
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        lenOfPage = browser.execute_script("return document.body.scrollHeight;")
        limit -= 1

        if lastCount == lenOfPage:
            logger.info(f"Stopped scrolling for board: {board_url}.")
            break
        else:
            logger.trace("Scrolling...")

    response = browser.page_source

    # Find all urls in the page source with regex
    all_urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', response)

    img_list: List[IndvImageURL] = []

    for url in all_urls:

        pass

def acquire_urls(boards: List[str]) -> List[IndvImageURL]:
    """
    Acquire a list of all target images' URLs.
    """

    # Initialize browser
    browser = webdriver.Chrome()

    # Initialize list
    img_urls: List[IndvImageURL] = []

    # Iterate through boards
    try:
        for board in boards:
            img_urls.extend(board_browser(browser=browser, board_url=board))
    except Exception as e:
        logger.error(f"Exception {e} during scraping board {board}.")

    return img_urls

def run_pinterest_scrape(start_id: int, base_path: str) -> int:
    """
    Orchestrate pinterest download process, and returns updated next image id.
    """

    # Initialize id counter
    id_cursor: int = start_id

    # Open and read preset boards
    with open(BOARDS_PATH, 'r') as f:
        boards = json.load(f)['boards']

    # Acquire all individual URLs for pins
    urls: List[IndvImageURL] = acquire_urls(boards=boards)

    # Perform download
    for url in urls:

        # Parse raw image URL
        raw_image_url = url['original_url']

        # Set download path
        save_path = path.join(base_path, f"{id_cursor}.jpg")

        # Download accordingly
        dl_response: ImageDL = download_image(url=raw_image_url, save_path=save_path)

        # If success, add row to prep DB
        if dl_response['success']:
            add_meme(original_url=raw_image_url, width=dl_response['width'], height=dl_response['height'], src_url=url['src_url'])
            id_cursor += 1

    return id_cursor

if __name__ == "__main__":
    run_pinterest_scrape(start_id=1)