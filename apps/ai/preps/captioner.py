from google import genai
from google.genai import types
from sqlite3 import Row
from ai.utils.schema import IndvCaption, BatchCaption
from .dblite import get_memes, update_captioned
from itertools import batched
from loguru import logger
from dotenv import load_dotenv
from os import getenv
from typing import List, Dict, Any

load_dotenv()

gemini_client = genai.Client()

SYSPROMPT = """
밈 이미지에 대해서 [OCR, 캡션, 이 밈이 재미있는 이유 설명]과 [태그]들을 추출해.
이때, 태그는 아래 제시될 정해져 있는 태그 목록에서만 2~4개를 선택해야 해.
제시된 json 스키마에 따라서 반환해.
"""
AVAIL_TAGS = ["웃긴", "슬픈", "귀여운", "동물", "사람", "카툰", "캐릭터"]

def gemini_caption(sys_prompt: str, available_tags: List[str], img_path: str) -> IndvCaption:
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

def caption_rows(target_rows: list) -> List[IndvCaption]:
    """
    Generates captions for input rows of memes,
    and returns a list of IndvCaption containing the image_id, caption, and tags.
    """

    captioned_rows = []

    # Perform gemini_caption on provided batch
    pass

    return captioned_rows

def captioner_operation() -> None:

    captioned_rows = caption_rows()

    if captioned_rows:
        update_captioned()
    else:
        logger.warning("No captioned rows returned by caption_rows.")

if __name__ == "__main__":
    captioner_operation()