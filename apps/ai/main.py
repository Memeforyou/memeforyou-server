from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from search import final_eval
from utils.schema import InputData, FullRecReturn

# Initialize FastAPI app
app = FastAPI(title="memeforyou AI API - GDGoC KU 2025 worktree")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://memeforyou-server-production.up.railway.app:8080", "http://memeforyou-server-production.up.railway.app:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ai/similar",
          response_model=FullRecReturn,
          summary="Get top N ranked meme recommendation results.",
          description="")
async def search_meme(request: InputData):

    logger.info(f"Recognized request: {request.count} results with {request.text}")

    search_response = await final_eval(user_input=request.text, final_cnt=request.count)

    # Construct return
    result = FullRecReturn(
        count=len(search_response.text),
        recommendations=search_response.text
    )

    if result:
        logger.success(f"Successfully acquired recommendations.")
    else:
        logger.error(f"Failed to acquire recommendations.")

    return result