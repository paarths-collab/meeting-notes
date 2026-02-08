import sys
import os
sys.path.insert(0, os.getcwd())

from backend.database import SessionLocal, init_db
from backend.models.database import User
from backend.auth import create_access_token, get_password_hash, verify_password
from backend.models.schemas import UserResponse
import jwt
from backend.auth import SECRET_KEY, ALGORITHM

# Initialize DB
init_db()
db = SessionLocal()

email = "test_repro@example.com"
password = "password123"

# 1. Create/Get User
user = db.query(User).filter(User.email == email).first()
if not user:
    print(f"Creating user {email}")
    user = User(
        email=email,
        hashed_password=get_password_hash(password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
else:
    print(f"User {email} exists")

# 2. Login (Get Token)
if not verify_password(password, user.hashed_password):
    print("ERROR: Password verification failed")
    sys.exit(1)

access_token = create_access_token(data={"sub": user.id})
print(f"Token: {access_token[:20]}...")

# 3. Decode Token (Simulate get_current_user)
try:
    payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
    user_id = payload.get("sub")
    print(f"Decoded user_id: {user_id} (Type: {type(user_id)})")
    
    if user_id is None:
        print("ERROR: user_id is None")
        sys.exit(1)
        
    # 4. Fetch User
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        print("ERROR: User not found in DB")
        sys.exit(1)
        
    print(f"User found: {db_user.email}")
    
    # 5. Validate Schema (Simulate UserResponse)
    try:
        user_response = UserResponse.from_orm(db_user)
        print("Schema Validation: SUCCESS")
        print(user_response.json())
    except Exception as e:
        print(f"ERROR: Schema Validation Failed: {e}")
        # Try Pydantic v2 method if v1 fails or vice-versa
        try:
             user_response = UserResponse.model_validate(db_user)
             print("Schema Validation (model_validate): SUCCESS")
        except Exception as e2:
             print(f"ERROR: Schema Validation (model_validate) Failed: {e2}")

except Exception as e:
    print(f"ERROR during token verification: {e}")
    sys.exit(1)

print("AUTH FLOW VERIFIED ✅")
