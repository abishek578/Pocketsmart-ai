from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Cookie, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .config import get_settings
from .database import get_db
from .models.db import User

settings = get_settings()
ALGORITHM = "HS256"

def create_access_token(user: User) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=settings.session_expire_minutes)
    return jwt.encode({"sub": str(user.id), "email": user.email, "exp": expires}, settings.secret_key, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    try: return jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
    except jwt.PyJWTError as exc: raise HTTPException(status_code=401, detail="Invalid or expired session.") from exc

def get_current_user(access_token: str | None = Cookie(default=None, alias=settings.session_cookie_name), db: Session = Depends(get_db)) -> User:
    if not access_token: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Login required.")
    payload = decode_access_token(access_token)
    user = db.get(User, int(payload["sub"]))
    if not user: raise HTTPException(status_code=401, detail="User not found.")
    return user
