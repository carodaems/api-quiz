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


class QuestionUpdates(QuestionUpdate):
    question_number: int


class Question(QuestionCreate):
    id: int


class QuestionCompare(BaseModel):
    guess: str
    team_id: int


class TeamCreate(BaseModel):
    number: int


class Team(TeamCreate):
    pass


class Score(BaseModel):
    team_id: int
    score: int
