from pydantic import BaseModel, Field
from typing import List

# --- Models for prep ---

# Metadata for each meme
class MemeMeta(BaseModel):
    ocr: str
    caption: str
    humor: str
    tags: List[str]

class IndvVector(BaseModel):
    image_id: int
    vector: List[float]

# --- Models for search inference
class IndvMemeReturn(BaseModel):
    image_id: int
    rank: int

class GeminiResponse(BaseModel):
    text: List[IndvMemeReturn]

class ImageTrivial(BaseModel):
    image_id: int
    caption: str

# --- Models for main FastAPI API ---

# User input data class
class InputData(BaseModel):
    text: str = Field(..., examples=['늦잠 자서 수업을 째 버렸어'], description="유저 텍스트 입력 값")
    count: int = Field(..., examples=[5, 10], description="반환받을 밈 개수")

# Full response class definition
class FullRecReturn(BaseModel):
    count: int
    recommendations: list[IndvMemeReturn]