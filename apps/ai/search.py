from google import genai
from google.cloud import firestore
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure
from google.cloud.firestore_v1.vector import Vector
from dotenv import load_dotenv
from loguru import logger
from apps.ai.utils.encoder import generate_embeddings
from typing import List, Optional
from apps.ai.utils.schema import ImageTrivial

load_dotenv()

# Define clients
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

    prompt = f"""
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
    
    candidates_str = ""
    
    return prompt

def gemini_call(prompt: str):
    pass

# Function for final evaluation request to Gemini
def final_eval(user_input: str):

    init_candidates_id: List[int] = vsearch_fs(user_input=user_input)

    pass

# For testing
if __name__ == "__main__":

    while True:
        query = input("\nEnter search text (or 'exit' to quit): ").strip()
        if query.lower() == "exit":
            break
        vsearch_fs(query)