from google import genai
from google.genai import types
from sqlite3 import Row
from utils.schema import IndvCaption, BatchCaption
from .dblite import get_memes, update_captioned
from itertools import batched
from loguru import logger
from dotenv import load_dotenv
from os import getenv, path
from typing import List, Tuple, Dict, Any

load_dotenv()

gemini_client = genai.Client()

SYSPROMPT = """
밈 이미지에 대해서 [OCR, 캡션, 이 밈이 재미있는 이유 설명]과 [태그]들을 추출해.
이때, 태그는 아래 제시될 정해져 있는 태그 목록에서만 2~4개를 선택해야 해.
제시된 json 스키마에 따라서 반환해.
"""
AVAIL_TAGS = ["웃긴", "슬픈", "귀여운", "동물", "사람", "카툰", "캐릭터"]
BPATH = "./downloads/"

def gemini_caption(sys_prompt: str, available_tags: List[str], img_id: int, img_path: str) -> IndvCaption:
    """
    Makes a structured content generation call to the Gemini API.
    """

    # Open subject meme image
    with open(img_path, 'rb') as f:
        image_bytes = f.read()

    # Define config for sys_prompt and structured response
    config = types.GenerateContentConfig(
        system_instruction=sys_prompt,
        response_mime_type="application/json",
        response_schema=IndvCaption
    )

    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                f"이용 가능한 태그 목록: {', '.join(available_tags)}",
                f"이번 이미지의 image_id: {img_id}",
                genai.types.Part.from_bytes(
                data=image_bytes,
                mime_type='image/jpeg'
            )],
            config=config
        )
        # Parse the JSON string into our Pydantic model.
        if response.text:
            parsed_response = IndvCaption.model_validate_json(response.text)
            return parsed_response
        else:
            logger.error(f"Gemini response parsing failed.")
            return None
        
    except Exception as e:
        logger.error(f"Gemini API call failed: {e}")
        return None
    
def fetch_and_batch(n: int = 100) -> List[List[Row]]:
    """
    Fetches 'PENDING' memes, and puts them into batches for fail-safe captioning.
    """

    logger.info("Fetching 'PENDING' memes for embedding...")
    target_rows = get_memes(status="PENDING")

    if not target_rows:
        logger.warning("No memes with status 'PENDING' found.")
        return []
    
    logger.info(f"Found {len(target_rows)} memes to caption. Now batching...")

    batches = [list(batch) for batch in batched(target_rows, n)]

    return batches

def caption_rows(target_rows: list, base_path: str) -> List[IndvCaption]:
    """
    Generates captions for input rows of memes,
    and returns a list of IndvCaption containing the image_id, caption, and tags.
    """

    # Initialize update list
    local_captioned_rows = []

    # Identify batch range for logging purposes
    first_meme_id = target_rows[0]['image_id']
    last_meme_id = target_rows[-1]['image_id']
    logger.debug(f"Captioning this batch: {first_meme_id} to {last_meme_id}...")

    # Perform gemini_caption on provided batch
    for i, row in enumerate(target_rows):

        # Acquire filename based on iteration
        image_id = row['image_id']
        fname = str(image_id)+'.jpg'
        img_path = path.join(base_path, fname)

        logger.trace(f"Acquired file path for {i}th image in this batch: ...{fname}. Now requesting...")

        res = gemini_caption(sys_prompt=SYSPROMPT, available_tags=AVAIL_TAGS, img_id=image_id, img_path=img_path)
        if res:
            local_captioned_rows.append(res)
            logger.trace(f"{i}th image in this batch captioned and appended to return.")
        else:
            logger.warning(f"Skipping meme ID {image_id} in batch {first_meme_id}-{last_meme_id} due to captioning failure.")

    return local_captioned_rows

def caption_converter(before_rows: List[IndvCaption]) -> Tuple[List[int], List[str], List[List[str]]]:
    """
    Convert the list of IndvCaption into updater compatible format
    """

    ids: List[int] = []
    captions: List[str] = []
    tags: List[List[str]] = []

    for row in before_rows:
        ids.append(row.image_id)
        # Combine ocr, caption, and humor into a single string for the database
        full_caption = f"OCR: {row.ocr}, Caption: {row.caption}, Humor: {row.humor}"
        captions.append(full_caption)
        tags.append(row.tags)

    return ids, captions, tags


def captioner_operation() -> None:
    """
    Overall captioner pipeline.
    """
    # Acquire batches
    batches = fetch_and_batch()

    # Iterate through batches
    for i, batch in enumerate(batches):
        
        logger.info(f"Processing Batch {i+1}/{len(batches)} ---")
        this_batch_captions = caption_rows(target_rows=batch, base_path=BPATH)

        if this_batch_captions:
            # Convert and update the database for this batch
            image_ids, captions, tags_list = caption_converter(before_rows=this_batch_captions)
            update_captioned(image_ids=image_ids, captions=captions, tags_list=tags_list)
            logger.success(f"Successfully updated {len(image_ids)} memes in the database for batch {i+1}.")
        else:
            logger.warning(f"No rows were successfully captioned in batch {i+1}. Nothing to update.")

if __name__ == "__main__":
    captioner_operation()