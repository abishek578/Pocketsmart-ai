from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models.db import User

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def ctx(request: Request, user=None):
    return {
        "request": request,
        "user": user,
    }


@router.get("/")
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"user": None},
    )


@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={},
    )


@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="register.html",
        context={},
    )


@router.get("/dashboard")
def dashboard(
    request: Request,
    user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"user": user},
    )


@router.get("/home-planner")
def home_planner(
    request: Request,
    user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        request=request,
        name="home_planner.html",
        context={"user": user},
    )


@router.get("/party-planner")
def party_planner(
    request: Request,
    user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        request=request,
        name="party_planner.html",
        context={"user": user},
    )


@router.get("/jewelry-planner")
def jewelry_planner(
    request: Request,
    user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        request=request,
        name="jewelry_planner.html",
        context={"user": user},
    )


@router.get("/history-page")
def history_page(
    request: Request,
    user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        request=request,
        name="history.html",
        context={"user": user},
    )


@router.get("/recommendation/{recommendation_id}")
def recommendation_detail_page(
    recommendation_id: int,
    request: Request,
    user: User = Depends(get_current_user),
):
    return templates.TemplateResponse(
        request=request,
        name="recommendation_detail.html",
        context={
            "user": user,
            "recommendation_id": recommendation_id,
        },
    )