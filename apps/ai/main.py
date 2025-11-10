from AI import search
from pydantic import BaseModel
from fastapi import FastAPI

app = FastAPI()

class InputData(BaseModel):
    text: str

@app.post("/search")
async def search_meme(data: InputData):
    user_text = data.text

    result = ""

    return result