from app.database.session import SessionLocal
from app.models.application import Application
from app.models.queue_assignment import QueueAssignment
from app.models.user import User

db = SessionLocal()
try:
    print("--- USERS ---")
    users = db.query(User).all()
    for u in users:
        print(f"User: {u.username}, Role: {u.role}, Dept: {u.department}")
        
    print("\n--- APPLICATIONS ---")
    apps = db.query(Application).all()
    for a in apps:
        print(f"ID: {a.application_id}, Status: {a.status}, Applicant: {a.applicant_name}, Cost: {a.estimated_cost}, Assigned to User ID: {a.assigned_to_user_id}")
        
    print("\n--- QUEUE ASSIGNMENTS ---")
    qas = db.query(QueueAssignment).all()
    for qa in qas:
        print(f"App ID: {qa.application_id}, Queue: {qa.queue_name}, Status: {qa.status}, Assigned to User ID: {qa.assigned_to_user_id}")
finally:
    db.close()
