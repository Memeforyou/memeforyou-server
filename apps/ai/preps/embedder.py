from ai.utils.encoder_gemini import generate_embedding_gemini
from .dblite import get_memes, update_ready
from google.cloud import firestore
from google.cloud.firestore_v1.vector import Vector
from loguru import logger
from dotenv import load_dotenv
from os import getenv
from typing import List, Dict, Any

load_dotenv()

COLLECTION_NAME = "embeddings_test"
DB_ID = "gdg-ku-meme4you-test"
PROJECT_ID = getenv("GOOGLE_PROJECT_ID")

db = firestore.Client(project=PROJECT_ID, database=DB_ID)

def embed_rows() -> List[Dict[str, Any]]:
    """
    Fetches 'CAPTIONED' memes, generates embeddings for their captions,
    and returns a list of dictionaries containing the image_id and its vector.
    """
    logger.info("Fetching 'CAPTIONED' memes for embedding...")
    target_rows = get_memes(status="CAPTIONED")

    if not target_rows:
        logger.warning("No memes with status 'CAPTIONED' found.")
        return []

    logger.info(f"Found {len(target_rows)} memes to embed.")

    # Prepare captions and corresponding image_ids for batch processing
    captions = [row['caption'] for row in target_rows]
    image_ids = [row['image_id'] for row in target_rows]

    # Generate embeddings in a single batch call
    embeddings = generate_embedding_gemini(texts=captions, task_type="RETRIEVAL_DOCUMENT")

    # Combine image_ids with their corresponding embeddings
    embedding_data = [{"image_id": image_id, "vector": vector} for image_id, vector in zip(image_ids, embeddings)]

    logger.success(f"Successfully generated {len(embedding_data)} embeddings.")
    return embedding_data