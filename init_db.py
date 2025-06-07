import asyncio
from database import database, metadata, engine, questions
import json
import os

async def init():
    # Drop all tables to ensure fresh schema
    metadata.drop_all(engine)  # Re-enabled to recreate tables and sync schema
    # Create tables
    metadata.create_all(engine)
    await database.connect()

    # Clear all rows from questions table before seeding
    delete_query = questions.delete()
    await database.execute(delete_query)

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
                    options=options_json,
                    req_runs=q.get("req_runs"),
                    balls_remaining=q.get("balls_remaining"),
                    batsman_total_runs=q.get("batsman_total_runs"),
                    batsman_balls_faced=q.get("batsman_balls_faced"),
                    nonstriker_total_runs=q.get("nonstriker_total_runs"),
                    nonstriker_balls_faced=q.get("nonstriker_balls_faced"),
                    team_run_rate=q.get("team_run_rate"),
                    wickets=q.get("wickets"),
                )
                await database.execute(query)

    await database.disconnect()

if __name__ == "__main__":
    asyncio.run(init())
