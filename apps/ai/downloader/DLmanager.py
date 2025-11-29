import os
import json
from PIL import Image
from loguru import logger
from ai.downloader.instagram import run_instagram_crawl
from ai.downloader.pinterest import run_pinterest_crawl
from ai.preps.dblite import add_meme

BASE_DIR = os.path.dirname(__file__)
SAVE_DIR = os.path.join(BASE_DIR, "output")
INST_META_JSON = os.path.join(SAVE_DIR, "metadata_insta.json")
PIN_META_JSON = os.path.join(SAVE_DIR, "metadata_pin.json")

def load_metadata(meta_path: str):
    if not os.path.exists(meta_path):
        logger.warning(f"Metadata file not found: {meta_path}")
        return []
    with open(meta_path, "r", encoding="utf-8") as f:
        return json.load(f)

def register_metadata_to_db(save_dir: str, metadata: list[dict]):
    for item in metadata:
        fname = item.get("fname")
        original_url = item.get("original_url")
        src_url = item.get("src_url")

        if not fname or not original_url:
            continue

        img_path = os.path.join(save_dir, fname)
        if not os.path.exists(img_path):
            logger.warning(f"Image file not found: {img_path}")
            continue

        try:
            with Image.open(img_path) as img:
                width, height = img.size
        except Exception as e:
            logger.error(f"Failed to open image {img_path}: {e}")
            continue

        image_id = add_meme(
            original_url=original_url,
            img_path = img_path,
            width=width,
            height=height,
            src_url=src_url or ""
        )
        logger.info(f"Registered image_id={image_id}, file={img_path}")

def managed_download():

    # Initialize image_id counter for id assignment coordination
    # Indicates the id the next meme should be assigned
    id_counter = 1

    # Run instagram download
    logger.info(f"Running Instagram crawl... (with beginning id {id_counter})")
    try: 
        after_id = run_instagram_crawl(start_id=id_counter)
        logger.success(f"Successfully downloaded from Instagram; {after_id-id_counter} images.")
        id_counter = after_id
    except Exception as e:
        logger.error(f"Instagram crawl failed: {e}")

    # Run Pinterest download
    logger.info(f"Running Pinterest crawl... (with beginning id {id_counter})")
    try:
        after_id = run_pinterest_crawl(start_id=id_counter)
        logger.success(f"Successfully downloaded from Pinterest; {after_id-id_counter} images.")
        id_counter = after_id
    except Exception as e:
        logger.error(f"Pinterest crawl failed: {e}")

    # 2) 메타데이터 로드 + DB insert
    inst_meta = load_metadata(INST_META_JSON)
    logger.info(f"Loaded {len(inst_meta)} instagram metadata rows.")
    register_metadata_to_db(SAVE_DIR, inst_meta)

    # pin_meta = load_metadata(PIN_META_JSON)
    # logger.info(f"Loaded {len(pin_meta)} pinterest metadata rows.")
    # register_metadata_to_db(SAVE_DIR, pin_meta)

    logger.success("DLmanager processing completed.")

if __name__ == "__main__":
    managed_download()