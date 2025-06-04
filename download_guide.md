# How to Download Complete Quiz Data

This guide explains how to download the complete quiz data (questions, assignments, and progress) as a JSON file from the Quiz Application.

---

## Prerequisites

- You must be a registered user and logged in to the Quiz Application.
- You need to have your authentication token (access token) obtained after login.

---

## Step-by-Step Instructions

### 1. Log in to the Quiz Application

- Open the Quiz Application in your browser (e.g., http://localhost:3000).
- Enter your username and password.
- Click the **Login** button.
- On successful login, you will receive an access token (handled automatically by the frontend).

### 2. Get Your Access Token (Optional)

If you want to manually get the access token, you can use the login API:

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

### 3. Download the Complete Data File

Use the following API endpoint to download the complete quiz data as a JSON file:

```
GET /data/complete-download
```

You must include your access token in the Authorization header.

#### Using cURL

```bash
curl "http://localhost:3000/data/complete-download" \
  -H "Authorization: Bearer your_access_token_here" \
  -o complete_quiz_data.json
```

This command will save the file as `complete_quiz_data.json` in your current directory.

### 4. Open and Use the Downloaded File

- The downloaded JSON file contains:
  - All quiz questions
  - Your assigned questions and answers
  - Your progress statistics

- You can open this file with any text editor or JSON viewer for analysis or backup.

---

## Notes

- Replace `http://localhost:3000` with your actual server URL if deployed elsewhere.
- Always keep your access token secure.
- The frontend app handles authentication and token management automatically if you use the UI.

---

If you need any help with these steps or want me to assist with automated scripts, feel free to ask!
