from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError

security = HTTPBearer()

SECRET_KEY = "7f9c6e4a8c2d1b3f9e6a7d5c4b2f1a9e6d3c5b7a9f2e4c6d8b1a3e5f7c9d2b4"
ALGORITHM = "HS256"


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("sub")
        role = payload.get("role")
        email = payload.get("email")

        if user_id is None or role is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        return {
            "id": int(user_id),
            "email": email,
            "role": role
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def require_student(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "student":
        raise HTTPException(status_code=403, detail="Only students can perform this action")
    return current_user