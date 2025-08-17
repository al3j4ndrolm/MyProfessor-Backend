# External imports
from fastapi.exceptions import HTTPException
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, Body
from pydantic import BaseModel

# Local imports
from api import response
from database import courses_db, classes_db, reports_db

# Initialize FastAPI app and router
app = FastAPI()
router = APIRouter()

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

class StartPostRequest(BaseModel):
    '''
    client_data = {
        "build_type": "dev" | "release",
        "platform": "iOS" | "Android"
    }
    user_data = {
        "is_new_user": "true" | "false"
    }
    '''
    client_data: dict
    user_data: dict

@router.post("/start")
def start_post(
    body: StartPostRequest = Body(...)
):
    if not body.client_data or not body.user_data:
        raise HTTPException(status_code=400)

    if body.client_data.get("build_type") is None or body.client_data.get("platform") is None:
        raise HTTPException(status_code=400)

    if body.user_data.get("is_new_user") is None:
        raise HTTPException(status_code=400)
    
    reports_db.save(supabase, body.client_data.get("build_type"), body.client_data.get("platform"), body.user_data)

    return response.response_start(supabase, body.client_data, body.user_data)

@router.get("/courses")
def courses_get(
    school: str = None
):
    if school is None:
        raise HTTPException(status_code=400)
    else:
        return courses_db.get(supabase, school)

@router.get("/classes")
def classes_get(
    school: str = None,
    term: str = None,
    department: str = None
):
    if school is None or term is None or department is None:
        raise HTTPException(status_code=400)
    else:
        return classes_db.get_one_entry(supabase, school, term, department)

class ReportsErrorsPostRequest(BaseModel):
    critical: bool
    details: str
    platform: str
    build: str
    version: str

@router.post("/reports/errors")
def reports_errors_post(
    body: ReportsErrorsPostRequest = Body(...)
):
    reports_db.save(supabase, body, is_error=True)

# TODO: Remove after client migrates to new classes endpoints
@router.get("/schools/")
@router.get("/schools")
def schools_get():
    return response.response_schools(supabase)

# TODO: Remove after client migrates to new classes endpoints
class ClassesPostRequest(BaseModel):
    school: str
    term: str
    department: str

app.include_router(router)
