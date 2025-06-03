from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
import random

from database import database, users, questions, assignments

# Security configurations
SECRET_KEY = "your-secret-key-for-jwt"  # In production, use a secure secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ASSIGNED_QUESTION_COUNT = 10

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

async def get_user(username: str):
    query = users.select().where(users.c.username == username)
    user = await database.fetch_one(query)
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user(username)
    if user is None:
        raise credentials_exception
    return user

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

# Routes
@app.post("/register")
async def register(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await get_user(form_data.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    hashed_password = get_password_hash(form_data.password)
    query = users.insert().values(username=form_data.username, hashed_password=hashed_password)
    await database.execute(query)
    return {"message": "User created successfully"}

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await get_user(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/start")
async def start_quiz(current_user: dict = Depends(get_current_user)):
    # Fetch all questions
    query = questions.select()
    all_questions = await database.fetch_all(query)
    if len(all_questions) < ASSIGNED_QUESTION_COUNT:
        raise HTTPException(status_code=400, detail="Insufficient questions available")
    
    # Randomly select questions
    selected_questions = random.sample(all_questions, ASSIGNED_QUESTION_COUNT)
    selected_ids = [q["id"] for q in selected_questions]
    
    # Remove selected questions from questions table
    for qid in selected_ids:
        delete_query = questions.delete().where(questions.c.id == qid)
        await database.execute(delete_query)
    
    # Assign questions to user
    for q in selected_questions:
        insert_query = assignments.insert().values(
            user_id=current_user["id"],
            question_id=q["id"],
            answer=None,
            assigned_at=datetime.utcnow()
        )
        await database.execute(insert_query)
    
    # Prepare response questions with options parsed from JSON string
    response_questions = []
    import json as js
    for q in selected_questions:
        response_questions.append({
            "id": q["id"],
            "question": q["question_text"],
            "options": js.loads(q["options"])
        })
    
    return {"message": "Quiz started", "questions": response_questions}

class AnswerInput(BaseModel):
    question_id: int
    answer: str

@app.post("/answer")
async def submit_answer(
    answer_input: AnswerInput,
    current_user: dict = Depends(get_current_user)
):
    # Check if question is assigned to user
    query = assignments.select().where(
        (assignments.c.user_id == current_user["id"]) &
        (assignments.c.question_id == answer_input.question_id)
    )
    assignment = await database.fetch_one(query)
    if not assignment:
        raise HTTPException(status_code=404, detail="Question not assigned")
    
    if answer_input.answer not in ["Yes", "No"]:
        raise HTTPException(status_code=400, detail="Invalid answer. Must be 'Yes' or 'No'")
    
    # Update answer
    update_query = assignments.update().where(
        (assignments.c.user_id == current_user["id"]) &
        (assignments.c.question_id == answer_input.question_id)
    ).values(answer=answer_input.answer)
    await database.execute(update_query)
    
    return {"message": "Answer saved successfully"}

@app.get("/progress")
async def get_progress(current_user: dict = Depends(get_current_user)):
    # Count answered questions
    answered_query = assignments.select().where(
        (assignments.c.user_id == current_user["id"]) &
        (assignments.c.answer != None)
    )
    answered = await database.fetch_all(answered_query)
    answered_count = len(answered)
    
    # Count total assigned questions
    total_query = assignments.select().where(assignments.c.user_id == current_user["id"])
    total = await database.fetch_all(total_query)
    total_count = len(total)
    
    return {
        "progress": answered_count,
        "total_questions": total_count,
        "percentage": (answered_count / total_count) * 100 if total_count > 0 else 0
    }

# Serve the HTML page
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
