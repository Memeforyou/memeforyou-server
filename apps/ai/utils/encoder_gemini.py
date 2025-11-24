from google import genai
from google.genai import types
from loguru import logger
from typing import List, Optional
from dotenv import load_dotenv
import time
import numpy as np
from numpy.linalg import norm

load_dotenv()

gemini_client = genai.Client()

def generate_embedding_gemini(
    texts: List[str], 
    task_type: str = "retrieval_document",
    batch_size: int = 100
) -> List[List[float]]:
    """
    Generates embeddings for a list of texts using the Gemini API (models/embedding-001).
    It processes texts in batches and includes a retry mechanism.

    :param texts: List of input texts to embed.
    :param task_type: The task type for the embedding. See Gemini docs for options.
                      Defaults to "retrieval_document".
    :param batch_size: The number of texts to process in a single API call. Gemini's limit is 100.
    :return: A list of embedding vectors.
    :raises ValueError: If an invalid task_type is provided.
    """
    if gemini_client is None:
        logger.error("Gemini client is not initialized.")
        raise RuntimeError("Gemini client not initialized.")

    if not texts:
        logger.warning("Empty list of texts provided for Gemini embedding.")
        return []

    valid_task_types = [
        "RETRIEVAL_QUERY", "RETRIEVAL_DOCUMENT"
    ]
    if task_type not in valid_task_types:
        raise ValueError(f"Invalid task_type '{task_type}'. Must be one of {valid_task_types}")

    all_embeddings: List[List[float]] = []
    MAX_RETRIES = 2  # Total 3 attempts

    i = 0
    while i < len(texts):
        chunk = texts[i : i + batch_size]
        chunk_index = i // batch_size
        
        attempt = 0
        batch_success = False
        
        while attempt <= MAX_RETRIES:
            try:
                logger.debug(f"Gemini Batch #{chunk_index} Attempt #{attempt + 1}/{MAX_RETRIES + 1} (Size: {len(chunk)})")
                start_time = time.perf_counter()

                result = gemini_client.models.embed_content(
                    model="gemini-embedding-001",
                    contents=chunk,
                    config=types.EmbedContentConfig(task_type=task_type, output_dimensionality=768)
                )
                
                duration_ms = (time.perf_counter() - start_time) * 1000
                logger.debug(f"Gemini Batch #{chunk_index} success, took {duration_ms:.1f}ms")
                
                # Normalize embeddings for consistent similarity search, as per Gemini docs for dimensions != 3072
                for embedding in result.embeddings:
                    embedding_np = np.array(embedding.values)
                    # Calculate the L2 norm (magnitude) of the vector
                    norm_value = norm(embedding_np)
                    # Normalize the vector by dividing by its norm
                    normalized_embedding = embedding_np / norm_value
                    # Append the normalized vector (as a list) to our results
                    all_embeddings.append(normalized_embedding.tolist())

                batch_success = True
                break
            except Exception as e:
                attempt += 1
                if attempt <= MAX_RETRIES:
                    logger.warning(f"Gemini Batch #{chunk_index} failed (Attempt {attempt}/{MAX_RETRIES}): {e}. Retrying in 3s.")
                    time.sleep(3)
                else:
                    logger.error(f"Gemini Batch #{chunk_index} failed after {MAX_RETRIES + 1} attempts. Aborting.")
                    return all_embeddings
        
        if not batch_success:
            break

        i += batch_size

    logger.info(f"Successfully generated {len(all_embeddings)} embeddings using Gemini.")
    return all_embeddings

if __name__ == "__main__":
    # This block allows you to test the function by running `python -m apps.ai.utils.encoder_gemini`
    # from the memeforyou-server directory.
    # Make sure your GOOGLE_API_KEY is set in your environment or a .env file.
    import os

    if not os.getenv("GOOGLE_API_KEY"):
        logger.error("GOOGLE_API_KEY not found in environment. Please set it to run the test.")

    logger.info("--- Running Test for generate_embedding_gemini ---")
    
    test_texts = [
        "오늘 날씨가 정말 좋네요.",
        "배가 고픈데 점심 메뉴 추천해주세요.",
        "이 밈은 정말 웃기다!",
        "파이썬으로 코딩하는 것은 즐거워."
    ]

    logger.info(f"Input texts: {test_texts}")

    # Test with the default task_type
    embeddings = generate_embedding_gemini(test_texts, task_type="RETRIEVAL_DOCUMENT")
    # Test with a query task_type
    query_embedding = generate_embedding_gemini(["하나의 쿼리 문장"], task_type="RETRIEVAL_QUERY")

    if embeddings:
        logger.success(f"Successfully generated {len(embeddings)} embeddings.")
        logger.info(f"Shape of the first embedding vector: {len(embeddings[0])} dimensions.")
        logger.info("First embedding vector (first 5 values): " + str(embeddings[0][:5]))
    else:
        logger.error("Failed to generate embeddings.")
