import json
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import desc, select
from sqlalchemy.orm import Session
from ..config import get_settings
from ..database import get_db
from ..dependencies import get_current_user
from ..models.db import Recommendation, User
from ..models.schemas import HomeRequest, JewelryRequest, PartyRequest
from ..services.ai_service import generate_home, generate_jewelry, generate_party

router = APIRouter()
settings = get_settings()
ALLOWED_IMAGE_TYPES = {"image/jpeg","image/png","image/webp"}

def _save(db, user, planner_type, request_data, result):
    row = Recommendation(user_id=user.id, planner_type=planner_type, request_json=json.dumps(request_data), result_json=result.model_dump_json())
    db.add(row); db.commit(); db.refresh(row)
    return row

@router.post("/generate-home")
def generate_home_route(data: HomeRequest, user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    result = generate_home(data)
    row = _save(db,user,"home",data.model_dump(),result)
    return {"id":row.id,"result":result.model_dump()}

@router.post("/generate-party")
def generate_party_route(data: PartyRequest, user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    result = generate_party(data)
    row = _save(db,user,"party",data.model_dump(),result)
    return {"id":row.id,"result":result.model_dump()}

@router.post("/generate-jewelry")
async def generate_jewelry_route(total_budget: float=Form(...), occasion: str=Form(...), style_preferences: str=Form("elegant"), metal_preference: str=Form("any"), color_preference: str=Form(""), additional_requirements: str=Form(""), outfit_image: UploadFile|None=File(default=None), user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    data = JewelryRequest(total_budget=total_budget, occasion=occasion, style_preferences=style_preferences, metal_preference=metal_preference, color_preference=color_preference, additional_requirements=additional_requirements)
    image_bytes=None; mime_type=None
    if outfit_image:
        if outfit_image.content_type not in ALLOWED_IMAGE_TYPES: raise HTTPException(400,"Only JPG, PNG and WEBP images are supported.")
        image_bytes=await outfit_image.read()
        if len(image_bytes)>settings.max_upload_mb*1024*1024: raise HTTPException(413,f"Image must be <= {settings.max_upload_mb} MB.")
        mime_type=outfit_image.content_type
    result=generate_jewelry(data,image_bytes,mime_type)
    row=_save(db,user,"jewelry",{**data.model_dump(),"image_uploaded":bool(image_bytes)},result)
    return {"id":row.id,"result":result.model_dump()}

@router.get("/recommendations-details/{recommendation_id}")
def recommendation_details(recommendation_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    row=db.scalar(select(Recommendation).where(Recommendation.id==recommendation_id,Recommendation.user_id==user.id))
    if not row: raise HTTPException(404,"Recommendation not found.")
    return {"id":row.id,"planner_type":row.planner_type,"request":json.loads(row.request_json),"result":json.loads(row.result_json),"created_at":row.created_at.isoformat()}

@router.get("/history")
def history(user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    rows=db.scalars(select(Recommendation).where(Recommendation.user_id==user.id).order_by(desc(Recommendation.created_at)).limit(50)).all()
    return [{"id":r.id,"planner_type":r.planner_type,"created_at":r.created_at.isoformat(),"request":json.loads(r.request_json)} for r in rows]

@router.get("/history/{recommendation_id}")
def history_item(recommendation_id:int,user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    return recommendation_details(recommendation_id,user,db)
