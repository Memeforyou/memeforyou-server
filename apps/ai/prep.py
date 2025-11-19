from google import genai
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import json
import time
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
from PIL import Image
from loguru import logger

load_dotenv()

client = genai.Client()

# Extract OCR, caption, and explain why this meme is funny. Return as JSON with keys {ocr, caption, humor}.
PROMPT = """
밈 이미지에 대해서 [OCR, 캡션, 이 밈이 재미있는 이유 설명]을 추출해. {ocr, caption, humor} 형식의 JSON으로 반환해.
"""
EMBEDDING_MODEL = "snunlp/KR-SBERT-V40K-klueNLI-augSTS"

# Configs (Paths are for seeding purpose run)
METADATA_OUTPUT = "./seed/tmp/images.json"
EMBEDDING_OUTPUT = "./seed/tmp/embeddings.json"

# Define response format for Gemini Structured Response
class MemeMeta(BaseModel):
    ocr: str
    caption: str
    humor: str

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

    return response.text

def load_image_size(path: str):
    try:
        with Image.open(path) as img:
            return img.width, img.height
    except:
        return 0, 0

# Prep config, subject to change
imgpath = ""
batch_size = 100
max_total = None
sleep_sec = 0

# Function to return the list of image files in given directory. Subject to change for Google Cloud Storage integration
def load_files(imgpath: str, max_total: int = None) -> List[str]:

    # Check if path exists
    if not os.path.isdir(imgpath):
        logger.error(f"Directory not fount at {imgpath}")
        return []
    
    # List files that end with right extensions
    files = [f for f in os.listdir(imgpath) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]
    
    # Check max_total
    if max_total is not None:
        files = files[:max_total]
    
    logger.info(f"Found {len(files)} total image files to process.")
    return files

# Function to process batches
def process_batch(
        imgpath: str,
        batch_files: List[str],
        batch_index: int,
        prompt: str,
        sleep_sec: float = 0
) -> None:
    logger.info(f"\nProcessing batch {batch_index}: {len(batch_files)} images.")
    results = {}
    batch_start = time.time()

    for fname in batch_files:
        path = os.path.join(imgpath, fname)
        try:
            result = process_image(path, prompt)
            results[fname] = result
        except Exception as e:
            logger.info(f"Error with image {fname}: {e}.")

        if sleep_sec > 0:
            time.sleep(sleep_sec)
    
    batch_time = time.time() - batch_start
    logger.info(f"Batch {batch_index} completed in {batch_time:.1f}s.")

    # Save results for the current batch.
    # Currently for seeding purpose. To be integrated with Prisma Client.
    output_fname = f"metadata_batch_{batch_index}.json"
    with open(output_fname, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    logger.info(f"Results saved to {output_fname}")

def build_embeddings(meta_dir: str) -> None:
    pass

def main(
        imgpath: str,
        batch_size: int = 100,
        max_total: int = None,
        sleep_sec: float = 0
) -> None:
    
    files = load_files(imgpath, max_total)
    if not files:
        logger.error("No files to process. Exiting.")
        return
    
    for i in range(0, len(files), batch_size):
        batch = files[i:i+batch_size]
        batch_index = i // batch_size + 1

        process_batch(imgpath, batch, batch_index, PROMPT, sleep_sec)

    logger.complete("Caption processing complete.")

    if __name__ == "__main__":

        image_dir = "./.seed_images"

        main(image_dir, batch_size=30, max_total=None, sleep_sec=0.1)