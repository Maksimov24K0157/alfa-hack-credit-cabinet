from backend.database import init_db, reset_db
from backend.seed import seed_database

reset_db()
init_db()
seed_database()