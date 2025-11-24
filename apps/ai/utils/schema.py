from pydantic import BaseModel
from typing import List

# --- Models for prep
class MemeMeta(BaseModel):
    ocr: str
    caption: str
    humor: str
    tags: List[str]

# --- Models for search inference
class IndvMemeReturn(BaseModel):
    image_id: int

class GeminiResponse(BaseModel):
    text: List[IndvMemeReturn]

class ImageTrivial(BaseModel):
    image_id: int
    caption: str