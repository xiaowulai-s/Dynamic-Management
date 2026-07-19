from app.database import SessionLocal
from app.models.user import User
from app.models.notification import Notification
from passlib.context import CryptContext

db = SessionLocal()
pwd = CryptContext(schemes=['bcrypt'], deprecated='auto')

test_accounts = [
    ("admin_test", "123456", "admin"),
    ("user_test", "123456", "user"),
]

for username, password, role in test_accounts:
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        existing.password_hash = pwd.hash(password)
        existing.role = role
        existing.is_test = True
        existing.is_active = True
        print(f"{username} updated")
    else:
        user = User(
            username=username,
            password_hash=pwd.hash(password),
            role=role,
            is_test=True,
            is_active=True
        )
        db.add(user)
        print(f"{username} created")

db.commit()
db.close()
print("DONE")
