from pydantic import BaseModel
from typing import List, Dict


class QuizRoundCreate(BaseModel):
    name: str
    key: str


class QuizRound(QuizRoundCreate):
    id: int


class QuizRoundUpdate(BaseModel):
    name: str
    key: str


class QuestionCreate(BaseModel):
    answer: str


class QuestionUpdate(BaseModel):
    answer: str


class Question(QuestionCreate):
    id: int


class QuestionCompare(BaseModel):
    guess: str
    team_id: int


# klasses voor teams

class TeamCreate(BaseModel):
    name: str


class Team(TeamCreate):
    pass
