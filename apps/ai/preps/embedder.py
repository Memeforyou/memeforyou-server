from utils.encoder_gemini import generate_embedding_gemini
from utils.schema import IndvVector
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

def embed_rows() -> List[IndvVector]:
    """
    Fetches 'CAPTIONED' memes, generates embeddings for their captions,
    and returns a list of IndvVector containing the image_id and its vector.
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

def upload_firestore(embeddings: List[IndvVector]) -> List[int]:

    processed_ids: List[int] = []
    if not PROJECT_ID:
        logger.error("GOOGLE_PROJECT_ID environment variable is not set.")
        return processed_ids

    try:

        # Connect to Firestore DB
        db = firestore.Client(project=PROJECT_ID, database=DB_ID)
        collection_ref = db.collection(COLLECTION_NAME)

        logger.success(f"Successfully connected to Firestore Project '{PROJECT_ID}' and Database '{DB_ID}'.")
        logger.info(f"Targeting collection: {COLLECTION_NAME}")

        batch = db.batch()
        batch_size = 500

        for i, item in enumerate(embeddings):

            # Check if vector field exists and is a list
            if item.get("vector") and isinstance(item["vector"], list):

                # Firestore Vector search requires the use of the Vector wrapper type
                vector_data = Vector(item["vector"])
                
                # Prepare the document data dictionary
                doc_id = str(item.get("image_id", f"doc_{i}"))
                
                document_data = {
                    "image_id": item.get("image_id"),
                    "vector": vector_data
                }
                processed_ids.append(item.get("image_id"))
                doc_ref = collection_ref.document(doc_id)
                batch.set(doc_ref, document_data)

                # Commit the batch if the limit is reached
                if (i + 1) % batch_size == 0:
                    batch.commit()
                    logger.info(f"Committed batch of {batch_size} documents (Total: {i + 1})")
                    batch = db.batch()
            else:
                logger.info(f"Skipping item {i}: 'vector' field is missing or invalid.")

        # Commit the final batch
        if batch._write_pbs: # Check if there are any remaining writes in the batch
            batch.commit()
            logger.info(f"Committed final batch (Total: {len(embeddings)})")

        logger.success("\nAll vector data successfully uploaded to Firestore.")
        return processed_ids

    except Exception as e:

        logger.error(f"Error during uploading vectors to Firestore: {e}")
        return processed_ids

def embedder_operation() -> None:

    embeddings = embed_rows()

    if embeddings:
        processed_ids = upload_firestore(embeddings)
    else:
        logger.warning("No embeddings to upload.")

    if processed_ids:
        update_ready(processed_ids)
    else:
        logger.warning("There are no processed_ids returned by upload_firestore.")

if __name__ == "__main__":
    embedder_operation()