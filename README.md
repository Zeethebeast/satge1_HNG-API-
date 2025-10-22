#🧠 String Analysis API

A Flask-based RESTful API that analyzes strings by providing information such as word count, palindrome check, SHA-256 hash, character frequency, and more.
This project demonstrates efficient string processing, query-based filtering, and REST API design in Python.

##🚀 Features

✅ Analyze any string (length, palindrome, hash, etc.)
✅ Retrieve previously analyzed strings
✅ Filter strings using query parameters (e.g., palindrome or length)
✅ Delete a string from storage
✅ Find similar strings using fuzzy matching
✅ Ready for Docker deployment with production WSGI server (waitress)

🧩 Endpoints
###1️⃣ POST /string

Analyze and store a new string.

Request (JSON):

{
  "value": "madam"
}


Response (201):

{
  "string": "madam",
  "length": 5,
  "is_palindrome": true,
  "word_count": 1,
  "unique_characters": ["a", "m", "d"],
  "frequency": {"m": 2, "a": 2, "d": 1},
  "sha256": "ab53a2911ddf9b4817ac01ddcd3d975..."
}

###2️⃣ GET /string/<string_value>

Retrieve the analysis of a specific string.

Example:
GET /string/hello

Response (200):

{
  "string": "hello",
  "length": 5,
  "is_palindrome": false,
  "word_count": 1,
  "unique_characters": ["e", "o", "l", "h"],
  "frequency": {"h":1,"e":1,"l":2,"o":1},
  "sha256": "2cf24dba5fb0a30e26e83b2ac5b9e29..."
}

###3️⃣ GET /string

Retrieve all analyzed strings, with optional filtering.

Query Parameters:

is_palindrome=true|false

length_gt=<number>

word_count=<number>

Example:
GET /string?is_palindrome=true&length_gt=3

###4️⃣ DELETE /string/<string_value>

Delete a specific string from the database.

Response:
204 No Content

###5️⃣ GET /string/matches/<string_value>

Find similar strings using fuzzy matching.

Example:
GET /string/matches/helo

Response:

{
  "matches": ["hello", "help"]
}

⚙️ Installation & Setup
1. Clone the repository
git clone https://github.com/<your-username>/<your-repo>.git
cd <your-repo>

2. Create a virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On Mac/Linux
venv\Scripts\activate     # On Windows

3. Install dependencies
pip install -r requirements.txt

4. Run the app locally
python app.py


The API will be available at:
👉 http://127.0.0.1:5000

🐳 Running with Docker
Build the image
docker build -t string-analyzer .

Run the container
docker run -d -p 5000:5000 string-analyzer

📦 Requirements

Your requirements.txt should include:

Flask==3.0.3
waitress==3.0.0

🧱 Dockerfile
# Use a lightweight official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy dependency file and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Expose port
EXPOSE 5000

# Use production WSGI server
CMD ["waitress-serve", "--host=0.0.0.0", "--port=5000", "app:app"]

🧠 Technologies Used

Python 3.10+

Flask (Web Framework)

Waitress (Production WSGI server)

Difflib (for fuzzy matching)

Docker (Containerization)

🧪 Example cURL Commands

Add a string:

curl -X POST http://localhost:5000/string -H "Content-Type: application/json" -d '{"value": "hello world"}'


Retrieve all strings:

curl http://localhost:5000/string


Delete a string:

curl -X DELETE http://localhost:5000/string/hello

👨🏽‍💻 Author

Chima Samuel
📧 [your-email@example.com
]
🌍 GitHub Profile