from ai.preps.dblite import add_meme
from .DLutils import IndvImageURL, ImageDL, download_image
import urllib.request
import re
import json
from os import path
from selenium import webdriver
from typing import List

BOARDS_PATH = "boards.json"

def board_browser(board_url: str) -> List[str]:
    """
    Identify all post URLs in a given board with Selenium.
    """
    pass

def pin_saver(pin_url: str) -> IndvImageURL:
    """
    Access the pin, and save URLs for that image with Selenium.
    """
    pass

def acquire_urls(boards: List[str]) -> List[IndvImageURL]:
    """
    Acquire a list of all target images' URLs.
    """

    # Initialize lists
    pins = []
    urls = []

    # Iterate through boards
    for board in boards:
        pin_urls = board_browser(board_url=board)
        pins.extend(pin_urls)

    # Iterate through pins
    for pin in pins:
        image_url = pin_saver(pin_url=pin)
        urls.append(image_url)

    return urls

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