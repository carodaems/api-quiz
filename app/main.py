from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from sqlalchemy import func


import os
import models
import schemas
from database import SessionLocal, engine

if not os.path.exists('.\sqlitedb'):
    os.makedirs('.\sqlitedb')

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


current_round = {
    "round": 1,
    "question": 1
}

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:3000",
    "http://localhost:3000",
    "https://gregarious-buttercream-79d640.netlify.app",
    "https://gregarious-buttercream-79d640",
    "https://63d57fc4af3368398f3afe7e--gregarious-buttercream-79d640",
    "https://63d57fc4af3368398f3afe7e--gregarious-buttercream-79d640.netlify.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    """
    Returns a new database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Endpoints

# PUT

@app.put("/quiz_rounds/{round_id}")
def update_quiz_round(round_id: int, round: schemas.QuizRoundUpdate, db: Session = Depends(get_db)):
    db_round = db.query(models.QuizRound).filter(
        models.QuizRound.id == round_id).first()
    if db_round is None:
        raise HTTPException(status_code=404, detail="Quiz round not found")
    db_round.name = round.name
    db_round.key = round.key
    db.add(db_round)
    db.commit()
    db.refresh(db_round)
    return db_round


@app.put("/quiz_rounds/questions/check")
def update_response(guess: schemas.QuestionCompare, db: Session = Depends(get_db)):
    question = db.query(models.Question).filter(
        models.Question.question_number == current_round["question"], models.Question.round_id == current_round["round"]).first()

    team = db.query(models.Team).filter(
        models.Team.id == guess.team_id).first()
    if team is None:
        raise HTTPException(status_code=400, detail="Team not found")

    if question.correct_answer == guess.guess:
        is_correct = True
    else:
        is_correct = False

    db_number = db.query(models.Responses).filter(
        models.Responses.team_id == guess.team_id, models.Responses.question_number == question.question_number, models.Responses.round_id == question.round_id
    ).first()

    if db_number is None:
        db_number = models.Responses(
            reponse=guess.guess, team_id=guess.team_id, correct=is_correct, round_id=question.round_id, question_number=question.question_number)
    else:
        db_number.reponse = guess.guess
        db_number.team_id = guess.team_id
        db_number.correct = is_correct
        db_number.round_id = question.round_id
        db_number.question_number = question.question_number
        db_number.id = db_number.id

    db.add(db_number)
    db.flush()
    db.commit()
    db.refresh(db_number)
    return db_number


@app.put("/teams/")
def create_team(team: schemas.TeamCreate, db: Session = Depends(get_db)):
    name = "Team " + str(team.number)

    db_team = db.query(models.Team).filter(
        models.Team.id == team.number, models.Team.team_name == name).first()
    if db_team is None:
        db_team = models.Team(team_name=name, id=team.number)
    else:
        db_team.id = team.number
        db_team.team_name = name

    db.add(db_team)
    db.flush()
    db.commit()
    db.refresh(db_team)
    return db_team


@app.put("/scores")
def update_scores(db: Session = Depends(get_db)):
    teams = db.query(models.Team).all()
    round_id = current_round["round"]
    for team in teams:
        for scores in team.scores:
            score = scores.score
            for response in team.responses:
                if response.correct and response.round_id == round_id:
                    score += 1
            team.scores.score = score
            db.add(scores)
            db.flush()
            db.commit()
            db.refresh(scores)
    current_round["round"] += 1
    return {"message": "updated"}


@app.put("/scores/{team_id}/increment")
def increment_score(team_id: int, db: Session = Depends(get_db)):
    team = db.query(models.Scores).filter(
        models.Scores.team_id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    team.score += 1
    db.commit()
    db.refresh(team)
    return {"detail": "Score incremented for team"}


@app.put("/scores/{team_id}/decrement")
def decrement_score(team_id: int, db: Session = Depends(get_db)):
    team = db.query(models.Scores).filter(
        models.Scores.team_id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    team.score -= 1
    db.commit()
    db.refresh(team)
    return {"detail": "Score decremented for team"}


@app.put("/quiz_rounds/{round_id}/answers")
def update_questions(round_id: int, questions: List[schemas.QuestionUpdates], db: Session = Depends(get_db)):
    db_questions = db.query(models.Question).filter(
        models.Question.round_id == round_id).all()
    if not db_questions:
        raise HTTPException(
            status_code=404, detail="Round not found or no question for this round")
    for db_question in db_questions:
        for question in questions:
            if db_question.question_number == question.question_number:
                db_question.correct_answer = question.answer
                db.add(db_question)
                db.commit()
                db.refresh(db_question)
    return {"detail": "questions updated"}


@app.put("/quiz_rounds/{round_id}/questions/{question_id}")
def update_question(round_id: int, question_id: int, question: schemas.QuestionUpdate, db: Session = Depends(get_db)):
    db_question = db.query(models.Question).filter(
        models.Question.id == question_id, models.Question.round_id == round_id).first()
    if db_question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    db_question.correct_answer = question.correct_answer
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question


# GET
@app.get("/quiz_rounds")
def read_quiz_rounds(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    quiz_rounds = db.query(models.QuizRound).offset(skip).limit(limit).all()
    return quiz_rounds


@app.get("/quiz_rounds/{round_id}")
def read_quiz_round(round_id: int, db: Session = Depends(get_db)):
    db_round = db.query(models.QuizRound).filter(
        models.QuizRound.id == round_id).first()
    if db_round is None:
        raise HTTPException(status_code=404, detail="Quiz round not found")
    return db_round


@app.get("/quiz_rounds/{round_id}/questions")
def read_questions(round_id: int, db: Session = Depends(get_db)):
    questions = db.query(models.Question).filter(
        models.Question.round_id == round_id).all()
    if not questions:
        raise HTTPException(status_code=404, detail="Questions not found")
    return questions


@app.get("/quiz_rounds/{round_id}/questions/{question_id}")
def read_question(round_id: int, question_id: int, db: Session = Depends(get_db)):
    question = db.query(models.Question).filter(
        models.Question.id == question_id, models.Question.round_id == round_id).first()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@app.get("/quiz_rounds/questions/check/{team_id}")
def check_responses(team_id: int, db: Session = Depends(get_db)):
    responses = db.query(models.Responses).filter(
        models.Responses.team_id == team_id).all()
    if not responses:
        raise HTTPException(status_code=404, detail="Responses not found")
    return responses


@app.get("/teams/")
def get_teams(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    teams = db.query(models.Team).offset(skip).limit(limit).all()
    return teams


@app.get("/scores")
def get_scores(db: Session = Depends(get_db)):
    db_scores = db.query(models.Scores).all()

    scores = {}
    for score in db_scores:
        scores[score.team.team_name] = score.score

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    converted_scores = dict(sorted_scores)

    return converted_scores


@app.get("/scores/raw")
def get_scores_raw(db: Session = Depends(get_db)):
    scores = db.query(models.Scores).all()
    return scores


@app.get("/getround")
async def get_round():
    return current_round


# DELETE

@app.delete("quiz_rounds/{round_id}")
def delete_quiz_round(round_id: int, db: Session = Depends(get_db)):
    db_round = db.query(models.QuizRound.filter(
        models.QuizRound.id == round_id)).first()
    if db_round is None:
        raise HTTPException(status_code=404, detail="Quiz round not found")
    db.delete(db_round)
    db.commit()
    return {"message": "Round deleted"}


@app.delete("/quiz_rounds/{round_id}/questions/{question_id}")
def delete_question(round_id: int, question_id: int, db: Session = Depends(get_db)):
    question = db.query(models.Question).filter(
        models.Question.id == question_id, models.Question.round_id == round_id).first()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    db.delete(question)
    db.commit()
    return {"message": "Question deleted"}


# POST

@app.post("/quiz_rounds")
def create_quiz_round(round: schemas.QuizRoundCreate, db: Session = Depends(get_db)):
    db_round = models.QuizRound(name=round.name, key=round.key)
    round_check = db.query(models.QuizRound).filter(
        models.QuizRound.name == round.name).first()
    if round_check is None:
        db.add(db_round)
        db.flush()
        db.commit()
        db.refresh(db_round)
    elif db_round.name == round_check.name:
        raise HTTPException(
            status_code=400, detail="This round already exists")
    return db_round


@app.post("/quiz_rounds/{round_id}/questions")
def create_question(round_id: int, question: schemas.QuestionCreate, db: Session = Depends(get_db)):
    db_round = db.query(models.QuizRound).filter(
        models.QuizRound.id == round_id).first()
    if db_round is None:
        raise HTTPException(status_code=404, detail="Quiz round not found")
    last_question_number = db.query(models.Question).filter(
        models.Question.round_id == round_id).order_by(models.Question.question_number.desc()).first()
    new_question_number = 1 if last_question_number is None else last_question_number.question_number + 1
    new_question = models.Question(
        correct_answer=question.answer, round_id=round_id, question_number=new_question_number)
    db.add(new_question)
    db.flush()
    db.commit()
    db.refresh(new_question)
    return new_question


@app.post("/quiz_rounds/{round_id}/answers/multiple")
async def create_multiple_quiz_answers(round_id: int, answers: List[schemas.QuestionCreate], db: Session = Depends(get_db)):
    db_round = db.query(models.QuizRound).filter(
        models.QuizRound.id == round_id).first()
    if db_round is None:
        name = "Round " + str(round_id)
        db_round = models.QuizRound(name=name, key=name)
        db.add(db_round)
        db.flush()
        db.commit()
        db.refresh(db_round)

    last_question_number = db.query(func.max(models.Question.question_number)).filter(
        models.Question.round_id == round_id).scalar()
    question_number = last_question_number + 1 if last_question_number else 1
    for answer in answers:
        question = models.Question(
            round_id=round_id, question_number=question_number, correct_answer=answer.answer)
        db.add(question)
        db.flush()
        question_number += 1
    db.commit()
    db.refresh(question)
    return {"status": "success"}


@app.post("/quiz_rounds/questions/check")
def compare_question(guess: schemas.QuestionCompare, db: Session = Depends(get_db)):
    question = db.query(models.Question).filter(
        models.Question.question_number == current_round["question"], models.Question.round_id == current_round["round"]).first()
    if question.correct_answer == guess.guess:
        is_correct = True
    else:
        is_correct = False
    db_response = models.Responses(
        reponse=guess.guess, team_id=guess.team_id, correct=is_correct, round_id=question.round_id, question_number=question.question_number)
    db.add(db_response)
    db.flush()
    db.commit()
    db.refresh(db_response)
    return db_response


@app.post("/setround")
async def set_round():
    current_round["round"] += 1
    return current_round


@app.post("/setquestion")
async def set_question():
    current_round["question"] += 1
    return current_round
