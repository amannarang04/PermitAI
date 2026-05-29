from app.database.session import SessionLocal
from app.models.application import Application
from app.tasks.extraction_tasks import run_extraction_sync

db = SessionLocal()
try:
    received_apps = db.query(Application).filter(Application.status == "received").all()
    for app in received_apps:
        print(f"Processing app ID {app.id} ({app.application_id})...")
        res = run_extraction_sync(app.id)
        print(f"Result: {res}")
finally:
    db.close()
