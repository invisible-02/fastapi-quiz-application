
Built by https://www.blackbox.ai

---

# FastAPI Quiz Application

## Project Overview

This is a FastAPI-based web application designed to facilitate quiz taking. It supports user registration, JWT token-based authentication, and allows users to answer quiz questions and track progress. The application is equipped with a simple HTML interface for user interaction.

## Installation

To set up the project environment, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment:**

   - On Windows:

     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:

     ```bash
     source venv/bin/activate
     ```

4. **Install the required packages:**

   ```bash
   pip install fastapi[all] passlib python-jose
   ```

5. **Create necessary directories and files:**

   ```bash
   mkdir data static
   touch data/users.json data/questions.json data/user_assignments.json
   ```

6. **Run the application:**

   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000
   ```

7. **Access the application:**
   
   Open your web browser and navigate to `http://localhost:8000`.

## Usage

### API Endpoints

- **Register a user:**
  - `POST /register`
  - Body (x-www-form-urlencoded):
    - `username`: string
    - `password`: string

- **Obtain a JWT token:**
  - `POST /token`
  - Body (x-www-form-urlencoded):
    - `username`: string
    - `password`: string

- **Start the quiz:**
  - `GET /start`
  
  Requires: Bearer token in the Authorization header.

- **Submit an answer:**
  - `POST /answer`
  - Body:
    ```json
    {
      "question_id": int,
      "answer": "Yes" | "No"
    }
    ```
  
  Requires: Bearer token in the Authorization header.

- **Get quiz progress:**
  - `GET /progress`
  
  Requires: Bearer token in the Authorization header.

- **View HTML interface:**
  - `GET /`

### Example Usage

You can use tools like Postman or curl to test the API endpoints. For example, to register a user:

```bash
curl -X POST "http://localhost:8000/register" -d "username=testuser&password=testpass"
```

## Features

- User registration and login with JWT authentication.
- Ability to start a quiz and get a set of questions.
- Submit answers for the quiz.
- Track user quiz progress and store answers.
- Simple HTML frontend to interact with the API.

## Dependencies

The project requires the following dependencies, as specified in `requirements.txt`:

- `fastapi`: A modern web framework for building APIs with Python 3.6+ based on standard Python type hints.
- `uvicorn`: ASGI server for serving FastAPI applications.
- `passlib`: Library for password hashing.
- `python-jose`: Library for encoding and decoding JSON Web Tokens (JWT).

## Project Structure

```
.
├── app.py                    # Main application file
├── data                      # Directory for data files
│   ├── user_assignments.json  # Stores user assignments and answers
│   ├── questions.json        # Stores quiz questions
│   └── users.json           # Stores user account information
├── static                    # Directory for static files
│   └── index.html           # HTML file for the web interface
├── requirements.txt          # List of dependencies
```

## Author

This project was developed as part of a learning exercise. Contributions and feedback are welcome!

## License

This project is licensed under the MIT License - see the LICENSE file for details.