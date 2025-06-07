import asyncio
from database import database, metadata, engine, questions
import json
import os

async def init():
    # Drop all tables to ensure fresh schema
    # metadata.drop_all(engine)  # Commented out to preserve existing data
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
                    req_runs=str(q.get("req_runs")) if q.get("req_runs") is not None else None,
                    balls_remaining=str(q.get("balls_remaining")) if q.get("balls_remaining") is not None else None,
                    batsman_total_runs=str(q.get("batsman_total_runs")) if q.get("batsman_total_runs") is not None else None,
                    batsman_balls_faced=str(q.get("batsman_balls_faced")) if q.get("batsman_balls_faced") is not None else None,
                    nonstriker_total_runs=str(q.get("nonstriker_total_runs")) if q.get("nonstriker_total_runs") is not None else None,
                    nonstriker_balls_faced=str(q.get("nonstriker_balls_faced")) if q.get("nonstriker_balls_faced") is not None else None,
                    team_run_rate=str(q.get("team_run_rate")) if q.get("team_run_rate") is not None else None,
                    wickets=str(q.get("wickets")) if q.get("wickets") is not None else None,
                )
                await database.execute(query)

    await database.disconnect()

if __name__ == "__main__":
    asyncio.run(init())
