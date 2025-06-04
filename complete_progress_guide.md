# How to Access and Use the Complete Progress Endpoint

This guide explains how to access and use the `/data/complete-progress` endpoint in the Quiz Application to get all assigned questions with their answer status.

---

## Prerequisites

- You must be a registered user and logged in.
- You need your authentication token (access token) obtained after login.

---

## Step-by-Step Instructions

### 1. Obtain Your Access Token

If you don't have your access token, get it by logging in via the API:

```bash
curl -X POST "http://localhost:3000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your_username&password=your_password"
```

The response will contain your access token:

```json
{
  "access_token": "your_access_token_here",
  "token_type": "bearer"
}
```

### 2. Access the Complete Progress Endpoint

Use the following API endpoint to get all assigned questions with answer status:

```
GET /data/complete-progress
```

Include your access token in the Authorization header.

#### Using cURL

```bash
curl "http://localhost:3000/data/complete-progress" \
  -H "Authorization: Bearer your_access_token_here"
```

### 3. Response Format

The response will be a JSON object with a `questions` array. Each question object contains:

- `id`: Question ID
- `question_text`: The question text
- `options`: Array of options (e.g., ["Yes", "No"])
- `answer`: Your answer to the question (or null if unanswered)

Example:

```json
{
  "questions": [
    {
      "id": 1,
      "question_text": "Do you like programming?",
      "options": ["Yes", "No"],
      "answer": "Yes"
    },
    {
      "id": 2,
      "question_text": "Have you used FastAPI before?",
      "options": ["Yes", "No"],
      "answer": null
    }
  ]
}
```

---

## Notes

- Replace `http://localhost:3000` with your actual server URL if deployed elsewhere.
- Keep your access token secure.
- You can use this data to display progress, generate reports, or export user responses.

If you need help with automated scripts or integrating this endpoint into your frontend, feel free to ask!
