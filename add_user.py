from database import SessionLocal
from models import User

db = SessionLocal()

new_user = User(
    name="Vishal",
    email="vishal@example.com",
    password_hash="dummy_hashed_password_123"
)

db.add(new_user)
db.commit()
db.refresh(new_user)

print("✅ User successfully save hua!")
print(f"User ID: {new_user.id}")
print(f"Name: {new_user.name}")
print(f"Email: {new_user.email}")

db.close()