from google import genai
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer

load_dotenv()

client = genai.Client()

# Final selection prompt
prompt = """
SOMEPROMPT
"""

# Config
metadata_dir = "./" # Remnant from local prototype
embedding_output = "meme_embeddings.json" # Remnant from local prototype
embedding_model = "all-MiniLM-L6-v2" # Subject to change for multilingual or Korean model
MODEL_PATH = "./models/"
top_n = 5

model = SentenceTransformer(embedding_model)

# Check if model exists locally and download if it is not
# Possibly subject to be moved to a seperate util module
if os.path.exists(MODEL_PATH) and True:
    pass
else:
    pass

# Function for cosine calculation
def cosine_similarity(a, b):
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    return float(np.dot(a, b))

# Function for building embedding file
# Currently for prototype, we need adapter for Prisma DB
# Subject to be moved to prep module altogether per purpose
def build_embeddings():
    all_items = []
    json_files = [f for f in os.listdir(metadata_dir) if f.startswith("metadata_batch_") and f.endswith(".json")]

    print(f"Found {len(json_files)} metadata batch files.")

    for fname in json_files:
        with open(os.path.join(metadata_dir, fname), "r", encoding="utf-8") as f:
            data = json.load(f)

        for img_name, content in data.items():
            combined_text = " ".join([
                content.get("ocr", ""),
                content.get("caption", ""),
                content.get("humor", "")
            ]).strip()

            if not combined_text:
                continue

            emb = model.encode(combined_text).astype(np.float32).tolist()

            all_items.append({
                "file": img_name,
                "text": combined_text,
                "embedding": emb
            })

    with open(embedding_output, "w", encoding="utf-8") as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)

    print(f"Embedded {len(all_items)} memes saved to {embedding_output}")

# Function for initial cosine search
def find_topn(query, top_n=top_n):

    # Identify embedding & open file
    # Currently for prototype; we need an adapter for Prisma DB
    if not os.path.exists(embedding_output):
        print("Embedding file not found. Run build_embeddings() first.")
        return
    with open(embedding_output, "r", encoding="utf-8") as f:
        memes = json.load(f)

    query_emb = model.encode(query)
    query_emb = query_emb / np.linalg.norm(query_emb)

    sims = []
    for m in memes:
        emb = np.array(m["embedding"], dtype=np.float32)
        emb = emb / np.linalg.norm(emb)
        sim = np.dot(query_emb, emb)
        sims.append((sim, m))

    sims.sort(key=lambda x: x[0], reverse=True)
    top_results = sims[:top_n]

    print(f"\nTop {top_n} similar memes for: \"{query}\"\n")
    for rank, (sim, m) in enumerate(top_results, 1):
        print(f"{rank}. {m['file']} — Similarity: {sim:.4f}")
        print(f"   Text: {m['text'][:150]}{'...' if len(m['text']) > 150 else ''}")
        print("-" * 60)

    # Return type shall be changed to properly return to main.py for API endpoint

# Function for final evaluation request to Gemini
def final_eval():
    pass

# For testing
if __name__ == "__main__":

    while True:
        query = input("\nEnter search text (or 'exit' to quit): ").strip()
        if query.lower() == "exit":
            break
        find_topn(query)