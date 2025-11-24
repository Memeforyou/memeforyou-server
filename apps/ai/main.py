# import search
from pydantic import BaseModel, Field
from fastapi import FastAPI
from typing import List
from loguru import logger
from search import final_eval
from utils.schema import InputData, FullRecReturn, IndvMemeReturn

# Initialize FastAPI app
app = FastAPI(title="memeforyou AI API - GDGoC KU 2025 worktree")

@app.post("/ai/similar",
          response_model=FullRecReturn,
          summary="Get top N ranked meme recommendation results.",
          description="")
async def search_meme(request: InputData):

    # Recommendation list; will call corresponding search.py function
    # for now, dummy data
    rec_list = [
        IndvMemeReturn(image_id=1, rank=1),
        IndvMemeReturn(image_id=2, rank=2),
        IndvMemeReturn(image_id=3, rank=3),
        IndvMemeReturn(image_id=4, rank=4),
        IndvMemeReturn(image_id=5, rank=5),
    ]

    search_response = await final_eval(request.text, request.count)

    # Construct return
    result = FullRecReturn(
        count=len(search_response.text),
        recommendations=search_response.text
    )

    return result