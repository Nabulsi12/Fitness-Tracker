import sys
import os

# Add project root to Python path for imports (do this before imports)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(project_root)

# Import database initialization functions after sys.path is set
from backend.db_users import init_db as init_user_db
from backend.db_fitness.connection import init_db as init_fitness_db  # Fixed import here

# Initialize the databases (create tables if needed)
init_user_db()      # Initialize user database (users.db)
init_fitness_db()   # Initialize fitness database (fitness.db)

# Import the run_session after init_db is ready
from frontend.user_interface import run_session

def main():
    run_session()

if __name__ == "__main__":
    main()
