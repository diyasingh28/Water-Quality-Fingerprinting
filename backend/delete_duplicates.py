from app.db.database import SessionLocal
from app.models.db_models import WaterReading
 
IDS_TO_DELETE = [60, 61, 62, 63, 64]
 
db = SessionLocal()
for row_id in IDS_TO_DELETE:
    row = db.query(WaterReading).filter(WaterReading.id == row_id).first()
    if row:
        print(f"Deleting id={row.id} station={row.station_id} year={row.year} name={row.station_name!r}")
        db.delete(row)
    else:
        print(f"No row found with id={row_id} (already deleted?)")
 
db.commit()
print("Done.")
 