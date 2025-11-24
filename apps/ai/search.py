import asyncio
from google import genai
from google.genai import types
from google.cloud import firestore
from google.cloud.firestore_v1.document import DocumentSnapshot
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure
from google.cloud.firestore_v1.vector import Vector
from dotenv import load_dotenv
from loguru import logger
from utils.encoder_gemini import generate_embedding_gemini
from utils.dbhandler import get_meta
from utils.schema import ImageTrivial, GeminiResponse
from typing import List, Optional, Tuple

load_dotenv()

# Define clients & models
firestore_client = firestore.Client(database="gdg-ku-meme4you-test")
gemini_client = genai.Client()
firestore_collection = firestore_client.collection("embeddings_test")

# Config
metadata_dir = "./" # Remnant from local prototype
embedding_output = "meme_embeddings.json" # Remnant from local prototype

# Function for firebase vector search
def vsearch_fs(user_input: str, k: int = 5) -> List[DocumentSnapshot]:

    ret = []

    # Embed the user's query using the 'retrieval_query' task type for optimal search performance
    user_input_embedding = generate_embedding_gemini(
        texts=[user_input], task_type="RETRIEVAL_QUERY"
    )[0]

    logger.info("Embedding acquired. Now performing vector search...")

    results = firestore_collection.find_nearest(
        vector_field="vector",
        query_vector=Vector(user_input_embedding),
        distance_measure=DistanceMeasure.COSINE,
        limit=k
    )

    if results:
        logger.success("Vector search complete.")

    for result in results.stream():
        ret.append(result)
    #logger.debug(f"Vector search results: {ret}")

    return ret

# Function to return the prompt for final Gemini selection
def get_prompt(cnt: int, images: List[ImageTrivial]) -> Tuple[str, str]:

    sys_prompt = f"""
너는 이용자의 상황에 딱 맞는 밈을 추천해주는데 통달한 유머러스하고 재치있는 조언자야.

제시된 후보 밈 중에서, 이용자의 상황 및 맥락에 가장 적절하게 적용될 수 있는 밈 상위 {cnt}개를 선정해.
선정한 {cnt}개의 밈을 가장 적절한 순서대로 아래 JSON 형식으로 반환해.

{{"text": [
    {{"image_id": <id of the best fitting meme image>}},
    {{"image_id": <id of the second best fitting meme image>}},
    ...,
    {{"image_id": <id of the {cnt}th best fitting meme image>}}
]}}
"""
    
    # Format the candidate images into a string for the user prompt
    candidates_list = []
    for img in images:
        # Using a simple, readable format for the model
        candidates_list.append(
            f"후보 밈:\n- ID: {img.image_id}\n- 설명: {img.caption}\n"
        )
    
    candidates_str = "---\n" + "\n".join(candidates_list)

    return sys_prompt, candidates_str

# Function for final evaluation request to Gemini
def gemini_call(sys_prompt: str, user_prompt: str) -> Optional[GeminiResponse]:
    """
    Makes a structured content generation call to the Gemini API.
    """

    config = types.GenerateContentConfig(
        system_instruction=sys_prompt,
        response_mime_type="application/json",
        response_schema=GeminiResponse
    )

    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[sys_prompt, user_prompt],
            config=config
        )
        # The response.text is a JSON string. We need to parse it into our Pydantic model.
        if response.text:
            parsed_response = GeminiResponse.model_validate_json(response.text)
            return parsed_response
        else:
            logger.error(f"Gemini response parsing failed.")
            return None
    except Exception as e:
        logger.error(f"Gemini API call failed: {e}")
        return None

# Overall rec pipeline
async def final_eval(user_input: str, k: int = 10, final_cnt: int = 5) -> Optional[GeminiResponse]:
    """
    user_input: user's natural language input
    k: vector search candidate numbers
    final_cnt: number of final recommendations to return

    Orchestrates the final evaluation process:
    1. Vector search for initial candidates.
    2. Get metadata for candidates.
    3. Call Gemini for final ranking.
    """
    # Get initial candidates from Firestore vector search
    vsearch_results = vsearch_fs(user_input=user_input, k=k)
    candidate_ids = [res.to_dict()['image_id'] for res in vsearch_results if 'image_id' in res.to_dict()]
    logger.info("Vector search complete.")
    logger.debug(f"Candidate IDs: {candidate_ids}")

    # Get metadata (captions) for the candidates
    # Note: get_meta is an async function, but we'll call it synchronously for simplicity here.
    # In a real FastAPI app, this should be handled with `await`.
    candidate_images = await get_meta(candidate_ids)
    logger.info("Metadata retrieval for candidates complete.")

    # Prepare prompts and call Gemini
    sys_prompt, user_prompt = get_prompt(cnt=final_cnt, images=candidate_images)
    logger.info("Prompt ready. Now calling Gemini...")
    gemini_response = gemini_call(sys_prompt=sys_prompt, user_prompt=user_prompt)
    logger.success("Final evaluation complete.")
    
    return gemini_response

# For testing
if __name__ == "__main__":

    logger.info("Script initiated.")

    while True:
        query = input("\nEnter search text (or 'exit' to quit): ").strip()
        if query.lower() == "exit":
            break
        result = asyncio.run(final_eval(query))
        print(result)