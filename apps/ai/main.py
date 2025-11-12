# import search
from pydantic import BaseModel
from fastapi import FastAPI
from typing import List

# Initialize FastAPI app
app = FastAPI(title="memeforyou AI API - GDGoC KU 2025 worktree")

# User input data class
class InputData(BaseModel):
    text: str
    count: int

# Individual meme to be included in full response
class IndvRec(BaseModel):
    image_id: int
    rank: int

# Full response class definition
class FullRecReturn(BaseModel):
    count: int
    recommendations: list["IndvRec"]

@app.post("/search",
          response_model=FullRecReturn,
          summary="Get top N ranked meme recommendation results.",
          description="")
async def search_meme(request: InputData):

    # Recommendation list; will call corresponding search.py function
    # for now, dummy data
    rec_list = [
        IndvRec(image_id=1, rank=1),
        IndvRec(image_id=2, rank=2),
        IndvRec(image_id=3, rank=3),
        IndvRec(image_id=4, rank=4),
        IndvRec(image_id=5, rank=5),
    ]

    # Construct return
    result = FullRecReturn(
        count=len(rec_list),
        recommendations=rec_list
    )

    return result