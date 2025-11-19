import os
import io
import time
import json
import requests
from loguru import logger
from PIL import Image
from hashlib import sha1
from dotenv import load_dotenv

load_dotenv()

# Config
API_KEY = os.getenv("CSE_API_KEY")
CX_ID = os.getenv("CX_ID")
# Paths for seeding purpose run
SAVE_DIR = "./.output_google"
META_JSON = "./.output_google/metadata.json"

# Hash function for image
def average_hash(image: Image.Image, hash_size: int = 8) -> str:
    """Compute a perceptual hash (average hash) of a PIL image."""
    image = image.convert("L").resize((hash_size, hash_size), Image.LANCZOS)
    pixels = list(image.getdata())
    avg = sum(pixels) / len(pixels)
    bits = "".join("1" if p > avg else "0" for p in pixels)
    return f"{int(bits, 2):0{hash_size**2 // 4}x}"

# Download image
def download_image(url: str, save_dir: str = SAVE_DIR):
    """
    Download image, save with temporary hash-based filename while preserving original extension.
    Returns (filename, hash) or (None, None) on failure.
    """
    os.makedirs(save_dir, exist_ok=True)
    try:
        resp = requests.get(url, stream=True, timeout=10)
        resp.raise_for_status()
        img_bytes = io.BytesIO(resp.content)
        image = Image.open(img_bytes)
        img_hash = average_hash(image)

        # Get original image format and convert to lower-case extension
        ext = image.format.lower()
        filename = os.path.join(save_dir, f"{img_hash}.{ext}")
        image.save(filename)
        return filename, img_hash
    except Exception as e:
        logger.error(f"Failed to download {url}: {e}")
        return None, None
    
# Google CSE Search
def search_pinterest_images(keywords: list[str], total_results: int = 50, date_restrict: str = "d90"):
    """Search Pinterest images via Google Custom Search API using OR keywords."""

    # Check env is in place
    if not API_KEY or not CX_ID:
        raise EnvironmentError("CSE_API_KEY and CX_ID must be set in env variables.")

    # Initiate list to hold results
    results = []

    # Query configs
    search_query = f"site:pinterest.com ({' OR '.join(f'\"{kw}\"' for kw in keywords)})"
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

# Main pipeline
def main():
    keywords = ["밈", "웃긴 짤", "재밌는 짤", "유머 짤"]
    total_per_keyword = 50
    seen_urls = set()
    seen_hashes = set()
    metadata_list = []

    logger.info(f"Searching Pinterest images for keywords: {keywords}...")
    search_results = search_pinterest_images(keywords, total_results=total_per_keyword)
    logger.info(f"found {len(search_results)} results.")

    for idx, result in enumerate(search_results, start=1):
        #if len(metadata_list) >= max_results:
        #    break
        orig_url = result.get("original_url")
        src_url = result.get("src_url")

        if not orig_url or orig_url in seen_urls:
            continue
        seen_urls.add(orig_url)

        filename, img_hash = download_image(orig_url)
        if not filename or img_hash in seen_hashes:
            if filename:
                os.remove(filename)
            continue
        seen_hashes.add(img_hash)

        metadata_list.append({
            "id": idx,
            "original_url": orig_url,
            "src_url": src_url
        })

        logger.info(f"[{idx}] Saved {filename} from {orig_url}")

    # Save metadata JSON for seeding
    os.makedirs(os.path.dirname(META_JSON), exist_ok=True)
    with open(META_JSON, "w", encoding="utf-8") as f:
        json.dump(metadata_list, f, ensure_ascii=False, indent=2)

    logger.info(f"\nSaved {len(metadata_list)} unique images locally in '{SAVE_DIR}'.")
    logger.info(f"Metadata JSON saved to '{META_JSON}'.")

if __name__ == "__main__":
    main()