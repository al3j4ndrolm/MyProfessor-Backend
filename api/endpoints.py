# External imports
from fastapi.exceptions import HTTPException
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, Body
from pydantic import BaseModel

# Local imports
from api import response
from database import courses_db, classes_db, reports_db, searches_db, summaries_db, db_keys

# Initialize FastAPI app and router
app = FastAPI()
router = APIRouter()

load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# GET ENDPOINTS ---------------------------------------------------------------

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
        searches_db.save(supabase, school, term, department)
        return classes_db.get_one_entry(supabase, school, term, department)

@router.get("/summary")
def summary_get(
    rmp_link: str = None
):
    if rmp_link is None:
        raise HTTPException(status_code=400)
    else:
        summary_entry = summaries_db.get_one_entry(supabase, rmp_link)
        return None if not summary_entry else summary_entry[db_keys.SUMMARIES_KEY_SUMMARY]

# POST ENDPOINTS ---------------------------------------------------------------

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
    reports_db.save_error(supabase, body.version, body.critical, body.details, body.platform, body.build)

app.include_router(router)
