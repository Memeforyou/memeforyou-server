from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import os
from loguru import logger
from downloader.DLutils import download_image, ImageDL, IndvImageURL
from preps.dblite import add_meme, get_all_img_urls

ACCOUNTS = [
    'https://www.instagram.com/supermemememememememememe/',
    'https://www.instagram.com/moongo_moongo/',
    'https://www.instagram.com/wafterbw/'
]

def browse_account(
        driver: webdriver.Chrome,
        id_cursor: int,
        base_path: str,
        target_account_url: str = 'https://www.instagram.com/supermemememememememememe',
        max_scroll: int = 5
        ) -> int:

    driver.get(target_account_url)
    time.sleep(5)

    # --- De-duplication Setup ---
    # Get URLs from DB to avoid re-downloading
    db_urls = get_all_img_urls()
    # Use a set for efficient lookup of both DB and newly scraped URLs
    seen_urls = set(db_urls) 
    logger.trace(f"Loaded {len(db_urls)} existing URLs from the database for de-duplication.")

    urls = []

    # --- Scroll and Collect Post URLs ---
    scroll = 0
    scroll_attempts = 0
    while scroll <= max_scroll: # Limit scrolls to prevent infinite loops
        last_height = driver.execute_script("return document.body.scrollHeight")

        try:
            blocks = driver.find_elements(By.CSS_SELECTOR, 'div._ac7v.x1ty9z65.xzboxd6') #검색어에 따른 수정 필요
            for block in blocks:
                a_tags = block.find_elements(By.TAG_NAME, 'a')
                for a in a_tags:
                    post_url = a.get_attribute('href')
                    img_tag = a.find_element(By.TAG_NAME, 'img')
                    img_url = img_tag.get_attribute('src')
                    urls.append(
                        IndvImageURL(original_url=img_url, src_url=post_url)
                    )
                    
        except Exception as e:
            logger.error(f"Error collecting post URLs: {e}")
        
        # Scroll down
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3) # Wait for new content to load

        # Check if page height has changed
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            scroll_attempts += 1
            logger.info(f"Page height hasn't changed. Attempt {scroll_attempts}/3 before stopping.")
            if scroll_attempts >= 3:
                logger.info("Stopping scroll, no new content detected.")
                break
        else:
            scroll_attempts = 0 # Reset counter if new content is loaded

        scroll += 1

    logger.info(f"Finished collecting. Total unique post URLs to process: {len(urls)}")

    # --- Download Images from Collected URLs ---
    for indvurl in urls:
        try:
            img_url = indvurl.original_url
            post_url = indvurl.src_url

            if img_url in seen_urls:
                continue
            
            save_path = os.path.join(base_path, f"{id_cursor}.jpg")
            dl_response: ImageDL = download_image(url=img_url, save_path=save_path)

            if dl_response.success:
                add_meme(original_url=img_url, width=dl_response.width, height=dl_response.height, src_url=post_url)
                logger.info(f"[{id_cursor}] Saved {save_path} from {post_url}")
                id_cursor += 1

        except Exception as e:
            logger.error(f"Failed to process post {post_url}: {e}")

    return id_cursor, driver

def run_instagram_scrape(start_id: int, base_path: str, max_scroll: int = 5) -> int:
    id_cursor = start_id

    driver = webdriver.Chrome()
    driver.get('https://www.instagram.com/accounts/login/')
    input("Press enter when you're logged in & ready.")
    time.sleep(2)

    for account in ACCOUNTS:
        id_cursor, driver = browse_account(driver=driver, id_cursor=id_cursor, base_path=base_path, target_account_url=account, max_scroll=max_scroll)
        logger.trace(f"Account browser returned from {account}")
    
    driver.quit()
    logger.info("Instagram scraping done.")
    return id_cursor
