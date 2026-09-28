from sqlalchemy import text
from sqlalchemy.exc import OperationalError
 
from app.db.database import engine
from app.models.db_models import WaterReading
 
table_name = WaterReading.__tablename__
 
with engine.connect() as conn:
    for stmt in [
        f"ALTER TABLE {table_name} ADD COLUMN is_anomaly BOOLEAN DEFAULT 0",
        f"ALTER TABLE {table_name} ADD COLUMN anomaly_details TEXT",
    ]:
        try:
            conn.execute(text(stmt))
            conn.commit()
            print(f"Applied: {stmt}")
        except OperationalError as e:
            print(f"Skipped (likely already exists): {stmt} -- {e}")
 
print("Migration complete.")