from pydantic import BaseModel
from enum import Enum
from typing import Any, Optional, List

class QuestionType(str, Enum):
    TEXT = "TEXT"
    CHECKBOX = "CHECKBOX"
    RADIO = "RADIO"
    DROPDOWN = "DROPDOWN"


class Choice(BaseModel):
    choiceText: str
    score: int

class Question(BaseModel):
    questionText: str
    questionType: QuestionType
    choices: List[Choice]

class QuestionnaireRequest(BaseModel):
    inputData: str
    loanCategory: str
    rules: Optional[Any] = None