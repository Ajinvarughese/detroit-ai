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
You generate sustainability loan questionnaires.

Rules:
{rules}

Requirements:
- Generate {num_questions} relevant questions.
- Use taxonomy rules.
- Include 3-5 choices per question.
- Positive score = sustainable.
- Negative score = risky.
- questionType must be RADIO | CHECKBOX | DROPDOWN | TEXT.

Return ONLY valid JSON.

Format:
[
  {{
    "questionText": "string",
    "questionType": "RADIO",
    "choices": [
      {{
        "choiceText": "string",
        "score": 1
      }}
    ]
  }}
]
"""
    },
    {
        "role": "user",
        "content": f"""
Topic: {topic}
Loan category: {loan_category}
"""
    }
]

    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=messages,
        temperature=0.3,
        max_tokens=8192
    )

    response = safe_message_content(completion.choices[0].message.content)

    response = response[response.find("["):response.rfind("]")+1]

    print(response)  

    data = json.loads(response)

    return data