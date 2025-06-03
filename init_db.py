import asyncio
from database import database, metadata, engine, questions
import json
import os

async def init():
    # Create tables
    metadata.create_all(engine)
    await database.connect()

    # Check if questions table is empty
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
    await database.disconnect()

if __name__ == "__main__":
    asyncio.run(init())
