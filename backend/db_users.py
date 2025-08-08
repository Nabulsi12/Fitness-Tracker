# backend/db_users.py

import os
import sqlite3

def get_connection():
    """
    Connects to the users.db database inside the backend directory.
    Creates the file if it doesn't exist.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "users.db")

    # Create the file if it doesn't exist
    if not os.path.exists(db_path):
        open(db_path, "a").close()

    try:
        return sqlite3.connect(db_path)
    except Exception as e:
        print(f"[ERROR] Could not connect to users.db: {e}")
        raise


def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()



def create_user(username: str):
    """
    Adds a new user to the users table.
    """
    conn = get_connection()
    c = conn.cursor()

    c.execute("INSERT INTO users (username) VALUES (?)", (username,))
    conn.commit()
    conn.close()


def get_user_by_username(username: str):
    """
    Returns the user if they exist, otherwise None.
    """
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT username FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()

    return user
