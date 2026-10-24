import sqlalchemy
from sqlalchemy import text

engine = sqlalchemy.create_engine("sqlite+pysqlite:///:memory:", echo=True)

with engine.connect() as conn:
    result = conn.execute(text("SELECT 'test text'"))
    print(result.all())