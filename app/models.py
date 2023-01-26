from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship


class QuizRound(Base):
    __tablename__ = "quiz_rounds"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    key = Column(String, index=True)
    questions = relationship("Question", back_populates="round")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question_number = Column(Integer, index=True, default=1)
    correct_answer = Column(String, index=True)
    round_id = Column(Integer, ForeignKey("quiz_rounds.id"))
    round = relationship("QuizRound", back_populates="questions")


# model voor team
# model voor opgegeven antwoorden van een team
