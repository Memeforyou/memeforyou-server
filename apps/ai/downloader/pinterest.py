import os
import time
import json
import requests
import re
from loguru import logger
from dotenv import load_dotenv
from downloader.DLutils import download_image, ImageDL, IndvImageURL
from preps.dblite import add_meme, get_all_img_urls
from typing import List

load_dotenv()

# Config
API_KEY = os.getenv("CSE_API_KEY")
CX_ID = os.getenv("CX_ID")
    
# Google CSE Search
def search_pinterest_images(
        keywords: list[str],
        total_results: int = 200,
        date_restrict: str = "d90"
        ) -> List[IndvImageURL]:
    """
    Search Pinterest images via Google Custom Search API using keywords.
    """

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
            results.append(
                IndvImageURL(original_url=item.get("link"), src_url=item.get("image", {}).get("contextLink"))
                )

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
def run_pinterest_scrape(start_id: int, base_path: str, max: int = 50) -> int:
    """
    Orchestrate Pinterest download process via Google CSE,
    running each keyword separately.
    Returns updated next image id.
    """
    id_cursor = start_id
    keywords = ["밈", "웃긴 짤", "재밌는 짤", "유머 짤"]
    total_per_keyword = int(max / len(keywords))
    seen_urls = set()

    db_urls = get_all_img_urls()
    for url in db_urls:
        norm_prev_url = normalize_pin_url(url)
        seen_urls.add(norm_prev_url)
    logger.trace(f"Retrieved existing img urls and added to seen_urls.")

    logger.info(f"Searching Pinterest images for keywords: {keywords}...")

    for kw in keywords:
        logger.info(f"Running CSE query for keyword: {kw}")

        # Query each keyword independently
        search_results = search_pinterest_images([kw], total_results=total_per_keyword)
        logger.info(f"Keyword '{kw}' returned {len(search_results)} results.")

        for result in search_results:
            orig_url = result.original_url
            src_url = result.src_url

            if not orig_url:
                continue

            normalized = normalize_pin_url(orig_url)

            # Skip if already seen
            if normalized in seen_urls:
                continue
            seen_urls.add(normalized)

            # Convert thumbnail to original resolution URL
            full_res_url = re.sub(r"/\d+x\d*/", "/originals/", orig_url)

            # Set download path
            save_path = os.path.join(base_path, f"{id_cursor}.jpg")

            # Download accordingly
            dl_response: ImageDL = download_image(url=full_res_url, save_path=save_path)

            # If success, add row to prep DB
            if dl_response.success:
                logger.debug(f"Now trying add_meme")
                add_meme(
                    original_url=full_res_url,
                    width=dl_response.width,
                    height=dl_response.height,
                    src_url=src_url,
                )
                logger.info(f"[{id_cursor}] Saved {save_path} from {orig_url}")
                id_cursor += 1

            # Small sleep to respect API and rate limit safety
            time.sleep(0.1)

    return id_cursor

if __name__ == "__main__":
    # For standalone testing
    run_pinterest_scrape(start_id=1, base_path="./downloads")