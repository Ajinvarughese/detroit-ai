import os
from dotenv import load_dotenv
from openai import OpenAI
from entity import *
from typing import List
from openai import OpenAI
import json
import re

# ================== CLIENT (cached) ==================

_client = None

def get_client():
    global _client
    if _client is None:
        load_dotenv()
        api_key = os.getenv("NVIDIA_API_KEY")
        if not api_key:
            raise ValueError("NVIDIA_API_KEY not found")
        _client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=api_key
        )
    return _client

# ================== HELPERS ==================

def safe_message_content(msg) -> str:
    if not msg:
        return ""
    if isinstance(msg, str):
        return msg.strip()
    if isinstance(msg, list):
        return " ".join(
            part.get("text", "") for part in msg if isinstance(part, dict)
        ).strip()
    return ""
# ================== AI CHAT ==================


def generate_questionnaire(data: QuestionnaireRequest) -> List[Question]:
    topic = data.inputData
    loan_category = data.loanCategory
    num_questions = 10
    rules = data.rules

    client = get_client()

    messages = [
        {
            "role": "system",
    "content": f"""
You are an expert sustainability questionnaire generator for a banking system.

Your task is to create a questionnaire used to evaluate whether a loan applicant
qualifies for sustainable finance.

The questionnaire MUST follow the bank taxonomy rules provided below.

Instructions:
- Use the taxonomy rules to design evaluation questions.
- Questions should measure sustainability impact, environmental practices,
  governance, and risk.
- Each question must contain choices with scores.
- Positive scores represent sustainable or desirable outcomes.
- Negative scores represent unsustainable or risky outcomes.
- Scores must reflect the evaluation logic from the taxonomy.
- Questions must be relevant to the loan category.

Taxonomy rules:
{rules}

Return ONLY valid JSON. """
+"""
Response format:
[
  {
    "questionText": "string",
    "questionType": "TEXT | CHECKBOX | RADIO | DROPDOWN",
    "choices": [
      {
        "choiceText": "string",
        "score": number
      }
    ]
  }
]
"""
        },
        {
            "role": "user",
            "content": f"""
Generate {num_questions} questionnaire questions about:

{topic}

loan category: {loan_category}
Each question must have 3-5 options with scores.
Return only JSON.
"""
        }
    ]

    completion = client.chat.completions.create(
        model="meta/llama-3.1-70b-instruct",
        messages=messages,
        temperature=0.3,
        max_tokens=2048
    )

    response = safe_message_content(completion.choices[0].message.content)

    # 🔧 Remove markdown code blocks like ```json ... ```
    response = response[response.find("["):response.rfind("]")+1]

    data = json.loads(response)

    return data