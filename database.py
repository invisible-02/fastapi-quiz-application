import sqlalchemy
from databases import Database
from sqlalchemy import Table, Column, Integer, String, MetaData, DateTime, ForeignKey, Text
import json
import os
from datetime import datetime

# Update DATABASE_URL to use PostgreSQL connection string
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://cricket_azy0_user:ypIy2vBkWWI5gdUWHsdABWd1JSgd6jan@dpg-d125vgbuibrs73esq3s0-a/cricket_azy0")

database = Database(DATABASE_URL)
metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True, index=True),
    Column("hashed_password", String),
)

questions = Table(
    "questions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("question_text", Text),
    Column("options", Text),  # JSON string of options
    Column("req_runs", Integer, nullable=True),
    Column("balls_remaining", Integer, nullable=True),
    Column("batsman_total_runs", Integer, nullable=True),
    Column("batsman_balls_faced", Integer, nullable=True),
    Column("nonstriker_total_runs", Integer, nullable=True),
    Column("nonstriker_balls_faced", Integer, nullable=True),
    Column("team_run_rate", String, nullable=True),
    Column("wickets", Integer, nullable=True),
)

assignments = Table(
    "assignments",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("question_id", Integer, ForeignKey("questions.id")),
    Column("answer", String, nullable=True),
    Column("assigned_at", DateTime, default=datetime.utcnow),
)

engine = sqlalchemy.create_engine(
    DATABASE_URL
)

def create_tables():
    metadata.create_all(engine)

async def init_db():
    await database.connect()
    create_tables()
    # Seed questions if table is empty
    query = "SELECT COUNT(*) FROM questions"
    count = await database.fetch_val(query)
    if count == 0:
        # Load questions from JSON file
        if os.path.exists("data/questions.json"):
            with open("data/questions.json", "r") as f:
                data = json.load(f)
                questions_list = data.get("questions", [])
                for q in questions_list:
                    options_json = json.dumps(q.get("options", []))
                    query = questions.insert().values(
                        id=q["id"],
                        question_text=q["question"],
                        options=options_json
                    )
                    await database.execute(query)
