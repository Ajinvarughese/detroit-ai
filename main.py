from fastapi import FastAPI
from entity import *
from chatAI import *
from typing import List

app = FastAPI()

@app.post("/ai/questionnaire")
async def questionnaire(data: QuestionnaireRequest):
    print("hello")
    question = generate_questionnaire(data)
    print(question)
    return question