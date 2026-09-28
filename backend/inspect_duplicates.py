from app.db.database import SessionLocal
from app.models.db_models import WaterReading
 
db = SessionLocal()
for station_id in ["9101", "9102"]:
    print(f"--- Station {station_id} ---")
    rows = (
        db.query(WaterReading)
        .filter(WaterReading.station_id == station_id)
        .order_by(WaterReading.year)
        .all()
    )
    for r in rows:
        source_type = getattr(r, "source_type", None)
        print(
            f"id={r.id} year={r.year} name={r.station_name!r} "
            f"source={r.predicted_source} "
            f"conductivity={r.conductivity_min}-{r.conductivity_max} "
            f"source_type={source_type}"
        )