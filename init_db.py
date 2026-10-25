from backend.database import init_db, reset_db
from backend.seed import seed_database, generate_historical_loans

reset_db()
init_db()
seed_database()
generate_historical_loans()