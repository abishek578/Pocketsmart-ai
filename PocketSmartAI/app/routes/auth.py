import hashlib, hmac, secrets
from fastapi import APIRouter, Depends, Form, status
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from ..config import get_settings
from ..database import get_db
from ..dependencies import create_access_token, get_current_user
from ..models.db import User
from ..models.schemas import LoginRequest, RegisterRequest

router = APIRouter()
settings = get_settings()

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 210_000)
    return f"{salt.hex()}${digest.hex()}"

def verify_password(password: str, encoded: str) -> bool:
    try:
        salt_hex, digest_hex = encoded.split("$", 1)
        expected = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), 210_000)
        return hmac.compare_digest(expected.hex(), digest_hex)
    except (ValueError, TypeError):
        return False

def set_session(response, user: User):
    response.set_cookie(settings.session_cookie_name, create_access_token(user), httponly=True, samesite="lax", secure=False, max_age=settings.session_expire_minutes*60)

@router.post("/register")
def register(email: str=Form(...), full_name: str=Form(...), password: str=Form(...), db: Session=Depends(get_db)):
    data = RegisterRequest(email=email, full_name=full_name, password=password)
    if db.scalar(select(User).where(User.email == data.email)):
        return JSONResponse({"detail":"Email is already registered."}, status_code=409)
    user = User(email=data.email, full_name=data.full_name, password_hash=hash_password(data.password))
    db.add(user); db.commit(); db.refresh(user)
    response = RedirectResponse("/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    set_session(response, user)
    return response

@router.post("/login")
def login(email: str=Form(...), password: str=Form(...), db: Session=Depends(get_db)):
    data = LoginRequest(email=email, password=password)
    user = db.scalar(select(User).where(User.email == data.email))
    if not user or not verify_password(data.password, user.password_hash):
        return JSONResponse({"detail":"Invalid email or password."}, status_code=401)
    response = RedirectResponse("/dashboard", status_code=status.HTTP_303_SEE_OTHER)
    set_session(response, user)
    return response

@router.post("/logout")
def logout():
    response = RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
    response.delete_cookie(settings.session_cookie_name)
    return response

@router.get("/token")
def token(user: User=Depends(get_current_user)):
    return {"access_token": create_access_token(user), "token_type":"bearer"}

@router.get("/session-info")
def session_info(user: User=Depends(get_current_user)):
    return {"logged_in":True,"user_id":user.id,"email":user.email,"full_name":user.full_name,"created_at":user.created_at.isoformat()}

@router.get("/session-data")
def session_data(user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    from ..models.db import Recommendation
    count = db.query(Recommendation).filter(Recommendation.user_id == user.id).count()
    return {"user_id":user.id,"recommendation_count":count}
