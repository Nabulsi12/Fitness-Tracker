# Fitness Tracker App

A personal fitness tracker built with Streamlit and SQLite.  
Track workouts, save workout templates, and manage user authentication.

## Features

- User signup and login with secure password hashing  
- Add, edit, and delete workouts (strength, bodyweight, cardio)  
- Save workout templates for easy reuse  
- View a timeline of past workouts  
- Validation for workout inputs  
- SQLite backend with separate databases for users and fitness data  

## Folder Structure

Fitness-Tracker/
│
├── .vscode/
│ └── settings.json
│
├── backend/
│ ├── pycache/
│ ├── .db/
│ │     └── fitness.db
│ ├── db_fitness/
│ │     ├── pycache/
│ │     ├── __init__.py
│ │     ├── connection.py
│ │     ├── workouts.py
│ │     ├── templates.py
│ │__init__.py
│ ├── auth.py
│ ├── db_users.py
│ ├── filters.py
│ ├── models.py
│ ├── users.db
│ └── validators.py
│
├── frontend/
│ ├── pycache/
│ ├── __init__.py
│ ├── add_workout.py
│ ├── main.py
│ ├── templates.py
│ ├── timeline.py
│ └── user_interface.py
│
├── README.md
├── requirements.txt
└── when_running

---

## Setup & Run Instructions

1. Create a virtual environment (recommended):

python -m venv venv
# Activate the environment:
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

2. Install dependencies:
pip install -r requirements.txt

3. Run the app:
streamlit run frontend/main.py

4. Usage:

Sign up or log in with your username and password.

Use the sidebar to navigate between "Add Workout", "Templates", and "Timeline".

Add workouts manually or load/save templates for quick entry.

View your workout history on the timeline.