from google import genai
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import json
import time
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
from ai.utils.schema import MemeMeta
from PIL import Image
from loguru import logger

load_dotenv()

client = genai.Client()

# Extract OCR, caption, and explain why this meme is funny. Return as JSON with keys {ocr, caption, humor}.
PROMPT = """
밈 이미지에 대해서 [OCR, 캡션, 이 밈이 재미있는 이유 설명]을 추출해. {ocr, caption, humor} 형식의 JSON으로 반환해.
"""

# Configs (Paths are for seeding purpose run)
METADATA_OUTPUT = "./.seed_json_tmp/images.json"
EMBEDDING_OUTPUT = "./.seed_json_tmp/embeddings.json"
IMAGE_DIR = "./.seed_images"

EMBEDDING_MODEL = "snunlp/KR-SBERT-V40K-klueNLI-augSTS"
MODEL_ROOT = "./.models"

# ensure root cache dir exists
os.makedirs(MODEL_ROOT, exist_ok=True)

# local folder name for the model (replace "/" with "__")
LOCAL_MODEL_DIR = os.path.join(MODEL_ROOT, EMBEDDING_MODEL.replace("/", "__"))

# download once if missing, otherwise load from disk
if not os.path.exists(LOCAL_MODEL_DIR):
    logger.warning(f"Model not found locally. Downloading {EMBEDDING_MODEL} ...")
    model_tmp = SentenceTransformer(EMBEDDING_MODEL)   # this downloads from HF
    model_tmp.save(LOCAL_MODEL_DIR)                    # persist to local cache
    logger.success(f"Model downloaded and saved to: {LOCAL_MODEL_DIR}")
else:
    logger.info(f"Loading embedding model from local cache: {LOCAL_MODEL_DIR}")

# load model once (from local path)
embedding_model = SentenceTransformer(LOCAL_MODEL_DIR)
logger.info("Embedding model ready.")

# Function for query per image
def process_image(img_path):

    # Open subject meme image: subject to change depending on image feed method
    with open(img_path, 'rb') as f:
        image_bytes = f.read()

    # Request to Gemini with image input and prompt
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            genai.types.Part.from_bytes(
                data=image_bytes,
                mime_type='image/jpeg'
            ),
            PROMPT
        ],
        # Structured Response config
        config={
            "response_mime_type": "application/json",
            "response_schema": MemeMeta,
        },
    )

    return json.loads(response.text)

def load_image_size(path: str):
    try:
        with Image.open(path) as img:
            return img.width, img.height
    except:
        return 0, 0

def process_item_with_retry(item: Dict[str, Any], img_dir: str, max_retries: int = 3) -> bool:
    """
    Processes a single item, attempting up to max_retries times.
    Returns True on success, False on failure.
    """
    image_id = item["image_id"]

    # Try multiple possible extensions
    img_path = None
    for ext in ("jpg", "jpeg", "png", "webp"):
        p = os.path.join(img_dir, f"{image_id}.{ext}")
        if os.path.exists(p):
            img_path = p
            break
    
    if img_path is None:
        logger.warning(f"Image file for id {image_id} not found.")
        return True # Treat as success to skip this item (no image found)

    for attempt in range(1, max_retries + 1):
        logger.trace(f"Processing image_id={image_id}, attempt {attempt}/{max_retries}")
        try:
            meta = process_image(img_path)

            combined_caption = " ".join([
                meta.get("ocr", ""),
                meta.get("caption", ""),
                meta.get("humor", "")
            ]).strip()

            item["caption"] = combined_caption

            # Fill width/height
            w, h = load_image_size(img_path)
            item["width"] = w
            item["height"] = h

            logger.trace(f"Successfully processed image_id={image_id} on attempt {attempt}.")
            return True # Success

        except Exception as e:
            logger.warning(f"Gemini error for {image_id} on attempt {attempt}: {e}")
            if attempt < max_retries:
                # Incremental sleep: 2 seconds, 4 seconds, 8 seconds...
                sleep_time = 2 ** attempt
                logger.info(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                logger.error(f"Failed to process image_id={image_id} after {max_retries} attempts.")
                return False # Final failure
    
    return False # Should be unreachable, but here for completeness

# Function to process the caption filling
def run_caption_filling(img_dir: str, max_total: int = None, sleep_sec: float = 0.2):
    if not os.path.exists(METADATA_OUTPUT):
        logger.error("images.json not found.")
        return

    with open(METADATA_OUTPUT, "r", encoding="utf-8") as f:
        items = json.load(f)

    logger.info(f"Loaded {len(items)} entries from images.json")

    processed = 0
    items_to_process = []
    
    # 1. Identify items needing processing
    for item in items:
        # Skip already-filled items
        if item.get("caption", "").strip():
            continue
        items_to_process.append(item)

    logger.info(f"Found {len(items_to_process)} items needing caption filling.")

    # 2. Main processing loop
    failed_items_round_1 = []
    
    for i, item in enumerate(items_to_process):
        if max_total is not None and processed >= max_total:
            break
        
        # We pass the mutable 'item' dictionary directly. If successful, it's updated.
        success = process_item_with_retry(item, img_dir)

        if success:
            processed += 1
        else:
            # If process_item_with_retry returns False, the item failed after all attempts
            failed_items_round_1.append(item)
            
        if sleep_sec > 0 and (success or not success):
            time.sleep(sleep_sec)

    logger.info(f"--- Round 1 complete. Processed: {processed}, Failed: {len(failed_items_round_1)} ---")
    
    # 3. Process failed items (Round 2)
    processed_round_2 = 0
    failed_items_round_2 = []
    
    if failed_items_round_1:
        logger.info(f"Starting Round 2 for {len(failed_items_round_1)} failed items.")
        
        for i, item in enumerate(failed_items_round_1):
            # Give failed items another full set of retry attempts
            success = process_item_with_retry(item, img_dir)
            
            if success:
                processed_round_2 += 1
                processed += 1 # Update total processed count
            else:
                failed_items_round_2.append(item)
                
            if sleep_sec > 0:
                # Add a small delay between retries
                time.sleep(sleep_sec)
                
        logger.info(f"--- Round 2 complete. Successfully processed: {processed_round_2}, Still failed: {len(failed_items_round_2)} ---")


    # 4. Save updated images.json
    with open(METADATA_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

    logger.success(f"Updated captions for a total of {processed} items across all rounds.")
    if failed_items_round_2:
        failed_ids = [item['image_id'] for item in failed_items_round_2]
        logger.error(f"Final failure count: {len(failed_items_round_2)}. IDs: {failed_ids}")

def build_embeddings():
    if not os.path.exists(METADATA_OUTPUT):
        logger.error("images.json missing.")
        return

    with open(METADATA_OUTPUT, "r", encoding="utf-8") as f:
        items = json.load(f)

    logger.info("Building embeddings for caption-filled items...")

    output = []

    for item in items:
        caption = item.get("caption", "").strip()
        if not caption:
            continue

        emb = embedding_model.encode(caption).astype(np.float32).tolist()

        output.append({
            "image_id": item["image_id"],
            "vector": emb
        })

    with open(EMBEDDING_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    logger.success(f"Saved {len(output)} embeddings to {EMBEDDING_OUTPUT}")

if __name__ == "__main__":

    logger.info("Initiating script...")

    #run_caption_filling(
    #    img_dir=IMAGE_DIR,
    #    max_total=None,
    #    sleep_sec=0.2
    #)

    logger.success("Caption filling complete, moving onto building embeddings...")

    build_embeddings()