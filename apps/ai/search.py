import json
from google import genai
from google.cloud import firestore
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure
from google.cloud.firestore_v1.vector import Vector
from dotenv import load_dotenv
from loguru import logger
from utils.encoder import generate_embeddings
from utils.dbhandler import get_meta
from utils.schema import ImageTrivial, GeminiResponse
from typing import List, Optional

load_dotenv()

# Define clients & models
firestore_client = firestore.Client(database="gdg-ku-meme4you-test")
gemini_client = genai.Client()
firestore_collection = firestore_client.collection("embeddings_test")

# Config
metadata_dir = "./" # Remnant from local prototype
embedding_output = "meme_embeddings.json" # Remnant from local prototype

# Function for firebase vector search
def vsearch_fs(user_input: str, k: int = 5):

    ret = []

    user_input_embedding = generate_embeddings([user_input])[0]

    results = firestore_collection.find_nearest(
        vector_field="vector",
        query_vector=Vector(user_input_embedding),
        distance_measure=DistanceMeasure.COSINE,
        limit=k
    )

    for result in results.stream():
        ret.append(result)

    return ret

# Function to return the prompt for final Gemini selection
def get_prompt(cnt: int, images: List[ImageTrivial]):

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

def gemini_call(sys_prompt: str, user_prompt: str) -> Optional[GeminiResponse]:
    """
    Makes a structured content generation call to the Gemini API.
    """
    try:
        response = gemini_client.generate_content(
            model="gemini-1.5-flash", # Using a fast and capable model
            contents=[sys_prompt, user_prompt],
            generation_config={
                "response_mime_type": "application/json",
            },
        )
        # The API already returns a JSON string when configured this way.
        # We parse it and then validate with Pydantic.
        response_json = json.loads(response.text)
        return GeminiResponse.model_validate(response_json)
    except Exception as e:
        logger.error(f"Gemini API call failed: {e}")
        return None

# Function for final evaluation request to Gemini
async def final_eval(user_input: str, k: int = 10, final_cnt: int = 5) -> Optional[GeminiResponse]:
    """
    Orchestrates the final evaluation process:
    1. Vector search for initial candidates.
    2. Get metadata for candidates.
    3. Call Gemini for final ranking.
    """
    # 1. Get initial candidates from Firestore vector search
    vsearch_results = vsearch_fs(user_input=user_input, k=k)
    candidate_ids = [res.to_dict()['image_id'] for res in vsearch_results if 'image_id' in res.to_dict()]
    
    # 2. Get metadata (captions) for the candidates
    # Note: get_meta is an async function, but we'll call it synchronously for simplicity here.
    # In a real FastAPI app, this should be handled with `await`.
    candidate_images = await get_meta(candidate_ids)

    # 3. Prepare prompts and call Gemini
    sys_prompt, user_prompt = get_prompt(cnt=final_cnt, images=candidate_images)
    gemini_response = gemini_call(sys_prompt=sys_prompt, user_prompt=user_prompt)
    
    return gemini_response

# For testing
if __name__ == "__main__":

    logger.info("Script initiated.")

    while True:
        query = input("\nEnter search text (or 'exit' to quit): ").strip()
        if query.lower() == "exit":
            break
        result = final_eval(query)
        print(result)