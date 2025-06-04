# Quiz Application API Guide

## Authentication
First, get your authentication token:
```bash
curl -X POST "http://localhost:3000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass123"
```

## Data Endpoints

Replace `<your_token>` with the access_token you received from the authentication step.

### 1. Get All Available Questions
```bash
curl "http://localhost:3000/data/questions" \
  -H "Authorization: Bearer <your_token>"
```

### 2. Get Your Question Assignments
```bash
curl "http://localhost:3000/data/user-assignments" \
  -H "Authorization: Bearer <your_token>"
```

### 3. Get Detailed Progress
```bash
curl "http://localhost:3000/data/user-progress" \
  -H "Authorization: Bearer <your_token>"
```

## Response Formats

### Questions Response
```json
{
    "questions": [
        {
            "id": 1,
            "question_text": "Sample question?",
            "options": ["Yes", "No"]
        }
        // ... more questions
    ]
}
```

### User Assignments Response
```json
{
    "assignments": [
        {
            "id": 1,
            "user_id": 1,
            "question_id": 5,
            "answer": "Yes",
            "assigned_at": "2024-02-20T12:00:00"
        }
        // ... more assignments
    ]
}
```

### Progress Response
```json
{
    "total_questions": 10,
    "questions_answered": 5,
    "questions_remaining": 5,
    "completion_percentage": 50.0,
    "assignments": [
        // detailed assignment data
    ]
}
```

## Notes
- All endpoints require authentication using a Bearer token
- Data is returned in JSON format
- The database automatically assigns 10 random questions per user
- Questions are removed from the pool once assigned
