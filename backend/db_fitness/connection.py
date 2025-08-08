# backend/db_fitness/connection.py

import os
import sqlite3

def init_db():
    """
    Initializes the fitness.db database with all necessary tables:
    workouts, workout_exercises, exercise_sets, templates, template_exercises, template_sets.
    """
    conn = get_connection()
    c = conn.cursor()

    # Workouts core table
    c.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            name TEXT,
            type TEXT,
            date TEXT,
            duration_minutes REAL,
            distance_mi REAL,
            intensity TEXT
        )
    """)

    # Workout exercises table
    c.execute("""
        CREATE TABLE IF NOT EXISTS workout_exercises (
            workout_id TEXT,
            exercise_index INTEGER,
            name TEXT,
            type TEXT,
            PRIMARY KEY (workout_id, exercise_index)
        )
    """)

    # Exercise sets table
    c.execute("""
        CREATE TABLE IF NOT EXISTS exercise_sets (
            workout_id TEXT,
            exercise_index INTEGER,
            set_number INTEGER,
            reps INTEGER,
            weight REAL,
            PRIMARY KEY (workout_id, exercise_index, set_number)
        )
    """)

    # Templates core table
    c.execute("""
        CREATE TABLE IF NOT EXISTS templates (
            id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            name TEXT NOT NULL,
            type TEXT NOT NULL
        )
    """)

    # Template exercises table
    c.execute("""
        CREATE TABLE IF NOT EXISTS template_exercises (
            template_id TEXT,
            exercise_index INTEGER,
            name TEXT,
            type TEXT,
            PRIMARY KEY (template_id, exercise_index)
        )
    """)

    # Template sets table
    c.execute("""
        CREATE TABLE IF NOT EXISTS template_sets (
            template_id TEXT,
            exercise_index INTEGER,
            set_number INTEGER,
            reps INTEGER,
            weight REAL,
            PRIMARY KEY (template_id, exercise_index, set_number)
        )
    """)

    conn.commit()
    conn.close()

def get_connection():
    """
    Connects to the fitness database located in `.db/fitness.db`. Creates the directory/file if missing.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".db"))
    os.makedirs(base_dir, exist_ok=True)

    db_path = os.path.join(base_dir, "fitness.db")
    if not os.path.exists(db_path):
        open(db_path, "a").close()

    return sqlite3.connect(db_path)
