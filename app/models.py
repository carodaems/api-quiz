from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship


class QuizRound(Base):
    __tablename__ = "quiz_rounds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    questions = relationship("Question", back_populates="round")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question_number = Column(Integer, index=True, default=1)
    correct_answer = Column(String, index=True)
    round_id = Column(Integer, ForeignKey("quiz_rounds.id"))
    round = relationship("QuizRound", back_populates="questions")


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    team_name = Column(String, index=True)
    responses = relationship("Responses", back_populates="team")
    scores = relationship("Scores", back_populates="team")


class Responses(Base):
    __tablename__ = "responses"

    id = Column(Integer, primary_key=True, index=True)
    reponse = Column(String, index=True)
    correct = Column(Boolean, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"))
    round_id = Column(Integer, index=True)
    question_number = Column(Integer, index=True)

    team = relationship("Team", back_populates="responses")


class Scores(Base):
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"))
    score = Column(Integer, index=True)

    team = relationship("Team", back_populates="scores")
