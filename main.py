from fastapi import FastAPI
from entity import *
from chatAI import *
from typing import List

app = FastAPI()

@app.post("/ai/questionnaire")
async def questionnaire(data: QuestionnaireRequest):
    return generate_questionnaire(data)