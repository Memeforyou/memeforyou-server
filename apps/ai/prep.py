from google import genai
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import json
import time
from sentence_transformers import SentenceTransformer

load_dotenv()

client = genai.Client()

# Extract OCR, caption, and explain why this meme is funny. Return as JSON with keys {ocr, caption, humor}.
prompt = """
밈 이미지에 대해서 [OCR, 캡션, 이 밈이 재미있는 이유 설명]을 추출해. {ocr, caption, humor} 형식의 JSON으로 반환해.
"""

# Configs (Paths are for seeding purpose run)
metadata_output = "./seed/tmp/images.json"
embedding_model = "snunlp/KR-SBERT-V40K-klueNLI-augSTS"
embedding_output = "./seed/tmp/embeddings.json"

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
            prompt
        ],
        # Structured Response config
        config={
            "response_mime_type": "application/json",
            "response_schema": MemeMeta,
        },
    )

    return response.text

# Prep config, subject to change
imgpath = ""
batch_size = 100
max_total = None
sleep_sec = 0

# File setup, subject to change to accomodate Google Cloud Storage
files = [f for f in os.listdir(imgpath)]
if max_total is not None:
    files = files[:max_total]

# Loop for prep, subject to be made into a function for automation
for i in range(0, len(files), batch_size):

    batch = files[i:i+batch_size]
    print(f"Processing batch {i//batch_size+1}: {len(batch)} images.")
    results = {}

    batch_start = time.time()

    for fname in batch:
        path = os.path.join(imgpath, fname)
        try:
            result = process_image(path)
            results[fname] = json.loads(result)
        except Exception as e:
            print(f"Error with {fname}: {e}")
        time.sleep(sleep_sec)

    batch_time = time.time() - batch_start
    print(f"[Batch {batch_size}] completed in {batch_time:.1f}s")

    with open(f"metadata_batch_{i//batch_size + 1}.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)