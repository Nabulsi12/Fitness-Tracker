import sqlite3  # For interacting with the SQLite database
import hashlib  # For hashing passwords
from backend.db_users import get_connection  # Function to get a database connection to users.db


# Hashes a given password using SHA-256 for secure storage
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


# Checks if a user with the given username already exists in the database
def user_exists(username: str) -> bool:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT 1 FROM users WHERE username = ?", (username,))
    exists = c.fetchone() is not None
    conn.close()
    return exists


# Creates a new user if the username doesn't already exist
# Returns True if created successfully, False otherwise
def create_user(username: str, password: str) -> bool:
    if user_exists(username):
        return False  # Username already exists

    hashed = hash_password(password)  # Hash the password before saving
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # This error occurs if a duplicate username is inserted due to a UNIQUE constraint
        return False
    finally:
        conn.close()


# Verifies that the provided password matches the stored password for the username
def authenticate_user(username: str, password: str) -> bool:
    hashed = hash_password(password)  # Hash the entered password for comparison
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    return row is not None and row[0] == hashed


# Wrapper function for logging in — currently just calls authenticate_user
def login_user(username: str, password: str) -> bool:
    return authenticate_user(username, password)


# Wrapper function for signing up — currently just calls create_user
def signup_user(username: str, password: str) -> bool:
    return create_user(username, password)
