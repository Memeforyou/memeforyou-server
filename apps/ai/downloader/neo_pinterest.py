from preps.dblite import add_meme
from downloader.DLutils import IndvImageURL, ImageDL, download_image
import urllib.request
import re
import json
import time
from os import path
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from typing import List

# Path of the .json file containing target boards' URLs
BOARDS_PATH = "downloader/boards.json"
# How many times to scroll on a single board
SCRLIMIT = 15
# Define a unique locator for the sign-up/login pop-up.
POPUP_LOCATOR = (By.XPATH, "//div[@role='dialog']//button[text()='로그인']")

def board_browser(browser: webdriver.Chrome, board_url: str) -> List[IndvImageURL]:
    """
    Identify all raw image URLs in a given board with Selenium.
    """
    
    browser.get(board_url)
    
    # Log-in check
    try:
        # Check if the pop-up element is present within 10 seconds.
        WebDriverWait(browser, 5).until(
            EC.presence_of_element_located(POPUP_LOCATOR)
        )
        
        # If the element IS found (the pop-up exists):
        logger.warning("\n*** LOGIN POP-UP DETECTED ***")
        logger.warning("Please manually log in or dismiss the pop-up in the browser window.")
        logger.warning("Script execution paused. Press ENTER in the console when ready to continue...")
        
        # Pause the script and wait for user input
        input() 
        logger.info("Resuming script...")
        
    except Exception:
        # If the element is NOT found within 10 seconds, assume either 
        # the user is already logged in or the pop-up didn't appear.
        logger.info("Login pop-up not detected or dismissed.")

    logger.info(f"Started working on board: {board_url}")

    time.sleep(1.5)

    limit = SCRLIMIT

    while limit > 0:

        lastCount = browser.execute_script("return document.body.scrollHeight;")
        time.sleep(2)
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        lenOfPage = browser.execute_script("return document.body.scrollHeight;")
        limit -= 1

        if lastCount == lenOfPage:
            logger.info(f"Stopped scrolling for board: {board_url}.")
            break
        else:
            logger.trace("Scrolling...")

    img_list: List[IndvImageURL] = []
    base_domain: str = "https://kr.pinterest.com/"

    try:
        # Target the <a> tag that contains the link AND the image as its child
        # pin_link_elements = browser.find_elements(By.XPATH, f"//div[contains(@class, 'V3gVHw') and contains(@class, 'TfR6nu')]//a[starts-with(@href, '/pin/')]")
        pin_links = browser.find_elements(By.CSS_SELECTOR, "a[href^='/pin/']")

    except Exception as e:
        logger.error(f"Error finding pin link elements: {e}")
        return []
    
    logger.debug(f"Identified {len(pin_links)} pin link elements for board: {board_url}")

    for link in pin_links:
        try:
            # Full pin URL (Pinterest now returns absolute URLs)
            full_pin_url = link.get_attribute("href")

            # Thumbnail image inside this pin
            img_element = link.find_element(By.CSS_SELECTOR, "img.hCL.kVc.L4E.MIw")
            raw_thumbnail = img_element.get_attribute("src")

            # Convert thumbnail to original
            original_url = re.sub(r"/\d+x/", "/originals/", raw_thumbnail)

            img_list.append(
                IndvImageURL(original_url=original_url, src_url=full_pin_url)
            )
                
        except Exception:
            # Skip if an <a> tag is found but the expected <img> child is missing/malformed
            try:
                logger.error(f"Error with pin {link.get_attribute('href')}: {e}, skipping this pin.")
            except:
                pass
            continue

    logger.info(f"Done working with board: {board_url}, found {len(img_list)} images.")

    return img_list

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