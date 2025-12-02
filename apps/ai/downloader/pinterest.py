import os
import time
import json
import requests
import re
from loguru import logger
from dotenv import load_dotenv
from downloader.DLutils import download_image, ImageDL
from preps.dblite import add_meme

load_dotenv()

# Config
API_KEY = os.getenv("CSE_API_KEY")
CX_ID = os.getenv("CX_ID")
    
# Google CSE Search
def search_pinterest_images(keywords: list[str], total_results: int = 50, date_restrict: str = "d90"):
    """Search Pinterest images via Google Custom Search API using OR keywords."""

    # Check env is in place
    if not API_KEY or not CX_ID:
        raise EnvironmentError("CSE_API_KEY and CX_ID must be set in env variables.")

    # Initiate list to hold results
    results = []

    # Query configs
    search_query = f"site:pinterest.com ({" ".join(keywords)})"
    logger.debug(f"search_query: {search_query}")
    url = "https://www.googleapis.com/customsearch/v1"
    start = 1

    # Query loop
    while len(results) < total_results:
        params = {
            "key": API_KEY,
            "cx": CX_ID,
            "q": search_query,
            "searchType": "image",
            "num": min(10, total_results - len(results)),
            "start": start,
            "dateRestrict": date_restrict
        }

        # Three attempts
        for attempt in range(3):
            try:
                resp = requests.get(url, params=params, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                break
            except Exception as e:
                logger.error(f"Request failed (attempt {attempt+1}): {e}")
                time.sleep(2)
        else:
            logger.error(f"Skipping page after 3 failed attempts.")
            break

        items = data.get("items", [])
        if not items:
            break

        # Append to results
        for item in items:
            results.append({
                "original_url": item.get("link"),
                "src_url": item.get("image", {}).get("contextLink")
            })

        # Iterate with sleep interval
        start += len(items)
        time.sleep(0.3)
        if "nextPage" not in data.get("queries", {}):
            break

    return results

def normalize_pin_url(url: str):
    """
    Normalizes url for clean de-dup (seen_urls)
    
    :param url: URL to normalize
    :type url: str
    """
    # remove tracking parameters
    url = url.split("?")[0]
    # convert thumbnails to originals
    url = re.sub(r"/\d+x\d*/", "/originals/", url)
    return url

# Main pipeline
def run_pinterest_scrape(start_id: int, base_path: str) -> int:
    """
    Orchestrate pinterest download process via Google CSE, and returns updated next image id.
    """
    id_cursor = start_id
    keywords = ["밈", "웃긴 짤", "재밌는 짤", "유머 짤"]
    total_per_keyword = 50
    seen_urls = set()

    logger.info(f"Searching Pinterest images for keywords: {keywords}...")
    search_results = search_pinterest_images(keywords, total_results=total_per_keyword)
    logger.info(f"found {len(search_results)} results.")

    for idx, result in enumerate(search_results, start=1):
        orig_url = result.get("original_url")
        src_url = result.get("src_url")

        if not orig_url or normalize_pin_url(orig_url) in seen_urls:
            continue
        seen_urls.add(normalize_pin_url(orig_url))

        # Convert thumbnail to original resolution URL
        full_res_url = re.sub(r"/\d+x\d*/", "/originals/", orig_url)

        # Set download path
        save_path = os.path.join(base_path, f"{id_cursor}.jpg")

        # Download accordingly
        dl_response: ImageDL = download_image(url=full_res_url, save_path=save_path)

        # If success, add row to prep DB
        if dl_response.success:
            add_meme(original_url=full_res_url, width=dl_response.width, height=dl_response.height, src_url=src_url)
            logger.info(f"[{idx}] Saved {save_path} from {orig_url}")
            id_cursor += 1

    return id_cursor

if __name__ == "__main__":
    # For standalone testing
    run_pinterest_scrape(start_id=1, base_path="./downloads")