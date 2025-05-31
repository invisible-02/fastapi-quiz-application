from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import json
import os
import random

# Security configurations
SECRET_KEY = "your-secret-key-for-jwt"  # In production, use a secure secret key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# File paths
USERS_FILE = "data/users.json"
QUESTIONS_FILE = "data/questions.json"
ASSIGNMENTS_FILE = "data/user_assignments.json"

# Helper functions
def get_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)['users']
    return []

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump({"users": users}, f, indent=4)

def get_questions():
    with open(QUESTIONS_FILE, 'r') as f:
        return json.load(f)['questions']

def get_user_assignments():
    if os.path.exists(ASSIGNMENTS_FILE):
        with open(ASSIGNMENTS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_user_assignments(assignments):
    with open(ASSIGNMENTS_FILE, 'w') as f:
        json.dump(assignments, f, indent=4)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(username: str):
    users = get_users()
    return next((user for user in users if user["username"] == username), None)

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
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user

# Routes
@app.post("/register")
async def register(form_data: OAuth2PasswordRequestForm = Depends()):
    users = get_users()
    if any(user["username"] == form_data.username for user in users):
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    hashed_password = get_password_hash(form_data.password)
    new_user = {
        "username": form_data.username,
        "hashed_password": hashed_password
    }
    users.append(new_user)
    save_users(users)
    return {"message": "User created successfully"}

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user(form_data.username)
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
    questions = get_questions()
    if len(questions) < 50:
        raise HTTPException(status_code=400, detail="Insufficient questions available")
    
    selected_questions = random.sample(questions, 50)
    assignments = get_user_assignments()
    assignments[current_user["username"]] = {
        "assigned_questions": selected_questions,
        "answers": {},
        "start_time": datetime.utcnow().isoformat()
    }
    save_user_assignments(assignments)
    
    return {"message": "Quiz started", "questions": selected_questions}

from pydantic import BaseModel

class AnswerInput(BaseModel):
    question_id: int
    answer: str

@app.post("/answer")
async def submit_answer(
    answer_input: AnswerInput,
    current_user: dict = Depends(get_current_user)
):
    assignments = get_user_assignments()
    user_assignment = assignments.get(current_user["username"])
    
    if not user_assignment:
        raise HTTPException(status_code=400, detail="Quiz not started")
    
    if not any(q["id"] == answer_input.question_id for q in user_assignment["assigned_questions"]):
        raise HTTPException(status_code=404, detail="Question not assigned")
    
    if answer_input.answer not in ["Yes", "No"]:
        raise HTTPException(status_code=400, detail="Invalid answer. Must be 'Yes' or 'No'")
    
    user_assignment["answers"][str(answer_input.question_id)] = answer_input.answer
    save_user_assignments(assignments)
    
    return {"message": "Answer saved successfully"}

@app.get("/progress")
async def get_progress(current_user: dict = Depends(get_current_user)):
    assignments = get_user_assignments()
    user_assignment = assignments.get(current_user["username"])
    
    if not user_assignment:
        return {"progress": 0, "total_questions": 50}
    
    answered = len(user_assignment["answers"])
    return {
        "progress": answered,
        "total_questions": 50,
        "percentage": (answered / 50) * 100
    }

# Serve the HTML page
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("static/index.html", "r") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
